from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from emissions.models import EmissionRecord


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    org_id = request.query_params.get("organization")
    if not org_id:
        return Response({"error": "organization parameter is required"}, status=400)

    records = EmissionRecord.objects.filter(organization_id=org_id)

    summary = {
        "total_records": records.count(),
        "pending_review": records.filter(status="imported").count(),
        "flagged": records.exclude(flag="none").count(),
        "approved": records.filter(status="approved").count(),
        "total_co2e_kg": records.aggregate(total=Sum("co2e_amount"))["total"] or Decimal("0"),
    }

    scope_breakdown = list(
        records.values("scope")
        .annotate(count=Count("id"), total_co2e_kg=Sum("co2e_amount"))
        .order_by("scope")
    )

    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly = (
        records.filter(activity_date_start__gte=six_months_ago)
        .extra(select={"month": "strftime('%%Y-%%m', activity_date_start)"})
        .values("month")
        .annotate(count=Count("id"), total_co2e_kg=Sum("co2e_amount"))
        .order_by("month")
    )

    source_breakdown = list(
        records.values("source_type")
        .annotate(count=Count("id"), total_co2e_kg=Sum("co2e_amount"))
        .order_by("source_type")
    )

    recent_suspicious = list(
        records.exclude(flag="none")
        .order_by("-updated_at")[:5]
        .values("id", "activity_type", "flag", "co2e_amount", "updated_at")
    )

    return Response({
        "summary": summary,
        "scope_breakdown": scope_breakdown,
        "monthly_trend": list(monthly),
        "source_breakdown": source_breakdown,
        "recent_suspicious": recent_suspicious,
    })
