# Meghan Development Guide

## Project Structure

```
meghan/
├── app/                          # FastAPI backend
│   ├── core/                     # Core configuration and database
│   │   ├── config.py            # Settings and environment variables
│   │   ├── database.py          # Database connections (PostgreSQL, MongoDB, Redis)
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── security.py          # Authentication and security
│   ├── models/                   # SQLAlchemy models (PostgreSQL)
│   ├── schemas/                  # Pydantic schemas for API
│   ├── routers/                  # API route handlers
│   ├── services/                 # Business logic services
│   └── main.py                   # FastAPI application entry point
├── frontend/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                  # Next.js 13+ app directory
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utility libraries
│   │   ├── types/                # TypeScript type definitions
│   │   └── hooks/                # Custom React hooks
│   ├── package.json              # Node.js dependencies
│   └── next.config.js            # Next.js configuration
├── tests/                        # Backend tests
├── docker-compose.yml            # Development environment
├── requirements.txt              # Python dependencies
└── pyproject.toml               # Python project configuration
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Primary database for user profiles, communities, hearts system
- **MongoDB**: Document database for chat sessions and wellbeing data
- **Redis**: Caching and session management
- **SQLAlchemy**: ORM for PostgreSQL
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **pytest**: Testing framework with async support
- **Hypothesis**: Property-based testing

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Hook Form**: Form handling
- **Zod**: Schema validation
- **Jest**: Testing framework
- **Testing Library**: React component testing

### Infrastructure
- **Docker**: Containerization for development
- **Docker Compose**: Multi-service orchestration
- **Alembic**: Database migrations
- **uvicorn**: ASGI server for FastAPI

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- Docker and Docker Compose
- Git

### Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd meghan
   ./setup-dev.sh
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development services:**
   ```bash
   # Option 1: Docker Compose (recommended)
   docker-compose up

   # Option 2: Manual startup
   # Terminal 1: Backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev

   # Terminal 3: Databases (if not using Docker)
   # Start PostgreSQL, MongoDB, and Redis manually
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Workflow

### Backend Development

1. **Add new dependencies:**
   ```bash
   # Add to requirements.txt and pyproject.toml
   pip install <package>
   ```

2. **Database changes:**
   ```bash
   # Create migration
   alembic revision --autogenerate -m "Description"
   
   # Apply migration
   alembic upgrade head
   ```

3. **Run tests:**
   ```bash
   # All tests
   pytest

   # Specific test file
   pytest tests/test_infrastructure.py

   # With coverage
   pytest --cov=app

   # Property-based tests only
   pytest -m property
   ```

### Frontend Development

1. **Add new dependencies:**
   ```bash
   cd frontend
   npm install <package>
   ```

2. **Run tests:**
   ```bash
   cd frontend
   
   # All tests
   npm test

   # Watch mode
   npm run test:watch

   # Coverage
   npm run test:coverage
   ```

3. **Linting and formatting:**
   ```bash
   cd frontend
   npm run lint
   ```

## Database Architecture

### PostgreSQL (Primary Database)
- User profiles and authentication
- Community management
- Hearts system transactions
- Moderation logs

### MongoDB (Document Store)
- Chat sessions and messages
- Wellbeing insights and analytics
- Journal entries
- Mood tracking data

### Redis (Cache & Sessions)
- Session management
- API response caching
- Rate limiting
- Real-time features

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Service interaction testing
- **Property-Based Tests**: Correctness validation with Hypothesis
- **API Tests**: Endpoint testing with TestClient

### Frontend Testing
- **Component Tests**: React component testing with Testing Library
- **Integration Tests**: User flow testing
- **Unit Tests**: Utility function testing

### Test Organization
```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── property/                # Property-based tests
└── conftest.py             # Test configuration
```

## Environment Configuration

### Development
- SQLite fallback for quick setup
- Local Docker services
- Hot reloading enabled
- Debug logging

### Production
- PostgreSQL primary database
- Managed MongoDB and Redis
- Optimized builds
- Security hardening

## API Documentation

The FastAPI backend automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   ```bash
   # Check Docker services
   docker-compose ps
   
   # Restart services
   docker-compose restart postgres mongodb redis
   ```

2. **Frontend build errors:**
   ```bash
   cd frontend
   rm -rf .next node_modules
   npm install
   npm run build
   ```

3. **Python dependency conflicts:**
   ```bash
   # Use virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Logs and Debugging

```bash
# Docker service logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Application logs
tail -f app.log

# Database logs
docker-compose exec postgres psql -U meghan_user -d meghan
```

## Contributing

1. Create feature branch from main
2. Implement changes with tests
3. Run full test suite
4. Update documentation
5. Submit pull request

### Code Style
- Backend: Follow PEP 8, use Black formatter
- Frontend: Follow ESLint rules, use Prettier
- Commit messages: Conventional Commits format

## Security Considerations

- Environment variables for secrets
- Input validation with Pydantic/Zod
- SQL injection prevention with ORM
- CORS configuration
- Rate limiting
- Authentication tokens
- Data encryption at rest and in transit