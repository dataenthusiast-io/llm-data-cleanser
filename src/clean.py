from pathlib import Path
import sys
from libs.utils import setup_logging, logger
import csv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Constants
LOG_FILE = str(project_root / "logs/app.log")
ANALYZED_FILE = str(project_root / "output/analyzed_contacts.csv")
CLEANED_FILE = str(project_root / "output/cleaned_contacts.csv")

def extract_real_contacts(analyzed_file: str, output_file: str):
    """Extract only real contacts and save to final cleaned CSV."""
    logger.info(f"Extracting real contacts from {analyzed_file}")
    try:
        real_contacts = []
        
        # Read analyzed contacts
        with open(analyzed_file, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Convert string 'True'/'False' to boolean
                is_real = str(row.get('is_real', '')).lower() == 'true'
                if is_real:
                    # Handle potential BOM in field names
                    contact = {}
                    name_key = '\ufeffname' if '\ufeffname' in row else 'name'
                    contact['name'] = row[name_key]
                    contact['organization'] = row['organization']
                    contact['email'] = row['email']
                    real_contacts.append(contact)
        
        # Save real contacts
        if real_contacts:
            output_fields = ['name', 'organization', 'email']
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(real_contacts)
            
            logger.info(f"Saved {len(real_contacts)} real contacts to {output_file}")
        else:
            logger.warning("No real contacts found to save")
            
    except Exception as e:
        logger.error(f"Error extracting real contacts: {str(e)}")
        raise

def main():
    setup_logging(LOG_FILE)
    logger.info("Starting contact cleaning")
    
    try:
        extract_real_contacts(ANALYZED_FILE, CLEANED_FILE)
        logger.info(f"Cleaning complete. Clean contacts saved to {CLEANED_FILE}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
