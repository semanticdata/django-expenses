from django.contrib import admin
from .models import Category, RecurringExpense, ExpensePayment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'category', 'frequency', 'due_date', 'is_active')
    list_filter = ('frequency', 'category', 'is_active')
    search_fields = ('name', 'description')
    date_hierarchy = 'due_date'

@admin.register(ExpensePayment)
class ExpensePaymentAdmin(admin.ModelAdmin):
    list_display = ('recurring_expense', 'payment_date', 'amount_paid')
    list_filter = ('payment_date', 'recurring_expense__category')
    search_fields = ('recurring_expense__name', 'notes')
    date_hierarchy = 'payment_date'
