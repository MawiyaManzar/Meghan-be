# Testing Guide

This directory contains integration tests for the Phase 3 endpoints.

## Setup

1. Install test dependencies:
```bash
pip install pytest httpx
```

Or if using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests

**Note:** The `manual_test_script.py` file is a standalone script (not a pytest test) that requires the server to be running. It won't be picked up by pytest.

Run all pytest tests:
```bash
pytest tests/ -v
```

Run a specific test file:
```bash
pytest tests/test_phase3_endpoints.py -v
```

Run a specific test class:
```bash
pytest tests/test_phase3_endpoints.py::TestUserStateEndpoints -v
```

Run a specific test:
```bash
pytest tests/test_phase3_endpoints.py::TestUserStateEndpoints::test_get_user_state_creates_default -v
```

## Test Coverage

The test file `test_phase3_endpoints.py` includes:

### User State Endpoints (Task 3.2)
- GET /api/users/me/state - Creates default state
- PUT /api/users/me/state - Partial and full updates
- PUT /api/users/me/state - Validation (invalid tier/mood)
- PUT /api/users/me/state - "Others" stress source validation
- POST /api/users/me/state/xp - XP addition and level calculation
- POST /api/users/me/state/xp - Level up at thresholds

### User Profile Endpoints (Task 3.2)
- GET /api/users/me/profile - Creates empty profile
- PUT /api/users/me/profile - Updates profile fields
- PUT /api/users/me/profile - XP bonuses for new fields
- PUT /api/users/me/profile - No XP for updating existing fields

### Chat Endpoints (Task 3.1)
- POST /api/chat/conversations - Create with default/explicit values
- POST /api/chat/conversations - Validation
- GET /api/chat/conversations - List conversations
- GET /api/chat/conversations/{id}/messages - Get messages
- POST /api/chat/conversations/{id}/messages - Send message (requires GEMINI_API_KEY)

### Authentication
- All endpoints require authentication
- Unauthorized access returns 401

## Notes

- Tests use an in-memory SQLite database (isolated per test)
- Chat message tests that require LLM are marked with `@pytest.mark.skip` by default
- To test LLM endpoints, set `GEMINI_API_KEY` environment variable and remove the skip marker
- Each test creates a fresh database, so tests can run in parallel

## Test Output

Expected output when all tests pass:
```
tests/test_phase3_endpoints.py::TestUserStateEndpoints::test_get_user_state_creates_default PASSED
tests/test_phase3_endpoints.py::TestUserStateEndpoints::test_update_user_state_partial PASSED
...
```

