from .models import OrganizationMember


def get_user_org_ids(user):
    if user.is_anonymous:
        return []
    return list(
        OrganizationMember.objects.filter(user=user).values_list(
            "organization_id", flat=True
        )
    )


class OrgFilterMixin:
    def get_org_ids(self):
        return get_user_org_ids(self.request.user)

    def filter_by_org(self, queryset, org_param="organization"):
        org_ids = self.get_org_ids()
        if not org_ids:
            return queryset.none()
        return queryset.filter(**{f"{org_param}_id__in": org_ids})
