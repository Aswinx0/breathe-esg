# Sources

## 1. SAP — Fuel & Procurement Data

### What I researched
SAP stores procurement and materials data in modules MM (Materials Management) and FI (Financial Accounting). The most common ways sustainability teams extract this data are:
- Transaction SE16N or ME2M: direct table exports as CSV or Excel
- Transaction FAGLL03: FI line items export
- SAP List Viewer exports: any report can be exported as CSV

Real SAP exports have these characteristics:
- Column headers can be in German (Menge = Quantity, Werk = Plant, Buchungsdatum = Posting Date)
- Dates are in YYYYMMDD format (20240101 not 2024-01-01)
- Plant codes are internal codes (PL01, PL02) that mean nothing without a master data lookup table
- Units use SAP internal codes (L for litres, KG for kilograms, M3 for cubic metres)
- Material codes are numbers (100000023) not human readable names

### What my sample data looks like
I simplified the real format to make it processable without a master data lookup table:
- Used human readable material names (Diesel, Petrol) instead of material codes
- Used simple plant codes (PL01, PL02, PL03)
- Used standard date format instead of YYYYMMDD
- Kept Quantity and Unit columns which are realistic

### What would break in real deployment
- Real SAP exports would have numeric material codes needing a lookup table to identify as fuel
- German column headers would need detection and remapping
- YYYYMMDD dates would need parsing
- Multiple unit types (L, KG, M3) need different emission factors
- Plant codes need mapping to locations for regional emission factors

---

## 2. Utility — Electricity Data

### What I researched
Utility data comes in three main ways:
- PDF bills: most common for small sites, hard to parse programmatically
- Portal CSV exports: most utility providers (EDF, British Gas, Octopus) have business portals where admins can export consumption data as CSV
- Green Button Data: US open standard (ESPI protocol) that utilities support for machine-readable energy data

Real utility CSV exports contain:
- Meter ID or MPAN (Meter Point Administration Number in UK)
- Billing period start and end dates (which rarely align with calendar months)
- kWh consumed in the period
- Peak and off-peak breakdown sometimes
- Tariff name and unit rate
- Site or location identifier

### What my sample data looks like
I modelled it on a typical UK utility portal export:
- Meter_ID as identifier
- Billing_Period_Start and Billing_Period_End to capture the actual period
- kWh as the consumption figure
- Tariff and Site for context

### What would break in real deployment
- Billing periods crossing month boundaries need to be split for monthly reporting
- Some exports give gas in cubic metres not kWh, needing a calorific value conversion
- Multiple meters per site need aggregation
- Some utilities export MWh not kWh, causing a 1000x error if not detected
- PDF bills would need OCR or a parsing library like pdfplumber

---

## 3. Corporate Travel — Flights, Hotels, Ground Transport

### What I researched
Corporate travel platforms like Concur (SAP), Navan, and Egencia expose data in two ways:
- REST API: Concur has a public API at developer.concur.com with endpoints for trip reports and expense reports. Requires OAuth 2.0 with corporate credentials.
- CSV export: Admins can export trip reports as CSV from the platform UI. This is how most sustainability teams get the data today.

Real travel exports contain:
- Employee ID and name
- Trip type (air, hotel, car, rail)
- For flights: origin and destination (usually airport codes like BOM, DEL), sometimes distance, sometimes just city names
- For hotels: property name, city, check-in and check-out dates
- For ground: vendor name, distance sometimes not given

Distances are often not provided for flights — you only get airport codes and have to calculate great circle distance yourself.

### What my sample data looks like
I modelled it on a Concur trip export with three categories:
- FLIGHT with origin and destination airport codes (Indian domestic routes)
- HOTEL with number of nights
- GROUND with distance in km

For airport distances I built a small lookup table of common Indian domestic routes. In production this would use a great circle distance calculation from airport coordinates.

### What would break in real deployment
- International routes not in my lookup table default to 1000km which is wrong
- No differentiation between economy and business class (business is ~3x the emission factor)
- Hotel emission factors vary significantly by country and star rating — I used a single average
- Ground transport doesn't distinguish between taxi, rental car, or rail (very different factors)
- Some Concur exports give city names not airport codes, needing a city-to-airport mapping
- Connecting flights are logged as separate segments but my model treats each row independently