from django.db import models
from django.contrib.auth.models import User

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class IngestionRun(models.Model):
    SOURCE_TYPES = [
        ('SAP', 'SAP Fuel & Procurement'),
        ('UTILITY', 'Utility Electricity'),
        ('TRAVEL', 'Corporate Travel'),
    ]
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw_file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    def __str__(self):
        return f"{self.source_type} - {self.uploaded_at}"

class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        (1, 'Scope 1'),
        (2, 'Scope 2'),
        (3, 'Scope 3'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked'),
    ]
    ingestion_run = models.ForeignKey(IngestionRun, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    category = models.CharField(max_length=100)
    activity_value = models.FloatField()
    activity_unit = models.CharField(max_length=50)
    normalized_value = models.FloatField()
    normalized_unit = models.CharField(max_length=50, default='kg_co2e')
    emission_factor = models.FloatField()
    emission_factor_source = models.CharField(max_length=255)
    source_row = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.normalized_value} kg CO2e"

class AuditLog(models.Model):
    record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} - {self.performed_at}"