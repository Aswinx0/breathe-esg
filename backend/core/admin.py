from django.contrib import admin
from .models import Tenant, IngestionRun, EmissionRecord, AuditLog

admin.site.register(Tenant)
admin.site.register(IngestionRun)
admin.site.register(EmissionRecord)
admin.site.register(AuditLog)