#\!/bin/bash

set -e

echo "🤖 Setting up Ergon..."

# Check if Python is installed
if \! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 10 ]); then
    echo "❌ Python 3.10+ is required. You have Python $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ \! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "🔧 Installing Ergon in development mode..."
pip install -e .

# Create .env file if it doesn't exist
if [ \! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️ Please edit .env file to add your API keys."
fi

# Create .env.owner file if it doesn't exist
if [ \! -f ".env.owner" ]; then
    echo "📝 Creating .env.owner file for personal settings..."
    cat > .env.owner << EOL
# Owner configuration - this file is ignored by Git

# API Keys (only one required)
OPENAI_API_KEY=\${OPENAI_API_KEY:-""}
ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY:-""}
OLLAMA_BASE_URL=\${OLLAMA_BASE_URL:-"http://localhost:11434"}

# Model settings
DEFAULT_MODEL=\${DEFAULT_MODEL:-"claude-3-7-sonnet-20250219"}
USE_LOCAL_MODELS=\${USE_LOCAL_MODELS:-false}
EMBEDDING_MODEL=\${EMBEDDING_MODEL:-"sentence-transformers/all-MiniLM-L6-v2"}

# Application settings
LOG_LEVEL=\${LOG_LEVEL:-"INFO"}
DEBUG=\${DEBUG:-false}
EOL
    echo "⚠️ .env.owner created with environment variables. Please edit if needed."
fi

# Create .env.local file if it doesn't exist
if [ \! -f ".env.local" ]; then
    echo "📝 Creating .env.local file for local development..."
    cat > .env.local << EOL
# Local development configuration - this file is ignored by Git

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434

# Model settings - using Phi-3 model for local development
DEFAULT_MODEL=ollama/phi3-mini
USE_LOCAL_MODELS=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Debug settings
LOG_LEVEL=DEBUG
DEBUG=true
EOL
    echo "⚠️ .env.local created for local development. Please edit if needed."
fi

# Initialize database
echo "🗃️ Initializing database..."
ergon init

echo "✅ Setup complete\! You can now use Ergon:"
echo ""
echo "🖥️ Start the UI:           ergon ui"
echo "📋 List agents:            ergon list"
echo "🤖 Create a new agent:     ergon create -n \"my_agent\" -d \"Description\""
echo ""
echo "📚 For more information, run: ergon --help"
echo ""
echo "🧩 To set up agent-specific environments, run: ./setup_agents.sh"
