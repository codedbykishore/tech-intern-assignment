from django.db import models


class ImportBatch(models.Model):
    SOURCE_CHOICES = [
        ("utility", "Utility"),
        ("sap", "SAP"),
        ("travel", "Travel"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("parsing", "Parsing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type}: {self.filename} ({self.status})"


class UtilityRawRow(models.Model):
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="utility_rows")
    row_index = models.IntegerField()
    meter_number = models.CharField(max_length=100, blank=True)
    meter_read_date = models.CharField(max_length=50, blank=True)
    billing_start_date = models.CharField(max_length=50, blank=True)
    billing_end_date = models.CharField(max_length=50, blank=True)
    consumption = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    consumption_unit = models.CharField(max_length=20, blank=True)
    tariff_name = models.CharField(max_length=200, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    facility_name = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["batch", "row_index"]


class SapRawRow(models.Model):
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="sap_rows")
    row_index = models.IntegerField()
    material_number = models.CharField(max_length=100, blank=True)
    material_description = models.CharField(max_length=500, blank=True)
    plant_code = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    posting_date = models.CharField(max_length=50, blank=True)
    document_number = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    cost_center = models.CharField(max_length=100, blank=True)
    material_group = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["batch", "row_index"]
