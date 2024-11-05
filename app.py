from pathlib import Path
from typing import Dict

# Base directories
BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_DIR = SRC_DIR / "prompts"

# Application settings
APP_SETTINGS: Dict = {
    # File paths
    "INPUT_FILE": INPUT_DIR / "contacts.csv",
    "ANALYZED_FILE": OUTPUT_DIR / "analyzed_contacts.csv",
    "CLEANED_FILE": OUTPUT_DIR / "cleaned_contacts.csv",
    "LOG_FILE": OUTPUT_DIR / "processing.log",
    "PROMPT_FILE": PROMPT_DIR / "analyze.yaml",
    
    # LLM settings
    "CHUNK_SIZE": 10,
    "MODEL_NAME": "llama3.2",
    "TEMPERATURE": 0,
}

def init_directories():
    """Initialize required directories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)

def get_settings():
    """Return application settings."""
    return APP_SETTINGS

if __name__ == "__main__":
    init_directories()
