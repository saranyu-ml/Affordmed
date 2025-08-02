# shortener/models.py
from django.db import models
from django.utils import timezone
import shortuuid

class ShortURL(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortuuid.ShortUUID().random(length=6)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

class URLStats(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='stats')
    clicked_at = models.DateTimeField(auto_now_add=True)
    referrer = models.CharField(max_length=2048, blank=True, null=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Click on {self.short_url.short_code} at {self.clicked_at}"