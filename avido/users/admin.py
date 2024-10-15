from django.contrib import admin

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Custom user model in admin."""

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "phone_number",
        "call_availability",
        "status",
    )
    list_filter = (
        "email",
        "first_name",
        "last_name",
        "role",
    )
    search_fields = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
    )
