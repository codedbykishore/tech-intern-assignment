from django.contrib import admin
from .models import EmissionRecord, EmissionFactor, AuditLog


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ["activity_type", "scope", "status", "flag", "co2e_amount", "organization", "created_at"]
    list_filter = ["scope", "status", "flag", "source_type"]


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "factor", "source", "region"]
    list_filter = ["source", "region"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["emission_record", "action", "changed_by", "timestamp"]
