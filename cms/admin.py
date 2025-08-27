from django.contrib import admin
from .models import Entry, PublishedEntries


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "created_at",
        "updated_at",
        "published_at",
        "is_published",
    )
    list_filter = ("created_at", "updated_at", "published_at", "owner")
    search_fields = ("contents", "owner__username")
    readonly_fields = ("created_at", "updated_at", "published_at")

    def get_queryset(self, request):
        # Optimize queries by selecting related user data
        return super().get_queryset(request).select_related("owner")


@admin.register(PublishedEntries)
class PublishedEntriesAdmin(admin.ModelAdmin):
    list_display = ("owner_username", "published_at", "created_at")
    list_filter = ("published_at", "owner_username")
    search_fields = ("contents", "owner_username")
    readonly_fields = (
        "original_entry",
        "owner_username",
        "contents",
        "created_at",
        "updated_at",
        "published_at",
    )

    def has_add_permission(self, request):
        # Prevent manual creation of published entries
        return False
