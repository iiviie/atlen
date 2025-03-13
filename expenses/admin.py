from django.contrib import admin
from .models import Budget, BudgetCategory, Expense

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('trip', 'total_amount', 'currency', 'created_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('trip__title',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-created_at',)

    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()
    get_remaining_amount.short_description = 'Remaining Amount'

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'budget', 'allocated_amount', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('budget__trip__title',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('budget',)
    ordering = ('budget', 'category')

    def get_spent_amount(self, obj):
        return obj.get_spent_amount()
    get_spent_amount.short_description = 'Spent Amount'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'date', 'payment_method', 'created_by')
    list_filter = ('payment_method', 'date', 'created_at')
    search_fields = ('title', 'category__budget__trip__title', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('category', 'created_by')
    ordering = ('-date', '-created_at')
