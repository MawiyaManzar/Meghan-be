# Meghan API (Backend)

FastAPI backend for **Meghan**, an AI-powered Student Wellness Assistant for students and young adults.

## Why Meghan

- **Problem**: Students and young adults experience relentless daily stress (exams, career, finances, family, social comparison), often amplified by social media's impact on anxiety and distraction.
- **Current gaps**: Existing solutions are inadequate: therapy apps feel clinical, productivity tools ignore emotional health, and mainstream social platforms prioritize addiction over mental wellbeing.
- **Need**: Young people lack a safe, accessible, and engaging daily space for open communication, validation, habit development, and peer support.
- **Solution**: An AI-powered, supportive community that bridges social media and therapy, designed to safeguard mental wellbeing and foster growth among young adults.

## Product Overview

- **Meghan is**: an AI-powered Student Wellness Assistant offering personalized support
- **Support areas**: mental health, productivity, and routines
- **Interface**: single-interface digital companion using natural conversation
- **Target audience/issues**: academic pressure, anxiety, burnout, loneliness, and poor habits
- **Core offerings**: immediate emotional support, coping strategies, and skill-building promotion
- **Safety & trust**: privacy-first design, safety validation, crisis detection, and professional oversight

## Core Features

- AI chat-based wellness companion
- Daily mental check-ins
- Stress and burnout detection
- Guided reflection and journaling
- Habit and routine suggestions
- Focus and productivity coaching
- Calm, friendly UX
- Privacy-first design

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Configure Environment

Edit `.env` and set:
- `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `GEMINI_API_KEY`: get from `https://aistudio.google.com/app/apikey`
- `CORS_ORIGINS`: your frontend URL(s)

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API**: `http://localhost:8000`
- **Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```text
Be/
├── app/
│   ├── core/            # Core configuration and settings
│   ├── models/          # Database ORM models (SQLAlchemy)
│   ├── schemas/         # Pydantic schemas (API request/response)
│   ├── routers/         # API route handlers
│   ├── services/        # Business logic and services
│   └── main.py          # FastAPI application entry point
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
├── STRUCTURE.md         # Project structure guide
└── README.md            # This file
```

- **`app/models/`**: SQLAlchemy ORM models (database table definitions)
- **`app/schemas/`**: Pydantic schemas (API request/response validation)
- **More detail**: see `STRUCTURE.md`

## API Endpoints

Base URL (local): `http://localhost:8000`

**Auth**
- Most `/api/*` endpoints require `Authorization: Bearer <token>` (JWT).
- Therapist endpoints require a therapist/admin-capable account (see `TherapistUser` dependency in code).

### Core
- **GET** `/` - Root welcome payload
- **GET** `/health` - API health check

### Authentication (`/api/auth`)
- **POST** `/api/auth/register` - Register a new user
- **POST** `/api/auth/login` - Login (OAuth2 form: username=email, password)
- **POST** `/api/auth/login-json` - Login (JSON body)
- **GET** `/api/auth/me` - Get current user (requires auth)

### LLM (`/api/llm`)
- **GET** `/api/llm/health` - LLM config health (no auth)
- **GET** `/api/llm/test` - Test LLM connection (requires auth)

### Chat (`/api/chat`) (requires auth)
- **POST** `/api/chat/conversations` - Create a conversation
- **GET** `/api/chat/conversations` - List user conversations
- **GET** `/api/chat/conversations/{conversation_id}/messages` - Get conversation history
- **POST** `/api/chat/conversations/{conversation_id}/messages` - Send a message (AI reply is generated)

### Users (`/api/users`) (requires auth)
- **GET** `/api/users/me/state` - Get current user state
- **PUT** `/api/users/me/state` - Update current user state
- **POST** `/api/users/me/state/xp` - Add XP (legacy; see hearts system)
- **GET** `/api/users/me/profile` - Get user profile/bio
- **PUT** `/api/users/me/profile` - Update user profile/bio
- **GET** `/api/users/me/dashboard` - Get aggregated dashboard data

### Hearts (`/api/hearts`) (requires auth)
- **GET** `/api/hearts/balance` - Get hearts balance and totals
- **POST** `/api/hearts/earn` - Award hearts (protected; intended for backend/internal flows)

### Onboarding (`/api/onboarding`) (requires auth)
- **PUT** `/api/onboarding/profile` - Save onboarding fields (age_range, life_stage, struggles)
- **PUT** `/api/onboarding/privacy` - Save onboarding privacy preference

### Check-ins (`/api/checkins`) (requires auth)
- **POST** `/api/checkins/first` - Store first emotional check-in

### Communities (`/api/communities`) (requires auth)
- **GET** `/api/communities` - List communities (optional query: `stress_source`)
- **POST** `/api/communities/{community_id}/join` - Join/update anonymity for a community

### Therapist (`/api/therapist`) (requires therapist access)
- **GET** `/api/therapist/crisis-events` - List crisis events (optional query: `community_id`, `limit`)

## Development

### Environment Variables

See `.env.example` for all available configuration options.

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

