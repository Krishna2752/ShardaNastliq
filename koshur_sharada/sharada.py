"""
Sharada <-> phoneme mapping.

Codepoints verified against the official Unicode Sharada block chart
(U+11180-U+111DF, https://www.unicode.org/charts/PDF/U11180.pdf) and the
Unicode block Wikipedia summary. Consonant/vowel names follow the
standard Brahmic naming convention used in the Unicode NamesList.

IMPORTANT -- Kashmiri-only vowels (schwa, ue, uue, oe, ooe, ...):
Plain Sharada has NO dedicated codepoints for these (see phonemes.py
docstring). Two encoding strategies exist; pick one via `KASHMIRI_VOWEL_MODE`:

  "sequence" (default) -- the convention actually used by the Kashmiri
      Sharada revival community (Core Sharada Foundation / Sanjeevani
      Sharda Kendra): write the nearest existing Sharada vowel sign
      followed by a Devanagari combining diacritic borrowed for the
      purpose. Renders in existing Sharada fonts, at the cost of being
      a mixed-script grapheme cluster.

  "pua" -- write into the Unicode Private Use Area using the code
      offsets proposed in L2/23-122, for projects willing to ship a
      custom font/rendering layer and want single-codepoint vowels.
      Swap PUA_BASE for the real block start the day Unicode assigns one.
"""

from typing import Dict, Tuple

KASHMIRI_VOWEL_MODE = "sequence"  # "sequence" | "pua"
PUA_BASE = 0xF200  # arbitrary private-use start; change if it collides
                    # with something else in your font/toolchain

# --- Independent vowels: SHARADA LETTER A .. AU, U+11183-U+11190 -------
INDEPENDENT_VOWELS: Dict[str, str] = {
    "a":  "\U00011183",
    "aa": "\U00011184",
    "i":  "\U00011185",
    "ii": "\U00011186",
    "u":  "\U00011187",
    "uu": "\U00011188",
    "e":  "\U0001118D",
    "ai": "\U0001118E",
    "o":  "\U0001118F",
    "au": "\U00011190",
}

# --- Dependent vowel signs (attach to a consonant), U+111B3-U+111BF ----
# Note: short "a" has NO vowel sign -- it's the inherent vowel of every
# consonant letter, removed by virama (U+111C0).
VOWEL_SIGNS: Dict[str, str] = {
    "aa": "\U000111B3",
    "i":  "\U000111B4",
    "ii": "\U000111B5",
    "u":  "\U000111B6",
    "uu": "\U000111B7",
    "e":  "\U000111BC",
    "ai": "\U000111BD",
    "o":  "\U000111BE",
    "au": "\U000111BF",
}

# Devanagari diacritics borrowed by the Sharada revival community for
# Kashmiri-only vowels, per L2/23-122 section 4.1. Combined with the
# nearest independent vowel / vowel sign above.
_KASHMIRI_DEVANAGARI_COMBINER = {
    "schwa":      "\u093A",  # DEVANAGARI VOWEL SIGN OE-ish short candra
    "schwa_long": "\u0945",  # DEVANAGARI VOWEL SIGN CANDRA E
    "ue":         "\u0956",  # DEVANAGARI VOWEL SIGN UE
    "uue":        "\u0957",  # DEVANAGARI VOWEL SIGN UUE
    "oe":         "\u0949",  # DEVANAGARI VOWEL SIGN CANDRA O (approx.)
    "ooe":        "\u0947",  # DEVANAGARI VOWEL SIGN E (used for long ooe)
}
# Which existing Sharada base each Kashmiri vowel rides on:
_KASHMIRI_BASE_INDEP = {"schwa": "a", "schwa_long": "aa", "ue": "a",
                         "uue": "aa", "oe": "o", "ooe": "o"}
_KASHMIRI_BASE_SIGN = dict(_KASHMIRI_BASE_INDEP)  # same pairing for signs

for _pid in _KASHMIRI_DEVANAGARI_COMBINER:
    INDEPENDENT_VOWELS[_pid] = (
        INDEPENDENT_VOWELS[_KASHMIRI_BASE_INDEP[_pid]]
        + _KASHMIRI_DEVANAGARI_COMBINER[_pid]
    )
    # Vowel signs for "a" have no dedicated sign (inherent vowel), so the
    # sign-form of schwa/ue is just the bare combiner; others attach to
    # the existing sign.
    _base = _KASHMIRI_BASE_SIGN[_pid]
    VOWEL_SIGNS[_pid] = (
        (VOWEL_SIGNS[_base] if _base in VOWEL_SIGNS else "")
        + _KASHMIRI_DEVANAGARI_COMBINER[_pid]
    )

