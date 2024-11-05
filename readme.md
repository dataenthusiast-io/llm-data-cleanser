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
- Outputs a new CSV with additional columns for analysis results
- Error handling and recovery mechanisms

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

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Quick Start

The easiest way to start the application is using the provided start script:

```bash
./start.sh
```

This will:
- Set up a Python virtual environment
- Source the virtual environment
- Install the required packages
- Run the analysis and cleaning pipeline sequentially

## Command Line Usage

You can also use the application directly from the command line:

1. For analyzing contacts:
```bash
python src/analyze.py --input input/contacts.csv --output output/analyzed_contacts.csv
```

2. For cleaning contacts:
```bash
python src/clean.py --input input/contacts.csv --output output/cleaned_contacts.csv
```

## Configuration

The application can be configured through several methods:
- Environment variables
- Command line arguments
- Configuration files in the `src/prompts` directory

Key configuration options:
- `CHUNK_SIZE`: Number of contacts to process in each batch (default: 10)
- `MODEL_NAME`: Ollama model to use (default: "llama3.2")
- `INPUT_FILE`: Path for input file (default: "input/contacts.csv")
- `ANALYZED_FILE`: Path for analyzed file (default: "output/analyzed_contacts.csv")
- `CLEANED_FILE`: Path for cleaned file (default: "output/cleaned_contacts.csv")
- `LOG_FILE`: Path for log file (default: "output/processing.log")
- `PROMPT_FILE`: Path for prompt file (default: "src/prompts/analyze.yaml")

## Input File Format

The input CSV file should contain the following columns:
- name
- organization
- email

Additional columns will be preserved in the output.

## Output Format

The application produces two types of output files:
1. Analyzed contacts (`analyzed_contacts.csv`):
   - All original columns
   - `analysis_result`: Detailed analysis of the contact
   - `confidence_score`: Confidence level of the analysis

2. Cleaned contacts (`cleaned_contacts.csv`):
   - All original columns
   - `is_real`: Boolean indicating if the entry is likely a real contact
   - `reason`: Explanation for why the entry was flagged (if applicable)

## Logging

The application maintains detailed logs including:
- Processing start/end times
- Number of contacts processed
- Any errors or issues encountered
- Processing status for each chunk
- Web interface access logs

Logs are written to both the console and log files in the `output` directory.

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