# Context: koshur-sharada

For whoever (including future-you) picks this up next.

## What this is

A phoneme-hub transliteration engine between Kashmiri Perso-Arabic
(Nastaliq) and Sharada, for eventual submission to the KashmirAI
resource hub (kashmirairesearch.online/resources). Architecture:

```
Perso-Arabic ─┐
              ├─→  Phoneme ID  ─┐
Sharada     ──┘                 ├─→ any target script
Devanagari  ──────(not built)───┘
```

See `README.md` for usage and the up-to-date list of what's verified
vs. provisional. This file is the "why" and "what we already ruled
out" — read it before re-deriving something that was already checked.

## Facts established from primary sources (not guesses)

- **Sharada Unicode block**: U+11180–U+111DF, verified against the
  official Unicode chart (unicode.org/charts/PDF/U11180.pdf). All
  consonant/vowel codepoints in `sharada.py` are cited from there, not
  from memory or a secondary source.
- **Plain Sharada has no codepoints for Kashmiri's central vowels**
  (schwa, ɨ, ɔ and long forms). A 2023 Unicode proposal to add 8 new
  vowel signs (Vinodh Rajan, L2/23-122) is still pending — not
  standardized, no font support. The Kashmiri Sharada revival
  community (Core Sharada Foundation, Sanjeevani Sharda Kendra) works
  around this by writing the nearest existing Sharada vowel + a
  borrowed Devanagari combining diacritic. That's what `sharada.py`
  does. **This workaround is the single biggest thing to get a native
  speaker / the revival community to sanity-check** — my mapping of
  which vowel rides on which base letter is inferred from the proposal
  document, not copied from an actual primer.
- **Kashmiri's dental affricates (ژ /t͡s/, ژھ /t͡sʰ/) don't exist in
  Sharada at all** — they're outside the Sanskrit inventory Sharada
  was designed for. No documented community convention was found for
  these either. Currently rendered as nukta-marked ca/cha; flag for
  review.
- **An existing model already does the diacritic-recovery problem**:
  HNM Research's *Koshur Diacritizer* (arXiv:2606.15883), byte-level
  seq2seq, listed on the KashmirAI hub. Don't rebuild this — wrap it
  as a preprocessing step in front of `persoarabic_to_sharada()`.

## A candidate pipeline we evaluated and rejected

Someone (or something) produced an alternative Perso-Arabic→Sharada
pipeline with the same two-stage shape (diacritic restorer +
transliteration engine). It looked plausible on inspection but broke
on its own bundled test sentence:

```
Input:  کشر زبان پرن لِکھن
Output: 𑆑𑆶𑆯𑆴𑆱 ز𑆬𑆳𑆩 𑆪𑆱𑆩 𑆬𑆴𑆑ھ𑆩
```

Two problems visible without reading Sharada: a raw `ز` and a raw `ھ`
leak straight into the output. The more serious problem needed
checking against the actual Unicode chart: **its consonant table was
correct for the first ~16 entries then silently scrambled** — ن
(na) pointed at the MA glyph, م (ma) at the VA glyph, ر (ra) at the SA
glyph, پ (pa) at the YA glyph, and so on. It read as fluent Sharada,
which is the dangerous failure mode: wrong output that only someone
who can actually read the script would catch.

**Lesson taken from this**: `tests/test_roundtrip.py::TestVerifiedCodepoints`
exists specifically to pin every consonant to an explicit `U+XXXXX`
literal cross-checked against the chart, so this exact class of bug
fails a test instead of shipping silently. If you add a new consonant
to `sharada.py`, add a corresponding pinned assertion.

## Bugs the test suite caught in *our own* first draft

Writing the tests wasn't just precautionary — it immediately found two
real bugs in the engine, both now fixed (see `transliterate.py` for
the fix comments, and the corresponding tests):

1. **Nukta-marked consonants (z, rr, f, q, x, gh_, ts, tsh) are two
   codepoints** (base letter + U+111CA NUKTA), but `sharada_to_units`
   was only ever checking single characters. Result: parsing
   `𑆗𑇊` (cha+nukta, meant as "tsh") silently dropped the nukta and
   read it back as plain "ch" — caught by `test_aspirated_consonant`.
2. **Nasalization was only implemented for the Sharada side.**
   `units_to_persoarabic` never emitted the Kashmiri nasal mark
   (`ں`, U+06BA) for a nasalized vowel, and `persoarabic_to_units`
   never read it back in — an anusvara/candrabindu would silently
   vanish on a round trip through Perso-Arabic. Caught by
   `test_nasalized_vowel`.

## Genuine (not-a-bug) limitations pinned by tests, not silently accepted

- **e/ii and o/uu share one Perso-Arabic spelling.** Kashmiri/Urdu-style
  orthography writes long-i and long-e both as ZER+YEH, and long-u and
  long-o both as PESH+WAW. There's no diacritic-only way to distinguish
  them in the script itself — this is a property of the orthography,
  not something to "fix" in code. See
  `test_e_and_ii_share_one_perso_arabic_spelling`.
- **Explicit-but-conventionally-omitted short-a (zabar) doesn't
  round-trip.** Perso-Arabic (like Urdu) normally leaves the short-a
  diacritic unwritten on a bare consonant; this renderer follows that
  convention on output, so writing zabar explicitly on input and
  expecting it back out doesn't hold. See the `*_normalizes_*` tests
  in `TestPersoArabicRoundTrip`.

## Still open (not started)

- Devanagari as a third target script. (Tabled for now, by request.)

## Done since the above was written

- **Koshur Diacritizer wiring**: `koshur_sharada/diacritizer.py` wraps
  the real model (`Omarrran/koshur-diacritizer-byt5-small` on Hugging
  Face) behind `persoarabic_to_sharada(text, diacritize=True)` / the
  CLI's `--diacritize` flag. Lazily imports `transformers`/`torch` so the
  core engine still has zero required dependencies.
- **Combinatorial coverage suite** (`tests/test_coverage.py`): every
  consonant supported by both scripts × every unambiguous shared vowel,
  plus nasalization and consonant clusters, round-tripped and checked for
  internal consistency (836 cases, all passing as of this writing). This
  is NOT a linguistic validation set — see the file's own docstring and
  `REVIEW.md` for why a real gold-standard set wasn't buildable without a
  verified source.
- **Native-speaker review packet** (`REVIEW.md`): a standalone document
  listing every specific unverified linguistic decision (the vowel
  workaround table, the ts/tsh nukta convention, the Perso-Arabic
  diacritic codepoints) with rendered examples, written for a native
  Kashmiri speaker or the Sharada revival community to actually check —
  this still needs a human with that expertise to close out, which is not
  something achievable from inside this codebase.
- **Web demo** (`demo/`): a live browser page
  ([published here](https://claude.ai/artifact/GJTEa7WVYtq6GZi3Hjg2nW))
  covering `sh2pa`/`pa2sh`. Runs a JS port of `transliterate.py`'s control
  flow (Pyodide wasn't viable in a static-artifact sandbox — its runtime
  needs binary asset fetches that get blocked); the codepoint TABLES are
  generated straight from `sharada.py`/`persoarabic.py` by
  `demo/generate_data.py` rather than hand-retyped into JS, and the JS
  port was cross-checked against the real Python engine across all 836
  coverage-suite cases before publishing (0 mismatches) to catch exactly
  the kind of silent-drift bug this file warns about elsewhere.
