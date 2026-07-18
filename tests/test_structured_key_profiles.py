import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "blade_profile", "transponder_id", "technology_family", "chip_type",
    "chip_ic", "remote_configuration", "frequency",
)
CHIP_TYPES = {
    "Glass Chip", "Carbon Chip", "Ceramic Chip", "Integrated Remote Chip",
    "Integrated Proximity Chip", "PCB Mounted Chip", "No Separate Transponder",
    "Research Required",
}
REMOTE_TYPES = {"Separate", "Integrated", "Integrated Proximity", "No Remote", "Research Required"}


class StructuredKeyProfileTests(unittest.TestCase):
    def records(self):
        for path in (ROOT / "database/vehicles").glob("*/*/models.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            records = list(data.get("items", {}).values()) + data.get("generations", [])
            for record in records:
                yield path, record.get("vehicle_information", record)

    def test_all_records_have_structured_profile(self):
        count = 0
        for path, info in self.records():
            count += 1
            for field in FIELDS:
                self.assertIsInstance(info.get(field), str, f"{path}: {field}")
                self.assertTrue(info[field].strip(), f"{path}: {field}")
            self.assertIn(info["chip_type"], CHIP_TYPES, str(path))
            self.assertIn(info["remote_configuration"], REMOTE_TYPES, str(path))
        self.assertEqual(count, 1499)

    def test_populated_structured_values_have_evidence_lists(self):
        for path, info in self.records():
            evidence = info.get("key_profile_evidence")
            self.assertIsInstance(evidence, dict, str(path))
            for field in FIELDS:
                self.assertIsInstance(evidence.get(field), list, f"{path}: {field}")
                if info[field] != "Research Required" and field in {"chip_type", "chip_ic", "remote_configuration"}:
                    self.assertTrue(evidence[field], f"{path}: populated {field} lacks evidence")

    def test_canonical_transponders_have_structured_family_metadata(self):
        path = ROOT / "database/reference/uk_transponder_catalogue.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for family_id, item in data["items"].items():
            for field in ("canonical_id", "display_name", "technology_family", "known_possible_ics", "known_chip_types", "aliases", "notes", "evidence", "confidence"):
                self.assertIn(field, item, f"{family_id}: {field}")


if __name__ == "__main__":
    unittest.main()
