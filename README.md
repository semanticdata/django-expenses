# Recurring Expenses Tracker

A Django-based web application for tracking and managing recurring expenses. This tool helps users keep track of their regular financial commitments and monitor spending patterns over time.

## Features

- Track monthly, quarterly, and annual recurring expenses
- Categorize expenses for better organization
- View expense history and patterns
- User authentication and personal expense tracking
- Simple and intuitive interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/semanticdata/django-expenses.git
cd django-expenses
```

2. Create and activate a virtual environment (recommended):

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Create a superuser (admin):

```bash
python manage.py createsuperuser
```

## Usage

Run the development server:

```bash
python manage.py runserver
```

The application will be available at <http://127.0.0.1:8000/>

## Development

### Project Structure

- `expenses/` - Main application directory containing models, views, and forms
- `recurringtracker/` - Project configuration directory
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)

### Making Changes

1. Create a new branch for your feature:

```bash
git checkout -b feature-name
```

2. Make your changes and test thoroughly

3. Run tests:

```bash
python manage.py test
```

4. Create new migrations if you modified models:

```bash
python manage.py makemigrations
```

### Adding New Features

1. Create new models in `expenses/models.py`
2. Create corresponding views in `expenses/views.py`
3. Add URL patterns in `expenses/urls.py`
4. Create templates in `templates/` directory
5. Update tests in `expenses/tests.py`

## Testing

The application includes a comprehensive test suite that covers models, views, utility functions, and admin functionality. The tests ensure that the application works correctly and help catch regressions when making changes.

### Running Tests

To run the entire test suite:

```bash
python manage.py test
```

To run tests for a specific app:

```bash
python manage.py test expenses
```

### Test Coverage

The test suite includes:

1. **Model Tests**:
   - Tests for `Category`, `RecurringExpense`, and `ExpensePayment` models
   - Validation of model fields and constraints
   - String representation methods

2. **View Tests**:
   - Authentication and authorization
   - Context data and calculations
   - User-specific data isolation

3. **Utility Function Tests**:
   - Tests for the `calculate_next_recurrence` function with different frequencies
   - Handling of edge cases

4. **Admin Tests**:
   - Admin access and permissions
   - CRUD operations through the admin interface

5. **Multi-User Tests**:
   - Data isolation between different users
   - User-specific views and calculations

### Writing New Tests

When adding new features, make sure to add corresponding tests in `expenses/tests.py`. Follow these guidelines:

1. Create a new test class for each major component
2. Use descriptive test method names that explain what is being tested
3. Set up test data in the `setUp` method
4. Test both normal operation and edge cases
5. Use Django's test client for testing views and forms

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

The code in this repository is available under the [MIT License](LICENSE).
