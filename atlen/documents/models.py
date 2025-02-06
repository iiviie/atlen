from django.db import models
from django.conf import settings
from trip.models import Trip
import uuid
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('PASSPORT', 'Passport'),
        ('VISA', 'Visa'),
        ('ID_CARD', 'ID Card'),
        ('INSURANCE', 'Insurance'),
        ('VACCINATION', 'Vaccination Certificate'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(
        upload_to='documents/user/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

class TripDocument(models.Model):
    DOCUMENT_TYPES = [
        ('BOOKING', 'Booking Confirmation'),
        ('TICKET', 'Ticket'),
        ('ITINERARY', 'Itinerary'),
        ('RESERVATION', 'Reservation'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(
        upload_to='documents/trips/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.trip.title}"
