"""Camada de unidades oficiais (auditoria Grok 2026-11-12): contagens, códigos únicos e ausência de relações."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OfficialUnitsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layer = json.loads((ROOT / "data/official_units.json").read_text(encoding="utf-8"))
        cls.topics = cls.layer["topics"]
        base = []
        for name in ("brazil_topics.json", "international.json", "east_asia.json"):
            base += json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))["topics"]
        cls.base = base

    def test_contagens(self):
        kinds = {}
        for t in self.topics:
            key = (t["origin"][0], t["kind"])
            kinds[key] = kinds.get(key, 0) + 1
        self.assertEqual(kinds, {("BR", "objetivo-ei"): 104, ("JP", "unidade-oficial"): 1695, ("CN", "unidade-oficial"): 1340})
        self.assertEqual(len(self.base), 4668)

    def test_ids_e_codigos_unicos(self):
        ids = [t["id"] for t in self.topics] + [t["id"] for t in self.base]
        self.assertEqual(len(ids), len(set(ids)))
        for origin in ("BR", "JP", "CN"):
            codes = [t["standards"][0]["code"] for t in self.topics if t["origin"] == [origin]]
            self.assertEqual(len(codes), len(set(codes)), origin)

    def test_sem_relacoes_novas(self):
        self.assertTrue(all(not t.get("prerequisites") for t in self.topics))

    def test_vinculos_editoriais_existem(self):
        known = {t["id"] for t in self.base}
        for t in self.topics:
            for ref in t.get("editorialMicrotopicIds", []):
                self.assertIn(ref, known)

    def test_anos_dentro_do_sistema(self):
        limits = {"BR": {0}, "JP": set(range(1, 10)), "CN": set(range(1, 10))}
        for t in self.topics:
            for p in t["schoolPlacements"]:
                self.assertTrue(set(p["years"]) <= limits[p["system"]], t["id"])

    def test_china_nao_verificada(self):
        for t in self.topics:
            if t["origin"] == ["CN"]:
                self.assertFalse(t["standards"][0]["verified"])
                self.assertLessEqual(len(t["description"].rstrip("\u2026")), 40)


if __name__ == "__main__":
    unittest.main()
