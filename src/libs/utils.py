import csv
import json
import logging
from pathlib import Path
from typing import List, Dict
import yaml
from tqdm import tqdm
import time
from datetime import datetime

# Global logger and progress bar
logger = logging.getLogger('llm_cleanser')
progress_bar = None

class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_blue = "\x1b[1;34m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: bold_blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def setup_logging(base_log_dir: str = "logs") -> logging.Logger:
    """Configure logging to both file and console with timestamped log file."""
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create timestamped log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = Path(base_log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"llm_cleanser_{timestamp}.log"
    
    # Set logging level
    logger.setLevel(logging.DEBUG)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file)
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colored formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)
    
    logger.info(f"📝 Logging to: {log_file}")
    return logger

def log_network_call(endpoint: str, prompt_preview: str = None, **kwargs):
    """Log network calls with relevant details."""
    timestamp = time.strftime('%H:%M:%S')
    if progress_bar:
        progress_bar.clear()  # Temporarily clear progress bar
    
    logger.info(f"🌐 API Call to: {endpoint}")
    if prompt_preview:
        preview = prompt_preview[:100] + "..." if len(prompt_preview) > 100 else prompt_preview
        logger.debug(f"📤 Prompt: {preview}")
    
    # Log additional parameters if provided
    for key, value in kwargs.items():
        if key not in ['prompt']:  # Skip full prompt to avoid cluttering
            logger.debug(f"  {key}: {value}")
    
    if progress_bar:
        progress_bar.refresh()  # Redraw progress bar

def init_progress_bar(total: int, desc: str = "Processing") -> tqdm:
    """Initialize a progress bar."""
    global progress_bar
    if progress_bar:
        progress_bar.close()
    progress_bar = tqdm(total=total, desc=desc, position=0, leave=True)
    return progress_bar

def update_progress(n: int = 1, desc: str = None, additional_info: str = None):
    """Update the progress bar with optional additional information."""
    global progress_bar
    if progress_bar is not None:
        progress_bar.clear()  # Clear current progress bar
        if desc:
            progress_bar.set_description(desc)
        if additional_info:
            logger.info(f"📊 {additional_info}")
        progress_bar.update(n)
        progress_bar.refresh()  # Redraw progress bar

def read_csv(file_path: str) -> List[Dict]:
    """Read CSV file and return list of dictionaries."""
    logger.info(f"📂 Reading CSV file: {file_path}")
    try:
        contacts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)
        logger.info(f"✅ Successfully read {len(contacts)} contacts")
        return contacts
    except Exception as e:
        logger.error(f"❌ Error reading CSV file: {str(e)}")
        raise

def chunk_contacts(contacts: List[Dict], chunk_size: int) -> List[List[Dict]]:
    """Split contacts into chunks of specified size."""
    chunks = [contacts[i:i + chunk_size] for i in range(0, len(contacts), chunk_size)]
    total_chunks = len(chunks)
    logger.info(f"📦 Split {len(contacts)} contacts into {total_chunks} chunks of size {chunk_size}")
    # Initialize progress bar for total chunks
    init_progress_bar(total_chunks, "Processing chunks")
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
        parsed = json.loads(json_str)
        logger.debug(f"✅ Successfully parsed LLM response with {len(parsed)} items")
        return parsed
    except Exception as e:
        logger.error(f"❌ Error parsing LLM response: {str(e)}\nResponse was: {response}")
        return []

def load_prompt(prompt_file: str) -> dict:
    """Load prompt from YAML file."""
    logger.info(f"📄 Loading prompt from: {prompt_file}")
    try:
        with open(prompt_file, 'r') as f:
            prompt_data = yaml.safe_load(f)
        logger.info("✅ Prompt loaded successfully")
        return prompt_data
    except Exception as e:
        logger.error(f"❌ Error loading prompt file: {str(e)}")
        raise