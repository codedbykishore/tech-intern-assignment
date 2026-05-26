import csv
import io

GERMAN_ALIASES = {
    "Materialnummer": "material_number",
    "Material-Nr.": "material_number",
    "Materialkurztext": "material_description",
    "Materialbezeichnung": "material_description",
    "Werk": "plant_code",
    "Menge": "quantity",
    "Menge (E)": "quantity",
    "Einheit": "unit",
    "ME": "unit",
    "Buchungsdatum": "posting_date",
    "Belegnummer": "document_number",
    "Betrag": "amount",
    "Währung": "currency",
    "Waehrung": "currency",
    "Kostenstelle": "cost_center",
    "Materialgruppe": "material_group",
}

ENGLISH_ALIASES = {
    "Material Number": "material_number",
    "Material Description": "material_description",
    "Plant": "plant_code",
    "Plant Code": "plant_code",
    "Quantity": "quantity",
    "Unit": "unit",
    "UOM": "unit",
    "Posting Date": "posting_date",
    "Document Number": "document_number",
    "Document No": "document_number",
    "Amount": "amount",
    "Currency": "currency",
    "Cost Center": "cost_center",
    "Material Group": "material_group",
    "Material Group": "material_group",
}

ALL_ALIASES = {**GERMAN_ALIASES, **ENGLISH_ALIASES}

UNIT_NORMALIZATION = {
    "Litres": "L",
    "Litres": "L",
    "Liter": "L",
    "Tons": "t",
    "Tonnen": "t",
    "Ton": "t",
    "Kilograms": "kg",
    "Kilogramm": "kg",
    "Cubic meters": "m3",
    "Kubikmeter": "m3",
    "Cubic Meters": "m3",
}


def parse_sap_csv(csv_string):
    reader = csv.DictReader(io.StringIO(csv_string))
    raw_headers = reader.fieldnames or []

    header_map = {}
    for h in raw_headers:
        header_map[h] = ALL_ALIASES.get(h.strip(), h)

    rows = []
    for i, row in enumerate(reader):
        mapped = {}
        for k, v in row.items():
            key = header_map.get(k, k)
            mapped[key] = v.strip() if v else ""

        unit_raw = mapped.get("unit", "")
        unit_normalized = UNIT_NORMALIZATION.get(unit_raw, unit_raw)

        record = {
            "row_index": i,
            "material_number": mapped.get("material_number", ""),
            "material_description": mapped.get("material_description", ""),
            "plant_code": mapped.get("plant_code", ""),
            "quantity": _parse_decimal(mapped.get("quantity")),
            "unit": unit_normalized,
            "posting_date": mapped.get("posting_date", ""),
            "document_number": mapped.get("document_number", ""),
            "amount": _parse_decimal(mapped.get("amount")),
            "currency": mapped.get("currency", ""),
            "cost_center": mapped.get("cost_center", ""),
            "material_group": mapped.get("material_group", ""),
        }
        rows.append(record)
    return rows


def _parse_decimal(val):
    if not val or not val.strip():
        return None
    cleaned = val.strip().replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None
