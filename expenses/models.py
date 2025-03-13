from django.db import models
from django.conf import settings
from trip.models import Trip
from django.db.models import Sum
import uuid

class Budget(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('AUD', 'Australian Dollar'),
        ('CAD', 'Canadian Dollar'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name='budget'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_remaining_amount(self):
        spent = self.categories.aggregate(
            total=Sum('expenses__amount')
        )['total'] or 0
        return self.total_amount - spent

    def __str__(self):
        return f"Budget for {self.trip.title}"

class BudgetCategory(models.Model):
    CATEGORY_CHOICES = [
        ('ACCOMMODATION', 'Accommodation'),
        ('TRANSPORTATION', 'Transportation'),
        ('FOOD', 'Food & Dining'),
        ('ACTIVITIES', 'Activities & Entertainment'),
        ('SHOPPING', 'Shopping'),
        ('MISC', 'Miscellaneous'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['budget', 'category']
        verbose_name_plural = 'budget categories'

    def get_spent_amount(self):
        return self.expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0

    def __str__(self):
        return f"{self.get_category_display()} - {self.budget.trip.title}"

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CREDIT', 'Credit Card'),
        ('DEBIT', 'Debit Card'),
        ('MOBILE', 'Mobile Payment'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        BudgetCategory,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    receipt_image = models.ImageField(
        upload_to='expenses/receipts/',
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['payment_method']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} {self.category.budget.currency}"
