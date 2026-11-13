"""Regressão da etapa EI, sem misturá-la ao consenso do Ensino Fundamental."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    SPEC = importlib.util.spec_from_file_location("early_childhood", SCRIPTS / "import_early_childhood.py")
    MODULE = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MODULE)
finally:
    sys.path.remove(str(SCRIPTS))


class EarlyChildhoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data/brazil_topics.json").read_text(encoding="utf-8"))
        cls.topics = [topic for topic in cls.data["topics"] if topic.get("layer") == "ei-source"]
        cls.report = MODULE.verify_ei_sources(ROOT)

    def test_104_official_objectives_are_93_bncc_and_11_computing(self):
        self.assertEqual(len(self.topics), 104)
        self.assertEqual(len({topic["code"] for topic in self.topics}), 104)
        self.assertEqual(sum(topic["code"][4:6] == "CO" for topic in self.topics), 11)
        self.assertEqual(sum(topic["code"][4:6] != "CO" for topic in self.topics), 93)
        self.assertEqual({topic["code"] for topic in self.topics}, set(MODULE.ei_references(ROOT)))

    def test_every_code_and_full_text_is_in_same_official_pdf_block(self):
        self.assertEqual(self.report["status"], "pass")
        self.assertEqual(self.report["counts"]["codeAndFullTextMatches"], 104)
        self.assertEqual(self.report["missingFromPdf"], [])
        self.assertEqual(self.report["extraInPdf"], [])
        self.assertTrue(all(row["codeAndFullTextInSameBlock"] and row["pdfHashMatchesManifest"] for row in self.report["rows"]))
        by_code = {row["code"]: row for row in self.report["rows"]}
        self.assertTrue(all(topic["description"] == by_code[topic["code"]]["literalText"] == topic["sourceLiteral"]["text"] == topic["standards"][0]["description"] for topic in self.topics))

    def test_stage_and_age_groups_are_preserved_without_inventing_school_year(self):
        for topic in self.topics:
            placement = topic["schoolPlacements"][0]
            self.assertEqual((placement["system"], placement["stage"], placement["years"], placement["certainty"]), ("BR", "EI", [], "source-stage"))
            self.assertEqual(placement["ageGroup"], "EI" + topic["code"][2:4])
            self.assertEqual(placement["ageGroupLabel"], MODULE.AGE_GROUPS[topic["code"][2:4]])
            self.assertEqual((topic["gradeMin"], topic["gradeMax"]), (0, 0))
            self.assertIn("apenas convenção visual", topic["gradeDisplayConvention"])

    def test_ei_layer_is_optional_and_does_not_inflate_1408_ef_or_3315_consensus(self):
        layer = next(layer for layer in self.data["layers"] if layer["id"] == "ei-source")
        self.assertFalse(layer["defaultEnabled"])
        self.assertFalse(layer["includedInConsensusBase"])
        self.assertEqual(sum(topic.get("kind") == "habilidade" for topic in self.data["topics"]), 1408)
        self.assertEqual(sum(topic.get("kind") == "microtopico" for topic in self.data["topics"]), 743)
        self.assertEqual(self.data["coverage"]["baseConsensusIncludingMarble"], 3315)
        self.assertEqual(self.data["coverage"]["earlyChildhoodObjectives"], 104)
        self.assertTrue(all(topic["kind"] == "objetivo-ei" and topic["recordType"] == "curriculum-source-unit" and topic["prerequisites"] == [] for topic in self.topics))

    def test_official_codes_have_direct_aliases_and_government_pdf_locators(self):
        for topic in self.topics:
            self.assertTrue(MODULE.EI_CODE.fullmatch(topic["code"]))
            self.assertEqual(self.data["aliases"][topic["code"]], topic["id"])
            self.assertEqual(topic["sourceLiteral"]["codeKind"], "official")
            self.assertEqual(topic["sourceLiteral"]["code"], topic["code"])
            self.assertIn(".gov.br/", topic["sourceLiteral"]["url"])
            self.assertIn("#page=", topic["sourceLiteral"]["url"])

    def test_untrusted_contribution_is_not_promoted_with_footer_contamination(self):
        comparison = self.report["externalContribution"]
        if comparison["available"]:
            self.assertFalse(comparison["promotedVerbatim"])
            self.assertEqual({row["code"] for row in comparison["differences"]}, {"EI02EF03", "EI03CG05", "EI03EF05", "EI03EO05", "EI03ET06"})
        self.assertTrue(all(not topic["description"][:1].isdigit() for topic in self.topics))
        reading = next(topic for topic in self.topics if topic["code"] == "EI02EF03")
        self.assertIn("adulto-leitor", reading["description"])
        self.assertNotIn("adulto- -leitor", reading["description"])
        self.assertTrue(any("translineação" in rule for rule in reading["sourceLiteral"]["normalizationRules"]))

    def test_import_is_idempotent_and_preserves_fundamental_topics(self):
        source = copy.deepcopy(self.data)
        once = MODULE.append_ei_layer(copy.deepcopy(source), self.report, ROOT)
        twice = MODULE.append_ei_layer(copy.deepcopy(once), self.report, ROOT)
        self.assertEqual(source, once)
        self.assertEqual(once, twice)
        before = [topic for topic in source["topics"] if topic.get("layer") != "ei-source"]
        after = [topic for topic in twice["topics"] if topic.get("layer") != "ei-source"]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
