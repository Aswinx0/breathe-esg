from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Tenant, IngestionRun, EmissionRecord, AuditLog
from django.contrib.auth.models import User
import csv
import io

def get_default_user():
    return User.objects.first()

def get_default_tenant():
    return Tenant.objects.first()

# ── SAP ingestion ──────────────────────────────────────────────
def process_sap(file, run):
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    records = []
    for row in reader:
        try:
            quantity = float(row.get('Quantity', 0))
            unit = row.get('Unit', 'L').strip()
            # Convert to kg CO2e using diesel emission factor (DEFRA 2023)
            if unit == 'L':
                ef = 2.68  # kg CO2e per litre of diesel
            else:
                ef = 2.68
            normalized = quantity * ef
            records.append(EmissionRecord(
                ingestion_run=run,
                tenant=run.tenant,
                scope=1,
                category=row.get('Material', 'Fuel'),
                activity_value=quantity,
                activity_unit=unit,
                normalized_value=round(normalized, 4),
                normalized_unit='kg_co2e',
                emission_factor=ef,
                emission_factor_source='DEFRA 2023',
                source_row=dict(row),
                status='pending'
            ))
        except Exception:
            continue
    EmissionRecord.objects.bulk_create(records)

# ── Utility ingestion ──────────────────────────────────────────
def process_utility(file, run):
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    records = []
    for row in reader:
        try:
            kwh = float(row.get('kWh', 0))
            ef = 0.233  # kg CO2e per kWh (UK grid average, DEFRA 2023)
            normalized = kwh * ef
            records.append(EmissionRecord(
                ingestion_run=run,
                tenant=run.tenant,
                scope=2,
                category='Electricity',
                activity_value=kwh,
                activity_unit='kWh',
                normalized_value=round(normalized, 4),
                normalized_unit='kg_co2e',
                emission_factor=ef,
                emission_factor_source='DEFRA 2023',
                source_row=dict(row),
                status='pending'
            ))
        except Exception:
            continue
    EmissionRecord.objects.bulk_create(records)

# ── Travel ingestion ───────────────────────────────────────────
AIRPORT_DISTANCES = {
    ('BOM', 'DEL'): 1148,
    ('DEL', 'BOM'): 1148,
    ('BLR', 'DEL'): 1740,
    ('DEL', 'BLR'): 1740,
    ('BOM', 'BLR'): 845,
    ('BLR', 'BOM'): 845,
    ('MAA', 'DEL'): 1754,
    ('DEL', 'MAA'): 1754,
    ('CCU', 'DEL'): 1305,
    ('DEL', 'CCU'): 1305,
}

def process_travel(file, run):
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    records = []
    for row in reader:
        try:
            travel_type = row.get('Type', '').strip().upper()
            if travel_type == 'FLIGHT':
                origin = row.get('Origin', '').strip().upper()
                dest = row.get('Destination', '').strip().upper()
                distance = AIRPORT_DISTANCES.get((origin, dest), 1000)
                ef = 0.255  # kg CO2e per km per passenger (economy, DEFRA 2023)
                normalized = distance * ef
                category = f"Flight {origin}-{dest}"
            elif travel_type == 'HOTEL':
                nights = float(row.get('Nights', 1))
                ef = 31.0  # kg CO2e per night (average hotel, DEFRA 2023)
                normalized = nights * ef
                category = 'Hotel Stay'
                distance = nights
            else:
                km = float(row.get('Distance_km', 0))
                ef = 0.14  # kg CO2e per km (average taxi/ground)
                normalized = km * ef
                category = 'Ground Transport'
                distance = km

            records.append(EmissionRecord(
                ingestion_run=run,
                tenant=run.tenant,
                scope=3,
                category=category,
                activity_value=distance,
                activity_unit='km' if travel_type != 'HOTEL' else 'nights',
                normalized_value=round(normalized, 4),
                normalized_unit='kg_co2e',
                emission_factor=ef,
                emission_factor_source='DEFRA 2023',
                source_row=dict(row),
                status='pending'
            ))
        except Exception:
            continue
    EmissionRecord.objects.bulk_create(records)

# ── Upload endpoint ────────────────────────────────────────────
@api_view(['POST'])
def upload_file(request):
    source_type = request.data.get('source_type')
    file = request.FILES.get('file')
    if not file or not source_type:
        return Response({'error': 'file and source_type required'}, status=400)

    tenant = get_default_tenant()
    user = get_default_user()

    # Read file content before saving
    file_content = file.read()
    file.seek(0)

    run = IngestionRun.objects.create(
        tenant=tenant,
        source_type=source_type,
        uploaded_by=user,
        raw_file=file,
        status='processing'
    )

    try:
        import io
        file_like = io.BytesIO(file_content)

        if source_type == 'SAP':
            process_sap(file_like, run)
        elif source_type == 'UTILITY':
            process_utility(file_like, run)
        elif source_type == 'TRAVEL':
            process_travel(file_like, run)
        run.status = 'complete'
        run.save()
    except Exception as e:
        run.status = 'failed'
        run.save()
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Upload successful', 'run_id': run.id})

# @api_view(['POST'])
# def upload_file(request):
#     source_type = request.data.get('source_type')
#     file = request.FILES.get('file')
#     if not file or not source_type:
#         return Response({'error': 'file and source_type required'}, status=400)

#     tenant = get_default_tenant()
#     user = get_default_user()

#     run = IngestionRun.objects.create(
#         tenant=tenant,
#         source_type=source_type,
#         uploaded_by=user,
#         raw_file=file,
#         status='processing'
#     )

#     try:
#         if source_type == 'SAP':
#             process_sap(request.FILES.get('file'), run)
#         elif source_type == 'UTILITY':
#             process_utility(request.FILES.get('file'), run)
#         elif source_type == 'TRAVEL':
#             process_travel(request.FILES.get('file'), run)
#         run.status = 'complete'
#         run.save()
#     except Exception as e:
#         run.status = 'failed'
#         run.save()
#         return Response({'error': str(e)}, status=500)

#     return Response({'message': 'Upload successful', 'run_id': run.id})

# ── Records endpoint ───────────────────────────────────────────
@api_view(['GET'])
def get_records(request):
    records = EmissionRecord.objects.all().order_by('-created_at')
    data = []
    for r in records:
        data.append({
            'id': r.id,
            'scope': r.scope,
            'category': r.category,
            'activity_value': r.activity_value,
            'activity_unit': r.activity_unit,
            'normalized_value': r.normalized_value,
            'normalized_unit': r.normalized_unit,
            'emission_factor': r.emission_factor,
            'emission_factor_source': r.emission_factor_source,
            'status': r.status,
            'source_type': r.ingestion_run.source_type,
            'uploaded_at': r.ingestion_run.uploaded_at,
        })
    return Response(data)

# ── Approve/Reject endpoint ────────────────────────────────────
@api_view(['POST'])
def review_record(request, record_id):
    action = request.data.get('action')
    if action not in ['approved', 'rejected']:
        return Response({'error': 'action must be approved or rejected'}, status=400)
    try:
        record = EmissionRecord.objects.get(id=record_id)
        record.status = action
        record.reviewed_by = get_default_user()
        record.reviewed_at = timezone.now()
        record.save()
        AuditLog.objects.create(
            record=record,
            action=action,
            performed_by=get_default_user(),
        )
        return Response({'message': f'Record {action}'})
    except EmissionRecord.DoesNotExist:
        return Response({'error': 'Record not found'}, status=404)