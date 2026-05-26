# Decisions

## Why CSV flat file upload (not API/PDF)

**Chosen**: Flat file CSV upload for all three sources.

**Rationale**: Real SAP integrations use IDocs, BAPIs, or OData — but every SAP shop also knows how to dump a flat file from transaction Z_CSV_EXPORT. For a 4-day prototype, supporting the lowest-common-denominator format means we can demo with actual client data without negotiating API access. PDF parsing (utility bills, Concur receipts) is fragile and would consume the entire timeline for marginal gain.

**What I'd ask the PM**: "Do existing clients have a preferred SAP export method? If OData is standard for them, we should prioritize that over CSV."

## Why German header support

**Chosen**: Parser handles both German and English column headers.

**Rationale**: SAP's language setting controls export headers. A US multinational with a German SAP instance gets `Materialnummer` not `Material Number`. Hard-coding English headers would break for half our clients.

## Why 3 separate raw tables vs 1 generic table

**Chosen**: Three typed tables (`UtilityRawRow`, `SapRawRow`, `TravelRawRow`).

**Rationale**: Each source has a distinct schema. A single "raw_rows" table with a JSONB payload or EAV pattern would:
1. Lose column-level type enforcement (dates stay strings, decimals stay decimals)
2. Make indexing impractical (you can't index a specific field in JSONB efficiently)
3. Obscure the schema from anyone reading the model file

The cost is slightly more code per source, but the benefit is clarity and type safety.

## Why UUID `source_row_id` instead of a polymorphic FK

**Chosen**: Generic UUID field `source_row_id` on `EmissionRecord`.

**Rationale**: Django doesn't support polymorphic FKs natively. A GenericForeignKey would work but prevents using `select_related()`. A UUID allows looking up the source row across three tables without introducing a polymorphic dependency. In practice, `source_type + source_row_id` identifies the origin.

## Scope determination logic

**Scope is assigned at normalization time**, based on source type and material category:

| Source | Material/Activity | Scope |
|--------|------------------|-------|
| SAP — FUELS | Diesel, Natural Gas | 1 (direct combustion) |
| SAP — RAW_MATERIALS | Steel, Cement | 3 (upstream procurement) |
| SAP — PACKAGING | Packaging materials | 3 (upstream procurement) |
| Utility | Electricity | 2 (purchased energy) |
| Travel | All categories | 3 (business travel) |

This is simple and defensible. A more sophisticated system would let the analyst override scope per record.

## Emission factor source: EPA + DEFRA

**Chosen**: Both EPA and DEFRA factors.

**Rationale**: EPA provides US-specific electricity grid factors by region. DEFRA provides comprehensive travel factors (flights by distance tier, hotels, etc.). Using both gives coverage across all three source types. The `source` field on `EmissionFactor` tracks which agency provided each factor.

## Why dates are strings in raw tables

**Chosen**: CharField for dates in raw tables, DateField in normalized records.

**Rationale**: Raw data arrives in inconsistent formats (DD.MM.YYYY from SAP, MM/DD/YYYY from US utilities, ISO 8601 from APIs). Storing as-is preserves the original value. Parsing happens during normalization, where we can validate and reject bad dates without losing the raw input.

## What I'd ask the PM (if I could only ask 3 questions)

1. **"Do you want analysts to override the auto-assigned scope per record, or is the normalization logic authoritative?"** — This changes the UI significantly (editable scope field vs. read-only badge).

2. **"What's the actual SAP export mechanism for this client? Is it a flat file dump, or do they have an OData service we should hit?"** — Determines whether we need to build a poller or keep the upload UI.

3. **"Do we need to support custom emission factors per client, or are the EPA/DEFRA defaults sufficient?"** — If clients want to upload their own factors, that's another model and upload flow.
