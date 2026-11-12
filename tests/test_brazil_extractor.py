"""Regressão dos dois objetivos anteriormente omitidos, sem gravar os dados."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SPEC = importlib.util.spec_from_file_location("brazil_extractor_regression", SCRIPTS / "build_brazil.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(SCRIPTS))
try:
    SPEC.loader.exec_module(MODULE)
finally:
    sys.path.remove(str(SCRIPTS))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BrazilExtractorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_paths = [ROOT / "data" / name for name in ["brazil_topics.json", "international.json", "east_asia.json", "translations.json"]]
        cls.before = {path: digest(path) for path in cls.data_paths if path.exists()}
        cls.records = {}
        cls.sources = {}
        cls.warnings = []
        for original in MODULE.SOURCES:
            source = copy.deepcopy(original)
            records, warnings = MODULE.extract(source)
            cls.records.update(records)
            cls.sources[source["id"]] = source
            cls.warnings.extend(warnings)

    @classmethod
    def tearDownClass(cls):
        after = {path: digest(path) for path in cls.before}
        if after != cls.before:
            raise AssertionError("O teste de leitura modificou dados canônicos.")

    def test_short_punctuation_skill_is_preserved(self):
        record = self.records["EF67LP33"]
        self.assertEqual(record["description"], "Pontuar textos adequadamente.")
        self.assertEqual(record["sourceCodeLiteral"], "EF67LP33")
        self.assertEqual(record["sourceId"], "bncc-mec-2018")
        self.assertEqual(record["pdfPage"], 173)
        self.assertFalse(any(warning["code"] == "EF67LP33" for warning in self.warnings))
        self.assertEqual(self.sources["bncc-mec-2018"]["skillCount"], 1304)

    def test_computing_code_keeps_literal_and_editorial_normalization(self):
        record = self.records["EF05CO11"]
        self.assertEqual(record["description"], "Identificar a adequação de diferentes tecnologias computacionais na resolução de problemas.")
        self.assertEqual(record["sourceCodeLiteral"], "EF05CO011")
        self.assertEqual(record["sourceId"], "bncc-computacao-2022")
        self.assertEqual(record["pdfPage"], 36)
        self.assertEqual(record["normalizationStatus"], "editorial-correction")
        self.assertIn("EF05CO011", record["normalizationNote"])
        self.assertEqual(self.sources["bncc-computacao-2022"]["skillCount"], 104)
        self.assertEqual(len(self.records), 1408)


if __name__ == "__main__":
    unittest.main()
