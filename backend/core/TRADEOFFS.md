# Tradeoffs

## 1. No Real Authentication

**What I didn't build:** A proper login system with user accounts, passwords, sessions, and per-user tenant assignment.

**What I built instead:** A single hardcoded admin user. All uploads and approvals are attributed to the first user in the database.

**Why:** Authentication is important but it's not what this prototype is testing. The goal was to demonstrate the data pipeline — ingest, normalize, review, approve. Adding auth would have taken 4-6 hours and pushed out the core functionality. In production this would use Django's built-in auth system with JWT tokens for the React frontend, and each user would be assigned to a tenant so they only see their own data.

**What breaks without it:** Anyone with the URL can upload data or approve records. Not acceptable for production but fine for a prototype review.

---

## 2. No Scheduled API Pulls

**What I didn't build:** Automated connectors that pull data directly from SAP OData, Concur REST API, or utility APIs on a schedule.

**What I built instead:** Manual file upload for all three sources.

**Why:** API integrations require OAuth credentials, connection management, error handling for timeouts and rate limits, and scheduled job infrastructure (like Celery with Redis). Each integration is a week of work on its own. File upload achieves the same end result for a prototype — data gets into the system, gets normalized, gets reviewed. The data model and normalization logic is identical whether data comes from a file or an API.

**What breaks without it:** The client has to manually export and upload files. This doesn't scale for large clients with monthly reporting cycles. The fix is to build API connectors on top of the existing normalization logic — the pipeline stays the same, only the ingestion entry point changes.

---

## 3. No Emission Factor Database

**What I didn't build:** A separate EmissionFactor table that stores factors by category, year, region, and source, updated independently of the codebase.

**What I built instead:** Hardcoded emission factors in the ingestion functions in views.py.

**Why:** A proper EF database with versioning, regional variations, and an admin UI to update factors is significant scope. For a prototype the factors don't change so hardcoding is fine. DEFRA publishes updated factors annually — in production you can't redeploy code every year just to update a number.

**What