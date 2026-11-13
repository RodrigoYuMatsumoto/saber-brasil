"""Confere as unidades de fonte contra células e atribuições oficiais preservadas."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def assignment_from_official_xlsx():
    with ZipFile(ROOT / "data/source_tables/jp_code_assignment.xlsx") as source:
        xml = ET.fromstring(source.read("xl/sharedStrings.xml"))
        strings = []
        for element in xml:
            # Não incluir os campos de furigana (rPh) no texto visível da célula.
            strings.append("".join(child.text or "" for child in element.findall("s:t", NS)) +
                           "".join(child.text or "" for child in element.findall("s:r/s:t", NS)))
        sheet = ET.fromstring(source.read("xl/worksheets/sheet10.xml"))
        mapping = {}
        for row in sheet.findall("s:sheetData/s:row", NS):
            values = {}
            for cell in row.findall("s:c", NS):
                value = cell.find("s:v", NS)
                if value is not None:
                    values[re.sub(r"\d", "", cell.attrib["r"])] = strings[int(value.text)] if cell.attrib.get("t") == "s" else value.text
            if "D" in values and "E" in values and int(row.attrib["r"]) <= 23:
                mapping[values["E"]] = unicodedata.normalize("NFKC", values["D"])
        return mapping


class EastAsiaLiteralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = load("data/east_asia.json")
        cls.topics = cls.document["topics"]
        cls.jp = [t for t in cls.topics if t.get("layer") == "jp-source"]
        cls.cn = [t for t in cls.topics if t.get("layer") == "cn-source"]
        cls.sources = {s["id"]: s for s in load("data/east_asia_source_manifest.json")["sources"]}

    def test_official_japanese_text_and_codes_are_exact_csv_cells(self):
        rows = {}
        for stage in ["primary", "secondary"]:
            path = ROOT / "data/source_tables" / ("jp_" + stage + "_codes.csv")
            with path.open(encoding="utf-8-sig", newline="") as stream:
                for number, row in enumerate(csv.reader(stream), 1):
                    if len(row) > 3 and re.fullmatch(r"[0-9A-Z]{16}", row[3]):
                        rows[row[3]] = (row[2], number)
        self.assertEqual(len(self.jp), 1695)
        self.assertEqual(len({t["officialCode"] for t in self.jp}), 1695)
        for topic in self.jp:
            literal = topic["sourceLiteral"]
            self.assertEqual((literal["text"], literal["csvLine"]), rows[topic["officialCode"]])
            self.assertEqual(topic["originalText"], literal["text"])
            self.assertEqual(topic["standards"][0]["description"], literal["text"])

    def test_japanese_years_follow_official_assignment_workbook(self):
        mapping = assignment_from_official_xlsx()
        for topic in self.jp:
            code = topic["officialCode"]
            band = code[5]
            label = mapping[band]
            if band == "0":
                self.assertIn("全学年適用", label)
                expected = list(range(1, 7 if code[1] == "2" else 4))
            else:
                numbers = [int(n) for n in re.findall(r"第(\d)学年", label)]
                self.assertTrue(numbers, label)
                expected = list(range(numbers[0], numbers[-1] + 1))
            expected = [n + (6 if code[1] == "3" else 0) for n in expected]
            self.assertEqual(topic["schoolPlacements"][0]["years"], expected, topic["id"])

    def test_chinese_sample_has_fourteen_subject_sources_and_local_codes(self):
        self.assertEqual(len(self.cn), 48)
        self.assertEqual(len({t["sourceLiteral"]["sourceId"] for t in self.cn}), 14)
        for topic in self.cn:
            self.assertEqual(topic["codeKind"], "local")
            self.assertNotIn("officialCode", topic)
            self.assertEqual(topic["sourceLiteral"]["codeKind"], "local")
            self.assertEqual(topic["originalText"], topic["standards"][0]["description"])
            self.assertEqual(topic["translationStatus"], "automatic-ai")
            self.assertTrue(topic["sourceLiteral"]["text"])
            self.assertTrue((ROOT / topic["sourceLiteral"]["visualEvidence"]).is_file())
            self.assertEqual(topic["sourceLiteral"]["sha256"], self.sources[topic["sourceLiteral"]["sourceId"]]["sha256"])

    def test_ocr_candidates_are_not_misrepresented_as_literal_units(self):
        candidates = load("data/east_asia_candidates.json")
        self.assertEqual(candidates["status"], "excluded-from-graph")
        self.assertEqual(len(candidates["china"]), 1340)
        ids = {t["id"] for t in self.topics}
        self.assertFalse(ids.intersection(row["id"] for row in candidates["china"]))

    def test_editorial_layers_and_edge_strengths_remain_separate(self):
        editorial = [t for t in self.topics if t.get("layer") in {"jp-editorial", "cn-editorial"}]
        self.assertEqual(len(editorial), 610)
        self.assertTrue(all(t["camada"] == "editorial-ia-asia" for t in editorial))
        edges = [p for t in editorial for p in t["prerequisites"]]
        self.assertEqual(len(edges), 42)
        self.assertTrue(all(p["strength"] == "proposed" and p["reason"] and p["strengthBasis"] for p in edges))
        self.assertTrue(all(not t["prerequisites"] for t in self.jp + self.cn))

    def test_chronology_conflict_is_quarantined_and_not_recreated_by_seed(self):
        source_id = "jp_matematica_expressoes_algebricas"
        target_id = "jp_matematica_equacoes_de_primeiro_grau"
        topics = {topic["id"]: topic for topic in self.topics}
        self.assertFalse(any(p["id"] == source_id for p in topics[target_id]["prerequisites"]))
        self.assertFalse(any(p["id"] == target_id for p in topics[source_id]["prerequisites"]))
        ledger = load("data/east_asia_relation_candidates.json")
        candidate = next(row for row in ledger["candidates"] if row["from"] == source_id and row["to"] == target_id)
        self.assertEqual(candidate["reasonKind"], "source-chronology-conflict")
        self.assertEqual(candidate["sourceChronology"]["from"]["years"], [8])
        self.assertEqual(candidate["sourceChronology"]["to"]["years"], [7])
        self.assertEqual(candidate["status"], "quarantined")
        self.assertFalse(candidate["automaticReversal"])
        self.assertIn("não constitui B.9", candidate["reviewInput"]["scope"])
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from build_east_asia import add_editorial_links
            minimal = [{"id": source_id, "name": "Expressões algébricas", "origin": ["JP"], "prerequisites": []},
                       {"id": target_id, "name": "Equações de primeiro grau", "origin": ["JP"], "prerequisites": []}]
            add_editorial_links(minimal)
            self.assertTrue(all(not topic["prerequisites"] for topic in minimal))
        finally:
            sys.path.pop(0)

    def test_source_tables_match_published_hashes(self):
        for source_id in ["jp_primary_codes", "jp_secondary_codes", "jp_code_assignment"]:
            source = self.sources[source_id]
            path = ROOT / (source["path"] if source_id == "jp_code_assignment" else "data/source_tables/" + source_id + ".csv")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source["sha256"])

    def test_broad_chinese_secondary_placements_do_not_claim_narrow_years(self):
        for topic in self.topics:
            if "CN" in topic["origin"] and (topic["subject"] == "geografia" or topic["domain"] in {"Física do secundário inferior", "Química do secundário inferior", "Biologia do secundário inferior"}):
                self.assertEqual(topic["schoolPlacements"][0]["years"], [7, 8, 9])


if __name__ == "__main__":
    unittest.main()
