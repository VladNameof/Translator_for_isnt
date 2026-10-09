import unittest
from src.core.glossary_manager import GlossaryManager

class TestGlossaryManager(unittest.TestCase):
    def setUp(self):
        self.glossary = GlossaryManager()
        self.glossary.load_from_dict({
            "INSTRUKCJA STANOWISKOWA": "РОБОЧА ІНСТРУКЦІЯ",
            "Włącz aplikacje [1]\r\nSprawdź drukarkę": "Увімкніть застосунок [1]\r\nПеревірте принтер"
        })

    def test_exact_lookup(self):
        self.assertEqual(
            self.glossary.find_translation("INSTRUKCJA STANOWISKOWA"),
            "РОБОЧА ІНСТРУКЦІЯ"
        )

    def test_trimmed_lookup(self):
        self.assertEqual(
            self.glossary.find_translation("  INSTRUKCJA STANOWISKOWA   "),
            "РОБОЧА ІНСТРУКЦІЯ"
        )

    def test_normalized_lookup(self):
        # Different line endings and spaces
        raw = "Włącz\xa0aplikacje [1] \r Sprawdź drukarkę"
        self.assertEqual(
            self.glossary.find_translation(raw),
            "Увімкніть застосунок [1]\r\nПеревірте принтер"
        )

    def test_unknown_string(self):
        self.assertIsNone(self.glossary.find_translation("Nonexistent String 12345"))

if __name__ == "__main__":
    unittest.main()
