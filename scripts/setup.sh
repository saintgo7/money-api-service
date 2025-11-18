#!/bin/bash
# Setup script for Money API Service

set -e

echo "🚀 Setting up Money API Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.11" | bc -l) )); then
    echo "❌ Python 3.11+ is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys and configuration"
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker detected"

    read -p "Start database services with Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐳 Starting database services..."
        docker-compose up -d postgres redis

        echo "⏳ Waiting for databases to be ready..."
        sleep 5
    fi
else
    echo "⚠️  Docker not found. Please install Docker to run databases"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Create first admin user (optional)
read -p "Create admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "👤 Creating admin user..."
    python scripts/create_admin.py
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: make dev"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "For production deployment, see docs/DEPLOYMENT.md"
