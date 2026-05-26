from django.test import TestCase
from ingestion.parsers.utility_parser import parse_utility_csv


class UtilityParserTest(TestCase):
    def test_parse_basic_csv(self):
        csv_data = "Meter #,Read Date,Period Start,Period End,Usage,UOM,Tariff,Total Cost,Facility\nM001,01.01.2024,01.01.2024,31.01.2024,15000,kWh,Commercial A,3000.00,NYC Office\nM002,01.02.2024,01.02.2024,28.02.2024,12000,kWh,Commercial A,2400.00,Chicago Office\n"
        rows = parse_utility_csv(csv_data)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["meter_number"], "M001")
        self.assertEqual(rows[0]["consumption"], 15000.0)
        self.assertEqual(rows[0]["facility_name"], "NYC Office")

    def test_parse_with_aliases(self):
        csv_data = "Meter Number,Usage,Facility Name\nM005,22000,SF Office\n"
        rows = parse_utility_csv(csv_data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["meter_number"], "M005")
        self.assertEqual(rows[0]["consumption"], 22000.0)
        self.assertEqual(rows[0]["facility_name"], "SF Office")
