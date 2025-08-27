from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Entry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    contents = models.TextField()

    def __str__(self):
        return f"Entry by {self.owner.username} - {self.created_at.strftime('%Y-%m-%d')}"

    def is_published(self):
        return self.published_at is not None

    def publish(self):
        """Publish this entry and create/update a PublishedEntries record"""
        self.published_at = timezone.now()
        self.save()

        # Create or update the published version
        PublishedEntries.objects.update_or_create(
            original_entry=self,
            defaults={
                "owner_username": self.owner.username,
                "contents": self.contents,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "published_at": self.published_at,
            },
        )

    class Meta:
        verbose_name_plural = "entries"


class PublishedEntries(models.Model):
    original_entry = models.OneToOneField(
        Entry, on_delete=models.CASCADE, related_name="published_version"
    )
    owner_username = models.CharField(max_length=150)
    contents = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    published_at = models.DateTimeField()

    def __str__(self):
        return f"Published: {self.owner_username} - {self.published_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Published Entry"
        verbose_name_plural = "Published Entries"
        ordering = ["-published_at"]
