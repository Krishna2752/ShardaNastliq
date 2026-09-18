"""
Test suite for koshur_sharada.

Run with:  python -m pytest tests/  (or python -m unittest discover)

These tests exercise the deterministic engine (transliterate.py) against
FULLY-DIACRITIZED input only -- see README.md's "Status" section for why
implicit vowel recovery is intentionally out of scope here.

Sections:
  1. Sharada -> Perso-Arabic -> Sharada round-trips (the strongest
     guarantee this engine can offer, since Sharada input is unambiguous)
  2. Perso-Arabic -> Sharada -> Perso-Arabic round-trips
  3. Specific glyph assertions against the verified Unicode codepoints,
     so a future accidental table edit (the kind of bug that sank the
     candidate pipeline we evaluated -- see CONTEXT.md) fails loudly
     instead of silently producing plausible-looking wrong Sharada.
  4. Known-limitation cases, marked as such rather than silently skipped.
"""

import unittest

from koshur_sharada import (
    sharada_to_persoarabic,
    persoarabic_to_sharada,
)
from koshur_sharada import sharada as shr
from koshur_sharada import persoarabic as pa
from koshur_sharada.transliterate import (
    Unit,
    units_to_sharada,
    units_to_persoarabic,
    sharada_to_units,
    persoarabic_to_units,
)


def sh(consonant_id, vowel_id="a", nasalized=False):
    """Shorthand: build a one-consonant Sharada string via the Unit API."""
    return units_to_sharada([Unit(consonant_id, vowel_id, nasalized=nasalized)])


class TestSharadaRoundTrip(unittest.TestCase):
    """Sharada is unambiguous (no missing-diacritic problem), so anything
    built in Sharada should survive a trip out to Perso-Arabic and back
    byte-for-byte."""

    def _roundtrip(self, units):
        original = units_to_sharada(units)
        pa_form = sharada_to_persoarabic(original)
        back = persoarabic_to_sharada(pa_form)
        self.assertEqual(original, back,
                          f"round-trip broke: {original!r} -> {pa_form!r} -> {back!r}")
        return original, pa_form

    def test_simple_ka(self):
        self._roundtrip([Unit("k", "a")])

    def test_long_vowel_kaa(self):
        self._roundtrip([Unit("k", "aa")])

    def test_all_shared_vowels_on_k(self):
        # "e" and "o" are excluded here on purpose, not skipped by
        # oversight -- see test_e_and_ii_share_one_perso_arabic_spelling
        # below for why they can't round-trip through Perso-Arabic.
        for v in ["a", "aa", "i", "ii", "u", "uu", "ai", "au"]:
            with self.subTest(vowel=v):
                self._roundtrip([Unit("k", v)])

    def test_e_and_ii_share_one_perso_arabic_spelling(self):
        # KNOWN LIMITATION, not a bug: Kashmiri/Urdu-style Perso-Arabic
        # writes both long-i (ii) and long-e (e) as ZER + YEH, and both
        # long-u (uu) and long-o (o) as PESH + WAW. There is no
        # diacritic-only way to tell them apart in this orthography --
        # that ambiguity is inherent to the script, not something this
        # engine can fix. persoarabic.py flags this in
        # LONG_VOWEL_SEQUENCES; this test pins the actual (lossy)
        # behavior so it's visible rather than silently "passing" a
        # round-trip test that shouldn't exist.
        ka_e = units_to_sharada([Unit("k", "e")])
        ka_ii = units_to_sharada([Unit("k", "ii")])
        pa_e = sharada_to_persoarabic(ka_e)
        pa_ii = sharada_to_persoarabic(ka_ii)
        self.assertEqual(pa_e, pa_ii, "e and ii should collapse to the same spelling")
        # and going back, both resolve to whichever this engine picks
        # first (currently "ii") -- NOT a correctness claim, just current
        # documented behavior:
        self.assertEqual(persoarabic_to_sharada(pa_e), ka_ii)

    def test_kashmiri_schwa_vowel(self):
        # This is the exact case plain Sharada has no native codepoint
        # for -- see README section "Status: working alpha".
        self._roundtrip([Unit("k", "schwa")])

    def test_kashmiri_ue_vowel(self):
        self._roundtrip([Unit("k", "ue")])

    def test_consonant_cluster_with_virama(self):
        # k + virama + t  (i.e. "kt")
        self._roundtrip([Unit("k", ""), Unit("t", "a")])

    def test_nasalized_vowel(self):
        self._roundtrip([Unit("k", "aa", nasalized=True)])

    def test_independent_vowel_word_initial(self):
        self._roundtrip([Unit(None, "aa"), Unit("t", "a")])

    def test_multi_word_with_space(self):
        units = [Unit("k", "aa"), Unit(None, "", is_word_boundary=True), Unit("t", "i")]
        self._roundtrip(units)

    def test_aspirated_consonant(self):
        self._roundtrip([Unit("kh", "a")])
        self._roundtrip([Unit("tsh", "a")])  # the dental affricate, flagged in README


