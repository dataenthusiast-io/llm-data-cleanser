# Data Cleanser - Contact Database Auditor

A Python application that uses Large Language Models (LLM) to automatically identify and flag test/dummy entries in contact databases.

## Purpose

This tool helps database administrators and data analysts clean their contact databases by automatically identifying potentially fake or test entries. It uses LangChain with Ollama to analyze contact information and determine whether each entry appears to be legitimate or a test/dummy entry. By leveraging Ollama for local LLM processing, all data remains on your machine, ensuring complete privacy and compliance with data protection requirements - no contact information ever leaves your system.

## Features

- Processes CSV files containing contact information
- Uses AI to identify test/dummy entries based on multiple criteria:
  - Obviously fake names
  - Test/dummy email patterns
  - Incomplete or suspicious data
  - Organization name validation
- Processes contacts in configurable batch sizes for efficiency
- Comprehensive logging system
- Outputs analyzed and cleaned CSV files
- Error handling and recovery mechanisms
- Local processing using Ollama for data privacy

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Required Python packages (install via pip):
  - langchain
  - langchain-ollama
  - tqdm
  - pathlib
  - pyyaml

## Installation

1. Clone this repository:

```bash
git clone https://github.com/dataenthusiast-io/llm-data-cleanser.git
cd llm-data-cleanser
```

2. Run the setup script which will set up everything automatically:

```bash
./setup.sh
```

The setup script will:
- Check for Python 3 installation
- Create a Python virtual environment if it doesn't exist
- Install all required packages
- Check for Ollama installation and install if needed
- Pull the required LLM model specified in your .env file

3. After setup is complete, you can run the pipeline using:

```bash
./start.sh
```

The start script will:
- Run the analysis and cleaning pipeline sequentially
- Output results to the output directory

## Configuration

The application is configured through a `.env` file located at the root of the project:

```
MODEL_NAME=llama3.2        # The Ollama model to use
TEMPERATURE=0.1          # Temperature setting for LLM responses
CHUNK_SIZE=10            # Number of contacts to process in each batch
```

**Info:** We recommend setting the `CHUNK_SIZE` not > 25 to avoid token limit issues.

## Input/Output Structure

### Input File Format

The input CSV file should contain the following required columns:
- name
- organization
- email

### Output Files

The application produces two types of output files:

1. Analyzed contacts (`analyzed_contacts.csv`):
   - All original columns
   - `is_real`: Boolean indicating if the entry appears legitimate
   - `confidence_score`: Confidence level of the analysis
   - `reason`: Explanation for the analysis result

2. Cleaned contacts (`cleaned_contacts.csv`):
   - Contains only entries marked as real contacts
   - Includes only the essential columns:
     - name
     - organization
     - email

## Command Line Usage

While the start script is recommended, you can run individual components directly:

1. For analyzing contacts:
```bash
python src/analyze.py
```

2. For cleaning contacts:
```bash
python src/clean.py
```

## Logging

The application maintains detailed logs in the configured log file (`logs/app.log`), including:
- Processing start/end times
- Number of contacts processed
- Any errors or issues encountered
- Processing status for each chunk

## Error Handling

The application includes robust error handling for:
- File I/O operations
- CSV parsing
- LLM processing
- JSON parsing
- Web interface errors
- Individual chunk processing failures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.