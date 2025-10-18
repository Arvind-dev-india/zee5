#!/bin/bash

# ZEE5 Streaming Service - Development Setup Script
echo "🔧 Setting up ZEE5 Streaming Service for development..."

# Check Python version
echo ""
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✓ Python $python_version found"

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "🎭 Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/cache
mkdir -p logs

# Copy environment file
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please update with your configuration."
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create cache directory placeholder
touch data/cache/.gitkeep

echo ""
echo "✅ Development setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Update .env with your configuration"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python -m uvicorn app.main:app --reload"
echo "   4. Open: http://localhost:5052"
echo ""
echo "🐳 Or use Docker:"
echo "   ./scripts/start.sh"
