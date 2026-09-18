"""
Kashmiri Perso-Arabic <-> phoneme mapping.

Base consonant inventory cross-checked against the "Kashmiri alphabet"
sidebar reproduced on multiple Wikipedia extended-Arabic-letter pages
(e.g. the Dal/Rre/Tte articles), which lists:

    ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ
    ع غ ف ق ک گ ل م ن (ں) و ۆ ۄ ھ ء ی ؠ ے

and against Unicode's own Kashmiri-specific-character notes (e.g.
U+0673 ARABIC LETTER ALEF WITH WAVY HAMZA BELOW and U+06C4 ARABIC LETTER
WAW WITH RING are documented by the Unicode Consortium as Kashmiri
letters).

CONFIDENCE NOTE: consonant-to-phoneme correspondences below are
reasonably solid (standard Urdu-derived retroflex/dental distinctions
apply the same way in Kashmiri). The vowel-diacritic layer is the part
that most needs a native-speaker/linguist pass before this ships:
Kashmiri's ~16-way vowel distinction is realized through combinations
of the standard Arabic short-vowel marks (zabar/zer/pesh) plus several
Kashmiri-only marks that don't have one settled Unicode representation
across fonts (this is exactly the "diacritic recovery" problem your
spec called out, and it's also why the Koshur Diacritizer model exists
-- see README).
"""

from typing import Dict

# --- Consonants ---------------------------------------------------------
CONSONANTS: Dict[str, str] = {
    "b":   "\u0628",  # ب
    "p":   "\u067E",  # پ
    "t":   "\u062A",  # ت  (dental)
    "tt":  "\u0679",  # ٹ  (retroflex)
    "s":   "\u062B",  # ث  (merges with s in speech)
    "j":   "\u062C",  # ج  (palatal)
    "c":   "\u0686",  # چ  (palatal)
    "h":   "\u062D",  # ح
    "x":   "\u062E",  # خ
    "d":   "\u062F",  # د  (dental)
    "dd":  "\u0688",  # ڈ  (retroflex)
    "z":   "\u0630",  # ذ
    "r":   "\u0631",  # ر
    "rr":  "\u0691",  # ڑ  (retroflex flap)
    "z2":  "\u0632",  # ز  (a second /z/ letter; kept distinct at grapheme level)
    "ts":  "\u0698",  # ژ  ("tse" /t͡s/ -- see phonemes.py note)
    "ss":  "\u0633",  # س
    "sh":  "\u0634",  # ش
    "s2":  "\u0635",  # ص
    "z3":  "\u0636",  # ض
    "t2":  "\u0637",  # ط
    "z4":  "\u0638",  # ظ
    "gh_": "\u063A",  # غ
    "f":   "\u0641",  # ف
    "q":   "\u0642",  # ق
    "k":   "\u06A9",  # ک
    "g":   "\u06AF",  # گ
    "l":   "\u0644",  # ل
    "m":   "\u0645",  # م
    "n":   "\u0646",  # ن
    "v":   "\u0648",  # و  (also carries vowel duty -- see VOWELS)
    "h2":  "\u06BE",  # ھ  (aspiration marker, used after consonants)
    "y":   "\u06CC",  # ی  (also carries vowel duty -- see VOWELS)
    "ye":  "\u0620",  # ؠ  (Kashmiri-specific yeh variant)
}

# Aspirated consonants are written as base letter + ھ (U+06BE) in Urdu-
# derived orthographies; Kashmiri follows the same convention.
ASPIRATE_MARK = "\u06BE"  # ھ
ASPIRATED_PAIRS = {
    "kh": "k", "gh": "g", "ch": "c", "jh": "j",
    "tth": "tt", "ddh": "dd", "th": "t", "dh": "d",
    "ph": "p", "bh": "b", "tsh": "ts",
}

# --- Vowel diacritics (harakat) -----------------------------------------
# Standard Arabic short-vowel marks, reused for Kashmiri's short vowels.
ZABAR  = "\u064E"   # فَتحہ  -- short a
ZER    = "\u0650"   # کسرہ  -- short i
PESH   = "\u064F"   # پیش   -- short u
SUKUN  = "\u0652"   # no vowel (virama-equivalent)

# Kashmiri-specific vowel marks used in Nastaliq typesetting for the
# central vowels. These do NOT have one universally agreed codepoint
# across fonts/keyboards -- treat this table as a starting point to
# validate against whatever input corpus/keyboard layout you target
# (e.g. the CRULP or PASCII conventions), not as settled fact.
GORD_ZAIR = "\u065B"  # ٛ  ARABIC VOWEL SIGN INVERTED SMALL V ABOVE (proposed use: schwa-length marker)
TOOR      = "\u0656"  # ٖ  ARABIC SUBSCRIPT ALEF (proposed use: /ɨ/-adjacent)

VOWEL_DIACRITIC_TO_PHONEME: Dict[str, str] = {
    ZABAR: "a",
    ZER: "i",
    PESH: "u",
    GORD_ZAIR: "schwa",
    TOOR: "ue",
}

# Long vowels and diphthongs are written as short-vowel diacritic +
# matra letter (alef/waw/yeh), same principle as Urdu.
ALEF = "\u0627"  # ا
WAW  = "\u0648"  # و
YEH  = "\u06CC"  # ی

LONG_VOWEL_SEQUENCES: Dict[str, str] = {
    "aa": ZABAR + ALEF,
    "ii": ZER + YEH,
    "uu": PESH + WAW,
    "e":  ZER + YEH,     # context-dependent vs "ii" -- needs diacritizer disambiguation
    "o":  PESH + WAW,    # context-dependent vs "uu"
    "au": ZABAR + WAW,
    "ai": ZABAR + YEH,
}

# --- Nasalization ---------------------------------------------------
# Kashmiri (like Urdu) marks vowel nasalization with noon ghunna, distinct
# from the full ن consonant. Written word-finally after the vowel.
NASAL_MARK = "\u06BA"  # ں  ARABIC LETTER NOON GHUNNA

_REV_CONSONANTS: Dict[str, str] = {v: k for k, v in CONSONANTS.items()}
