"""
Core engine. Everything routes through a list of "Unit" objects -- one
per syllable-forming event -- so adding a fourth script later means
writing a `text_to_units` / `units_to_text` pair for it and nothing else.

This is a deterministic, rule-based engine. It assumes vowel diacritics
are ALREADY PRESENT in Perso-Arabic input (i.e. it does the "Explicit
Phonetic Alignment" half of your spec, not the "Implicit Vowel Recovery"
half). For real-world under-diacritized Kashmiri text, run it through a
diacritizer first -- see README for why we recommend reusing the
existing Koshur Diacritizer model rather than rebuilding one here.
"""

from dataclasses import dataclass
from typing import List, Optional

from . import sharada as shr
from . import persoarabic as pa
from .phonemes import get as get_phoneme


@dataclass
class Unit:
    consonant: Optional[str]   # phoneme id, or None for a standalone vowel
    vowel: str                 # phoneme id; defaults to inherent "a"
    nasalized: bool = False
    is_word_boundary: bool = False


# ---------------------------------------------------------------- Sharada

def sharada_to_units(text: str) -> List[Unit]:
    units: List[Unit] = []
    i = 0
    while i < len(text):
        ch = text[i]

        if ch in (" ", "\n", "\t"):
            units.append(Unit(None, "", is_word_boundary=True))
            i += 1
            continue

        two_char = text[i:i + 2]
        cons_phoneme = None
        if two_char in shr._REV_CONSONANTS:
            # Nukta-marked consonants (z, rr, f, q, x, gh_, ts, tsh) are
            # TWO codepoints (base letter + U+111CA NUKTA). Must be tried
            # before the single-character lookup below, or the nukta gets
            # silently dropped and the wrong (un-nuktaed) consonant comes
            # out -- this was a real bug caught by
            # tests/test_roundtrip.py::test_aspirated_consonant.
            cons_phoneme = shr.sharada_consonant_to_phoneme(two_char)
            i += 2
        elif ch in shr._REV_CONSONANTS:
            cons_phoneme = shr.sharada_consonant_to_phoneme(ch)
            i += 1

        if cons_phoneme is not None:
            vowel_phoneme = "a"  # inherent, unless overridden below
            nasal = False

            if i < len(text) and text[i] == shr.VIRAMA:
                vowel_phoneme = ""  # explicit vowel suppression
                i += 1
            elif i < len(text) and text[i] in shr._REV_VOWEL_SIGNS:
                # greedily try the 2-char Kashmiri sequence first
                two = text[i:i + 2]
                if two in shr._REV_VOWEL_SIGNS:
                    vowel_phoneme = shr._REV_VOWEL_SIGNS[two]
                    i += 2
                else:
                    vowel_phoneme = shr._REV_VOWEL_SIGNS[text[i]]
                    i += 1

            if i < len(text) and text[i] == shr.ANUSVARA:
                nasal = True
                i += 1

            units.append(Unit(cons_phoneme, vowel_phoneme, nasalized=nasal))
            continue

        if ch in shr._REV_INDEP_VOWELS:
            two = text[i:i + 2]
            if two in shr._REV_INDEP_VOWELS:
                units.append(Unit(None, shr._REV_INDEP_VOWELS[two]))
                i += 2
            else:
                units.append(Unit(None, shr._REV_INDEP_VOWELS[ch]))
                i += 1
            continue

        # Unrecognized character (punctuation, danda, etc.) -- pass through
        units.append(Unit(None, "", is_word_boundary=False))
        i += 1

    return units


def units_to_sharada(units: List[Unit]) -> str:
    out = []
    for u in units:
        if u.is_word_boundary:
            out.append(" ")
            continue
        if u.consonant is None:
            if u.vowel:
                out.append(shr.independent_vowel_to_sharada(u.vowel))
            continue
        out.append(shr.consonant_to_sharada(u.consonant))
        if u.vowel == "":
            out.append(shr.VIRAMA)
        elif u.vowel != "a":
            out.append(shr.vowel_sign_to_sharada(u.vowel))
        if u.nasalized:
            out.append(shr.ANUSVARA)
    return "".join(out)


# ----------------------------------------------------------- Perso-Arabic

