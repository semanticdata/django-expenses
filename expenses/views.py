from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
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
    
    # Get recent expense payments (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_payments = ExpensePayment.objects.filter(
        recurring_expense__user=request.user,
        payment_date__gte=thirty_days_ago
    ).order_by('-payment_date')
    
    # Track which expenses have been paid
    satisfied_expenses = {}
    for payment in recent_payments:
        expense_id = payment.recurring_expense.id
        due_date = payment.recurring_expense.due_date
        
        # If payment was made after due date and amount is sufficient
        if payment.payment_date >= due_date and payment.amount_paid >= payment.recurring_expense.amount:
            satisfied_expenses[expense_id] = {
                'payment': payment,
                'next_recurrence': calculate_next_recurrence(payment.recurring_expense)
            }
    
    # Get upcoming payments (due in the next 30 days)
    thirty_days = timezone.now().date() + timedelta(days=30)
    upcoming_payments = RecurringExpense.objects.filter(
        user=request.user,
        is_active=True,
        due_date__lte=thirty_days
    ).order_by('due_date')
    
    # Prepare upcoming payments with satisfaction status
    upcoming_with_status = []
    for expense in upcoming_payments:
        is_satisfied = expense.id in satisfied_expenses
        next_recurrence = None
        
        if is_satisfied:
            next_recurrence = satisfied_expenses[expense.id]['next_recurrence']
        
        upcoming_with_status.append({
            'expense': expense,
            'is_satisfied': is_satisfied,
            'next_recurrence': next_recurrence
        })
    
    context = {
        'expenses': expenses,
        'total_by_category': total_by_category,
        'upcoming_payments': upcoming_with_status[:5],  # Limit to 5 items
        'recent_payments': recent_payments[:5],  # Limit to 5 items
    }
    
    return render(request, 'expenses/home.html', context)

def calculate_next_recurrence(expense):
    """Calculate the next recurrence date based on frequency"""
    current_due = expense.due_date
    today = timezone.now().date()
    
    # If the current due date is in the future, return it
    if current_due > today:
        return current_due
    
    # Calculate next recurrence based on frequency
    if expense.frequency == 'DAILY':
        return current_due + timedelta(days=1)
    elif expense.frequency == 'WEEKLY':
        return current_due + timedelta(weeks=1)
    elif expense.frequency == 'MONTHLY':
        return current_due + relativedelta(months=1)
    elif expense.frequency == 'QUARTERLY':
        return current_due + relativedelta(months=3)
    elif expense.frequency == 'YEARLY':
        return current_due + relativedelta(years=1)
    
    # Default fallback
    return current_due
