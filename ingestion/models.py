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
