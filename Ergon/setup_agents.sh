#!/bin/bash
# Setup script for agent-specific virtual environments

# Setup browser agent
echo "Setting up browser agent environment..."
cd agents/browser
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ../..  # Install Ergon in development mode
deactivate
echo "Browser agent environment set up successfully"

# Setup mail agent
echo "Setting up mail agent environment..."
cd ../mail
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ../..  # Install Ergon in development mode
deactivate
echo "Mail agent environment set up successfully"

# Setup GitHub agent
echo "Setting up GitHub agent environment..."
cd ../github
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ../..  # Install Ergon in development mode
deactivate
echo "GitHub agent environment set up successfully"

echo "All agent environments set up successfully"