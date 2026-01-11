#!/bin/bash

echo "=================================="
echo "AI Schedule Manager - Installation"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Check if config needs to be updated
if grep -q "your_schedule_topic_changeme" config.yaml; then
    echo ""
    echo "⚠️  IMPORTANT: You need to update config.yaml!"
    echo ""
    echo "1. Edit config.yaml"
    echo "2. Change 'your_schedule_topic_changeme' to something unique and random"
    echo "3. Update your timezone if needed"
    echo ""
    echo "Example topic: my_secret_schedule_$(openssl rand -hex 8)"
    echo ""
fi

# Create data directory
mkdir -p data
echo "✓ Created data directory"

# Test notification
echo ""
read -p "Do you want to send a test notification? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! grep -q "your_schedule_topic_changeme" config.yaml; then
        echo "Sending test notification..."
        python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
        echo ""
        echo "✓ Check your phone for the notification!"
    else
        echo "⚠️  Please update config.yaml first!"
    fi
fi

echo ""
echo "=================================="
echo "Installation complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Update config.yaml with your ntfy.sh topic"
echo "2. Run example: python3 example_usage.py"
echo "3. Start daemon: python3 -m schedule_manager.daemon"
echo "4. Set up MCP for OpenCode (see README.md)"
echo ""
echo "For more info, see README.md"
echo ""
