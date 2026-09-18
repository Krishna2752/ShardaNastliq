"""
Combinatorial coverage suite: every consonant supported by BOTH scripts,
crossed with every non-ambiguous shared vowel, round-tripped in both
directions -- plus nasalization and consonant clusters across the same
consonant list.

WHAT THIS IS NOT: a linguistic validation set. It doesn't check output
against a Sharada primer, a native speaker, or any other independently-
verified source -- none was available (see README.md's "Status" section
and REVIEW.md for why, and what's still unverified). Nothing here proves
the *linguistic* correctness of any mapping.

WHAT THIS IS: a check on the engine's own internal consistency across its
FULL mapping table. test_roundtrip.py's example-based tests exercise a
handful of consonants (mostly "k"); a table typo/regression on, say,
consonant #30 could slip past those the same way the candidate pipeline's
scrambled table in CONTEXT.md slipped past a fluent-looking read. This
suite would catch that regardless of which entry breaks.
"""

import unittest

from koshur_sharada import sharada_to_persoarabic, persoarabic_to_sharada
from koshur_sharada import sharada as shr
from koshur_sharada import persoarabic as pa
from koshur_sharada.transliterate import Unit, units_to_sharada

# Consonants with a defined mapping on BOTH the Sharada side (sharada.py)
# and the Perso-Arabic side (persoarabic.py) -- the ones this project
# currently supports round-tripping for. (Sharada-only: ll/ng/nn/ny --
# no Perso-Arabic letter mapped yet. Perso-Arabic-only: h2/s2/t2/ye/z2/
# z3/z4 -- extra Arabic letters not yet routed to a Sharada nukta form.)
_SHARADA_CONSONANTS = set(shr.CONSONANTS)
_PERSOARABIC_CONSONANTS = set(pa._REV_CONSONANTS.values()) | set(pa.ASPIRATED_PAIRS)
SHARED_CONSONANTS = sorted(_SHARADA_CONSONANTS & _PERSOARABIC_CONSONANTS)

# Vowels with a defined mapping on both sides. "e" and "o" are deliberately
# excluded here -- they collapse with "ii"/"uu" in Perso-Arabic BY DESIGN
# (see test_roundtrip.py::test_e_and_ii_share_one_perso_arabic_spelling),
# so asserting a round-trip on them would be asserting a guarantee this
# engine explicitly does not offer.
SHARED_VOWELS = sorted(
    (set(shr.VOWEL_SIGNS) | {"a"})
    & (set(pa.VOWEL_DIACRITIC_TO_PHONEME.values()) | set(pa.LONG_VOWEL_SEQUENCES) | {"a"})
    - {"e", "o"}
)


class TestCoverageIsNonTrivial(unittest.TestCase):
    """Guard against this suite silently covering nothing (e.g. an import
    or set-intersection typo emptying the lists above), which would make
    every test below vacuously pass without exercising anything."""

    def test_shared_consonants_list_is_populated(self):
        self.assertGreaterEqual(len(SHARED_CONSONANTS), 30, SHARED_CONSONANTS)

    def test_shared_vowels_list_is_populated(self):
        self.assertGreaterEqual(len(SHARED_VOWELS), 8, SHARED_VOWELS)


class TestConsonantVowelCoverage(unittest.TestCase):
    """Every (consonant, vowel) pair the engine claims to support,
    round-tripped Sharada -> Perso-Arabic -> Sharada."""

    def test_every_consonant_every_vowel_roundtrips(self):
        failures = []
        for c in SHARED_CONSONANTS:
            for v in SHARED_VOWELS:
                original = units_to_sharada([Unit(c, v)])
                back = persoarabic_to_sharada(sharada_to_persoarabic(original))
                if back != original:
                    failures.append((c, v, original, back))
        self.assertEqual(
            failures, [],
            f"{len(failures)}/{len(SHARED_CONSONANTS) * len(SHARED_VOWELS)} "
            f"(consonant, vowel) pairs failed to round-trip: "
            f"{failures[:10]}{' ...' if len(failures) > 10 else ''}",
        )

    def test_every_consonant_nasalized(self):
        failures = []
        for c in SHARED_CONSONANTS:
            original = units_to_sharada([Unit(c, "aa", nasalized=True)])
            back = persoarabic_to_sharada(sharada_to_persoarabic(original))
            if back != original:
                failures.append((c, original, back))
        self.assertEqual(failures, [], f"nasalization broke for: {failures}")


class TestConsonantClusterCoverage(unittest.TestCase):
    """Every consonant as both the virama-suppressed first member and the
    vowel-bearing second member of a two-consonant cluster, cycling once
    through the list each way (O(n), not the full O(n^2) cross product --
    n^2 buys little extra confidence here for 37x the runtime)."""

    def test_clusters_roundtrip(self):
        failures = []
        n = len(SHARED_CONSONANTS)
        for i, c1 in enumerate(SHARED_CONSONANTS):
            c2 = SHARED_CONSONANTS[(i + 1) % n]
            units = [Unit(c1, ""), Unit(c2, "a")]
            original = units_to_sharada(units)
            back = persoarabic_to_sharada(sharada_to_persoarabic(original))
            if back != original:
                failures.append((c1, c2, original, back))
        self.assertEqual(
            failures, [],
            f"{len(failures)}/{n} clusters failed to round-trip: {failures[:10]}"
            f"{' ...' if len(failures) > 10 else ''}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
