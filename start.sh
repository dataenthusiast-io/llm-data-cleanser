#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source .venv/bin/activate

# Run the analysis and cleaning pipeline
echo "Starting analysis pipeline..."
python src/analyze.py
echo "Starting cleaning pipeline..."
python src/clean.py

echo "Process complete! Check the output directory for results."

# Deactivate virtual environment
deactivate