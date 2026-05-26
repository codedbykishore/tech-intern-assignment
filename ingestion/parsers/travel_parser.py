import csv
import io

VENDOR_CATEGORY_MAP = {
    "delta": "flight",
    "united": "flight",
    "american airlines": "flight",
    "southwest": "flight",
    "jetblue": "flight",
    "lufthansa": "flight",
    "emirates": "flight",
    "ryanair": "flight",
    "easyjet": "flight",
    "british airways": "flight",
    "air france": "flight",
    "marriott": "hotel",
    "hilton": "hotel",
    "hyatt": "hotel",
    "ibis": "hotel",
    "accor": "hotel",
    "airbnb": "hotel",
    "booking.com": "hotel",
    "uber": "rideshare",
    "lyft": "rideshare",
    "ola": "rideshare",
    "grab": "rideshare",
    "didl": "rideshare",
    "hertz": "car_rental",
    "avis": "car_rental",
    "enterprise": "car_rental",
    "budget": "car_rental",
    "sixt": "car_rental",
    "national": "car_rental",
    "europcar": "car_rental",
    "amtrak": "train",
    "sncf": "train",
    "deutsche bahn": "train",
    "eurostar": "train",
    "rail europe": "train",
    "renfe": "train",
    "trenitalia": "train",
}

COLUMN_ALIASES = {
    "Expense Type": "category",
    "Category": "category",
    "Type": "category",
    "Employee": "employee_name",
    "Employee Name": "employee_name",
    "Vendor": "vendor",
    "Merchant": "vendor",
    "Supplier": "vendor",
    "Origin": "origin",
    "From": "origin",
    "Departure": "origin",
    "Destination": "destination",
    "To": "destination",
    "Departure Date": "departure_date",
    "Start Date": "departure_date",
    "Return Date": "return_date",
    "End Date": "return_date",
    "Amount": "amount",
    "Total": "amount",
    "Currency": "currency",
    "Distance (km)": "distance_km",
    "Distance (mi)": "distance_mi",
    "Miles": "distance_mi",
    "Distance": "distance_km",
    "Hotel Nights": "hotel_nights",
    "Nights": "hotel_nights",
}


def _normalize_vendor(vendor_name):
    return vendor_name.strip().lower()


def _auto_detect_category(vendor_name, category_from_csv):
    if category_from_csv and category_from_csv.strip():
        return category_from_csv.strip().lower()

    normalized = _normalize_vendor(vendor_name)
    for key, cat in VENDOR_CATEGORY_MAP.items():
        if key in normalized:
            return cat
    return ""


def parse_travel_csv(csv_string):
    reader = csv.DictReader(io.StringIO(csv_string))
    raw_headers = reader.fieldnames or []

    header_map = {}
    for h in raw_headers:
        header_map[h] = COLUMN_ALIASES.get(h.strip(), h)

    rows = []
    for i, row in enumerate(reader):
        mapped = {}
        for k, v in row.items():
            key = header_map.get(k, k)
            mapped[key] = v.strip() if v else ""

        category = _auto_detect_category(
            mapped.get("vendor", mapped.get("employee_name", "")),
            mapped.get("category", ""),
        )

        distance_km_raw = mapped.get("distance_km", "")
        distance_mi_raw = mapped.get("distance_mi", "")
        if distance_km_raw:
            distance_km = _parse_decimal(distance_km_raw)
        elif distance_mi_raw:
            distance_mi = _parse_decimal(distance_mi_raw)
            distance_km = round(distance_mi * 1.60934, 2) if distance_mi else None
        else:
            distance_km = None

        record = {
            "row_index": i,
            "category": category,
            "employee_name": mapped.get("employee_name", ""),
            "vendor": mapped.get("vendor", ""),
            "origin": mapped.get("origin", ""),
            "destination": mapped.get("destination", ""),
            "departure_date": mapped.get("departure_date", ""),
            "return_date": mapped.get("return_date", ""),
            "amount": _parse_decimal(mapped.get("amount")),
            "currency": mapped.get("currency", ""),
            "distance_km": distance_km,
            "hotel_nights": _parse_int(mapped.get("hotel_nights")),
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


def _parse_int(val):
    if not val or not val.strip():
        return None
    try:
        return int(float(val.strip()))
    except ValueError:
        return None
