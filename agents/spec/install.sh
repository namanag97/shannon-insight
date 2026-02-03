#!/bin/bash
# Quick install script for Spec Generation Agent

echo "🚀 Setting up Spec Generation Agent..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (recommended) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for API key
echo ""
if [ -z "$GLM_API_KEY" ]; then
    echo "⚠️  GLM_API_KEY environment variable not set"
    echo ""
    echo "To use the agent, you need a GLM API key:"
    echo "1. Get your key from: https://open.bigmodel.cn/"
    echo "2. Set it with: export GLM_API_KEY=your-key-here"
    echo ""
    echo "Or add it to your ~/.bashrc or ~/.zshrc:"
    echo "  echo 'export GLM_API_KEY=your-key-here' >> ~/.bashrc"
else
    echo "✓ GLM_API_KEY found"
fi

# Make scripts executable
chmod +x agent.py example.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Quick start:"
echo "  1. Set your API key: export GLM_API_KEY=your-key-here"
echo "  2. Run the agent: python agent.py --idea \"Your idea here\""
echo "  3. Or try an example: python example.py"
echo ""
echo "For more info: cat README.md"
