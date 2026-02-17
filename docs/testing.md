# Testing

This guide covers how to write and run tests for WuLims.

## Overview

We use **pytest** as our test framework with the following libraries:

| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-django` | Django integration for pytest |
| `pytest-cov` | Code coverage reporting |
| `pytest-mock` | Mocking utilities |
| `assertpy` | Fluent assertion library |

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_samples.py

# Run a specific test class
uv run pytest tests/test_samples.py::TestSampleModel

# Run a specific test
uv run pytest tests/test_samples.py::TestSampleModel::test_create_sample

# Run tests matching a pattern
uv run pytest -k "approve"

# Run tests and stop on first failure
uv run pytest -x

# Run tests with print output visible
uv run pytest -s
```

## Code Coverage

Coverage is enabled by default. After running tests, you'll see a coverage summary in the terminal.

```bash
# View the HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

The HTML report shows line-by-line coverage, highlighting which lines were executed during tests.

---

## Test Organization

Tests live in the `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_accounts.py     # Tests for accounts app
└── test_samples.py      # Tests for samples app
```

### Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<behavior>`

Example:
```python
class TestSampleModel:
    def test_create_sample(self, db):
        ...

    def test_sample_id_unique(self, sample, db):
        ...
```

---

## Writing Tests

### Using Fixtures

Fixtures provide reusable test data. They're defined in `conftest.py`:

```python
# Available fixtures:

@pytest.fixture
def user(db) -> User:
    """A basic test user."""

@pytest.fixture
def admin_user(db) -> User:
    """An admin/superuser."""

@pytest.fixture
def authenticated_client(client, user) -> Client:
    """Django test client logged in as the test user."""

@pytest.fixture
def sample(db) -> Sample:
    """A sample in RECEIVED status."""

@pytest.fixture
def sample_in_review(db) -> Sample:
    """A sample in IN_REVIEW status (ready for approval)."""

@pytest.fixture
def approved_sample(db, user) -> Sample:
    """An already-approved sample."""
```

Use fixtures by adding them as test function parameters:

```python
def test_approve_success(self, authenticated_client, sample_in_review, user):
    response = authenticated_client.post(
        reverse("samples:approve", args=[sample_in_review.pk])
    )
    assert_that(response.status_code).is_equal_to(200)
```

### Database Access

Tests that need database access must use the `db` fixture:

```python
def test_create_sample(self, db):  # <-- db fixture enables database
    sample = Sample.objects.create(
        sample_id="TEST-001",
        client_name="Test Client",
    )
    assert_that(sample.pk).is_not_none()
```

Other fixtures like `user`, `sample`, etc. already depend on `db`, so you don't need to include it explicitly when using those.

### Using assertpy

We use `assertpy` for fluent, readable assertions:

```python
from assertpy import assert_that

# Basic assertions
assert_that(response.status_code).is_equal_to(200)
assert_that(sample.approved_at).is_not_none()
assert_that(sample.approved_by).is_none()

# String assertions
assert_that(response.content.decode()).contains("TEST-001")
assert_that(str(sample)).is_equal_to("TEST-001")

# Collection assertions
assert_that(statuses).contains("RECEIVED", "APPROVED")
assert_that(results).is_empty()

# Boolean assertions
assert_that(user.is_active).is_true()
assert_that(user.is_superuser).is_false()
```

### Testing Views

Test both authentication requirements and functionality:

```python
class TestSampleListView:
    def test_list_requires_login(self, client):
        """Unauthenticated users are redirected to login."""
        response = client.get(reverse("samples:list"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_list_accessible_when_authenticated(self, authenticated_client):
        """Authenticated users can access the list."""
        response = authenticated_client.get(reverse("samples:list"))

        assert_that(response.status_code).is_equal_to(200)
```

### Testing POST Endpoints

```python
def test_approve_requires_post(self, authenticated_client, sample_in_review):
    """GET requests are rejected."""
    response = authenticated_client.get(
        reverse("samples:approve", args=[sample_in_review.pk])
    )
    assert_that(response.status_code).is_equal_to(400)

def test_approve_success(self, authenticated_client, sample_in_review, user):
    """Sample can be approved when in IN_REVIEW status."""
    response = authenticated_client.post(
        reverse("samples:approve", args=[sample_in_review.pk])
    )

    assert_that(response.status_code).is_equal_to(200)

    # Refresh from database to see changes
    sample_in_review.refresh_from_db()
    assert_that(sample_in_review.status).is_equal_to(Sample.Status.APPROVED)
    assert_that(sample_in_review.approved_by).is_equal_to(user)
```

### Testing for Exceptions

```python
from django.db import IntegrityError

def test_sample_id_unique(self, sample, db):
    """Sample IDs must be unique."""
    with pytest.raises(IntegrityError):
        Sample.objects.create(
            sample_id="TEST-001",  # Same as fixture
            client_name="Different Client",
        )
```

---

## Mocking

Use `pytest-mock` for mocking external dependencies:

```python
def test_with_mock(self, mocker):
    # Mock a function
    mock_send = mocker.patch("samples.views.send_notification")

    # ... test code that calls send_notification ...

    # Verify mock was called
    mock_send.assert_called_once_with(sample_id="TEST-001")
```

---

## Code Quality

### Linting with Ruff

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### Type Checking with ty

```bash
uv run ty check .
```

---

## CI/CD

Tests run automatically on GitHub Actions when you:
- Push to non-`main` branches
- Open a pull request to `main`

The CI workflow includes:
1. Ruff lint and format checks
2. ty type checking
3. Pytest with coverage
4. MkDocs strict build (`mkdocs build --strict`)

Coverage reports are uploaded as artifacts and available for download from the Actions tab.

---

## Best Practices

1. **Test behavior, not implementation** - Focus on what the code does, not how it does it

2. **One assertion per concept** - Multiple assertions are fine if they test the same thing

3. **Use descriptive test names** - `test_approve_fails_when_sample_not_in_review` is better than `test_approve_error`

4. **Keep tests independent** - Each test should work in isolation

5. **Use fixtures for setup** - Don't repeat object creation across tests

6. **Test edge cases** - Empty inputs, None values, boundary conditions

7. **Test error conditions** - Ensure proper error handling and messages

---

## Adding Tests for New Features

When adding a new feature:

1. **Add fixtures** to `conftest.py` if you need new test data
2. **Create test class** with descriptive name (e.g., `TestNewFeature`)
3. **Write tests** covering:
   - Happy path (normal usage)
   - Authentication requirements
   - Validation errors
   - Edge cases
4. **Run tests** to verify they pass
5. **Check coverage** to ensure new code is tested

Example template:

```python
class TestNewFeature:
    """Tests for the new feature."""

    def test_requires_login(self, client):
        """Unauthenticated users are redirected."""
        response = client.get(reverse("app:new-feature"))
        assert_that(response.status_code).is_equal_to(302)

    def test_happy_path(self, authenticated_client):
        """Feature works correctly for authenticated users."""
        response = authenticated_client.get(reverse("app:new-feature"))
        assert_that(response.status_code).is_equal_to(200)

    def test_with_invalid_input(self, authenticated_client):
        """Proper error for invalid input."""
        response = authenticated_client.post(
            reverse("app:new-feature"),
            {"invalid": "data"},
        )
        assert_that(response.status_code).is_equal_to(400)
```
