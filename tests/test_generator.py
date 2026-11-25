from itertools import product
from math import log2
from string import digits
import unittest
from unittest.mock import patch

from spoken_otp import ENGLISH_HEURISTIC, OTPGenerator, SpeechProfile


class GeneratorTests(unittest.TestCase):
    def test_every_rank_maps_to_exactly_one_eligible_code(self):
        profile = SpeechProfile(
            digit_penalties=(0, 3, 2, 0, 4, 1, 2, 1, 0, 1),
            pair_penalties={"01": 5, "88": 1, "30": 2},
        )
        codes = ["".join(group) for group in product(digits, repeat=3)]
        scores = {code: profile.score(code) for code in codes}
        cutoff = sorted(scores.values())[149]
        expected = [code for code in codes if scores[code] <= cutoff]
        generator = OTPGenerator(length=3, min_candidates=150, profile=profile)

        self.assertGreater(len(expected), 150)
        self.assertEqual(generator.score_cutoff, cutoff)
        self.assertEqual(generator.candidate_count, len(expected))
        self.assertEqual(generator.entropy_bits, log2(len(expected)))
        with patch("spoken_otp.generator.secrets.randbelow", side_effect=range(len(expected))) as draw:
            self.assertEqual([generator.generate() for _ in expected], expected)
            self.assertTrue(all(call.args == (len(expected),) for call in draw.call_args_list))

    def test_full_space_preserves_leading_zeros_and_upper_edge(self):
        generator = OTPGenerator(length=4, min_candidates=10_000)
        self.assertEqual(generator.candidate_count, 10_000)
        with patch("spoken_otp.generator.secrets.randbelow", side_effect=[0, 9999]):
            self.assertEqual(generator.generate(), "0000")
            self.assertEqual(generator.generate(), "9999")

    def test_zero_penalties_keep_full_space_even_at_maximum_length(self):
        generator = OTPGenerator(length=12, min_candidates=1, profile=SpeechProfile())
        self.assertEqual(generator.candidate_count, 10**12)
        self.assertEqual(generator.score_cutoff, 0)
        with patch("spoken_otp.generator.secrets.randbelow", return_value=81234):
            self.assertEqual(generator.generate(), "000000081234")

    def test_default_pool_keeps_its_floor_and_excludes_higher_scores(self):
        generator = OTPGenerator()
        self.assertGreaterEqual(generator.entropy_bits, 19)
        self.assertLess(generator.candidate_count, 10**6)
        code = generator.generate()
        self.assertRegex(code, r"^[0-9]{6}$")
        self.assertLessEqual(ENGLISH_HEURISTIC.score(code), generator.score_cutoff)

    def test_rejects_invalid_or_impossible_parameters(self):
        for length, min_candidates in [(4, 10_001), (0, 1), (13, 1), (4, 0), (True, 1), (4, 1.5)]:
            with self.subTest(length=length, min_candidates=min_candidates):
                with self.assertRaises(ValueError):
                    OTPGenerator(length=length, min_candidates=min_candidates)


class ProfileTests(unittest.TestCase):
    def test_uses_adjacent_pairs_in_order_and_copies_input(self):
        penalties = {"82": 2}
        profile = SpeechProfile(pair_penalties=penalties)
        penalties["82"] = 9
        self.assertEqual(profile.score("8282"), 4)
        self.assertEqual(profile.score("28"), 0)

    def test_rejects_invalid_profile_weights_and_codes(self):
        for penalties in [{"8": 1}, {"８2": 1}, {"82": -1}, {"82": 11}, {"82": 0.5}]:
            with self.subTest(penalties=penalties):
                with self.assertRaises(ValueError):
                    SpeechProfile(pair_penalties=penalties)
        with self.assertRaises(ValueError):
            SpeechProfile(digit_penalties=(0,) * 9)
        for code in ["", "10 2", "８2"]:
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    ENGLISH_HEURISTIC.score(code)
