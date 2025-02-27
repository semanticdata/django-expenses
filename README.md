# Recurring Expenses Tracker

A Django-based web application for tracking and managing recurring expenses. This tool helps users keep track of their regular financial commitments and monitor spending patterns over time.

## Features

- Track monthly, quarterly, and annual recurring expenses
- Categorize expenses for better organization
- View expense history and patterns
- User authentication and personal expense tracking
- Export and import data for backup and transfer
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

## PythonAnywhere

If you've already cloned the repository to PythonAnywhere and want to update it with the latest changes from the main branch, you can use the following bash commands:

```bash
# Fetch the latest changes from the remote repository
git fetch origin

# Reset your local main branch to match the remote main branch
git checkout main
git reset --hard origin/main

# If you have local changes you want to keep, use this approach instead:
# 1. Stash your changes
git stash
# 2. Pull the latest changes
git pull origin main
# 3. Reapply your changes
git stash pop
```

These commands will ensure your local repository is synchronized with the latest version from the remote repository.

## Usage

Run the development server:

```bash
python manage.py runserver
```

The application will be available at <http://127.0.0.1:8000/>

## Data Export and Import

The application provides functionality to export and import your expense data, allowing you to:

- Create backups of your expense data
- Transfer data between different installations
- Restore your data if needed

### Exporting Data

To export your data:

1. Log in to your account
2. Click on the "Data" dropdown in the navigation bar
3. Select "Export Data"
4. Your data will be downloaded as a JSON file containing:
   - All your expense categories
   - All your recurring expenses
   - All payment records for your expenses

### Importing Data

To import previously exported data:

1. Log in to your account
2. Click on the "Data" dropdown in the navigation bar
3. Select "Import Data"
4. Upload your JSON backup file
5. Click "Import Data" to process the file

**Note:** When importing data, existing expenses with the same name and amount will be skipped to avoid duplicates.

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
