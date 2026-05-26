from rest_framework.permissions import BasePermission
from .models import OrganizationMember


class OrganizationMembershipRequired(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_id = (
            request.query_params.get("organization")
            or request.data.get("org_id")
            or request.data.get("organization")
        )
        if not org_id:
            return True
        return OrganizationMember.objects.filter(
            organization_id=org_id, user=request.user
        ).exists()
