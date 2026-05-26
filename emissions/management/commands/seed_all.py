from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify

from organizations.models import Organization, OrganizationMember
from ingestion.models import ImportBatch, UtilityRawRow, SapRawRow, TravelRawRow
from ingestion.parsers import PARSER_MAP
from emissions.models import EmissionRecord, EmissionFactor, AuditLog


EMISSION_FACTORS = [
    {
        "name": "Diesel (stationary combustion)",
        "category": "fuel",
        "subcategory": "diesel",
        "factor": "2.68",
        "factor_unit": "kgCO2e per L",
        "source": "EPA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Natural Gas (stationary combustion)",
        "category": "fuel",
        "subcategory": "natural_gas",
        "factor": "0.185",
        "factor_unit": "kgCO2e per kWh",
        "source": "EPA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Steel (procurement)",
        "category": "procurement",
        "subcategory": "steel",
        "factor": "1.50",
        "factor_unit": "tCO2e per t",
        "source": "EPA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Cement (procurement)",
        "category": "procurement",
        "subcategory": "cement",
        "factor": "0.85",
        "factor_unit": "tCO2e per t",
        "source": "EPA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Packaging (procurement)",
        "category": "procurement",
        "subcategory": "packaging",
        "factor": "0.50",
        "factor_unit": "kgCO2e per kg",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Electricity — US Northeast",
        "category": "electricity",
        "subcategory": "grid_avg",
        "factor": "0.410",
        "factor_unit": "kgCO2e per kWh",
        "source": "EPA",
        "region": "US-NE",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Electricity — US Midwest",
        "category": "electricity",
        "subcategory": "grid_avg",
        "factor": "0.620",
        "factor_unit": "kgCO2e per kWh",
        "source": "EPA",
        "region": "US-MW",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Electricity — US West",
        "category": "electricity",
        "subcategory": "grid_avg",
        "factor": "0.310",
        "factor_unit": "kgCO2e per kWh",
        "source": "EPA",
        "region": "US-West",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Flight — Short haul (<1000 km)",
        "category": "travel",
        "subcategory": "flight_short",
        "factor": "0.150",
        "factor_unit": "kgCO2e per km",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Flight — Medium haul (1000-4000 km)",
        "category": "travel",
        "subcategory": "flight_medium",
        "factor": "0.120",
        "factor_unit": "kgCO2e per km",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Flight — Long haul (>4000 km)",
        "category": "travel",
        "subcategory": "flight_long",
        "factor": "0.100",
        "factor_unit": "kgCO2e per km",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Hotel (per night)",
        "category": "travel",
        "subcategory": "hotel",
        "factor": "25.0",
        "factor_unit": "kgCO2e per night",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Car Rental (per day)",
        "category": "travel",
        "subcategory": "car_rental",
        "factor": "35.0",
        "factor_unit": "kgCO2e per day",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
    {
        "name": "Rideshare (per km)",
        "category": "travel",
        "subcategory": "rideshare",
        "factor": "0.200",
        "factor_unit": "kgCO2e per km",
        "source": "DEFRA",
        "region": "",
        "valid_from": "2024-01-01",
    },
]


FACILITY_REGION_MAP = {
    "NYC Office": "US-NE",
    "Chicago Plant": "US-MW",
    "Chicago Office": "US-MW",
    "SF Office": "US-West",
}


class Command(BaseCommand):
    help = "Seed the database with org, users, samples, and normalized emission records"

    def handle(self, *args, **options):
        self._create_org_and_users()
        self._seed_emission_factors()
        self._process_sample_data()
        self._flag_suspicious_records()
        self.stdout.write(self.style.SUCCESS("Database seeded successfully"))

    def _create_org_and_users(self):
        org, created = Organization.objects.get_or_create(
            name="Acme Corporation",
            defaults={"slug": slugify("Acme Corporation")},
        )

        analyst, created = User.objects.get_or_create(
            username="analyst",
            defaults={"email": "analyst@acme.com"},
        )
        if created:
            analyst.set_password("password123")
            analyst.save()

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@acme.com"},
        )
        if created:
            admin_user.set_password("password123")
            admin_user.save()

        OrganizationMember.objects.get_or_create(
            organization=org, user=analyst, defaults={"role": "analyst"}
        )
        OrganizationMember.objects.get_or_create(
            organization=org, user=admin_user, defaults={"role": "admin"}
        )

        self.org = org
        self.analyst = analyst
        self.admin = admin_user
        self.stdout.write(f"  Org: {org.name}, Analyst: {analyst.username}")

    def _seed_emission_factors(self):
        for ef_data in EMISSION_FACTORS:
            EmissionFactor.objects.get_or_create(
                name=ef_data["name"],
                defaults={
                    "category": ef_data["category"],
                    "subcategory": ef_data["subcategory"],
                    "factor": Decimal(ef_data["factor"]),
                    "factor_unit": ef_data["factor_unit"],
                    "source": ef_data["source"],
                    "region": ef_data["region"],
                    "valid_from": ef_data["valid_from"],
                },
            )
        self.stdout.write(f"  Seeded {len(EMISSION_FACTORS)} emission factors")

    def _process_sample_data(self):
        sample_dir = "ingestion/sample_data"
        samples = [
            ("utility", f"{sample_dir}/utility_sample.csv", UtilityRawRow),
            ("sap", f"{sample_dir}/sap_sample.csv", SapRawRow),
            ("travel", f"{sample_dir}/travel_sample.csv", TravelRawRow),
        ]

        for source_type, filepath, row_model in samples:
            with open(filepath) as f:
                csv_string = f.read()
            parser = PARSER_MAP[source_type]
            rows = parser(csv_string)

            batch = ImportBatch.objects.create(
                source_type=source_type,
                filename=filepath.split("/")[-1],
                status="completed",
            )

            row_objects = [row_model(batch=batch, **row) for row in rows]
            row_model.objects.bulk_create(row_objects)

            self._normalize_rows(source_type, batch, rows, row_model)
            self.stdout.write(f"  Processed {source_type}: {len(rows)} rows -> emission records")

    def _normalize_rows(self, source_type, batch, rows, row_model):
        if source_type == "utility":
            self._normalize_utility(batch, rows)
        elif source_type == "sap":
            self._normalize_sap(batch, rows)
        elif source_type == "travel":
            self._normalize_travel(batch, rows)

    def _normalize_utility(self, batch, rows):
        for row in rows:
            consumption = row["consumption"] or 0
            facility = row["facility_name"]
            region = FACILITY_REGION_MAP.get(facility, "US-MW")
            factor = EmissionFactor.objects.filter(
                category="electricity", region=region
            ).first()
            factor_name = factor.name if factor else "Unknown"
            factor_value = float(factor.factor) if factor else 0.410

            activity_date_start = self._parse_date(row.get("billing_start_date"))
            activity_date_end = self._parse_date(row.get("billing_end_date"))

            co2e = float(consumption) * factor_value

            self._create_emission_record(
                organization=self.org,
                batch=batch,
                source_type="utility",
                scope=2,
                subcategory="purchased_electricity",
                activity_type=f"Electricity — {facility}",
                activity_quantity=consumption,
                activity_unit="kWh",
                emission_factor_used=factor_name,
                co2e_amount=round(co2e, 2),
                activity_date_start=activity_date_start,
                activity_date_end=activity_date_end,
                facility_or_plant=facility,
            )

    def _normalize_sap(self, batch, rows):
        MATERIAL_SCOPE_MAP = {
            "FUELS": (1, "fuel"),
            "RAW_MATERIALS": (3, "procurement"),
            "PACKAGING": (3, "procurement"),
        }

        MATERIAL_FACTOR_MAP = {
            "FUELS": {
                "diesel": "Diesel (stationary combustion)",
                "natural_gas": "Natural Gas (stationary combustion)",
            },
            "RAW_MATERIALS": {
                "steel": "Steel (procurement)",
                "cement": "Cement (procurement)",
            },
            "PACKAGING": {
                "packaging": "Packaging (procurement)",
            },
        }

        for row in rows:
            mat_group = (row.get("material_group") or "").upper()
            scope, category = MATERIAL_SCOPE_MAP.get(mat_group, (3, "procurement"))

            description = (row.get("material_description") or "").lower()
            subcategory = "diesel"
            if "natural gas" in description or "gas" in description:
                subcategory = "natural_gas"
            elif "steel" in description:
                subcategory = "steel"
            elif "cement" in description or "concrete" in description:
                subcategory = "cement"
            elif "packaging" in description:
                subcategory = "packaging"

            factor_map = MATERIAL_FACTOR_MAP.get(mat_group, {})
            factor_name_key = factor_map.get(subcategory)
            factor = None
            if factor_name_key:
                factor = EmissionFactor.objects.filter(
                    subcategory=subcategory
                ).first()

            factor_name = factor.name if factor else "Unknown"
            factor_value = float(factor.factor) if factor else 0

            quantity = float(row["quantity"] or 0)
            unit = row.get("unit", "")

            if scope == 1:
                if unit == "L":
                    co2e = quantity * factor_value
                elif unit == "kWh":
                    co2e = quantity * factor_value
                else:
                    co2e = quantity * factor_value
            else:
                if unit == "t" and factor_value:
                    co2e = quantity * factor_value * 1000
                elif unit == "kg" and factor_value:
                    co2e = quantity * factor_value
                else:
                    co2e = quantity * factor_value

            posting_date = self._parse_date(row.get("posting_date"))

            self._create_emission_record(
                organization=self.org,
                batch=batch,
                source_type="sap",
                scope=scope,
                subcategory=subcategory,
                activity_type=f"{description.title()} — {row.get('plant_code', '')}",
                activity_quantity=quantity,
                activity_unit=unit,
                emission_factor_used=factor_name,
                co2e_amount=round(co2e, 2),
                activity_date_start=posting_date,
                activity_date_end=posting_date,
                facility_or_plant=row.get("plant_code", ""),
            )

    def _normalize_travel(self, batch, rows):
        for row in rows:
            category = row.get("category", "")
            distance = float(row["distance_km"]) if row.get("distance_km") else None
            nights = row.get("hotel_nights")
            amount = float(row["amount"]) if row.get("amount") else 0

            if category == "flight":
                if distance:
                    if distance < 1000:
                        subcategory = "flight_short"
                        factor_name = "Flight — Short haul (<1000 km)"
                    elif distance < 4000:
                        subcategory = "flight_medium"
                        factor_name = "Flight — Medium haul (1000-4000 km)"
                    else:
                        subcategory = "flight_long"
                        factor_name = "Flight — Long haul (>4000 km)"
                    factor = EmissionFactor.objects.filter(name__icontains="Flight").filter(
                        subcategory=subcategory
                    ).first()
                    factor_value = float(factor.factor) if factor else 0.12
                    co2e = distance * factor_value
                    quantity = distance
                    unit = "km"
                else:
                    co2e = amount * 0.5
                    quantity = amount
                    unit = "USD"
                    factor_name = "Estimated (spend-based)"
                    subcategory = "flight"

            elif category == "hotel":
                nights_val = float(nights) if nights else 1
                factor = EmissionFactor.objects.filter(subcategory="hotel").first()
                factor_value = float(factor.factor) if factor else 25.0
                co2e = nights_val * factor_value
                quantity = nights_val
                unit = "nights"
                factor_name = factor.name if factor else "Hotel (per night)"
                subcategory = "hotel"

            elif category == "car_rental":
                days = nights if nights else 1
                factor = EmissionFactor.objects.filter(subcategory="car_rental").first()
                factor_value = float(factor.factor) if factor else 35.0
                co2e = days * factor_value
                quantity = days
                unit = "days"
                factor_name = factor.name if factor else "Car Rental (per day)"
                subcategory = "car_rental"

            elif category == "rideshare":
                dist = distance or 15
                factor = EmissionFactor.objects.filter(subcategory="rideshare").first()
                factor_value = float(factor.factor) if factor else 0.2
                co2e = dist * factor_value
                quantity = dist
                unit = "km"
                factor_name = factor.name if factor else "Rideshare (per km)"
                subcategory = "rideshare"

            else:
                co2e = amount * 0.3
                quantity = amount
                unit = "USD"
                factor_name = "Estimated (spend-based)"
                subcategory = category or "unknown"

            dep_date = self._parse_date(row.get("departure_date"))
            ret_date = self._parse_date(row.get("return_date"))

            self._create_emission_record(
                organization=self.org,
                batch=batch,
                source_type="travel",
                scope=3,
                subcategory=subcategory,
                activity_type=f"{category.replace('_', ' ').title()} — {row.get('employee_name', '')}",
                activity_quantity=quantity,
                activity_unit=unit,
                emission_factor_used=factor_name,
                co2e_amount=round(co2e, 2),
                activity_date_start=dep_date,
                activity_date_end=ret_date,
                facility_or_plant=f"{row.get('origin', '')} → {row.get('destination', '')}",
            )

    def _create_emission_record(self, **kwargs):
        if "batch" in kwargs:
            kwargs["import_batch"] = kwargs.pop("batch")
        record = EmissionRecord.objects.create(**kwargs)
        AuditLog.objects.create(
            emission_record=record,
            action="create",
            changed_by=self.analyst,
        )
        return record

    def _flag_suspicious_records(self):
        records = EmissionRecord.objects.filter(organization=self.org)
        if records.count() >= 2:
            outlier = records.order_by("-co2e_amount").first()
            outlier.flag = "outlier"
            outlier.save()
            AuditLog.objects.create(
                emission_record=outlier,
                action="flag",
                field_name="flag",
                old_value="none",
                new_value="outlier",
                changed_by=self.analyst,
            )

        missing = records.filter(activity_quantity__isnull=True).first()
        if missing:
            missing.flag = "missing_data"
            missing.save()
            AuditLog.objects.create(
                emission_record=missing,
                action="flag",
                field_name="flag",
                old_value="none",
                new_value="missing_data",
                changed_by=self.analyst,
            )

    def _parse_date(self, date_str):
        if not date_str or not date_str.strip():
            return None
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None
