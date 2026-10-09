import unittest
from src.core.normalizer import TextNormalizer

class TestTextNormalizer(unittest.TestCase):
    def test_nbsp_replacement(self):
        raw = "Stanowisko\xa0I-01"
        self.assertEqual(TextNormalizer.normalize(raw), "Stanowisko I-01")

    def test_dash_replacement(self):
        raw = "1 \u2013 Naklejka \u2014 test"
        self.assertEqual(TextNormalizer.normalize(raw), "1 - Naklejka - test")

    def test_whitespace_collapse(self):
        raw = "  Włącz   aplikacje \r\n  [1]   "
        self.assertEqual(TextNormalizer.normalize(raw), "Włącz aplikacje [1]")

    def test_is_translatable(self):
        self.assertFalse(TextNormalizer.is_translatable("12"))
        self.assertFalse(TextNormalizer.is_translatable("A"))
        self.assertFalse(TextNormalizer.is_translatable("01.10.2026"))
        self.assertFalse(TextNormalizer.is_translatable("TYEH-ASY0015131R000-03_970"))
        self.assertTrue(TextNormalizer.is_translatable("Włącz aplikacje [1]"))
        self.assertTrue(TextNormalizer.is_translatable("KOMPONENTY"))

if __name__ == "__main__":
    unittest.main()
