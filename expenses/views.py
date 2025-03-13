from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, ExtractMonth
from trip.permissions import IsTripParticipant
from trip.models import Trip
from .models import Budget, BudgetCategory, Expense
from .serializers import BudgetSerializer, BudgetCategorySerializer, ExpenseSerializer
from datetime import timedelta
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]
    
    def get_queryset(self):
        return Budget.objects.filter(
            trip_id=self.kwargs['trip_pk']
        ).prefetch_related('categories', 'categories__expenses')

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        serializer.save(trip=trip)

    @extend_schema(responses={200: BudgetSerializer})
    @action(detail=True, methods=['get'])
    def analytics(self, request, trip_pk=None, pk=None):
        budget = self.get_object()
        
        # Category breakdown
        category_stats = BudgetCategory.objects.filter(
            budget=budget
        ).annotate(
            spent=Sum('expenses__amount'),
            transaction_count=Count('expenses'),
            avg_transaction=Avg('expenses__amount')
        ).values(
            'category', 'allocated_amount', 'spent',
            'transaction_count', 'avg_transaction'
        )

        # Daily spending trend
        daily_spending = Expense.objects.filter(
            category__budget=budget
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')

        # Payment method distribution
        payment_methods = Expense.objects.filter(
            category__budget=budget
        ).values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        return Response({
            'category_breakdown': category_stats,
            'daily_spending': daily_spending,
            'payment_methods': payment_methods,
        })

    @extend_schema(responses={200: BudgetSerializer})
    @action(detail=True, methods=['get'])
    def report(self, request, trip_pk=None, pk=None):
        budget = self.get_object()
        
        # Overall budget status
        total_spent = sum(cat.get_spent_amount() for cat in budget.categories.all())
        budget_status = {
            'total_budget': float(budget.total_amount),
            'total_spent': float(total_spent),
            'remaining': float(budget.total_amount - total_spent),
            'percentage_used': (total_spent / budget.total_amount) * 100
        }

        # Category-wise analysis
        categories = []
        for category in budget.categories.all():
            spent = category.get_spent_amount()
            categories.append({
                'name': category.get_category_display(),
                'allocated': float(category.allocated_amount),
                'spent': float(spent),
                'remaining': float(category.allocated_amount - spent),
                'percentage_used': (spent / category.allocated_amount) * 100
            })

        # Recent transactions
        recent_transactions = Expense.objects.filter(
            category__budget=budget
        ).order_by('-created_at')[:10].values(
            'title', 'amount', 'date', 'payment_method',
            'category__category'
        )

        return Response({
            'budget_status': budget_status,
            'categories': categories,
            'recent_transactions': recent_transactions,
        })