def units_to_persoarabic(units: List[Unit]) -> str:
    out = []
    for u in units:
        if u.is_word_boundary:
            out.append(" ")
            continue

        if u.consonant is None:
            # standalone vowel: alef + diacritic, or alef + matra letter
            if u.vowel in pa.LONG_VOWEL_SEQUENCES:
                out.append(pa.ALEF + pa.LONG_VOWEL_SEQUENCES[u.vowel])
            elif u.vowel in pa.VOWEL_DIACRITIC_TO_PHONEME.values():
                diac = next(k for k, v in pa.VOWEL_DIACRITIC_TO_PHONEME.items() if v == u.vowel)
                out.append(pa.ALEF + diac)
            if u.nasalized:
                out.append(pa.NASAL_MARK)
            continue

        # Aspirated consonant?
        base = None
        for asp_id, base_id in pa.ASPIRATED_PAIRS.items():
            if asp_id == u.consonant:
                base = base_id
                break
        if base:
            out.append(pa.CONSONANTS[base] + pa.ASPIRATE_MARK)
        else:
            out.append(pa.CONSONANTS.get(u.consonant, "?"))

        if u.vowel == "" :
            out.append(pa.SUKUN)
        elif u.vowel == "a":
            pass  # inherent-ish; Perso-Arabic usually leaves short 'a' unmarked
        elif u.vowel in pa.LONG_VOWEL_SEQUENCES:
            out.append(pa.LONG_VOWEL_SEQUENCES[u.vowel])
        elif u.vowel in pa.VOWEL_DIACRITIC_TO_PHONEME.values():
            diac = next(k for k, v in pa.VOWEL_DIACRITIC_TO_PHONEME.items() if v == u.vowel)
            out.append(diac)

        if u.nasalized:
            # NOTE: this was missing entirely until tests/test_roundtrip.py
            # ::test_nasalized_vowel caught it -- a Sharada anusvara/
            # candrabindu was silently dropped on the way out to
            # Perso-Arabic instead of becoming NASAL_MARK.
            out.append(pa.NASAL_MARK)
    return "".join(out)


def persoarabic_to_units(text: str) -> List[Unit]:
    """
    Assumes fully-diacritized input. Under-diacritized real-world text
    should go through a restoration model first (see README).
    """
    units: List[Unit] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in (" ", "\n", "\t"):
            units.append(Unit(None, "", is_word_boundary=True))
            i += 1
            continue

        if ch == pa.ALEF:
            # standalone vowel
            i += 1
            matched = False
            for phon, seq in pa.LONG_VOWEL_SEQUENCES.items():
                if text[i:i + len(seq)] == seq:
                    units.append(Unit(None, phon))
                    i += len(seq)
                    matched = True
                    break
            vowel = None
            if not matched and i < len(text) and text[i] in pa.VOWEL_DIACRITIC_TO_PHONEME:
                vowel = pa.VOWEL_DIACRITIC_TO_PHONEME[text[i]]
                i += 1
            elif not matched:
                vowel = "a"
            if vowel is not None:
                nasal = False
                if i < len(text) and text[i] == pa.NASAL_MARK:
                    nasal = True
                    i += 1
                units.append(Unit(None, vowel, nasalized=nasal))
            elif matched:
                # the LONG_VOWEL_SEQUENCES branch above already appended a
                # Unit without checking for a trailing nasal mark; check now
                if i < len(text) and text[i] == pa.NASAL_MARK:
                    units[-1].nasalized = True
                    i += 1
            continue

        if ch in pa._REV_CONSONANTS:
            cons = pa._REV_CONSONANTS[ch]
            i += 1
            # aspiration?
            if i < len(text) and text[i] == pa.ASPIRATE_MARK:
                for asp_id, base_id in pa.ASPIRATED_PAIRS.items():
                    if base_id == cons:
                        cons = asp_id
                        break
                i += 1
            vowel = "a"
            matched = False
            for phon, seq in pa.LONG_VOWEL_SEQUENCES.items():
                if text[i:i + len(seq)] == seq:
                    vowel = phon
                    i += len(seq)
                    matched = True
                    break
            if not matched and i < len(text) and text[i] == pa.SUKUN:
                vowel = ""
                i += 1
            elif not matched and i < len(text) and text[i] in pa.VOWEL_DIACRITIC_TO_PHONEME:
                vowel = pa.VOWEL_DIACRITIC_TO_PHONEME[text[i]]
                i += 1
            nasal = False
            if i < len(text) and text[i] == pa.NASAL_MARK:
                nasal = True
                i += 1
            units.append(Unit(cons, vowel, nasalized=nasal))
            continue

        units.append(Unit(None, "", is_word_boundary=False))
        i += 1

    return units


# ---------------------------------------------------------------- Public API

def sharada_to_persoarabic(text: str) -> str:
    return units_to_persoarabic(sharada_to_units(text))


def persoarabic_to_sharada(text: str, diacritize: bool = False) -> str:
    """
    diacritize=True runs `text` through the optional Koshur Diacritizer
    model first (see diacritizer.py) for under-diacritized input. Requires
    `pip install transformers torch`; the import only happens if this flag
    is used, so the rest of the package stays dependency-free.
    """
    if diacritize:
        from .diacritizer import restore_diacritics
        text = restore_diacritics(text)
    return units_to_sharada(persoarabic_to_units(text))
