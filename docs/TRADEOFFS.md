# Tradeoffs

Three things deliberately not built, and why.

## 1. Real-time API integrations

**Not built**: Automated polling of SAP OData, utility APIs, or Concur/Navan APIs.

**Why**: Each API integration is a multi-day effort (auth flows, pagination, rate limiting, error recovery, webhook setup). For a 4-day prototype, a file upload UI gets client data flowing immediately. In production, you'd build connectors incrementally — start with the most painful source (likely SAP) and automate it first.

**What breaks**: An analyst has to manually download and upload files. For a client uploading weekly utility data, this is fine. For a client with 50 facilities reporting daily, it's not.

## 2. PDF parsing for utility bills

**Not built**: Parsing PDF utility bills or Concur receipts.

**Why**: PDF parsing is a rabbit hole. Each utility formats their PDF differently; Concur receipts have no standard template. A PDF parser that works for Con Edison will likely fail for PG&E. CSV exports are already available from every utility portal and from Concur. The effort-to-coverage ratio is terrible.

**What breaks**: Clients who only have PDF bills (common for smaller facilities) can't upload them. The workaround is to manually enter data or request a CSV export from their utility provider.

## 3. Automated emission factor updates

**Not built**: A scheduler that pulls the latest EPA eGRID and DEFRA factors annually.

**Why**: EPA and DEFRA release updated factors once per year. The logic to download, parse, and validate updated spreadsheets is straightforward but requires error handling (what if the format changes? what if a factor is missing?). For a prototype, seeded factors are sufficient. In production, you'd build this as a quarterly management command with a diff review step so an analyst can approve changes before they apply retroactively.

**What breaks**: Factors gradually become stale. For a 2024 pilot, using 2024 factors is fine. By 2026, the numbers would be inaccurate enough to affect audit readiness.
