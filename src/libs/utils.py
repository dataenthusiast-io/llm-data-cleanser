import csv
import json
import logging
from pathlib import Path
from typing import List, Dict
import yaml

def setup_logging(log_file: str):
    """Configure logging to both file and console."""
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def read_csv(file_path: str) -> List[Dict]:
    """Read CSV file and return list of dictionaries."""
    logging.info(f"Reading CSV file: {file_path}")
    try:
        contacts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)
        logging.info(f"Successfully read {len(contacts)} contacts")
        return contacts
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        raise

def chunk_contacts(contacts: List[Dict], chunk_size: int) -> List[List[Dict]]:
    """Split contacts into chunks of specified size."""
    chunks = [contacts[i:i + chunk_size] for i in range(0, len(contacts), chunk_size)]
    logging.info(f"Split contacts into {len(chunks)} chunks of size {chunk_size}")
    return chunks

def parse_llm_response(response: str) -> List[Dict]:
    """Parse LLM response with error handling."""
    try:
        response = response.strip()
        start = response.find('[')
        end = response.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        json_str = response[start:end]
        return json.loads(json_str)
    except Exception as e:
        logging.error(f"Error parsing LLM response: {str(e)}\nResponse was: {response}")
        return []

def load_prompt(prompt_file: str) -> dict:
    """Load prompt from YAML file."""
    try:
        with open(prompt_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading prompt file: {str(e)}")
        raise 