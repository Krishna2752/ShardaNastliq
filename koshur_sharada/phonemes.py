"""
Canonical phoneme inventory for Kashmiri (Koshur).

Every script module (persoarabic.py, sharada.py, devanagari.py) maps its
graphemes onto these phoneme IDs, and back. Adding a new target script
means writing one new mapping file against this list -- it never touches
the other scripts.

IDs are plain ASCII slugs, not IPA symbols, so they're safe to use as
dict keys / JSON keys / CLI args. The `ipa` field is for documentation
and for anyone who wants to plug in a phonological rule layer later.

Sources for the vowel inventory:
- Standard Brahmic vowels (a, aa, i, ii, u, uu, e, ai, o, au) -- shared
  with Sanskrit/Devanagari/Sharada.
- Kashmiri-specific central vowels (e, oe, ue, ...) -- per Vinodh Rajan,
  "Proposal to Encode Kashmiri Sharada Characters in Unicode",
  Unicode L2/23-122 (2023), which documents the 2002/2009 Devanagari
  conventions these are built from.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Phoneme:
    id: str            # stable key used everywhere else in the codebase
    ipa: str            # IPA approximation, for humans reading this file
    kind: str           # "vowel" | "consonant" | "modifier"
    length: Optional[str] = None   # "short" | "long" | None (consonants)
    notes: str = ""


# --- Vowels shared with Sanskrit/Devanagari/Sharada -------------------
SHARED_VOWELS = [
    Phoneme("a",   "ə~a",  "vowel", "short"),
    Phoneme("aa",  "aː",   "vowel", "long"),
    Phoneme("i",   "i",    "vowel", "short"),
    Phoneme("ii",  "iː",   "vowel", "long"),
    Phoneme("u",   "u",    "vowel", "short"),
    Phoneme("uu",  "uː",   "vowel", "long"),
    Phoneme("e",   "eː",   "vowel", "long"),
    Phoneme("ai",  "ɛː",   "vowel", "long"),
    Phoneme("o",   "oː",   "vowel", "long"),
    Phoneme("au",  "ɔː",   "vowel", "long"),
]

# --- Kashmiri-specific central vowels ----------------------------------
# These are the ones missing from plain Sharada (see module docstring).
# Naming follows the transliteration column in L2/23-122.
KASHMIRI_VOWELS = [
    Phoneme("schwa",      "ə",  "vowel", "short", "IPA ə,  2009 Devanagari ऺ"),
    Phoneme("schwa_long", "əː", "vowel", "long",  "IPA əː"),
    Phoneme("ue",         "ɨ",  "vowel", "short", "IPA ɨ,  central high unrounded"),
    Phoneme("uue",        "ɨː", "vowel", "long",  "IPA ɨː"),
    Phoneme("oe",         "ɔ",  "vowel", "short", "IPA ɔ  (short o)"),
    Phoneme("ooe",        "ɔː", "vowel", "long",  "IPA ɔː (long o)"),
]

VOWELS = SHARED_VOWELS + KASHMIRI_VOWELS

# --- Consonants ----------------------------------------------------------
# id, ipa, notes. Ordered roughly by place of articulation (velar -> glottal),
# matching traditional Brahmic ordering, since that's what Sharada consonant
# order and most reference charts assume.
CONSONANTS = [
    Phoneme("k",    "k",    "consonant"),
    Phoneme("kh",   "kʰ",   "consonant"),
    Phoneme("g",    "g",    "consonant"),
    Phoneme("gh",   "gʱ",   "consonant"),
    Phoneme("ng",   "ŋ",    "consonant"),
    Phoneme("c",    "t͡ʃ",  "consonant", notes="palatal, Sharada ca-row, Perso-Arabic چ"),
    Phoneme("ch",   "t͡ʃʰ", "consonant", notes="Perso-Arabic چھ"),
    Phoneme("j",    "d͡ʒ",  "consonant", notes="Perso-Arabic ج"),
    Phoneme("jh",   "d͡ʒʱ", "consonant", notes="Perso-Arabic جھ"),
    Phoneme("ny",   "ɲ",    "consonant"),
    Phoneme("ts",   "t͡s",  "consonant", notes="Kashmiri 'tse'; NOT in Sanskrit/plain-Sharada inventory. Perso-Arabic ژ"),
    Phoneme("tsh",  "t͡sʰ", "consonant", notes="aspirated tse, Perso-Arabic ژھ"),
    Phoneme("tt",   "ʈ",    "consonant", notes="retroflex, Perso-Arabic ٹ"),
    Phoneme("tth",  "ʈʰ",   "consonant"),
    Phoneme("dd",   "ɖ",    "consonant", notes="retroflex, Perso-Arabic ڈ"),
    Phoneme("ddh",  "ɖʱ",   "consonant"),
    Phoneme("nn",   "ɳ",    "consonant"),
    Phoneme("t",    "t̪",    "consonant"),
    Phoneme("th",   "t̪ʰ",   "consonant"),
    Phoneme("d",    "d̪",    "consonant"),
    Phoneme("dh",   "d̪ʱ",   "consonant"),
    Phoneme("n",    "n",    "consonant"),
    Phoneme("p",    "p",    "consonant"),
    Phoneme("ph",   "pʰ",   "consonant"),
    Phoneme("b",    "b",    "consonant"),
    Phoneme("bh",   "bʱ",   "consonant"),
    Phoneme("m",    "m",    "consonant"),
    Phoneme("y",    "j",    "consonant"),
    Phoneme("r",    "r",    "consonant"),
    Phoneme("rr",   "ɽ",    "consonant", notes="retroflex flap, Perso-Arabic ڑ"),
    Phoneme("l",    "l",    "consonant"),
    Phoneme("v",    "v",    "consonant"),
    Phoneme("sh",   "ʃ",    "consonant"),
    Phoneme("ss",   "ʂ",    "consonant"),
    Phoneme("s",    "s",    "consonant"),
    Phoneme("h",    "h",    "consonant"),
    Phoneme("z",    "z",    "consonant", notes="not in Sanskrit consonant set; needed for loanwords + native Kashmiri"),
    Phoneme("f",    "f",    "consonant", notes="loanword consonant"),
    Phoneme("q",    "q",    "consonant", notes="loanword consonant"),
    Phoneme("x",    "x",    "consonant", notes="loanword consonant (خ)"),
    Phoneme("gh_",  "ɣ",    "consonant", notes="loanword consonant (غ), distinct from aspirated gh"),
]

# --- Modifiers -------------------------------------------------------
MODIFIERS = [
    Phoneme("virama",     "",  "modifier", notes="vowel suppressor / consonant conjunct former"),
    Phoneme("anusvara",   "ṃ", "modifier"),
    Phoneme("visarga",    "ḥ", "modifier"),
    Phoneme("candrabindu","̃",  "modifier", notes="nasalization"),
    Phoneme("nukta",      "",  "modifier", notes="subscript dot for loan/retroflex consonants"),
]

ALL_PHONEMES = {p.id: p for p in VOWELS + CONSONANTS + MODIFIERS}


def get(phoneme_id: str) -> Phoneme:
    try:
        return ALL_PHONEMES[phoneme_id]
    except KeyError:
        raise KeyError(f"Unknown phoneme id: {phoneme_id!r}")
