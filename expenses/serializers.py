from rest_framework import serializers
from .models import Budget, BudgetCategory, Expense
from trip.serializers import TripListSerializer, UserBasicSerializer

class ExpenseSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    category_name = serializers.CharField(source='category.get_category_display', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'amount', 'date', 'payment_method',
            'receipt_image', 'notes', 'created_by', 'category',
            'category_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

class BudgetCategorySerializer(serializers.ModelSerializer):
    spent_amount = serializers.DecimalField(
        source='get_spent_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    expenses = ExpenseSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BudgetCategory
        fields = [
            'id', 'category', 'category_display', 'allocated_amount',
            'spent_amount', 'expenses', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class BudgetSerializer(serializers.ModelSerializer):
    trip = TripListSerializer(read_only=True)
    categories = BudgetCategorySerializer(many=True, read_only=True)
    remaining_amount = serializers.DecimalField(
        source='get_remaining_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Budget
        fields = [
            'id', 'trip', 'total_amount', 'currency',
            'remaining_amount', 'categories', 'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 