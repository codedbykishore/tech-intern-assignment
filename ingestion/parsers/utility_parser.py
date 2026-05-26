import csv
import io


COLUMN_ALIASES = {
    "Usage": "consumption",
    "Meter #": "meter_number",
    "Meter Number": "meter_number",
    "Period Start": "billing_start_date",
    "Period End": "billing_end_date",
    "Period Start Date": "billing_start_date",
    "Period End Date": "billing_end_date",
    "Read Date": "meter_read_date",
    "Meter Read Date": "meter_read_date",
    "Consumption": "consumption",
    "Consumption (kWh)": "consumption",
    "UOM": "consumption_unit",
    "Unit": "consumption_unit",
    "Tariff": "tariff_name",
    "Tariff Name": "tariff_name",
    "Total Cost": "total_cost",
    "Cost": "total_cost",
    "Facility": "facility_name",
    "Facility Name": "facility_name",
    "Location": "facility_name",
}

REQUIRED = ["consumption"]


def parse_utility_csv(csv_string):
    reader = csv.DictReader(io.StringIO(csv_string))
    raw_headers = reader.fieldnames or []

    header_map = {}
    for h in raw_headers:
        header_map[h] = COLUMN_ALIASES.get(h, h)

    rows = []
    for i, row in enumerate(reader):
        mapped = {}
        for k, v in row.items():
            mapped[header_map[k]] = v.strip() if v else ""

        record = {
            "row_index": i,
            "meter_number": mapped.get("meter_number", ""),
            "meter_read_date": mapped.get("meter_read_date", ""),
            "billing_start_date": mapped.get("billing_start_date", ""),
            "billing_end_date": mapped.get("billing_end_date", ""),
            "consumption": _parse_decimal(mapped.get("consumption")),
            "consumption_unit": mapped.get("consumption_unit", ""),
            "tariff_name": mapped.get("tariff_name", ""),
            "total_cost": _parse_decimal(mapped.get("total_cost")),
            "facility_name": mapped.get("facility_name", ""),
        }
        rows.append(record)
    return rows


def _parse_decimal(val):
    if not val or not val.strip():
        return None
    cleaned = val.strip().replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None
