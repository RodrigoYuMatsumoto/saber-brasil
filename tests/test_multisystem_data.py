"""Regressão de identidade, currículos e catálogos de idioma."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("multisystem", ROOT / "scripts/validate_multisystem.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MultiSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = MODULE.validate(ROOT)
        cls.checks = {row["id"]: row for row in cls.report["checks"]}

    def require(self, *keys):
        for key in keys:
            with self.subTest(check=key):
                self.assertIn(key, self.checks)
                self.assertTrue(self.checks[key]["passed"], self.checks[key].get("detail"))

    def test_unique_concepts_not_multiplied_by_language(self):
        self.require("CROSS_DATASET_UNIQUE_IDS", "TRANSLATIONS_REFER_TO_IDENTITIES")

    def test_relations_resolve_without_cycles(self):
        self.require("CROSS_DATASET_REFERENCES", "CROSS_DATASET_ACYCLIC")

    def test_all_five_curriculum_systems_use_sources(self):
        self.require("REQUIRED_CURRICULUM_SYSTEMS", "PLACEMENT_SHAPE_AND_BANDS", "PLACEMENT_PRIMARY_AUTHORITY", "ENGLAND_FRAMEWORK_SCOPED")

    def test_source_band_may_be_single_year_interval(self):
        # A banda curricular de Química pode ser [9,9]; não se inventa outro ano.
        singleton = {"system": "CN", "years": [9], "framework": "MOE-2022", "certainty": "source-band"}
        self.assertTrue(MODULE.placement_is_valid(singleton))
        self.assertFalse(MODULE.placement_is_valid({**singleton, "years": [8, 9], "certainty": "source-explicit"}))
        self.assertFalse(MODULE.placement_is_valid({**singleton, "years": [True]}))

    def test_four_interfaces_have_matching_keys_and_variables(self):
        self.require("INTERFACE_LOCALES", "INTERFACE_KEY_COVERAGE", "INTERFACE_NO_BLANK_LABELS", "INTERFACE_PLACEHOLDERS", "INTERFACE_FALLBACK_LABELS")

    def test_portuguese_translations_preserve_english_originals(self):
        self.require("MARBLE_PT_AND_ORIGINAL_EN")

    def test_corrected_bncc_identifiers_are_explicit(self):
        self.require("EF67LP33_PRESENT_AND_LITERAL", "EF05CO11_NORMALIZATION_EXPLICIT")

    def test_east_asia_has_traceable_review_states(self):
        self.require("EAST_ASIA_BOTH_ORIGINS", "EAST_ASIA_TRACE_AND_REVIEW_STATE", "EAST_ASIA_FOUR_LANGUAGE_RECORDS")
        asia_count = self.report["datasets"]["eastAsia"]
        for locale in MODULE.EXPECTED_LOCALES:
            self.assertGreaterEqual(self.report["contentDescriptionCoverage"][locale], asia_count)
            self.assertGreaterEqual(self.report["contentNameCoverage"][locale], asia_count)

    def test_all_required_inputs_and_checks_pass(self):
        self.assertEqual(self.report["status"], "pass", self.report["errors"])


if __name__ == "__main__":
    unittest.main()
