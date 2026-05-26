from .utility_parser import parse_utility_csv
from .sap_parser import parse_sap_csv

PARSER_MAP = {
    "utility": parse_utility_csv,
    "sap": parse_sap_csv,
}
