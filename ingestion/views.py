from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ImportBatch, UtilityRawRow, SapRawRow
from .serializers import ImportBatchSerializer
from .parsers import PARSER_MAP

ROW_MODEL_MAP = {
    "utility": UtilityRawRow,
    "sap": SapRawRow,
}


class ImportBatchViewSet(viewsets.ModelViewSet):
    queryset = ImportBatch.objects.all()
    serializer_class = ImportBatchSerializer

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        file = request.FILES.get("file")
        source_type = request.data.get("source_type")

        if not file or not source_type:
            return Response(
                {"error": "file and source_type are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parser = PARSER_MAP.get(source_type)
        row_model = ROW_MODEL_MAP.get(source_type)
        if not parser or not row_model:
            return Response(
                {"error": f"unsupported source_type: {source_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch = ImportBatch.objects.create(
            source_type=source_type,
            filename=file.name,
            status="parsing",
        )

        try:
            csv_string = file.read().decode("utf-8-sig")
            rows = parser(csv_string)
            row_objects = [row_model(batch=batch, **row) for row in rows]
            row_model.objects.bulk_create(row_objects)
            batch.status = "completed"
            batch.save()
        except Exception as e:
            batch.status = "failed"
            batch.save()
            return Response(
                {"error": str(e), "batch_id": batch.id},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "batch_id": batch.id,
                "status": batch.status,
                "rows_imported": len(rows),
            },
            status=status.HTTP_201_CREATED,
        )
