from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import EmissionRecord, AuditLog
from .serializers import (
    EmissionRecordListSerializer,
    EmissionRecordDetailSerializer,
    EmissionRecordBulkActionSerializer,
)
from organizations.mixins import OrgFilterMixin


class EmissionRecordViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = EmissionRecord.objects.select_related("reviewed_by", "locked_by", "import_batch")
    serializer_class = EmissionRecordDetailSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return EmissionRecordListSerializer
        return EmissionRecordDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_by_org(qs)
        org_id = self.request.query_params.get("organization")
        if org_id:
            qs = qs.filter(organization_id=org_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        scope = self.request.query_params.get("scope")
        if scope:
            qs = qs.filter(scope=scope)

        flag = self.request.query_params.get("flag")
        if flag:
            qs = qs.filter(flag=flag)

        source_type = self.request.query_params.get("source_type")
        if source_type:
            qs = qs.filter(source_type=source_type)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(activity_type__icontains=search)

        return qs

    @action(detail=False, methods=["post"], url_path="bulk_action")
    def bulk_action(self, request):
        serializer = EmissionRecordBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record_ids = serializer.validated_data["record_ids"]
        action = serializer.validated_data["action"]
        flag_type = serializer.validated_data.get("flag_type")
        notes = serializer.validated_data.get("notes", "")

        records = EmissionRecord.objects.filter(id__in=record_ids)
        user = request.user
        results = []

        for record in records:
            old_status = record.status
            old_flag = record.flag

            if action == "approve":
                record.status = "approved"
                record.reviewed_by = user
            elif action == "reject":
                record.status = "rejected"
                record.reviewed_by = user
            elif action == "lock":
                record.status = "locked"
                record.locked_by = user
            elif action == "flag":
                if flag_type:
                    record.flag = flag_type
                else:
                    record.flag = "outlier"

            if notes:
                record.analyst_notes = notes

            record.save()

            AuditLog.objects.create(
                emission_record=record,
                action=action,
                field_name="status" if action != "flag" else "flag",
                old_value=old_status if action != "flag" else old_flag,
                new_value=getattr(record, "status" if action != "flag" else "flag"),
                changed_by=user,
            )
            results.append({"id": record.id, "status": record.status, "flag": record.flag})

        return Response({"results": results})
