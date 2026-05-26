# Data Model

## Overview

Six core models across three apps: `ingestion`, `organizations`, and `emissions`. Raw data is kept separate from normalized data to preserve auditability.

## ImportBatch (`ingestion`)

Tracks each file upload. Fields: `source_type` (utility/sap/travel), `filename`, `status` (pending/parsing/completed/failed), `created_at`. Every raw row and emission record links back to its batch.

**Why**: Source-of-truth tracking. If a parser changes, we can re-parse from raw rows without losing the original upload.

## Raw Row Tables (`ingestion`)

Three separate tables — `UtilityRawRow`, `SapRawRow`, `TravelRawRow` — rather than one generic table.

**Why**: Each source has a fundamentally different shape. A generic EAV or JSONB table would lose column-level type safety, make indexing harder, and obscure what fields exist.

### UtilityRawRow
- Dates stored as `CharField` (e.g. `01.01.2024`), not `DateField`
- `consumption` and `total_cost` as `Decimal`
- Units vary by meter (kWh, therm, etc.), stored in `consumption_unit`

### SapRawRow
- German headers supported through the parser layer
- `quantity` and `amount` as `Decimal`
- `unit` normalized at parse time (Liter→L, Tons→t)
- Unknown columns captured via `raw_*` dynamic fields
- `posting_date` as CharField

### TravelRawRow
- `category` with choices: flight/hotel/car_rental/rideshare/train
- `distance_km` stores normalized distance (miles converted at parse time)
- `hotel_nights` for hotel stays

## Organization (`organizations`)

`Organization` (name, slug) and `OrganizationMember` (org, user, role: admin/analyst/viewer).

**Why multi-tenancy**: An analyst should only see their client's data. The `OrgFilterMixin` enforces this at the view level by filtering querysets to orgs the user belongs to.

## EmissionRecord (`emissions`)

The core normalized record. Key design decisions:

- **Scope is stored as an integer choice** (1/2/3), determined at normalization time. This is correct because scope depends on the activity type and source, which are known when raw data is parsed.
- **Dates are `DateField`** here but `CharField` in raw tables. Normalization is the point where we parse and validate dates.
- **`co2e_amount`** is always in kgCO₂e. Storing in a standard unit avoids conversion confusion.
- **`source_row_id`** is a generic UUID field. It references the raw row across three different tables — the actual FK is determined by `source_type`.
- **Status lifecycle**: imported → approved/locked/rejected. Locked records are read-only for audit.
- **Flag field**: none/missing_data/outlier/unit_ambiguity/duplicate. Flags surface suspicious records on the dashboard.
- **`emission_factor_used`** is a `CharField`, not an FK. Emission factors change over time; we capture the name at the time of calculation.

### Indexes
- Composite indexes on (organization, status), (organization, scope), (organization, flag) — these cover the most common query patterns.

## AuditLog (`emissions`)

Every status change, flag change, or edit creates an audit entry: `action`, `field_name`, `old_value`, `new_value`, `changed_by`, `timestamp`.

**Why**: Audit trail is required for carbon accounting. An auditor needs to see who changed what and when.

## EmissionFactor (`emissions`)

Lookup table with `factor` (decimal), `factor_unit`, `source` (EPA/DEFRA), `region`, `valid_from`/`valid_until`. Seeded with 14 factors covering fuels, electricity by US region, flights by distance tier, hotels, car rental, and rideshare.

**Why not auto-update**: Factors change annually. Automated updates were intentionally not built (see TRADEOFFS.md).
