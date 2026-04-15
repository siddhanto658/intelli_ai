#!/bin/bash
echo "Setting up INTELLI..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 could not be found. Please install Python3."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing pip requirements..."
pip install -r requirements.txt

echo "Setup complete! Run './run.sh' or 'source venv/bin/activate && python run.py' to start INTELLI."
