"""Tests for Campus Lost & Found Matcher (optional for submission)."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main


class MatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file_patch = patch.object(main, "DATA_FILE", Path(self.temp.name) / "reports.json")
        self.file_patch.start()
        self.addCleanup(self.file_patch.stop)
        self.addCleanup(self.temp.cleanup)
        self.lost = main.ItemReport(1, "lost", "Bottle", "Black", "Fisher Library",
                                    "metal water bottle with sticker")
        self.found = main.ItemReport(2, "found", "Bottle", "black", "fisher library",
                                     "metal water bottle with sticker")

    def test_exact_properties_get_100(self):
        self.assertEqual(main.calculate_match_score(self.lost, self.found), 100)

    def test_wrong_category_gets_zero(self):
        other = main.ItemReport(3, "found", "Keys", "Black", "Fisher Library", "metal")
        self.assertEqual(main.calculate_match_score(self.lost, other), 0)

    def test_normalization_and_common_words(self):
        self.assertEqual(main.normalise(" FISHER   library "), "fisher library")
        self.assertEqual(main.description_words("A BLACK, metal bottle!"),
                         {"black", "metal", "bottle"})

    def test_save_and_reload(self):
        main.save_reports([self.lost, self.found])
        reloaded = main.load_reports()
        self.assertEqual(len(reloaded), 2)
        self.assertEqual(reloaded[1].report_type, "found")
        self.assertEqual(reloaded[0].status, "active")

    def test_id_is_unique(self):
        self.assertEqual(main.next_report_id([self.lost, self.found]), 3)
        self.assertEqual(main.next_report_id([]), 1)

    def test_resolved_report_not_matched(self):
        self.found.status = "resolved"
        out = io.StringIO()
        with patch("builtins.input", return_value="1"), redirect_stdout(out):
            main.find_matches([self.lost, self.found])
        self.assertIn("No close matches", out.getvalue())

    def test_highest_score_first(self):
        weaker = main.ItemReport(3, "found", "Bottle", "blue", "Other building",
                                 "metal water object")
        out = io.StringIO()
        with patch("builtins.input", return_value="1"), redirect_stdout(out):
            main.find_matches([self.lost, weaker, self.found])
        output = out.getvalue()
        self.assertLess(output.index("Similarity score: 100/100"),
                        output.index("Similarity score: 50/100"))

    def test_corrupt_file_does_not_disappear(self):
        main.DATA_FILE.write_text("broken JSON", encoding="utf-8")
        with self.assertRaises(ValueError):
            main.load_reports()
        self.assertEqual(main.DATA_FILE.read_text(encoding="utf-8"), "broken JSON")

    def test_mark_resolved_persists(self):
        main.save_reports([self.lost])
        out = io.StringIO()
        with patch("builtins.input", return_value="1"), redirect_stdout(out):
            main.mark_resolved([self.lost])
        self.assertEqual(main.load_reports()[0].status, "resolved")

    def test_add_report_rejects_empty_values(self):
        answers = iter(["2", "  ", "Black", "Fisher Library", "Metal bottle"])
        out = io.StringIO()
        with patch("builtins.input", side_effect=lambda *_: next(answers)), redirect_stdout(out):
            reports = []
            main.add_report(reports, "lost")
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].category, "Bottle")
        self.assertIn("cannot be empty", out.getvalue())


    def test_match_reasons_are_explained(self):
        score, reasons = main.match_breakdown(self.lost, self.found)
        self.assertEqual(score, 100)
        self.assertIn("Same category (+40)", reasons)
        self.assertIn("Same colour (+25)", reasons)
        self.assertIn("Same location (+15)", reasons)
        self.assertIn("Shared description words (+20)", reasons)

    def test_other_category_requires_shared_descriptive_word(self):
        lost = main.ItemReport(1, "lost", "Other", "red", "Library", "red umbrella")
        found = main.ItemReport(2, "found", "Other", "red", "Library", "red headphones")
        # Red is only a shared colour word; for broad "Other" that is not enough.
        self.assertEqual(main.calculate_match_score(lost, found), 0)
        different = main.ItemReport(3, "found", "Other", "red", "Library", "headphones")
        self.assertEqual(main.calculate_match_score(lost, different), 0)

    def test_category_mismatch_reasons_are_empty(self):
        keys = main.ItemReport(3, "found", "Keys", "Black", "Fisher Library", "metal")
        self.assertEqual(main.match_breakdown(self.lost, keys), (0, []))

    def test_only_same_type_no_matches(self):
        other_lost = main.ItemReport(3, "lost", "Bottle", "Black", "Fisher Library",
                                     "metal water bottle sticker")
        output = io.StringIO()
        with patch("builtins.input", return_value="1"), redirect_stdout(output):
            main.find_matches([self.lost, other_lost])
        self.assertIn("No close matches yet", output.getvalue())

    def test_normalise_case_and_spaces(self):
        self.assertEqual(main.normalise("  FISHER  Library  "), "fisher library")

    def test_description_punctuation_is_ignored(self):
        self.assertEqual(main.description_words("METAL, water-bottle!"),
                         {"metal", "water", "bottle"})

    def test_description_points_are_capped(self):
        first = main.ItemReport(1, "lost", "Bottle", "black", "Fisher Library",
                                "alpha beta gamma delta epsilon zeta")
        second = main.ItemReport(2, "found", "Bottle", "black", "Fisher Library",
                                 "alpha beta gamma delta epsilon zeta")
        self.assertEqual(main.calculate_match_score(first, second), 100)

    def test_no_file_means_fresh_start(self):
        self.assertEqual(main.load_reports(), [])

    def test_wrong_top_level_data_is_rejected(self):
        main.DATA_FILE.write_text('{"reports":[]}', encoding="utf-8")
        with self.assertRaises(ValueError):
            main.load_reports()

    def test_duplicate_ids_rejected_on_load(self):
        main.save_reports([self.lost, self.found])
        data = json.loads(main.DATA_FILE.read_text(encoding="utf-8"))
        data[1]["id"] = 1
        main.DATA_FILE.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            main.load_reports()

    def test_missing_fields_rejected_on_load(self):
        main.DATA_FILE.write_text('[{"id": 1}]', encoding="utf-8")
        with self.assertRaises(ValueError):
            main.load_reports()

    def test_invalid_id_input_does_not_crash(self):
        output = io.StringIO()
        with patch("builtins.input", return_value="abc"), redirect_stdout(output):
            self.assertIsNone(main.ask_report_id())
        self.assertIn("Invalid ID", output.getvalue())

    def test_negative_id_input_does_not_crash(self):
        output = io.StringIO()
        with patch("builtins.input", return_value="-2"), redirect_stdout(output):
            self.assertIsNone(main.ask_report_id())

    def test_existing_resolved_report_stays_resolved(self):
        self.lost.status = "resolved"
        output = io.StringIO()
        with patch("builtins.input", return_value="1"), redirect_stdout(output):
            main.mark_resolved([self.lost])
        self.assertIn("already marked", output.getvalue())

    def test_empty_report_list(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main.view_reports([])
        self.assertIn("No reports", output.getvalue())

    def test_full_menu_session_saves_and_quits(self):
        answers = iter([
            "1", "2", "Black", "Fisher Library", "Metal bottle sticker",
            "2", "2", "black", "fisher library", "Metal bottle sticker",
            "3", "1", "6",
        ])
        output = io.StringIO()
        with patch("builtins.input", side_effect=lambda *_: next(answers)):
            with redirect_stdout(output):
                main.main()
        self.assertIn("Similarity score: 95/100", output.getvalue())
        self.assertEqual(len(main.load_reports()), 2)


if __name__ == "__main__":
    unittest.main()
