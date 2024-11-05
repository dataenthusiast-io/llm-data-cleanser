import csv
import json
import logging
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Constants
CHUNK_SIZE = 10  # Number of contacts per chunk
INPUT_FILE = "input/<your-file>.csv"
OUTPUT_FILE = "output/cleaned_contacts.csv"
LOG_FILE = "output/processing.log"

# Setup logging
def setup_logging():
    """Configure logging to both file and console."""
    log_dir = Path(LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
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

def setup_llm_chain():
    """Setup LangChain processing chain."""
    logging.info("Setting up LLM chain")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a contact database auditor. Analyze the following contacts and identify any that appear to be test/dummy entries.
        For each contact, determine if it's likely a test entry based on:
        - Obviously fake names
        - Test/dummy email patterns
        - Incomplete or suspicious data
        
        You must respond with a valid JSON array where each object contains exactly these fields:
        - "email": the contact's work email (string)
        - "is_test": boolean indicating if it appears to be a test contact (true/false)
        - "reason": brief explanation if marked as test, empty string if not (string)
        
        Example response format:
        [
            {{"email": "test@example.com", "is_test": true, "reason": "Contains test in email"}},
            {{"email": "real@company.com", "is_test": false, "reason": ""}}
        ]
        
        Only mark contacts as test if you're reasonably confident."""),
        ("human", "Please analyze these contacts:\n{contacts}")
    ])

    model = ChatOllama(model="llama3.2", temperature=0)
    
    chain = (
        {"contacts": RunnablePassthrough()} 
        | prompt 
        | model 
        | StrOutputParser()
    )
    
    return chain

def parse_llm_response(response: str) -> List[Dict]:
    """Parse LLM response with error handling."""
    try:
        # Clean the response - remove any leading/trailing text
        response = response.strip()
        # Find the first '[' and last ']'
        start = response.find('[')
        end = response.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        json_str = response[start:end]
        return json.loads(json_str)
    except Exception as e:
        logging.error(f"Error parsing LLM response: {str(e)}\nResponse was: {response}")
        return []

def process_chunks(chunks: List[List[Dict]], chain) -> List[Dict]:
    """Process each chunk through the LLM chain."""
    results = []
    logging.info("Starting chunk processing")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        try:
            # Convert chunk to string format for LLM
            chunk_str = "\n".join([
                f"Name: {c['Person - Name']}, "
                f"Organization: {c['Person - Organization']}, "
                f"Email: {c['Person - Email - Work']}"
                for c in chunk
            ])
            
            # Process through LLM chain
            response = chain.invoke(chunk_str)
            chunk_results = parse_llm_response(response)
            results.extend(chunk_results)
            
            logging.debug(f"Processed chunk {i+1}/{len(chunks)}")
        except Exception as e:
            logging.error(f"Error processing chunk {i+1}: {str(e)}")
            continue
    
    logging.info(f"Completed processing {len(chunks)} chunks")
    return results

def save_results(results: List[Dict], original_contacts: List[Dict], output_file: str):
    """Save results to CSV file."""
    logging.info(f"Saving results to {output_file}")
    try:
        # Create output directory if it doesn't exist
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create lookup dictionary for results
        results_lookup = {r['email']: r for r in results}
        
        fieldnames = list(original_contacts[0].keys()) + ['is_test', 'test_reason']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for contact in original_contacts:
                email = contact['Person - Email - Work']
                result = results_lookup.get(email, {'is_test': False, 'reason': ''})
                
                row = {
                    **contact,
                    'is_test': result['is_test'],
                    'test_reason': result['reason']
                }
                writer.writerow(row)
        
        logging.info("Results saved successfully")
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")
        raise

def main():
    setup_logging()
    logging.info("Starting contact processing")
    
    try:
        # Read input CSV
        contacts = read_csv(INPUT_FILE)
        
        # Split into chunks
        chunks = chunk_contacts(contacts, CHUNK_SIZE)
        
        # Setup LLM chain
        chain = setup_llm_chain()
        
        # Process chunks
        results = process_chunks(chunks, chain)
        
        # Save results
        save_results(results, contacts, OUTPUT_FILE)
        
        logging.info(f"Processing complete. Results saved to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
