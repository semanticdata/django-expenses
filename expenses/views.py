from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import RecurringExpense, Category, ExpensePayment

# Create your views here.

@login_required
def home(request):
    # Get all active expenses for the current user
    expenses = RecurringExpense.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('due_date')
    
    # Calculate total by category
    total_by_category = []
    categories = Category.objects.all()
    for category in categories:
        total = RecurringExpense.objects.filter(
            user=request.user,
            category=category,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        if total > 0:
            total_by_category.append((category.name, total))
    
    # Add uncategorized total
    uncategorized_total = RecurringExpense.objects.filter(
        user=request.user,
        category__isnull=True,
        is_active=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    if uncategorized_total > 0:
        total_by_category.append(('Uncategorized', uncategorized_total))
    
    # Get upcoming payments (due in the next 30 days)
    thirty_days = timezone.now().date() + timedelta(days=30)
    upcoming_payments = RecurringExpense.objects.filter(
        user=request.user,
        is_active=True,
        due_date__lte=thirty_days
    ).order_by('due_date')[:5]
    
    # Get recent expense payments (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_payments = ExpensePayment.objects.filter(
        recurring_expense__user=request.user,
        payment_date__gte=thirty_days_ago
    ).order_by('-payment_date')[:5]
    
    context = {
        'expenses': expenses,
        'total_by_category': total_by_category,
        'upcoming_payments': upcoming_payments,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'expenses/home.html', context)
