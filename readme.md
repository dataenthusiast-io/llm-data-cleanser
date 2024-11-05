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

2. Install Ollama following instructions at https://ollama.ai/

3. Run the start script which will set up everything automatically:

```bash
./start.sh
```

The start script will:
- Create a Python virtual environment if it doesn't exist
- Activate the virtual environment
- Install all required packages
- Run the analysis and cleaning pipeline sequentially
- Deactivate the virtual environment when complete

## Configuration

The application is configured through a YAML file located at `src/config.yaml`:

```yaml
MODEL_NAME: mistral        # The Ollama model to use
TEMPERATURE: 0.1          # Temperature setting for LLM responses
CHUNK_SIZE: 5            # Number of contacts to process in each batch
LOG_FILE: logs/app.log   # Path to log file
INPUT_FILE: data/input/contacts.csv           # Input file path
ANALYZED_FILE: data/processed/analyzed_contacts.csv  # Analysis output path
CLEANED_FILE: data/processed/cleaned_contacts.csv    # Cleaned output path
PROMPT_FILE: src/prompts/analyze.yaml         # Analysis prompt file path
```

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