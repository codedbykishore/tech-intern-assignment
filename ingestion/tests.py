from django.test import TestCase
from ingestion.parsers.utility_parser import parse_utility_csv
from ingestion.parsers.sap_parser import parse_sap_csv
from ingestion.parsers.travel_parser import parse_travel_csv


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


class SapParserTest(TestCase):
    def test_parse_german_csv(self):
        csv_data = "Materialnummer,Materialkurztext,Werk,Menge,Einheit,Buchungsdatum,Belegnummer,Betrag,Währung,Kostenstelle,Materialgruppe\nMAT001,Diesel Low Sulfur,PLANT_A,1500.000,L,01.01.2024,DOC001,7500.00,EUR,CC100,FUELS\n"
        rows = parse_sap_csv(csv_data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["material_number"], "MAT001")
        self.assertEqual(rows[0]["material_description"], "Diesel Low Sulfur")
        self.assertEqual(rows[0]["plant_code"], "PLANT_A")
        self.assertEqual(rows[0]["quantity"], 1500.0)

    def test_parse_english_csv(self):
        csv_data = "Material Number,Material Description,Plant,Quantity,UOM,Posting Date,Document Number,Amount,Currency,Cost Center,Material Group\nMAT002,Natural Gas,PLANT_B,5000.000,kg,15.01.2024,DOC002,2500.00,EUR,CC200,GAS\n"
        rows = parse_sap_csv(csv_data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["material_number"], "MAT002")
        self.assertEqual(rows[0]["unit"], "kg")

    def test_unit_normalization(self):
        csv_data = "Menge,Einheit\n1000,Liter\n2000,Tons\n"
        rows = parse_sap_csv(csv_data)
        self.assertEqual(rows[0]["unit"], "L")
        self.assertEqual(rows[1]["unit"], "t")


class TravelParserTest(TestCase):
    def test_auto_detect_category(self):
        csv_data = "Employee,Vendor,Amount,Currency\nJohn Doe,Delta,500.00,USD\nJane Smith,Marriott,1200.00,USD\nBob Jones,Uber,45.00,USD\nAlice Williams,Hertz,350.00,USD\n"
        rows = parse_travel_csv(csv_data)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["category"], "flight")
        self.assertEqual(rows[1]["category"], "hotel")
        self.assertEqual(rows[2]["category"], "rideshare")
        self.assertEqual(rows[3]["category"], "car_rental")

    def test_distance_conversion_miles(self):
        csv_data = "Distance (mi)\n100\n"
        rows = parse_travel_csv(csv_data)
        self.assertAlmostEqual(rows[0]["distance_km"], 160.93, places=1)

    def test_distance_conversion_km(self):
        csv_data = "Distance (km)\n200\n"
        rows = parse_travel_csv(csv_data)
        self.assertAlmostEqual(rows[0]["distance_km"], 200.0)

    def test_explicit_category(self):
        csv_data = "Expense Type,Employee,Vendor,Amount\nFlight,John Doe,Delta,500.00\n"
        rows = parse_travel_csv(csv_data)
        self.assertEqual(rows[0]["category"], "flight")