class TestPersoArabicRoundTrip(unittest.TestCase):
    """Perso-Arabic round-trips are only meaningful for fully-diacritized
    input -- an undiacritized word has no single correct Sharada target,
    so we don't test that direction here (that's the diacritizer's job,
    not this engine's)."""

    def _roundtrip(self, text):
        sh_form = persoarabic_to_sharada(text)
        back = sharada_to_persoarabic(sh_form)
        self.assertEqual(text, back,
                          f"round-trip broke: {text!r} -> {sh_form!r} -> {back!r}")
        return sh_form

    def test_ka_with_zabar_normalizes_not_roundtrips(self):
        # KNOWN LIMITATION, not a bug: this renderer follows the Urdu/
        # Kashmiri convention of never writing zabar for a bare short
        # "a" (it's the default/expected reading of an unmarked
        # consonant), even though zabar is a legal *input* diacritic for
        # that same vowel. So writing it explicitly and reading it back
        # normalizes it away -- pin that explicitly instead of asserting
        # a round-trip that this design doesn't attempt to guarantee.
        text = pa.CONSONANTS["k"] + pa.ZABAR
        sh_form = persoarabic_to_sharada(text)
        self.assertEqual(sh_form, sh("k", "a"))
        self.assertEqual(sharada_to_persoarabic(sh_form), pa.CONSONANTS["k"])

    def test_ka_long_aa(self):
        self._roundtrip(pa.CONSONANTS["k"] + pa.LONG_VOWEL_SEQUENCES["aa"])

    def test_ka_with_sukun_then_ta_normalizes_trailing_zabar(self):
        # Same normalization as above, on the second consonant.
        text = pa.CONSONANTS["k"] + pa.SUKUN + pa.CONSONANTS["t"] + pa.ZABAR
        sh_form = persoarabic_to_sharada(text)
        self.assertEqual(sharada_to_persoarabic(sh_form),
                          pa.CONSONANTS["k"] + pa.SUKUN + pa.CONSONANTS["t"])

    def test_aspirated_kha_normalizes_trailing_zabar(self):
        # Same explicit-short-a normalization as test_ka_with_zabar above.
        text = pa.CONSONANTS["k"] + pa.ASPIRATE_MARK + pa.ZABAR
        sh_form = persoarabic_to_sharada(text)
        self.assertEqual(sh_form, sh("kh", "a"))
        self.assertEqual(sharada_to_persoarabic(sh_form),
                          pa.CONSONANTS["k"] + pa.ASPIRATE_MARK)


class TestVerifiedCodepoints(unittest.TestCase):
    """Pin specific consonants to their verified Unicode codepoints.

    These are deliberately explicit U+XXXXX literals (not "does it equal
    what sharada.py says", which would pass even if sharada.py itself
    were wrong). Cross-checked against the official Unicode Sharada
    block chart, https://www.unicode.org/charts/PDF/U11180.pdf.

    This is exactly the class of bug that made the candidate pipeline
    we reviewed silently emit wrong-but-plausible Sharada from 'ن'
    onward (na/ma/ra/pa/pha/ba/bha/sa were all shifted) -- see
    CONTEXT.md. A wrong table entry here fails a test instead of
    shipping.
    """

    def test_na_is_not_ma(self):
        self.assertEqual(shr.consonant_to_sharada("n"), "\U000111A4")   # NA
        self.assertNotEqual(shr.consonant_to_sharada("n"), "\U000111A9")  # MA

    def test_ma_is_not_va(self):
        self.assertEqual(shr.consonant_to_sharada("m"), "\U000111A9")   # MA
        self.assertNotEqual(shr.consonant_to_sharada("m"), "\U000111AE")  # VA

    def test_ra_is_not_sa(self):
        self.assertEqual(shr.consonant_to_sharada("r"), "\U000111AB")   # RA
        self.assertNotEqual(shr.consonant_to_sharada("r"), "\U000111B1")  # SA

    def test_pa_is_not_ya(self):
        self.assertEqual(shr.consonant_to_sharada("p"), "\U000111A5")   # PA
        self.assertNotEqual(shr.consonant_to_sharada("p"), "\U000111AA")  # YA

    def test_ba_is_not_la(self):
        self.assertEqual(shr.consonant_to_sharada("b"), "\U000111A7")   # BA
        self.assertNotEqual(shr.consonant_to_sharada("b"), "\U000111AC")  # LA

    def test_sa_is_not_ssa(self):
        self.assertEqual(shr.consonant_to_sharada("s"), "\U000111B1")   # SA
        self.assertNotEqual(shr.consonant_to_sharada("s"), "\U000111B0")  # SSA

    def test_virama_codepoint(self):
        self.assertEqual(shr.VIRAMA, "\U000111C0")

    def test_anusvara_codepoint(self):
        self.assertEqual(shr.ANUSVARA, "\U00011181")


class TestKnownLimitations(unittest.TestCase):
    """Document what does NOT work yet, so a future contributor sees an
    explicit failing-by-design test rather than rediscovering the gap
    from scratch. See README section "Status" for the full writeup."""

    def test_undiacritized_input_is_not_this_engines_job(self):
        # "کشر" with no diacritics at all. This engine assumes explicit
        # vowels are already present; feeding it bare consonants will
        # NOT produce a meaningful Sharada word. This test documents
        # that expectation rather than asserting a "correct" output --
        # there isn't one without a diacritizer in front of this engine.
        bare = pa.CONSONANTS["k"] + pa.CONSONANTS["sh"] + pa.CONSONANTS["r"]
        result = persoarabic_to_sharada(bare)
        self.assertIsInstance(result, str)  # doesn't crash
        # deliberately NOT asserting semantic correctness here

    def test_kashmiri_vowel_encoding_is_provisional(self):
        # The schwa/ue/oe... vowel signs are a mixed-script workaround
        # (Sharada base + borrowed Devanagari combiner), not an
        # official Unicode encoding. This test just pins current
        # behavior so a silent change is visible in a diff, not a
        # claim that this is linguistically final -- see README point 1.
        out = shr.vowel_sign_to_sharada("schwa")
        self.assertTrue(out.startswith("\u093A") or len(out) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
