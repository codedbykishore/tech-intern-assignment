from rest_framework import serializers
from .models import EmissionRecord, AuditLog, EmissionFactor


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "action", "field_name", "old_value", "new_value", "changed_by_name", "timestamp"]


class EmissionRecordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionRecord
        fields = [
            "id", "organization", "source_type", "scope", "subcategory",
            "activity_type", "activity_quantity", "activity_unit",
            "co2e_amount", "activity_date_start", "activity_date_end",
            "facility_or_plant", "status", "flag", "created_at",
        ]


class EmissionRecordDetailSerializer(serializers.ModelSerializer):
    audit_logs = AuditLogSerializer(many=True, read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.username", read_only=True)
    locked_by_name = serializers.CharField(source="locked_by.username", read_only=True)
    import_batch_filename = serializers.CharField(source="import_batch.filename", read_only=True, default=None)

    class Meta:
        model = EmissionRecord
        fields = "__all__"


class EmissionRecordBulkActionSerializer(serializers.Serializer):
    record_ids = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(
        choices=["approve", "flag", "reject", "lock"]
    )
    flag_type = serializers.ChoiceField(
        choices=["none", "missing_data", "outlier", "unit_ambiguity", "duplicate"],
        required=False,
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = "__all__"
