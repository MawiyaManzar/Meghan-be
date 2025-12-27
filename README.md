# Meghan API - Backend

FastAPI backend for the Meghan student wellness assistant application.

## Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit `.env` file and set the required variables:
   - `SECRET_KEY`: Generate a secure random string (use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
   - `GEMINI_API_KEY`: Your Google Gemini API key (get from https://aistudio.google.com/app/apikey)
   - `CORS_ORIGINS`: Update with your frontend URL(s)

### Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Project Structure

```
Be/
├── app/
│   ├── core/           # Core configuration and settings
│   ├── models/         # Database ORM models (SQLAlchemy)
│   ├── schemas/        # Pydantic schemas (API request/response)
│   ├── routers/        # API route handlers
│   ├── services/       # Business logic and services
│   └── main.py         # FastAPI application entry point
├── .env.example        # Example environment variables
├── requirements.txt    # Python dependencies
├── STRUCTURE.md        # Project structure guide
└── README.md          # This file
```

**Directory Purpose:**
- `models/`: SQLAlchemy ORM models (database table definitions)
- `schemas/`: Pydantic schemas (API request/response validation)
- See `STRUCTURE.md` for detailed explanation of the separation

## Development

### Environment Variables

See `.env.example` for all available configuration options.

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

