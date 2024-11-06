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
        ("human", "{contacts}")
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

def save_chunk_results(chunk_results: List[Dict], original_contacts: List[Dict], output_file: str, first_chunk: bool = False):
    """Save chunk results to CSV file, either creating new file or appending."""
    logger.info(f"Saving chunk results to {output_file}")
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create a lookup dictionary for the chunk results
        results_lookup = {
            r.get('email'): {
                'is_real': r.get('is_real', True),
                'confidence_score': r.get('confidence_score', 0.5),
                'reason': r.get('reason', 'No issues found')
            } for r in chunk_results if r.get('email')
        }
        
        # Get emails from this chunk's results
        chunk_emails = set(results_lookup.keys())
        
        # Filter original contacts to only those in this chunk
        relevant_contacts = [
            contact for contact in original_contacts 
            if contact['email'] in chunk_emails
        ]
        
        mode = 'w' if first_chunk else 'a'
        fieldnames = list(original_contacts[0].keys()) + ['is_real', 'confidence_score', 'reason']
        
        with open(output_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if first_chunk:
                writer.writeheader()
            
            for contact in relevant_contacts:
                email = contact['email']
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
        
        logger.info(f"Saved results for {len(relevant_contacts)} contacts")
    except Exception as e:
        logger.error(f"Error saving chunk results: {str(e)}")
        raise

def process_chunks(chunks: List[List[Dict]], chain, original_contacts: List[Dict], output_file: str) -> None:
    """Process each chunk through the LLM chain and save results immediately."""
    logger.info("Starting chunk processing")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        try:
            # Filter chunk to only include relevant fields
            filtered_chunk = [{
                'name': contact.get('name', ''),
                'email': contact.get('email', ''),
                'organization': contact.get('organization', '')
            } for contact in chunk]
            
            chunk_str = json.dumps(filtered_chunk, indent=2)
            response = chain.invoke(chunk_str)
            chunk_results = parse_llm_response(response)
            
            # Save results immediately after processing each chunk
            save_chunk_results(
                chunk_results, 
                original_contacts, 
                output_file, 
                first_chunk=(i == 0)
            )
            
            logger.debug(f"Processed and saved chunk {i+1}/{len(chunks)}")
        except Exception as e:
            logger.error(f"Error processing chunk {i+1}: {str(e)}")
            continue

def main():
    setup_logging(LOG_FILE)
    logger.info("Starting contact analysis")
    
    try:
        contacts = read_csv(INPUT_FILE)
        chunks = chunk_contacts(contacts, CHUNK_SIZE)
        chain = setup_llm_chain(PROMPT_FILE)
        # Modified to pass original contacts and output file
        process_chunks(chunks, chain, contacts, ANALYZED_FILE)
        logger.info(f"Analysis complete. Results saved to {ANALYZED_FILE}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 