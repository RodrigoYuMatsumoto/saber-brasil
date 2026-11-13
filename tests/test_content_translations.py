"""Confere cobertura real e proveniência sem presumir qualidade linguística."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContentTranslationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.marble = json.loads((ROOT / "data/international.json").read_text(encoding="utf-8"))["topics"]
        cls.translations = json.loads((ROOT / "data/translations.json").read_text(encoding="utf-8"))["topics"]
        cls.originals = {topic["id"]: topic for topic in json.loads((ROOT / "data/upstream/topics.json").read_text(encoding="utf-8"))["topics"]}

    def test_every_marble_has_four_languages_and_three_complete_fields(self):
        self.assertEqual(len(self.marble), 1907)
        for topic in self.marble:
            for language in ("pt-BR", "en", "ja", "zh-Hant"):
                record = self.translations[topic["id"]][language]
                for field in ("name", "description", "assessmentPrompt"):
                    with self.subTest(topic=topic["id"], language=language, field=field):
                        self.assertTrue(record.get(field, "").strip())

    def test_english_questions_are_not_overwritten(self):
        def display_typography(text):
            return text.replace(chr(8211), "-").replace(chr(8212), "-")
        for topic in self.marble:
            original = self.originals[topic["id"]]
            expected = display_typography(original.get("assessmentPrompt", ""))
            self.assertEqual(topic["assessmentPrompt"], expected)
            self.assertEqual(topic["originalAssessmentPrompt"], expected)
            self.assertEqual(self.translations[topic["id"]]["en"]["assessmentPrompt"], expected)

    def test_automatic_translations_have_source_and_review_label(self):
        for topic in self.marble:
            for language in ("pt-BR", "ja", "zh-Hant"):
                record = self.translations[topic["id"]][language]
                self.assertTrue(record["_automatic"])
                self.assertEqual(record["translationMode"], "automatic-ia")
                self.assertEqual(record["sourceAgent"], "Code/Claude")
                self.assertEqual(record["reviewState"], "linguistic-review-required")
                self.assertEqual(len(record["sourceSha256"]), 64)
                self.assertTrue(record["sourcePath"])


if __name__ == "__main__":
    unittest.main()
