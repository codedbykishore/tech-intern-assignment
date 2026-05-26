# Source Research

## SAP Exports (Fuel & Procurement)

**Format chosen**: Flat file CSV.

**Research**: SAP can export data via IDoc, BAPI, OData, or flat file. The most common way non-SAP systems consume SAP data is a CSV dump from a transaction (e.g., ZMM_MATERIAL_STOCK or a custom Z program). German headers (`Materialnummer`, `Werk`, `Menge`) appear when the SAP instance language is German. Units are mixed (L, kg, t, m3). Dates use DD.MM.YYYY format.

**Sample data rationale**: 8 rows covering diesel, natural gas, steel, cement, and packaging materials. Two facilities (DE-PLANT-01, DE-PLANT-02). Mixed units (L, kWh, t, kg). German headers to test the internationalization support. Material groups (FUELS, RAW_MATERIALS, PACKAGING) drive scope assignment in normalization.

**What breaks in production**:
- Plant codes are meaningless without a material master lookup table
- Prices (amount/quantity) may include VAT or not depending on configuration
- Some SAP exports include header rows before the CSV data that need to be stripped
- Very large exports (>100k rows) may need streaming CSV parsing instead of loading into memory

## Utility Exports (Electricity)

**Format chosen**: CSV from utility portal.

**Research**: Con Edison, PG&E, and ComEd all offer CSV export from their online portals. Typical fields: meter number, read date (or start/end dates), consumption (kWh or therm), tariff name, and total cost. Some utilities include demand charges, taxes, and surcharges as separate columns. Billing periods rarely align with calendar months — they follow the meter read cycle.

**Sample data rationale**: 6 rows across 3 facilities (NYC, Chicago, SF) with 2 months each. Realistic tariffs (Commercial A, Industrial B, Green Tariff C). Consumption ranges aligned with typical office/plant usage. Dates in DD.MM.YYYY format.

**What breaks in production**:
- Some utility exports are PDF, not CSV (would need PDF parsing — see TRADEOFFS.md)
- Interval meters export 15-minute or hourly data (potentially thousands of rows per month)
- Tariff names are utility-specific and don't map cleanly between providers
- Facilities may have multiple meters, and meter-to-facility mapping is often manual

## Travel Exports (Concur)

**Format chosen**: CSV from Concur expense reports.

**Research**: Concur's expense report export includes employee name, expense type (Flight/Hotel/Car Rental), vendor, travel dates, amount, and currency. Distances are not always included — domestic flights often show $0 distance or missing data. Hotel receipts include nightly rate × nights. International travel may include origin/destination airport codes instead of city names.

**Sample data rationale**: 8 rows spanning all major categories (flight, hotel, car_rental, rideshare, train). Mix of domestic and international trips. Some rows have explicit distances (km), others rely on spend-based estimation. Multiple currencies (USD, EUR) to test currency handling. Vendor names chosen to trigger auto-categorization (Delta→flight, Marriott→hotel, Uber→rideshare).

**What breaks in production**:
- Distances are frequently missing — spend-based estimation is a fallback but introduces error
- Expense type categorization is unreliable (some vendors appear under multiple categories)
- Currency conversion rates change daily; storing in original currency is essential
- Concur also offers a REST API that could replace CSV upload entirely
