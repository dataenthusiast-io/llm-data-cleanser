#!/bin/bash

# Exit on error
set -e

echo "Setting up virtual environment..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run the analysis and cleaning pipeline
echo "Starting analysis pipeline..."
python src/analyze.py
echo "Starting cleaning pipeline..."
python src/clean.py

echo "Process complete! Check the output directory for results."

# Deactivate virtual environment
deactivate