#!/bin/bash

# Quick Fix Script for Telegram Bot Issues
echo "🔧 Quick Fix Script for Telegram Bot"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root"
    exit 1
fi

echo "📦 Installing missing dependencies..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/upgrade requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed!"

# Set up environment variables template
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env template..."
    cp .env_example .env
    echo ""
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
    echo "   - XAI_API_KEY=your_xai_api_key"
    echo "   - HUGGINGFACE_API_KEY=your_huggingface_api_key"
    echo ""
fi

# Run the test script
echo "🧪 Running migration test..."
python test_migration.py

echo ""
echo "🎉 Quick fix completed!"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has all required API keys"
echo "2. Run: make run"
echo "3. Test your bot with a simple message"
