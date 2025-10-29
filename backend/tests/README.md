# ÉpítAI Construction Management System - Test Suite

This directory contains comprehensive tests for the ÉpítAI Construction Management System backend API.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── README.md                   # This file
├── api/                        # API tests
│   ├── __init__.py
│   └── v1/                     # API v1 tests
│       ├── __init__.py
│       └── endpoints/          # Endpoint tests
│           ├── __init__.py
│           └── test_users.py   # User API tests
├── utils/                      # Test utilities
│   ├── __init__.py
│   └── test_helpers.py         # Helper functions and test data
└── fixtures/                   # Test fixtures (if needed)
```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner script:

```bash
# Run all tests
python run_tests.py

# Run tests with specific pattern
python run_tests.py --pattern users

# Run specific test module
python run_tests.py --module api.v1.endpoints.test_users

# Run specific test class
python run_tests.py --module api.v1.endpoints.test_users --class TestUserAPI

# Run specific test method
python run_tests.py --module api.v1.endpoints.test_users --class TestUserAPI --method test_create_user_success

# Run with failfast (stop on first failure)
python run_tests.py --failfast

# Run with different verbosity levels
python run_tests.py --verbosity 0  # Quiet
python run_tests.py --verbosity 1  # Normal
python run_tests.py --verbosity 2  # Verbose (default)
```

### Using unittest directly

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.api.v1.endpoints.test_users

# Run specific test class
python -m unittest tests.api.v1.endpoints.test_users.TestUserAPI

# Run specific test method
python -m unittest tests.api.v1.endpoints.test_users.TestUserAPI.test_create_user_success
```

### Using pytest (if installed)

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/api/v1/endpoints/test_users.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=. tests/
```

## Test Coverage

The test suite covers the following areas:

### User API Tests (`test_users.py`)

**CRUD Operations:**
- ✅ Create user (success and validation)
- ✅ Get user by ID (success and not found)
- ✅ Get users list (with pagination and filtering)
- ✅ Update user (success, validation, and not found)
- ✅ Delete user (success and not found)

**Advanced Features:**
- ✅ User filtering by role, department, status
- ✅ User search by name or email
- ✅ User pagination
- ✅ User statistics
- ✅ User authentication

**Error Handling:**
- ✅ Duplicate email validation
- ✅ Invalid data validation
- ✅ Password validation
- ✅ Not found scenarios
- ✅ Database constraint violations

**Edge Cases:**
- ✅ Empty database scenarios
- ✅ Large dataset pagination
- ✅ Special characters in search
- ✅ Password updates
- ✅ Email updates with validation

## Test Data

Test data is managed through the `TestDataFactory` class in `utils/test_helpers.py`:

- `create_user_data()` - Creates valid user data
- `create_user_update_data()` - Creates user update data
- `create_multiple_users_data()` - Creates multiple users for testing

## Fixtures

Pytest fixtures are defined in `conftest.py`:

- `db_session` - Fresh database session for each test
- `client` - Test client with database override
- `sample_user_data` - Sample user data
- `sample_user_update_data` - Sample user update data
- `created_user` - Pre-created user for testing
- `multiple_users` - Multiple pre-created users

## Database Testing

Tests use an in-memory SQLite database to ensure:
- Fast test execution
- Isolation between tests
- No side effects on development database
- Automatic cleanup after each test

## Best Practices

1. **Test Isolation**: Each test is independent and doesn't affect others
2. **Clean Setup/Teardown**: Database is cleaned before and after each test
3. **Comprehensive Coverage**: All endpoints and edge cases are tested
4. **Clear Naming**: Test methods clearly describe what they test
5. **Helper Functions**: Common functionality is extracted to helper classes
6. **Error Testing**: Both success and failure scenarios are tested

## Adding New Tests

When adding new API endpoints or functionality:

1. Create test file in appropriate directory
2. Follow naming convention: `test_<module_name>.py`
3. Create test class: `Test<ModuleName>API`
4. Add test methods: `test_<functionality>_<scenario>`
5. Use helper functions from `test_helpers.py`
6. Ensure proper setup/teardown
7. Test both success and failure cases

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- No external dependencies
- Fast execution
- Clear pass/fail indicators
- Detailed error reporting
- Exit codes for automation

## Troubleshooting

**Import Errors:**
- Ensure you're running from the backend directory
- Check that all dependencies are installed
- Verify Python path includes the backend directory

**Database Errors:**
- Tests use in-memory SQLite, no external database needed
- Each test gets a fresh database session
- Tables are created/dropped automatically

**Test Failures:**
- Check test output for specific error messages
- Use `--verbosity 2` for detailed output
- Use `--failfast` to stop on first failure
- Check that the API is working correctly outside of tests
