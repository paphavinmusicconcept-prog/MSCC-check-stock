import unittest

from stock_cleaning import clean_product_name, normalize_product, to_number


class StockCleaningTest(unittest.TestCase):
    def test_removes_semicolon_quantity_tail_and_keeps_inch_quote(self):
        self.assertEqual(
            clean_product_name('PAISTE PSTX SWISS THIN CRASH 16";;;;;;2"ใบ'),
            'PAISTE PSTX SWISS THIN CRASH 16"',
        )

    def test_removes_comma_quantity_tail_and_keeps_inch_quote(self):
        self.assertEqual(
            clean_product_name('PAISTE PSTX SWISS THIN CRASH 16",,,,,,2,"ใบ'),
            'PAISTE PSTX SWISS THIN CRASH 16"',
        )

    def test_keeps_real_product_quotes(self):
        self.assertEqual(
            clean_product_name('PAISTE ALPHA "B" METAL CRASH 20"'),
            'PAISTE ALPHA "B" METAL CRASH 20"',
        )

    def test_normalizes_product_fields_separately(self):
        product = normalize_product(
            " PT-PSTX-C-T16 ",
            ' PAISTE PSTX SWISS THIN CRASH 16";;;;;;2"ใบ ',
            ' 0 ตัว ',
            " ใบ ",
            " คลังสำนักงานเพชรบุรีตัดใหม่ ",
        )

        self.assertEqual(product["sku"], "PT-PSTX-C-T16")
        self.assertEqual(product["name"], 'PAISTE PSTX SWISS THIN CRASH 16"')
        self.assertEqual(product["qty"], 0)
        self.assertEqual(product["unit"], "ใบ")
        self.assertEqual(product["warehouse"], "คลังสำนักงานเพชรบุรีตัดใหม่")

    def test_to_number(self):
        self.assertEqual(to_number("2 ใบ"), 2)
        self.assertEqual(to_number(None), 0)


if __name__ == "__main__":
    unittest.main()
