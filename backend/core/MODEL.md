# Data Model

## Overview
The data model is designed around a simple pipeline:
Tenant → IngestionRun → EmissionRecord → AuditLog

Every piece of data knows where it came from, who touched it, and what state it's in.

## Tables

### Tenant
Represents a client company using the platform.
- id, name, created_at
- All data is scoped to a tenant so one client never sees another's data.
- For this prototype, multi-tenancy is handled with a FK on every table (row-level), not separate database schemas. This is simpler to build but means extra care is needed in queries to always filter by tenant.

### IngestionRun
Represents one file upload event.
- source_type: SAP, UTILITY, or TRAVEL
- uploaded_by, uploaded_at: who uploaded and when
- raw_file: original file is always stored, never deleted
- status: processing → complete or failed
- Why: we need to know exactly which file produced which records. If data is wrong, we trace back to the source file.

### EmissionRecord
The core table. One row per emission activity.
- scope: 1 (direct), 2 (electricity), 3 (indirect like travel)
- activity_value + activity_unit: the original number and unit from the source (e.g. 500 L)
- normalized_value + normalized_unit: always kg CO2e after conversion
- emission_factor + emission_factor_source: what factor was used and where it came from (DEFRA 2023)
- source_row: the full original CSV row stored as JSON, so nothing is lost
- status: pending → approved or rejected
- reviewed_by, reviewed_at: who approved/rejected and when
- is_edited: flag if an analyst changed the value after ingestion

### AuditLog
Append-only log of every approve/reject action.
- record, action, performed_by, performed_at, note
- This table is never updated, only inserted into. This gives a full history for auditors.

## Scope Classification
- Scope 1: SAP fuel data (direct combustion)
- Scope 2: Utility electricity data (indirect, purchased energy)
- Scope 3: Corporate travel (value chain emissions)

## Unit Normalization
All activity values are converted to kg CO2e at ingestion time using DEFRA 2023 emission factors:
- Diesel: 2.68 kg CO2e per litre
- Petrol: 2.68 kg CO2e per litre  
- Electricity: 0.233 kg CO2e per kWh (UK grid average)
- Flights: 0.255 kg CO2e per km per passenger (economy)
- Hotels: 31.0 kg CO2e per night
- Ground transport: 0.14 kg CO2e per km

Original units are always preserved in activity_unit so nothing is lost.

## What I Would Add With More Time
- Separate EmissionFactor table so factors can be updated without changing code
- User authentication and per-user tenant assignment
- Schema-level multi-tenancy for stronger data isolation
- Locked status on records after audit sign-off