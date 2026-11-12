"""Verificações da conciliação e das séries curriculares de origem."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reconciliation", ROOT / "scripts/reconcile_sources.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brazil = json.loads((ROOT / "data/brazil_topics.json").read_text(encoding="utf-8"))
        cls.international = json.loads((ROOT / "data/international.json").read_text(encoding="utf-8"))
        cls.report = json.loads((ROOT / "evidence/Consenso_Taxonomias.json").read_text(encoding="utf-8"))

    def test_no_language_duplicates(self):
        topics = self.brazil["topics"] + self.international["topics"]
        self.assertEqual(len(topics), len({t["id"] for t in topics}))
        self.assertTrue(self.report["internationalIdentity"]["allThreeIdenticalIds"])

    def test_omissions_verified(self):
        self.assertEqual({r["code"] for r in self.report["verifiedCorrections"]}, {"EF67LP33", "EF05CO11"})
        self.assertTrue(all(r["codeAndFullDescriptionMatch"] for r in self.report["verifiedCorrections"]))
        code = next(t for t in self.brazil["topics"] if t["id"] == "br_ef05co11")
        self.assertEqual(code["standards"][0]["sourceCodeLiteral"], "EF05CO011")
        self.assertEqual(code["standards"][0]["normalizationStatus"], "editorial-correction")

    def test_year_parser_bands(self):
        self.assertEqual(MODULE.parse_years("Kindergarten"), [0])
        self.assertEqual(MODULE.parse_years("Years 3 and 4"), [3, 4])
        self.assertEqual(MODULE.parse_years("K-2"), [0, 1, 2])
        self.assertEqual(MODULE.parse_years("CCR"), [])

    def test_stage_is_not_single_year(self):
        system, years = MODULE.standard_placement("uk-nc-2013", {"code": "Hist.KS2.1", "data": {"keyStage": "Key Stage 2"}})
        self.assertEqual((system, years), ("GB-ENG", [3, 4, 5, 6]))
        system, years = MODULE.standard_placement("ngss-ms", {"code": "MS-ESS1-1"})
        self.assertEqual((system, years), ("US", [6, 7, 8]))

    def test_explicit_year_overrides_stage(self):
        system, years = MODULE.standard_placement("uk-nc-2013", {"code": "Y4.Sci.1", "data": {"keyStage": "Key Stage 2", "year": "Year 4"}})
        self.assertEqual((system, years), ("GB-ENG", [4]))

    def test_no_age_estimate_promoted(self):
        placements = [p for d in [self.brazil, self.international] for t in d["topics"] for p in t["schoolPlacements"]]
        self.assertTrue(placements)
        self.assertTrue(all(p["certainty"] in {"source-explicit", "source-band"} for p in placements))
        self.assertTrue(all(p["sourceCode"] and p["sourceUrl"] for p in placements))

    def test_heuristics_not_promoted(self):
        self.assertEqual(self.report["candidates"]["promotedHeuristicRelations"], 0)
        self.assertEqual(self.report["candidates"]["promotedOfficialEquivalences"], 0)
        self.assertGreater(self.report["translationAudit"]["heuristicallyFlagged"], 0)

    def test_partial_decomposition_is_visible(self):
        stats = self.report["canonical"]
        self.assertEqual(stats["brazilianOfficialSkills"], 1408)
        self.assertEqual(stats["brazilianEditorialMicrotopics"], 743)
        self.assertEqual(stats["brazilianSkillsDecomposed"], 341)
        self.assertEqual(stats["brazilianSkillsUndecomposed"], 1067)


if __name__ == "__main__":
    unittest.main()