# --- Consonants (inherent vowel "a"), U+11191-U+111B2 ------------------
CONSONANTS: Dict[str, str] = {
    "k":   "\U00011191", "kh": "\U00011192", "g":  "\U00011193",
    "gh":  "\U00011194", "ng": "\U00011195",
    "c":   "\U00011196", "ch": "\U00011197", "j":  "\U00011198",
    "jh":  "\U00011199", "ny": "\U0001119A",
    "tt":  "\U0001119B", "tth":"\U0001119C", "dd": "\U0001119D",
    "ddh": "\U0001119E", "nn": "\U0001119F",
    "t":   "\U000111A0", "th": "\U000111A1", "d":  "\U000111A2",
    "dh":  "\U000111A3", "n":  "\U000111A4",
    "p":   "\U000111A5", "ph": "\U000111A6", "b":  "\U000111A7",
    "bh":  "\U000111A8", "m":  "\U000111A9",
    "y":   "\U000111AA", "r":  "\U000111AB", "l":  "\U000111AC",
    "v":   "\U000111AE",
    "sh":  "\U000111AF", "ss": "\U000111B0", "s":  "\U000111B1",
    "h":   "\U000111B2",
    # Kashmiri needs a few more than plain Sanskrit Sharada provides;
    # represented with SHARADA SIGN NUKTA (U+111CA) on the nearest
    # existing letter, matching the Devanagari nukta convention.
    "z":   "\U000111B1" + "\U000111CA",  # sa + nukta (za)
    "rr":  "\U000111AB" + "\U000111CA",  # ra + nukta (rra / flap)
    "f":   "\U000111A6" + "\U000111CA",  # pha + nukta (fa)
    "q":   "\U00011191" + "\U000111CA",  # ka + nukta (qa)
    "x":   "\U00011192" + "\U000111CA",  # kha + nukta (xa)
    "gh_": "\U00011193" + "\U000111CA",  # ga + nukta (ghain)
    "ll":  "\U000111AD",
    # Kashmiri dental affricates /t͡s/ /t͡sʰ/ (Perso-Arabic ژ / ژھ) have no
    # native Sharada letter at all (not part of the Sanskrit inventory
    # Sharada was built for). Nukta-marked "ca"/"cha" is this project's
    # working convention, pending confirmation against what the Sharada
    # revival community's own primers actually use for these -- flag
    # for native-speaker/community review before treating as final.
    "ts":  "\U00011196" + "\U000111CA",  # ca + nukta
    "tsh": "\U00011197" + "\U000111CA",  # cha + nukta
}

VIRAMA = "\U000111C0"
ANUSVARA = "\U00011181"
VISARGA = "\U00011182"
CANDRABINDU = "\U00011180"
NUKTA = "\U000111CA"
DANDA = "\U000111C5"
DOUBLE_DANDA = "\U000111C6"

# Reverse lookups for Sharada -> phoneme direction
_REV_CONSONANTS: Dict[str, str] = {v: k for k, v in CONSONANTS.items()}
_REV_VOWEL_SIGNS: Dict[str, str] = {v: k for k, v in VOWEL_SIGNS.items() if v}
_REV_INDEP_VOWELS: Dict[str, str] = {v: k for k, v in INDEPENDENT_VOWELS.items()}


def consonant_to_sharada(phoneme_id: str) -> str:
    return CONSONANTS[phoneme_id]


def vowel_sign_to_sharada(phoneme_id: str) -> str:
    """Empty string for short 'a' -- it's inherent, no sign needed."""
    if phoneme_id == "a":
        return ""
    return VOWEL_SIGNS[phoneme_id]


def independent_vowel_to_sharada(phoneme_id: str) -> str:
    return INDEPENDENT_VOWELS[phoneme_id]


def sharada_consonant_to_phoneme(ch: str) -> str:
    return _REV_CONSONANTS[ch]


def sharada_vowel_sign_to_phoneme(ch: str) -> str:
    return _REV_VOWEL_SIGNS.get(ch, "a")
