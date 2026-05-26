from django.contrib import admin
from .models import ImportBatch, UtilityRawRow, SapRawRow


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ["source_type", "filename", "status", "created_at"]


@admin.register(UtilityRawRow)
class UtilityRawRowAdmin(admin.ModelAdmin):
    list_display = ["batch", "row_index", "meter_number", "consumption", "facility_name"]


@admin.register(SapRawRow)
class SapRawRowAdmin(admin.ModelAdmin):
    list_display = ["batch", "row_index", "material_number", "material_description", "plant_code"]
