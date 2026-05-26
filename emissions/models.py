from django.db import models
from django.contrib.auth.models import User
from organizations.models import Organization
from ingestion.models import ImportBatch


class EmissionFactor(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    factor = models.DecimalField(max_digits=14, decimal_places=6)
    factor_unit = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    region = models.CharField(max_length=100, blank=True)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.source})"


class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        (1, "Scope 1"),
        (2, "Scope 2"),
        (3, "Scope 3"),
    ]
    STATUS_CHOICES = [
        ("imported", "Imported"),
        ("approved", "Approved"),
        ("locked", "Locked"),
        ("rejected", "Rejected"),
    ]
    FLAG_CHOICES = [
        ("none", "None"),
        ("missing_data", "Missing Data"),
        ("outlier", "Outlier"),
        ("unit_ambiguity", "Unit Ambiguity"),
        ("duplicate", "Duplicate"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="emission_records"
    )
    import_batch = models.ForeignKey(
        ImportBatch, on_delete=models.SET_NULL, null=True, related_name="emission_records"
    )
    source_type = models.CharField(max_length=20)
    source_row_id = models.UUIDField(null=True, blank=True)

    scope = models.IntegerField(choices=SCOPE_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True)
    activity_type = models.CharField(max_length=200, blank=True)
    activity_quantity = models.DecimalField(max_digits=16, decimal_places=6, null=True, blank=True)
    activity_unit = models.CharField(max_length=50, blank=True)
    emission_factor_used = models.CharField(max_length=255, blank=True)
    co2e_amount = models.DecimalField(max_digits=16, decimal_places=4)
    activity_date_start = models.DateField(null=True, blank=True)
    activity_date_end = models.DateField(null=True, blank=True)
    facility_or_plant = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="imported")
    flag = models.CharField(max_length=20, choices=FLAG_CHOICES, default="none")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_records"
    )
    locked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="locked_records"
    )
    analyst_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "scope"]),
            models.Index(fields=["organization", "flag"]),
        ]

    def __str__(self):
        return f"[Scope {self.scope}] {self.activity_type} — {self.co2e_amount} kgCO2e"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("approve", "Approve"),
        ("flag", "Flag"),
        ("reject", "Reject"),
        ("lock", "Lock"),
        ("edit", "Edit"),
        ("note", "Note"),
    ]

    emission_record = models.ForeignKey(
        EmissionRecord, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="audit_actions"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} on record {self.emission_record_id} by {self.changed_by}"
