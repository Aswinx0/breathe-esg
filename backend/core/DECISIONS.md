# Decisions

## SAP — Flat File CSV Upload

**What I chose:** CSV flat file upload via browser.

**Why:** SAP can export data in many ways — IDoc (EDI format), OData API, BAPI function calls, or plain flat file exports via transaction SE16N or FAGLL03. For a prototype with a new client onboarding, flat file is the most realistic starting point. Most sustainability teams don't have an integration team setting up OData connections — they export a spreadsheet and email it. IDoc requires middleware (SAP PI/PO or Integration Suite) which is a full engineering project on its own. Flat file gets data moving on day one.

**What I handled:** Material name, quantity, unit, plant code, date, document number.

**What I ignored:** Plant code lookup tables (in reality PL01 means nothing without a master data table mapping it to a location), German column headers (some SAP configs export Menge instead of Quantity), and multi-currency procurement data.

**What I'd ask the PM:** Do they have a master data table mapping plant codes to locations and emission factors? Are they exporting from MM60 (materials) or FI (finance)? Which SAP transaction does their team use to pull this data?

---

## Utility — Portal CSV Export

**What I chose:** CSV upload mimicking a utility portal export.

**Why:** There are three realistic ways to get utility data — PDF bills, portal CSV exports, or Green Button Data (an open standard many US utilities support). PDF parsing is fragile and breaks when the bill format changes. Green Button requires the utility to support it, which not all do especially outside the US. Portal CSV is what most facilities teams actually do — log into the utility portal, select a date range, export CSV. It's manual but reliable and realistic.

**What I handled:** Meter ID, billing period start/end, kWh consumed, tariff name, site name.

**What I ignored:** Tiered tariff structures (where the first 1000 kWh is priced differently), demand charges, power factor corrections, and billing periods that don't align with calendar months (a bill from Jan 15 to Feb 14 is hard to split across months).

**What I'd ask the PM:** Which utility providers do their sites use? Do they have multiple meters per site? Do they need to split bills across accounting periods?

---

## Corporate Travel — Concur CSV Export

**What I chose:** CSV upload mimicking a Concur expense/trip export.

**Why:** Concur has a REST API but it requires OAuth setup with corporate credentials, which we can't prototype without a real account. Navan is similar. However both platforms let admins export trip reports as CSV. This is how most sustainability teams get travel data today — a quarterly export from the travel platform. The CSV approach is realistic and handles the same data fields the API would return.

**What I handled:** Flight (origin/destination airport codes, distance lookup), hotel (number of nights), ground transport (distance in km).

**What I ignored:** Flight class (business vs economy has very different emission factors — business is roughly 3x economy), connecting flights vs direct (affects distance), car rental vs taxi for ground transport, and international flights where I don't have distance data.

**What I'd ask the PM:** Do they need business vs economy class differentiation? Do they have Concur admin access for direct API integration? How many countries do their employees travel to?

---

## Ingestion Mechanism — File Upload for All Three

**What I chose:** Browser file upload for all three sources.

**Why:** The alternative is scheduled API pulls (connect once, pull automatically). API pulls are better long-term but require credentials, OAuth setup, scheduled jobs, and error handling for connection failures. For onboarding a new client in 4 days, file upload is faster to implement and easier for the client to control. They upload when they're ready, not on our schedule.

---

## Emission Factors — DEFRA 2023 Hardcoded

**What I chose:** Hardcoded DEFRA 2023 factors in the ingestion logic.

**Why:** DEFRA (UK Department for Environment, Food and Rural Affairs) publishes annual emission factors that are widely used in corporate carbon accounting. Hardcoding them is fine for a prototype. In production these