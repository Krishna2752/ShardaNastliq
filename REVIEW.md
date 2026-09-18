# Review request: koshur-sharada mapping decisions

**Who this is for**: someone fluent in Kashmiri who is also familiar with
the Sharada revival materials (e.g. Core Sharada Foundation's *Kȫśura
Praveśikā*, Sanjeevani Sharda Kendra's *Śāradā Vāṇī*) — not a software
reviewer. You don't need to read code or install anything to help with
this: the [live browser demo](https://claude.ai/artifact/GJTEa7WVYtq6GZi3Hjg2nW)
lets you type Sharada or Perso-Arabic text and see what this engine
produces in the other script.

This project (`koshur-sharada`, a Perso-Arabic ↔ Sharada transliteration
engine, see `README.md`) is a working alpha built without native-speaker
input at any stage. Everything below is a specific point where the code
made a guess instead of citing a source, and needs a yes/no/correction
before this is trusted for real use. Where possible, each item shows the
exact rendered output so you can judge it directly rather than reading
Unicode names.

If you can point to a specific example in an actual Sharada-Kashmiri
publication for any of these (a photo of a page, a page number, anything
citable), that's more valuable than a general impression — the goal is to
replace a guess with a citation, not just a "looks fine."

---

## 1. Kashmiri-only vowels (no Unicode codepoint exists yet)

Plain Sharada (Unicode block U+11180–U+111DF) only covers the Sanskrit
vowel set: a, ā, i, ī, u, ū, e, ai, o, au. Kashmiri has additional central
vowels — schwa (ə), a long schwa, /ɨ/, a long /ɨ/, a short and long /ɔ/ —
that have no assigned codepoint. A 2023 Unicode proposal (Vinodh Rajan,
L2/23-122) covers this but nothing has been assigned yet.

This engine's current workaround: write the **nearest existing Sharada
vowel**, then a **borrowed Devanagari combining diacritic**, based on
reading the proposal document — not copied from an actual primer:

| Kashmiri vowel | rides on Sharada base | on consonant क/𑆑 (k) | as an independent vowel |
|---|---|---|---|
| schwa (ə) | a | 𑆑ऺ | 𑆃ऺ |
| long schwa (əː) | ā | 𑆑𑆳ॅ | 𑆄ॅ |
| ue (ɨ) | a | 𑆑ॖ | 𑆃ॖ |
| long ue (ɨː) | ā | 𑆑𑆳ॗ | 𑆄ॗ |
| oe (ɔ) | o | 𑆑𑆾ॉ | 𑆏ॉ |
| long oe (ɔː) | o | 𑆑𑆾े | 𑆏े |

**Questions for review:**
- Is "nearest base vowel + Devanagari combiner" the convention actually
  used in Sharada-Kashmiri materials, or is there a different convention
  (e.g. a different existing Sharada mark repurposed, or plain
  transliteration into Devanagari for these words instead)?
- If the general approach is right, is each vowel riding on the *correct*
  base letter? E.g. is short "ue" really closer to "a" than to "i", is
  "oe" really built on "o"?
- Are the specific Devanagari combining marks chosen (e.g. U+093A for
  schwa, U+0956 for ue) the ones actually used, or arbitrary substitutes?

(Code: `koshur_sharada/sharada.py`, `_KASHMIRI_DEVANAGARI_COMBINER` and
`_KASHMIRI_BASE_INDEP`/`_KASHMIRI_BASE_SIGN`.)

---

## 2. Kashmiri dental affricates ts/tsh (ژ / ژھ) — no Sharada letter at all

Kashmiri's /t͡s/ and /t͡sʰ/ sounds (written ژ and ژھ in Perso-Arabic) are
outside the Sanskrit consonant inventory Sharada was designed for, and no
documented gap-filling convention was found for them.

Current placeholder: nukta-marked "ca"/"cha" (the same device Devanagari
uses for loan consonants like क़/ख़):

| Kashmiri consonant | Perso-Arabic | this engine's Sharada rendering |
|---|---|---|
| ts (/t͡s/) | ژ | 𑆖𑇊  (ca + nukta) |
| tsh (/t͡sʰ/) | ژھ | 𑆗𑇊  (cha + nukta) |

**Question for review:** is nukta-marked ca/cha an actual convention seen
in Sharada-Kashmiri writing for these two sounds, or is there a different
established gap-filler (or should these simply not be written in Sharada
at all)?

(Code: `koshur_sharada/sharada.py`, `CONSONANTS["ts"]` / `["tsh"]`.)

---

## 3. Kashmiri-specific Perso-Arabic vowel diacritics ("toor", "gord-zair")

Kashmiri Nastaliq needs a couple of vowel marks beyond the standard
Arabic zabar/zer/pesh, and there's no single codepoint agreed on across
fonts/keyboards for them. This engine currently picks:

| name | codepoint | example (on ک / k) |
|---|---|---|
| gord-zair (schwa marker) | U+065B ARABIC VOWEL SIGN INVERTED SMALL V ABOVE | کٛ |
| toor (/ɨ/-adjacent marker) | U+0656 ARABIC SUBSCRIPT ALEF | کٖ |

**Question for review:** do these match what you'd actually see typed in
Kashmiri Nastaliq (e.g. via a PASCII or CRULP keyboard layout, or a
specific font's cmap), or are they placeholders that happen to render but
aren't what real text uses?

(Code: `koshur_sharada/persoarabic.py`, `GORD_ZAIR` / `TOOR`.)

---

## 4. General consonant/vowel correspondence sanity check

The base Sharada codepoints are cross-checked against the official
Unicode chart (unicode.org/charts/PDF/U11180.pdf) and pinned in
`tests/test_roundtrip.py::TestVerifiedCodepoints`, so those specific
glyph assignments (na ≠ ma ≠ ra ≠ ..., etc.) are correct as *Unicode*, not
just plausible-looking. What hasn't been checked is whether the
*linguistic* pairing is right end-to-end — e.g. whether Kashmiri's retroflex
flap really corresponds to Sharada's ऱ-equivalent the way this engine
assumes, or whether the standard Urdu-derived consonant-to-phoneme
readings in `persoarabic.py` hold the same way in Kashmiri as in Urdu for
every letter, not just the common ones.

The full table is easiest to check via the
[live demo](https://claude.ai/artifact/GJTEa7WVYtq6GZi3Hjg2nW) — type a
real Kashmiri word you know the correct Sharada (or Perso-Arabic) spelling
for, and see whether the other side matches.

---

## How to send back feedback

Any of these is useful, roughly in order of how directly it helps:

1. A specific citation ("*Kȫśura Praveśikā*, page N, shows X for Y") —
   turns a guess directly into a fact.
2. "This is wrong, it should be ___" for any row above.
3. "This looks right" for any specific row — confirms it doesn't need
   further work, which is also useful signal.

There's no deadline tied to this — it's a prerequisite for treating this
engine as more than a working prototype, tracked in `README.md`'s
"Status" section and `CONTEXT.md`.
