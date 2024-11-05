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
- Processes contacts in configurable batch sizes for efficiency
- Comprehensive logging system
- Outputs a new CSV with additional columns for test status and reasoning
- Error handling and recovery mechanisms

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Required Python packages (install via pip):
  - langchain
  - langchain-ollama
  - tqdm
  - pathlib

## Installation

1. Clone this repository:

```bash
git clone [repository-url]
cd data-cleanser
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Pull the llama3.2 model:

```bash
ollama pull llama3.2
```


## Configuration

The following constants can be modified in `clean.py`:

- `CHUNK_SIZE`: Number of contacts to process in each batch (default: 10)
- `INPUT_FILE`: Path to input CSV file (default: "input/people-5730288-126.csv")
- `OUTPUT_FILE`: Path for cleaned output CSV (default: "output/cleaned_contacts.csv")
- `LOG_FILE`: Path for log file (default: "output/processing.log")

## Input File Format

The input CSV file should contain the following columns:
- Person - Name
- Person - Organization
- Person - Email - Work

## Usage

1. Place your input CSV file in the specified input location
2. Run the script:

```bash
python clean.py
```

3. Check the output directory for:
- Cleaned CSV file with additional columns: `is_test` and `test_reason`
- Processing log file

## Output Format

The output CSV will contain all original columns plus:
- `is_test`: Boolean indicating if the entry is likely a test contact
- `test_reason`: Explanation for why the entry was flagged (if applicable)

## Logging

The application maintains detailed logs including:
- Processing start/end times
- Number of contacts processed
- Any errors or issues encountered
- Processing status for each chunk

Logs are written to both the console and a log file.

## Error Handling

The application includes robust error handling for:
- File I/O operations
- CSV parsing
- LLM processing
- JSON parsing
- Individual chunk processing failures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.