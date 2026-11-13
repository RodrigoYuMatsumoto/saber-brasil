"""Aceite da base de consenso e da camada editorial opcional."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("consensus_layers", ROOT / "scripts/consensus_layers.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ConsensusLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brazil = json.loads((ROOT / "data/brazil_topics.json").read_text(encoding="utf-8"))
        cls.official = [t for t in cls.brazil["topics"] if t.get("kind") == "habilidade"]
        cls.editorial = [t for t in cls.brazil["topics"] if t.get("kind") == "microtopico"]
        cls.report = MODULE.validate_consensus(ROOT, verify_pdfs=True)

    def test_consensus_base_is_3315_with_each_official_code_as_node(self):
        counts = self.report["counts"]
        self.assertEqual((counts["bncc2018"], counts["computing2022"], counts["baseBrazil"], counts["baseMarble"], counts["baseConsensus"]), (1304, 104, 1408, 1907, 3315))
        codes = {t["code"] for t in self.official}
        self.assertEqual(len(codes), 1408)
        self.assertEqual(codes, set(MODULE.reference_records(ROOT)))

    def test_all_1408_codes_and_full_texts_match_fixed_reference(self):
        rows = self.report["codes"]["rows"]
        self.assertEqual(len(rows), 1408)
        self.assertTrue(all(row["textMatchesReferenceAfterDeclaredTypography"] for row in rows))
        self.assertEqual(self.report["codes"]["missing"], [])
        self.assertEqual(self.report["codes"]["extra"], [])

    def test_all_1408_codes_and_texts_are_checked_against_official_pdfs(self):
        result = self.report["codes"]
        self.assertTrue(result["pdfCheckPerformed"])
        self.assertEqual(result["pdfUniqueNormalized"], 1408)
        self.assertEqual(result["missingFromPdf"], [])
        self.assertEqual(result["extraInPdf"], [])
        self.assertTrue(all(row["pdfCodeVerified"] and row["pdfTextVerified"] for row in result["rows"]))

    def test_editorial_nodes_have_own_ids_no_official_code_and_source_parent(self):
        self.assertEqual(len(self.editorial), 743)
        self.assertEqual(self.report["editorial"]["invalidRecords"], [])
        for topic in self.editorial:
            self.assertTrue(topic["id"].startswith("ED-"))
            self.assertEqual(topic["camada"], "editorial-ia")
            self.assertNotIn("code", topic)
            self.assertEqual(topic["standards"], [])
            self.assertEqual(topic["parentStandards"][0]["code"], topic["parentCode"])
            self.assertIn("requer revisão", topic["editorialLabel"])

    def test_editorial_layer_starts_disabled_and_preserves_legacy_links(self):
        layer = next(layer for layer in self.brazil["layers"] if layer["id"] == "editorial-ia")
        self.assertFalse(layer["defaultEnabled"])
        self.assertEqual(layer["count"], 743)
        aliases = self.brazil["aliases"]
        self.assertEqual(aliases["br_ef01ci01_m01"], "ED-EF01CI01-01")
        self.assertEqual(aliases["EF67LP33"], "br_ef67lp33")
        self.assertTrue(all(aliases[t["legacyIds"][0]] == t["id"] for t in self.editorial))

    def test_brazil_inferred_edges_have_reason_and_nonempirical_weight(self):
        edges = [edge for t in self.brazil["topics"] for edge in t["prerequisites"]]
        self.assertEqual(len(edges), 840)
        self.assertTrue(all(edge["reason"] and 0 <= edge["strength"] <= 1 and edge["strengthBasis"] and edge["official"] is False for edge in edges))
        self.assertEqual(sum(edge["relation"] == "parte-da-habilidade" for edge in edges), 743)
        self.assertEqual(sum(edge["relation"] == "pre-requisito-pedagogico-proposto" for edge in edges), 97)

    def test_combined_graph_has_complete_topological_order_and_marble_edges(self):
        graph = self.report["graph"]
        self.assertTrue(graph["acyclic"])
        self.assertEqual(graph["nodes"], graph["topologicalNodes"])
        self.assertEqual(graph["unresolvedReferences"], [])
        self.assertEqual(graph["edgesByType"]["marble"], 4003)

    def test_migration_is_idempotent(self):
        source = copy.deepcopy(self.brazil)
        once = MODULE.apply_brazil_layers(copy.deepcopy(source), ROOT)
        twice = MODULE.apply_brazil_layers(copy.deepcopy(once), ROOT)
        self.assertEqual(source, once)
        self.assertEqual(once, twice)

    def test_punctuation_and_computing_code_and_pi_corrections_are_explicit(self):
        by_code = {t["code"]: t for t in self.official}
        self.assertEqual(by_code["EF67LP33"]["description"], "Pontuar textos adequadamente.")
        self.assertEqual(by_code["EF67LP33"]["standards"][0]["pdfPage"], 173)
        self.assertEqual(by_code["EF05CO11"]["standards"][0]["sourceCodeLiteral"], "EF05CO011")
        pi = by_code["EF07MA33"]
        self.assertIn("número π como", pi["description"])
        self.assertEqual(pi["standards"][0]["visualGlyphVerification"]["glyph"], "π")


if __name__ == "__main__":
    unittest.main()
