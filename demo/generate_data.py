"""
Dumps the authoritative Python mapping tables (sharada.py, persoarabic.py)
to demo/data.json for the browser demo's JS port to consume.

Why: the web demo needs to run in a static Artifact page, which can't
actually execute Pyodide reliably (its runtime needs many binary asset
fetches the sandbox blocks) or ship transformers/torch for the
diacritizer. So demo.js re-implements transliterate.py's CONTROL FLOW in
JS -- but the CODEPOINT TABLES themselves are generated here, straight
from sharada.py/persoarabic.py, instead of hand-transcribed into JS. That
keeps exactly one authoritative source for the data that matters most
(see CONTEXT.md on why a silently-wrong table is the dangerous failure
mode here); only the control flow is duplicated, not the data.

Run with:  python demo/generate_data.py
(regenerate this whenever sharada.py or persoarabic.py change)
"""

import json
import os

from koshur_sharada import sharada as shr
from koshur_sharada import persoarabic as pa

data = {
    "sharada": {
        "independentVowels": shr.INDEPENDENT_VOWELS,
        "vowelSigns": shr.VOWEL_SIGNS,
        "consonants": shr.CONSONANTS,
        "virama": shr.VIRAMA,
        "anusvara": shr.ANUSVARA,
    },
    "persoarabic": {
        "consonants": pa.CONSONANTS,
        "aspiratePairs": pa.ASPIRATED_PAIRS,
        "aspirateMark": pa.ASPIRATE_MARK,
        "vowelDiacriticToPhoneme": pa.VOWEL_DIACRITIC_TO_PHONEME,
        "longVowelSequences": pa.LONG_VOWEL_SEQUENCES,
        "alef": pa.ALEF,
        "sukun": pa.SUKUN,
        "nasalMark": pa.NASAL_MARK,
    },
}

out_path = os.path.join(os.path.dirname(__file__), "data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"wrote {out_path}")
