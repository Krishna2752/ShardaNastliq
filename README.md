# koshur-sharada

A phoneme-hub transliteration engine between Kashmiri Perso-Arabic
(Nastaliq) and the Sharada script, built so a third/fourth script
(Devanagari, Roman) can be added later without touching the existing
mappings.

```
Perso-Arabic ─┐
              ├─→  Phoneme ID  ─┐
Sharada     ──┘                 ├─→ any target script
Devanagari  ──────(not yet)─────┘
```

## Status: working alpha, not yet validated by native speakers

The engine round-trips correctly for the cases tested (`k`+`aa`, the
Kashmiri schwa vowel, and virama-joined consonant clusters — see
`test_roundtrip` below). But several specific mapping choices are
**best-effort placeholders that need review by someone fluent in
Kashmiri and familiar with the Sharada revival materials**, not
verified linguistic fact:

1. **Kashmiri-only Sharada vowels have no real Unicode codepoints yet.**
   Plain Sharada (U+11180–U+111DF) only covers the Sanskrit vowel set.
   A 2023 Unicode proposal to add 8 Kashmiri vowel signs
   (Vinodh Rajan, L2/23-122) is still pending — no codepoints
   assigned, no font support. This package writes them as the
   community's actual workaround: nearest Sharada vowel + a borrowed
   Devanagari combining diacritic (`sharada.py`,
   `_KASHMIRI_DEVANAGARI_COMBINER`). **This is the single most
   important thing to validate against real Sharada-Kashmiri
   publications** (Core Sharada Foundation's *Kȫśura Praveśikā*,
   Sanjeevani Sharda Kendra's *Śāradā Vāṇī*) before trusting any
   output — my mapping of which vowel rides on which base letter is a
   reasonable guess from the proposal document, not a citation from
   those primers.

2. **Kashmiri's dental affricates (ژ /t͡s/, ژھ /t͡sʰ/) don't exist in
   Sharada at all** — not even as a gap-filler convention I could find
   documented. I'm currently rendering them as nukta-marked
   `ca`/`cha` (`sharada.py`, `CONSONANTS["ts"]`/`["tsh"]`). Flag this
   for community review before shipping.

3. **The Kashmiri-specific Perso-Arabic vowel diacritics** (what your
   spec called "toor" and "gord-zair") don't have one settled Unicode
   codepoint across fonts/keyboards. `persoarabic.py` picks specific
   Arabic diacritic codepoints as placeholders — validate these
   against whatever real Kashmiri Nastaliq corpus or keyboard layout
   (PASCII, CRULP, or a specific font's cmap) you're actually
   targeting.

4. **This engine assumes fully-diacritized Perso-Arabic input.** It
   does not attempt implicit vowel recovery itself — for real-world
   under-diacritized text, `persoarabic_to_sharada(text, diacritize=True)`
   (or the CLI's `--diacritize` flag) runs it through HNM Research's
   *Koshur Diacritizer* first, a byte-level seq2seq model built for
   exactly this (arXiv:2606.15883,
   [model on Hugging Face](https://huggingface.co/Omarrran/koshur-diacritizer-byt5-small)).
   It's optional — `pip install transformers torch` to use it; the rest
   of the package has no dependencies. The model's own reported accuracy
   against native-speaker judgment is 77.5%, so treat its output as a
   best-effort restoration, not certainly correct.

## Usage

```python
from koshur_sharada import sharada_to_persoarabic, persoarabic_to_sharada

persoarabic_to_sharada("کَاش")   # -> Sharada Unicode string
sharada_to_persoarabic(shr_text) # -> Perso-Arabic Unicode string

# under-diacritized input: restore diacritics first (pip install transformers torch)
persoarabic_to_sharada("کشر", diacritize=True)
```

```bash
python -m koshur_sharada.cli sh2pa "𑆑𑆳"
python -m koshur_sharada.cli pa2sh "کَا"
echo "𑆑𑆳" | python -m koshur_sharada.cli sh2pa
python -m koshur_sharada.cli pa2sh "کشر" --diacritize   # under-diacritized input
```

## Package layout

- `phonemes.py` — the shared phoneme inventory every script maps onto.
  Start here when adding a new script or fixing a wrong correspondence.
- `sharada.py` — Sharada codepoints (verified against the official
  Unicode block chart) + the Kashmiri-vowel workaround.
- `persoarabic.py` — Kashmiri Perso-Arabic letters and diacritics.
- `transliterate.py` — the actual parsing/rendering engine, script-agnostic
  except for calling into the two mapping modules above.
- `diacritizer.py` — optional wrapper around the Koshur Diacritizer model
  for under-diacritized Perso-Arabic input; lazily imports
  `transformers`/`torch` so the rest of the package stays dependency-free.
- `cli.py` — thin CLI wrapper.

## Next steps toward your original spec

- **Devanagari target** (tabled for now): add `devanagari.py` mirroring
  `sharada.py`'s shape (it's a strictly easier case — Devanagari already
  has official codepoints for all the Kashmiri vowels via the 2002/2009
  government orthography, so no workaround layer needed), then a
  `units_to_devanagari` / `devanagari_to_units` pair in
  `transliterate.py`.
- ~~**Implicit vowel recovery**~~ — done, see `diacritizer.py` and the
  `diacritize=True` / `--diacritize` option above.
- **Web demo**: see `demo/` — a static page (Pyodide-based, so it runs
  the actual `koshur_sharada` source in-browser rather than a re-port)
  with Noto Sans Sharada and Noto Nastaliq Urdu loaded for correct
  rendering. Covers `sh2pa`/`pa2sh` only — the diacritizer needs
  `transformers`/`torch` and isn't wired into the browser demo.
- **Validation set**: `tests/test_coverage.py` is a combinatorial suite
  (every consonant × every vowel × nasalization × clusters) that checks
  the engine's own internal round-trip consistency across its full
  table, not linguistic correctness — there's no independently-verified
  real-Kashmiri-text corpus available to check against yet. See
  `REVIEW.md` for the specific unverified linguistic decisions a native
  speaker or the Core Sharada Foundation / Sanjeevani Sharda Kendra
  would need to check before this ships for real use.
