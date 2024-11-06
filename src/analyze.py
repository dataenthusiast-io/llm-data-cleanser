from typing import List, Dict
import json
from tqdm import tqdm
import csv
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Constants
LOG_FILE = str(project_root / "logs/app.log")
INPUT_FILE = str(project_root / "input/contacts.csv")
ANALYZED_FILE = str(project_root / "output/analyzed_contacts.csv")
CLEANED_FILE = str(project_root / "output/cleaned_contacts.csv")
PROMPT_FILE = str(Path(__file__).parent / "prompts/analyze.yaml")

# Environment variables
MODEL_NAME = os.getenv("MODEL_NAME")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))

from libs.utils import (
    setup_logging, read_csv, chunk_contacts, 
    parse_llm_response, load_prompt, logger
)

def setup_llm_chain(prompt_file: str):
    """Setup LangChain processing chain."""
    logger.info("Setting up LLM chain")
    
    prompt_config = load_prompt(prompt_file)
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_config['system']),
        ("human", "Please analyze these contacts: {contacts}")
    ])

    model = ChatOllama(
        model=MODEL_NAME, 
        temperature=TEMPERATURE
    )
    
    chain = (
        {"contacts": RunnablePassthrough()} 
        | prompt 
        | model 
        | StrOutputParser()
    )
    
    return chain

def process_chunks(chunks: List[List[Dict]], chain) -> List[Dict]:
    """Process each chunk through the LLM chain."""
    results = []
    logger.info("Starting chunk processing")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        try:
            chunk_str = json.dumps(chunk, indent=2)
            response = chain.invoke(chunk_str)
            chunk_results = parse_llm_response(response)
            results.extend(chunk_results)
            logger.debug(f"Processed chunk {i+1}/{len(chunks)}")
        except Exception as e:
            logger.error(f"Error processing chunk {i+1}: {str(e)}")
            continue
    
    return results

def save_analyzed_results(results: List[Dict], original_contacts: List[Dict], output_file: str):
    """Save all analyzed results to CSV file."""
    logger.info(f"Saving analyzed results to {output_file}")
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        # Create a lookup dictionary with default values for missing results
        results_lookup = {}
        for r in results:
            email = r.get('email')
            if email:
                results_lookup[email] = {
                    'is_real': r.get('is_real', True),  # Default to True if missing
                    'confidence_score': r.get('confidence_score', 0.5),
                    'reason': r.get('reason', 'No issues found')
                }
        
        fieldnames = list(original_contacts[0].keys()) + ['is_real', 'confidence_score', 'reason']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for contact in original_contacts:
                email = contact['email']
                # Get result with defaults if email not found
                result = results_lookup.get(email, {
                    'is_real': True,
                    'confidence_score': 0.5,
                    'reason': 'No analysis available'
                })
                
                row = {
                    **contact,
                    'is_real': result['is_real'],
                    'confidence_score': result['confidence_score'],
                    'reason': result['reason']
                }
                writer.writerow(row)
        
        logger.info("Analyzed results saved successfully")
    except Exception as e:
        logger.error(f"Error saving analyzed results: {str(e)}")
        raise

def main():
    setup_logging(LOG_FILE)
    logger.info("Starting contact analysis")
    
    try:
        contacts = read_csv(INPUT_FILE)
        chunks = chunk_contacts(contacts, CHUNK_SIZE)
        chain = setup_llm_chain(PROMPT_FILE)
        results = process_chunks(chunks, chain)
        save_analyzed_results(results, contacts, ANALYZED_FILE)
        logger.info(f"Analysis complete. Results saved to {ANALYZED_FILE}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 