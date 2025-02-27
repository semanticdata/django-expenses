from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from .models import RecurringExpense, Category, ExpensePayment
import json
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
import datetime
import io
from django.core.exceptions import ValidationError
from django.db import transaction

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

@login_required
def export_data(request):
    """Export user data as JSON for backup purposes"""
    # Get user's categories
    categories = []
    for category in Category.objects.all():
        # Check if the category is used by any of the user's expenses
        if RecurringExpense.objects.filter(user=request.user, category=category).exists():
            categories.append({
                'id': category.id,
                'name': category.name,
                'description': category.description
            })
    
    # Get user's recurring expenses
    expenses = []
    for expense in RecurringExpense.objects.filter(user=request.user):
        expense_data = {
            'name': expense.name,
            'amount': str(expense.amount),  # Convert Decimal to string for JSON serialization
            'category_id': expense.category.id if expense.category else None,
            'category_name': expense.category.name if expense.category else None,
            'frequency': expense.frequency,
            'due_date': expense.due_date.isoformat(),
            'description': expense.description,
            'is_active': expense.is_active,
            'payments': []
        }
        
        # Get payments for this expense
        for payment in ExpensePayment.objects.filter(recurring_expense=expense):
            expense_data['payments'].append({
                'payment_date': payment.payment_date.isoformat(),
                'amount_paid': str(payment.amount_paid),
                'notes': payment.notes
            })
        
        expenses.append(expense_data)
    
    # Create the complete data structure
    data = {
        'export_date': timezone.now().isoformat(),
        'username': request.user.username,
        'categories': categories,
        'expenses': expenses
    }
    
    # Create the response with the JSON data
    response = HttpResponse(json.dumps(data, indent=4), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="expenses_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    return response

@login_required
def import_data(request):
    """Import user data from a JSON file"""
    if request.method == 'POST' and request.FILES.get('import_file'):
        try:
            import_file = request.FILES['import_file']
            
            # Read and parse the JSON data
            file_content = import_file.read().decode('utf-8')
            data = json.loads(file_content)
            
            # Validate the data structure
            if not all(key in data for key in ['categories', 'expenses']):
                messages.error(request, "Invalid backup file format. Missing required data.")
                return redirect('expenses:home')
            
            # Use a transaction to ensure all-or-nothing import
            with transaction.atomic():
                # Process categories
                category_mapping = {}  # Maps original category IDs to new ones
                
                for category_data in data['categories']:
                    # Check if category already exists by name
                    category, created = Category.objects.get_or_create(
                        name=category_data['name'],
                        defaults={'description': category_data.get('description', '')}
                    )
                    
                    # Store the mapping from original ID to the actual category object
                    category_mapping[category_data['id']] = category
                
                # Process expenses
                for expense_data in data['expenses']:
                    # Get or create the category if it exists in the mapping
                    category = None
                    if expense_data.get('category_id') and expense_data['category_id'] in category_mapping:
                        category = category_mapping[expense_data['category_id']]
                    elif expense_data.get('category_name'):
                        # Try to find by name if ID mapping failed
                        try:
                            category = Category.objects.get(name=expense_data['category_name'])
                        except Category.DoesNotExist:
                            # Create a new category if it doesn't exist
                            category = Category.objects.create(
                                name=expense_data['category_name'],
                                description=''
                            )
                    
                    # Check if a similar expense already exists
                    existing_expense = RecurringExpense.objects.filter(
                        user=request.user,
                        name=expense_data['name'],
                        amount=expense_data['amount']
                    ).first()
                    
                    if existing_expense:
                        # Skip this expense as it already exists
                        continue
                    
                    # Create the expense
                    expense = RecurringExpense.objects.create(
                        user=request.user,
                        name=expense_data['name'],
                        amount=expense_data['amount'],
                        category=category,
                        frequency=expense_data['frequency'],
                        due_date=datetime.date.fromisoformat(expense_data['due_date']),
                        description=expense_data.get('description', ''),
                        is_active=expense_data.get('is_active', True)
                    )
                    
                    # Process payments for this expense
                    for payment_data in expense_data.get('payments', []):
                        ExpensePayment.objects.create(
                            recurring_expense=expense,
                            payment_date=datetime.date.fromisoformat(payment_data['payment_date']),
                            amount_paid=payment_data['amount_paid'],
                            notes=payment_data.get('notes', '')
                        )
            
            messages.success(request, "Data imported successfully!")
        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON file. Please upload a valid backup file.")
        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error importing data: {str(e)}")
        
        return redirect('expenses:home')
    
    # If GET request or no file uploaded, show the import form
    return render(request, 'expenses/import.html')
