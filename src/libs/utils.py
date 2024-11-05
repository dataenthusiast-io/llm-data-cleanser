import csv
import json
import logging
from pathlib import Path
from typing import List, Dict
import yaml

# Global logger
logger = logging.getLogger('llm_cleanser')

def setup_logging(log_file: str) -> logging.Logger:
    """Configure logging to both file and console."""
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create log directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set logging level
    logger.setLevel(logging.INFO)
    
    # Create formatters and handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def read_csv(file_path: str) -> List[Dict]:
    """Read CSV file and return list of dictionaries."""
    logger.info(f"Reading CSV file: {file_path}")
    try:
        contacts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)
        logger.info(f"Successfully read {len(contacts)} contacts")
        return contacts
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        raise

def chunk_contacts(contacts: List[Dict], chunk_size: int) -> List[List[Dict]]:
    """Split contacts into chunks of specified size."""
    chunks = [contacts[i:i + chunk_size] for i in range(0, len(contacts), chunk_size)]
    logger.info(f"Split contacts into {len(chunks)} chunks of size {chunk_size}")
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
        logger.error(f"Error parsing LLM response: {str(e)}\nResponse was: {response}")
        return []

def load_prompt(prompt_file: str) -> dict:
    """Load prompt from YAML file."""
    try:
        with open(prompt_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading prompt file: {str(e)}")
        raise