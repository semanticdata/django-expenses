from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
import json
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Category, RecurringExpense, ExpensePayment
from .views import calculate_next_recurrence

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
    
    def test_category_creation(self):
        """Test that a category can be created with the expected attributes"""
        self.assertEqual(self.category.name, "Utilities")
        self.assertEqual(self.category.description, "Monthly utility bills")
    
    def test_category_string_representation(self):
        """Test the string representation of a category"""
        self.assertEqual(str(self.category), "Utilities")

class RecurringExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
        self.expense = RecurringExpense.objects.create(
            name="Electricity Bill",
            amount=Decimal('100.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            description="Monthly electricity bill",
            user=self.user,
            is_active=True
        )
    
    def test_expense_creation(self):
        """Test that a recurring expense can be created with the expected attributes"""
        self.assertEqual(self.expense.name, "Electricity Bill")
        self.assertEqual(self.expense.amount, Decimal('100.00'))
        self.assertEqual(self.expense.category, self.category)
        self.assertEqual(self.expense.frequency, "MONTHLY")
        self.assertEqual(self.expense.description, "Monthly electricity bill")
        self.assertEqual(self.expense.user, self.user)
        self.assertTrue(self.expense.is_active)
    
    def test_expense_string_representation(self):
        """Test the string representation of a recurring expense"""
        expected_str = f"Electricity Bill - 100.00 (Monthly)"
        self.assertEqual(str(self.expense), expected_str)

class ExpensePaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
        self.expense = RecurringExpense.objects.create(
            name="Electricity Bill",
            amount=Decimal('100.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            description="Monthly electricity bill",
            user=self.user,
            is_active=True
        )
        self.payment = ExpensePayment.objects.create(
            recurring_expense=self.expense,
            payment_date=timezone.now().date(),
            amount_paid=Decimal('100.00'),
            notes="Paid on time"
        )
    
    def test_payment_creation(self):
        """Test that an expense payment can be created with the expected attributes"""
        self.assertEqual(self.payment.recurring_expense, self.expense)
        self.assertEqual(self.payment.amount_paid, Decimal('100.00'))
        self.assertEqual(self.payment.notes, "Paid on time")
    
    def test_payment_string_representation(self):
        """Test the string representation of an expense payment"""
        expected_str = f"Electricity Bill - {timezone.now().date()} - 100.00"
        self.assertEqual(str(self.payment), expected_str)

class CalculateNextRecurrenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.today = timezone.now().date()
        
        # Create expenses with different frequencies
        self.daily_expense = RecurringExpense.objects.create(
            name="Daily Expense",
            amount=Decimal('10.00'),
            frequency="DAILY",
            due_date=self.today - timedelta(days=1),  # Yesterday
            user=self.user
        )
        
        self.weekly_expense = RecurringExpense.objects.create(
            name="Weekly Expense",
            amount=Decimal('50.00'),
            frequency="WEEKLY",
            due_date=self.today - timedelta(days=7),  # A week ago
            user=self.user
        )
        
        self.monthly_expense = RecurringExpense.objects.create(
            name="Monthly Expense",
            amount=Decimal('100.00'),
            frequency="MONTHLY",
            due_date=self.today - timedelta(days=30),  # A month ago
            user=self.user
        )
        
        self.quarterly_expense = RecurringExpense.objects.create(
            name="Quarterly Expense",
            amount=Decimal('300.00'),
            frequency="QUARTERLY",
            due_date=self.today - timedelta(days=90),  # 3 months ago
            user=self.user
        )
        
        self.yearly_expense = RecurringExpense.objects.create(
            name="Yearly Expense",
            amount=Decimal('1000.00'),
            frequency="YEARLY",
            due_date=self.today - timedelta(days=365),  # A year ago
            user=self.user
        )
        
        self.future_expense = RecurringExpense.objects.create(
            name="Future Expense",
            amount=Decimal('200.00'),
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=15),  # 15 days in the future
            user=self.user
        )
    
    def test_calculate_next_recurrence_daily(self):
        """Test calculating next recurrence for daily frequency"""
        next_date = calculate_next_recurrence(self.daily_expense)
        expected_date = self.daily_expense.due_date + timedelta(days=1)
        self.assertEqual(next_date, expected_date)
    
    def test_calculate_next_recurrence_weekly(self):
        """Test calculating next recurrence for weekly frequency"""
        next_date = calculate_next_recurrence(self.weekly_expense)
        expected_date = self.weekly_expense.due_date + timedelta(weeks=1)
        self.assertEqual(next_date, expected_date)
    
    def test_calculate_next_recurrence_monthly(self):
        """Test calculating next recurrence for monthly frequency"""
        next_date = calculate_next_recurrence(self.monthly_expense)
        expected_date = self.monthly_expense.due_date + relativedelta(months=1)
        self.assertEqual(next_date, expected_date)
    
    def test_calculate_next_recurrence_quarterly(self):
        """Test calculating next recurrence for quarterly frequency"""
        next_date = calculate_next_recurrence(self.quarterly_expense)
        expected_date = self.quarterly_expense.due_date + relativedelta(months=3)
        self.assertEqual(next_date, expected_date)
    
    def test_calculate_next_recurrence_yearly(self):
        """Test calculating next recurrence for yearly frequency"""
        next_date = calculate_next_recurrence(self.yearly_expense)
        expected_date = self.yearly_expense.due_date + relativedelta(years=1)
        self.assertEqual(next_date, expected_date)
    
    def test_calculate_next_recurrence_future_date(self):
        """Test that future due dates are returned as is"""
        next_date = calculate_next_recurrence(self.future_expense)
        self.assertEqual(next_date, self.future_expense.due_date)

class HomeViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Create categories
        self.utilities = Category.objects.create(name="Utilities")
        self.rent = Category.objects.create(name="Rent")
        self.uncategorized = None  # For testing uncategorized expenses
        
        # Create expenses
        self.today = timezone.now().date()
        
        # Active expenses
        self.electricity = RecurringExpense.objects.create(
            name="Electricity",
            amount=Decimal('75.00'),
            category=self.utilities,
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=5),
            user=self.user,
            is_active=True
        )
        
        self.internet = RecurringExpense.objects.create(
            name="Internet",
            amount=Decimal('50.00'),
            category=self.utilities,
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=10),
            user=self.user,
            is_active=True
        )
        
        self.rent_expense = RecurringExpense.objects.create(
            name="Apartment Rent",
            amount=Decimal('1000.00'),
            category=self.rent,
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=1),
            user=self.user,
            is_active=True
        )
        
        self.misc_expense = RecurringExpense.objects.create(
            name="Miscellaneous",
            amount=Decimal('25.00'),
            category=self.uncategorized,  # No category
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=15),
            user=self.user,
            is_active=True
        )
        
        # Inactive expense
        self.inactive_expense = RecurringExpense.objects.create(
            name="Old Subscription",
            amount=Decimal('15.00'),
            category=self.utilities,
            frequency="MONTHLY",
            due_date=self.today + timedelta(days=20),
            user=self.user,
            is_active=False
        )
        
        # Create a payment for one of the expenses
        self.payment = ExpensePayment.objects.create(
            recurring_expense=self.electricity,
            payment_date=self.today,
            amount_paid=Decimal('75.00'),
            notes="Paid current bill"
        )
    
    def test_home_view_requires_login(self):
        """Test that the home view requires login"""
        # Logout first
        self.client.logout()
        
        # Try to access the home page
        response = self.client.get(reverse('expenses:home'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_home_view_with_authenticated_user(self):
        """Test that authenticated users can access the home view"""
        response = self.client.get(reverse('expenses:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/home.html')
    
    def test_home_view_context(self):
        """Test that the home view provides the expected context"""
        response = self.client.get(reverse('expenses:home'))
        
        # Check that all active expenses are in the context
        self.assertIn('expenses', response.context)
        expenses = response.context['expenses']
        self.assertEqual(len(expenses), 4)  # All active expenses
        
        # Check that inactive expenses are not included
        self.assertNotIn(self.inactive_expense, expenses)
        
        # Check category totals
        self.assertIn('total_by_category', response.context)
        category_totals = response.context['total_by_category']
        
        # Convert to dict for easier testing
        category_totals_dict = dict(category_totals)
        
        # Check utility total (75 + 50 = 125)
        self.assertEqual(category_totals_dict.get('Utilities'), Decimal('125.00'))
        
        # Check rent total (1000)
        self.assertEqual(category_totals_dict.get('Rent'), Decimal('1000.00'))
        
        # Check uncategorized total (25)
        self.assertEqual(category_totals_dict.get('Uncategorized'), Decimal('25.00'))
        
        # Check upcoming payments
        self.assertIn('upcoming_payments', response.context)
        upcoming = response.context['upcoming_payments']
        
        # Should have at most 5 items
        self.assertLessEqual(len(upcoming), 5)
        
        # Check recent payments
        self.assertIn('recent_payments', response.context)
        recent = response.context['recent_payments']
        
        # Should have at most 5 items
        self.assertLessEqual(len(recent), 5)
        
        # Should include our payment
        self.assertIn(self.payment, recent)

class RecurringExpenseValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
    
    def test_negative_amount_validation(self):
        """Test that a negative amount is not allowed"""
        with self.assertRaises(ValidationError):
            expense = RecurringExpense(
                name="Invalid Expense",
                amount=Decimal('-10.00'),  # Negative amount
                category=self.category,
                frequency="MONTHLY",
                due_date=timezone.now().date(),
                user=self.user
            )
            expense.full_clean()  # This should raise ValidationError
    
    def test_zero_amount_validation(self):
        """Test that a zero amount is not allowed"""
        with self.assertRaises(ValidationError):
            expense = RecurringExpense(
                name="Invalid Expense",
                amount=Decimal('0.00'),  # Zero amount
                category=self.category,
                frequency="MONTHLY",
                due_date=timezone.now().date(),
                user=self.user
            )
            expense.full_clean()  # This should raise ValidationError
    
    def test_invalid_frequency_validation(self):
        """Test that an invalid frequency is not allowed"""
        with self.assertRaises(ValidationError):
            expense = RecurringExpense(
                name="Invalid Expense",
                amount=Decimal('100.00'),
                category=self.category,
                frequency="INVALID",  # Invalid frequency
                due_date=timezone.now().date(),
                user=self.user
            )
            expense.full_clean()  # This should raise ValidationError

class ExpensePaymentValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
        self.expense = RecurringExpense.objects.create(
            name="Electricity Bill",
            amount=Decimal('100.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            user=self.user
        )
    
    def test_negative_payment_amount_validation(self):
        """Test that a negative payment amount is not allowed"""
        with self.assertRaises(ValidationError):
            payment = ExpensePayment(
                recurring_expense=self.expense,
                payment_date=timezone.now().date(),
                amount_paid=Decimal('-50.00')  # Negative amount
            )
            payment.full_clean()  # This should raise ValidationError
    
    def test_zero_payment_amount_validation(self):
        """Test that a zero payment amount is not allowed"""
        with self.assertRaises(ValidationError):
            payment = ExpensePayment(
                recurring_expense=self.expense,
                payment_date=timezone.now().date(),
                amount_paid=Decimal('0.00')  # Zero amount
            )
            payment.full_clean()  # This should raise ValidationError
    
    def test_future_payment_date(self):
        """Test that a payment can be made with a future date"""
        future_date = timezone.now().date() + timedelta(days=5)
        payment = ExpensePayment.objects.create(
            recurring_expense=self.expense,
            payment_date=future_date,
            amount_paid=Decimal('100.00')
        )
        self.assertEqual(payment.payment_date, future_date)

class MultiUserTest(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )
        
        # Create a category
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
        
        # Create expenses for both users
        self.expense1 = RecurringExpense.objects.create(
            name="User1 Expense",
            amount=Decimal('100.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            user=self.user1
        )
        
        self.expense2 = RecurringExpense.objects.create(
            name="User2 Expense",
            amount=Decimal('200.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            user=self.user2
        )
        
        # Create clients for both users
        self.client1 = Client()
        self.client1.login(username='user1', password='password1')
        
        self.client2 = Client()
        self.client2.login(username='user2', password='password2')
    
    def test_user_isolation(self):
        """Test that users can only see their own expenses"""
        # User 1 should only see their expense
        response1 = self.client1.get(reverse('expenses:home'))
        expenses1 = response1.context['expenses']
        self.assertEqual(len(expenses1), 1)
        self.assertIn(self.expense1, expenses1)
        self.assertNotIn(self.expense2, expenses1)
        
        # User 2 should only see their expense
        response2 = self.client2.get(reverse('expenses:home'))
        expenses2 = response2.context['expenses']
        self.assertEqual(len(expenses2), 1)
        self.assertIn(self.expense2, expenses2)
        self.assertNotIn(self.expense1, expenses2)

class AdminSiteTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpassword'
        )
        
        # Create test data
        self.category = Category.objects.create(
            name="Utilities",
            description="Monthly utility bills"
        )
        
        self.expense = RecurringExpense.objects.create(
            name="Electricity Bill",
            amount=Decimal('100.00'),
            category=self.category,
            frequency="MONTHLY",
            due_date=timezone.now().date(),
            user=self.regular_user,
            is_active=True
        )
        
        self.payment = ExpensePayment.objects.create(
            recurring_expense=self.expense,
            payment_date=timezone.now().date(),
            amount_paid=Decimal('100.00'),
            notes="Paid on time"
        )
        
        # Create admin client
        self.admin_client = Client()
        self.admin_client.login(username='admin', password='adminpassword')
        
        # Create regular client
        self.regular_client = Client()
        self.regular_client.login(username='regular', password='regularpassword')
    
    def test_category_admin_access(self):
        """Test that admin can access category admin page"""
        url = reverse('admin:expenses_category_changelist')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_recurring_expense_admin_access(self):
        """Test that admin can access recurring expense admin page"""
        url = reverse('admin:expenses_recurringexpense_changelist')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_expense_payment_admin_access(self):
        """Test that admin can access expense payment admin page"""
        url = reverse('admin:expenses_expensepayment_changelist')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_admin_access_denied(self):
        """Test that regular users cannot access admin pages"""
        # Try to access category admin
        url = reverse('admin:expenses_category_changelist')
        response = self.regular_client.get(url)
        self.assertNotEqual(response.status_code, 200)
        
        # Try to access recurring expense admin
        url = reverse('admin:expenses_recurringexpense_changelist')
        response = self.regular_client.get(url)
        self.assertNotEqual(response.status_code, 200)
        
        # Try to access expense payment admin
        url = reverse('admin:expenses_expensepayment_changelist')
        response = self.regular_client.get(url)
        self.assertNotEqual(response.status_code, 200)
    
    def test_admin_can_edit_category(self):
        """Test that admin can edit a category"""
        url = reverse('admin:expenses_category_change', args=[self.category.id])
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST to update category
        post_data = {
            'name': 'Updated Utilities',
            'description': 'Updated description'
        }
        response = self.admin_client.post(url, post_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        
        # Verify the category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Utilities')
        self.assertEqual(self.category.description, 'Updated description')
    
    def test_admin_can_add_category(self):
        """Test that admin can add a new category"""
        url = reverse('admin:expenses_category_add')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST to add category
        post_data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        response = self.admin_client.post(url, post_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        
        # Verify the category was created
        self.assertTrue(Category.objects.filter(name='New Category').exists())

class DataExportImportTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        
        # Create a test expense
        self.expense = RecurringExpense.objects.create(
            name='Test Expense',
            amount=Decimal('100.00'),
            category=self.category,
            frequency='MONTHLY',
            due_date=date.today(),
            description='Test Description',
            user=self.user,
            is_active=True
        )
        
        # Create a test payment
        self.payment = ExpensePayment.objects.create(
            recurring_expense=self.expense,
            payment_date=date.today() - timedelta(days=5),
            amount_paid=Decimal('100.00'),
            notes='Test Payment'
        )
        
        # Set up the client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_export_data(self):
        """Test that data can be exported correctly"""
        response = self.client.get(reverse('expenses:export_data'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the content type is JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON data
        data = json.loads(response.content.decode('utf-8'))
        
        # Check that the data structure is correct
        self.assertIn('export_date', data)
        self.assertIn('username', data)
        self.assertIn('categories', data)
        self.assertIn('expenses', data)
        
        # Check that the category data is correct
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], 'Test Category')
        
        # Check that the expense data is correct
        self.assertEqual(len(data['expenses']), 1)
        self.assertEqual(data['expenses'][0]['name'], 'Test Expense')
        self.assertEqual(data['expenses'][0]['amount'], '100.00')
        
        # Check that the payment data is correct
        self.assertEqual(len(data['expenses'][0]['payments']), 1)
        self.assertEqual(data['expenses'][0]['payments'][0]['amount_paid'], '100.00')
    
    def test_import_data(self):
        """Test that data can be imported correctly"""
        # Create a sample export data
        export_data = {
            'export_date': date.today().isoformat(),
            'username': 'testuser',
            'categories': [
                {
                    'id': 999,  # Different ID to test mapping
                    'name': 'New Category',
                    'description': 'New Description'
                }
            ],
            'expenses': [
                {
                    'name': 'New Expense',
                    'amount': '200.00',
                    'category_id': 999,
                    'category_name': 'New Category',
                    'frequency': 'WEEKLY',
                    'due_date': date.today().isoformat(),
                    'description': 'New Description',
                    'is_active': True,
                    'payments': [
                        {
                            'payment_date': date.today().isoformat(),
                            'amount_paid': '200.00',
                            'notes': 'New Payment'
                        }
                    ]
                }
            ]
        }
        
        # Create a temporary file with the export data
        json_data = json.dumps(export_data)
        temp_file = SimpleUploadedFile('export.json', json_data.encode('utf-8'), content_type='application/json')
        
        # Post the file to the import view
        response = self.client.post(reverse('expenses:import_data'), {'import_file': temp_file})
        
        # Check that the response redirects to the home page
        self.assertRedirects(response, reverse('expenses:home'))
        
        # Check that the new category was created
        self.assertTrue(Category.objects.filter(name='New Category').exists())
        
        # Check that the new expense was created
        self.assertTrue(RecurringExpense.objects.filter(name='New Expense').exists())
        
        # Check that the new payment was created
        new_expense = RecurringExpense.objects.get(name='New Expense')
        self.assertTrue(ExpensePayment.objects.filter(recurring_expense=new_expense).exists())
    
    def test_import_invalid_data(self):
        """Test handling of invalid import data"""
        # Create invalid JSON data
        invalid_data = "This is not valid JSON"
        temp_file = SimpleUploadedFile('invalid.json', invalid_data.encode('utf-8'), content_type='application/json')
        
        # Post the file to the import view
        response = self.client.post(reverse('expenses:import_data'), {'import_file': temp_file})
        
        # Check that the response redirects to the home page
        self.assertRedirects(response, reverse('expenses:home'))
        
        # Check that no new data was created
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(RecurringExpense.objects.count(), 1)
        self.assertEqual(ExpensePayment.objects.count(), 1)
