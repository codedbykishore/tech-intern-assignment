from .utility_parser import parse_utility_csv
from .sap_parser import parse_sap_csv
from .travel_parser import parse_travel_csv

PARSER_MAP = {
    "utility": parse_utility_csv,
    "sap": parse_sap_csv,
    "travel": parse_travel_csv,
}
