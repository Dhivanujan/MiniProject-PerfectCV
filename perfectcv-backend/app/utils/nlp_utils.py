try:
    import spacy
except ImportError:
    spacy = None

import logging
import re
from typing import List, Dict, Tuple, Set

logger = logging.getLogger(__name__)

# Global variable to cache the model
_nlp = None

def load_spacy_model():
    """Load the spaCy model, downloading it if necessary (not possible in this env, but good practice)."""
    global _nlp
    if spacy is None:
        logger.warning("Spacy not installed. NLP features will be disabled.")
        return None

    if _nlp is not None:
        return _nlp
    
    try:
        _nlp = spacy.load("en_core_web_sm")
        logger.info("Loaded en_core_web_sm model.")
    except OSError:
        logger.warning("Spacy model 'en_core_web_sm' not found. Please run `python -m spacy download en_core_web_sm`.")
        try:
            # Fallback to a blank English model if the specific one isn't found
            _nlp = spacy.blank("en")
        except Exception:
            _nlp = None
    except Exception as e:
        logger.error(f"Failed to load spacy: {e}")
        _nlp = None
    
    return _nlp

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities like PERSON, ORG, GPE, DATE."""
    nlp = load_spacy_model()
    
    entities = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],
        "DATE": [],
        "EDU": [] # Custom label if we had a trained model
    }

    if nlp is None:
        return entities
    
    try:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
    except Exception as e:
        logger.warning(f"NLP entity extraction failed: {e}")
            
    return entities

def extract_noun_chunks(text: str) -> List[str]:
    """Extract noun chunks for skill matching."""
    nlp = load_spacy_model()
    if nlp is None:
        return []
        
    try:
        doc = nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]
    except Exception:
        return []

def clean_text_nlp(text: str) -> str:
    """Use NLP to clean text (e.g. remove stop words - optional, usually we want full text)."""
    # For CVs, we usually want to keep the text as is, just normalized.
    # This function is a placeholder for more advanced cleaning if needed.
    return text.strip()

def classify_header_nlp(text: str, candidate_headers: Dict[str, List[str]]) -> str:
    """
    Classify a line of text as a section header using NLP similarity.
    
    Args:
        text: The line to classify.
        candidate_headers: A dictionary mapping section keys (e.g., 'experience') to lists of keywords.
        
    Returns:
        The section key if a match is found, else None.
    """
    # Direct keyword match is faster and often more accurate for simple headers
    # We do this first regardless of NLP availability
    text_lower = text.lower().strip()
    for section, keywords in candidate_headers.items():
        for keyword in keywords:
            if text_lower == keyword or text_lower.startswith(keyword + ":"):
                return section

    nlp = load_spacy_model()
    if nlp is None:
        return None

    try:
        doc = nlp(text.lower())
        
        # If the text is too long, it's unlikely to be a header
        if len(doc) > 5: 
            return None
    except Exception:
        pass

    # If we had word vectors loaded (en_core_web_md/lg), we could use similarity.
    # en_core_web_sm doesn't have real vectors, so similarity is not effective.
    # We will stick to robust keyword matching here, but structure it for NLP expansion.
    
    return None
