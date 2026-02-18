# Testing Guide

This directory contains integration tests for core Meghan backend endpoints, including Phase 3 endpoints and newer features (micro expressions, journaling, insights, crisis detection).

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

Run newer feature test files:
```bash
# Micro expressions (Task 6)
pytest tests/test_expressions.py -v

# Journaling + prompts + voice stub (Task 7)
pytest tests/test_journal.py -v

# Weekly insights (Task 8)
pytest tests/test_insights.py -v

# Crisis detection & resources (Task 9)
pytest tests/test_crisis.py -v
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

### `test_phase3_endpoints.py` – Core Phase 3

**User State Endpoints (Task 3.2)**
- `GET /api/users/me/state` - Creates default state
- `PUT /api/users/me/state` - Partial and full updates
- `PUT /api/users/me/state` - Validation (invalid tier/mood)
- `PUT /api/users/me/state` - "Others" stress source validation
- `POST /api/users/me/state/xp` - XP addition and level calculation
- `POST /api/users/me/state/xp` - Level up at thresholds

**User Profile Endpoints (Task 3.2)**
- `GET /api/users/me/profile` - Creates empty profile
- `PUT /api/users/me/profile` - Updates profile fields
- `PUT /api/users/me/profile` - XP bonuses for new fields
- `PUT /api/users/me/profile` - No XP for updating existing fields

**Chat Endpoints (Task 3.1)**
- `POST /api/chat/conversations` - Create with default/explicit values
- `POST /api/chat/conversations` - Validation
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}/messages` - Get messages
- `POST /api/chat/conversations/{id}/messages` - Send message (requires `GEMINI_API_KEY`)

**Authentication**
- All endpoints require authentication
- Unauthorized access returns 401

### `test_expressions.py` – Micro Expressions (Task 6)

**Expressions API**
- `POST /api/expressions` - Create micro expression (280 char limit, optional `community_id`, `is_anonymous`)
- `GET /api/expressions` - List expressions with pagination and optional `community_id` filter
- `POST /api/expressions/{id}/empathy` - Add empathy response (280 char limit)

**Safety & Hearts Integration**
- Keyword-based + safety gate blocking for high-risk content
- `CrisisEvent` logging on blocked content
- Hearts awarded for expressions and empathy responses
- Authentication required for all endpoints

### `test_journal.py` – Journaling (Task 7)

**Journal API**
- `GET /api/journal/prompts` - Returns hardcoded prompt catalog
- `POST /api/journal/entries` - Create journal entry (optional `mood_at_time`, `tier_at_time`)
- `GET /api/journal/entries` - List entries with pagination
- `POST /api/journal/entries/{id}/voice` - Voice upload stub (audio validation only)

**Safety & Hearts Integration**
- Safety gate on journal content with `CrisisEvent` logging for high-risk entries
- Hearts awarded for journal completion
- Authentication required

### `test_insights.py` – Weekly Insights (Task 8)

**Insights API**
- `GET /api/insights/weekly` - Weekly wellbeing insights for current user
  - Mood trends (from `JournalEntry` and `Conversation`)
  - Trigger patterns (stress sources + severity)
  - Progress indicators (journaling, chat sessions, hearts earned)
  - Recommendations and encouragement message
  - Summary stats (totals, most common mood/tier)

### `test_crisis.py` – Crisis Detection Enhancement (Task 9)

**Crisis API**
- `POST /api/crisis/detect` - Crisis risk assessment (low/medium/high) using:
  - Keyword-based detection
  - Optional LLM-based risk assessment for nuanced cases
- `GET /api/crisis/resources` - Emergency resources:
  - Default International resources
  - Country-specific resources (e.g. `US`, `CA`, `IN`)

**Integration**
- Safety gate used across chat, micro expressions, and journal
- `CrisisEvent` logging and therapist notification stub (`NotificationService`)

## Notes

- Tests use an in-memory SQLite database (isolated per test)
- Some behavior (e.g. LLM risk assessment) is monkeypatched in tests to avoid real API calls
- To exercise real LLM behavior, set `GEMINI_API_KEY` and remove/adjust monkeypatches as needed
- Each test creates a fresh database, so tests can run in parallel

## Test Output

Expected output when all tests pass:
```
tests/test_phase3_endpoints.py::TestUserStateEndpoints::test_get_user_state_creates_default PASSED
tests/test_phase3_endpoints.py::TestUserStateEndpoints::test_update_user_state_partial PASSED
...
```

