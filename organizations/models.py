from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("viewer", "Viewer"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="org_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["organization", "user"]

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name} ({self.role})"
