from django.db import models
from django.conf import settings
from trip.models import Location, Trip
import uuid

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('ATTRACTION', 'Tourist Attraction'),
        ('RESTAURANT', 'Restaurant'),
        ('MUSEUM', 'Museum'),
        ('OUTDOOR', 'Outdoor Activity'),
        ('SHOPPING', 'Shopping'),
        ('ENTERTAINMENT', 'Entertainment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    google_place_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    price_level = models.IntegerField(null=True)  
    website = models.URLField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'activities'
        ordering = ['-rating', 'name']
        indexes = [
            models.Index(fields=['activity_type']),
            models.Index(fields=['google_place_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()})"

class ActivityPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_reference = models.CharField(max_length=500)  
    photo_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
