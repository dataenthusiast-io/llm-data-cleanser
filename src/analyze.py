import logging
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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from libs.utils import (
    setup_logging, read_csv, chunk_contacts, 
    parse_llm_response, load_prompt
)
from app import get_settings

# Get settings
SETTINGS = get_settings()

def setup_llm_chain(prompt_file: str):
    """Setup LangChain processing chain."""
    logging.info("Setting up LLM chain")
    
    prompt_config = load_prompt(prompt_file)
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_config['system']),
        ("human", "Please analyze these contacts: {contacts}")
    ])

    model = ChatOllama(
        model=SETTINGS["MODEL_NAME"], 
        temperature=SETTINGS["TEMPERATURE"]
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
    logging.info("Starting chunk processing")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        try:
            chunk_str = json.dumps(chunk, indent=2)
            response = chain.invoke(chunk_str)
            chunk_results = parse_llm_response(response)
            results.extend(chunk_results)
            logging.debug(f"Processed chunk {i+1}/{len(chunks)}")
        except Exception as e:
            logging.error(f"Error processing chunk {i+1}: {str(e)}")
            continue
    
    return results

def save_analyzed_results(results: List[Dict], original_contacts: List[Dict], output_file: str):
    """Save all analyzed results to CSV file."""
    logging.info(f"Saving analyzed results to {output_file}")
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        results_lookup = {r['email']: r for r in results}
        fieldnames = list(original_contacts[0].keys()) + ['is_real', 'reason']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for contact in original_contacts:
                email = contact['email']
                result = results_lookup.get(email, {'is_real': True, 'reason': 'No issues found'})
                row = {
                    **contact,
                    'is_real': result['is_real'],
                    'reason': result['reason'] if result['reason'] else 'No issues found'
                }
                writer.writerow(row)
        
        logging.info("Analyzed results saved successfully")
    except Exception as e:
        logging.error(f"Error saving analyzed results: {str(e)}")
        raise

def main():
    setup_logging(SETTINGS["LOG_FILE"])
    logging.info("Starting contact analysis")
    
    try:
        contacts = read_csv(SETTINGS["INPUT_FILE"])
        chunks = chunk_contacts(contacts, SETTINGS["CHUNK_SIZE"])
        chain = setup_llm_chain(SETTINGS["PROMPT_FILE"])
        results = process_chunks(chunks, chain)
        save_analyzed_results(results, contacts, SETTINGS["ANALYZED_FILE"])
        logging.info(f"Analysis complete. Results saved to {SETTINGS['ANALYZED_FILE']}")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 