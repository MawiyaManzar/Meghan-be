#!/bin/bash

# Development setup script for Meghan AI Community Support System

set -e

echo "🚀 Setting up Meghan development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values"
fi

if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local file from example..."
    cp frontend/.env.example frontend/.env.local
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for faster installation..."
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
cd frontend
if command -v npm &> /dev/null; then
    npm install
else
    echo "❌ npm is not installed. Please install Node.js and npm first."
    exit 1
fi
cd ..

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres mongodb redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations (if any)
echo "🗄️  Running database setup..."
# Note: Add actual migration commands here when Alembic is set up

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/test_infrastructure.py -v

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env with your actual configuration values"
echo "2. Add your Gemini API key to .env"
echo "3. Start the backend: uvicorn app.main:app --reload"
echo "4. Start the frontend: cd frontend && npm run dev"
echo "5. Or use Docker: docker-compose up"
echo ""
echo "📚 Useful commands:"
echo "- Backend tests: pytest"
echo "- Frontend tests: cd frontend && npm test"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"