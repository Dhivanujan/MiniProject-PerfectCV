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
_spacy_warning_shown = False  # Track if we've already shown the warning


def get_nlp():
    """Get spaCy NLP instance with safe lazy loading.
    
    Returns spaCy nlp object or None if unavailable.
    This is the recommended way to access spaCy in the codebase.
    """
    global _nlp, _spacy_warning_shown
    
    # Check if spaCy is installed
    if spacy is None:
        if not _spacy_warning_shown:
            logger.warning("⚠ spaCy not installed. NLP features disabled. Install with: pip install spacy && python -m spacy download en_core_web_sm")
            _spacy_warning_shown = True
        return None
    
    # Return cached model if available
    if _nlp is not None:
        return _nlp
    
    # Try to load the model
    try:
        _nlp = spacy.load("en_core_web_sm")
        logger.info("✓ Loaded spaCy model: en_core_web_sm")
        return _nlp
    except OSError:
        # Model not downloaded
        if not _spacy_warning_shown:
            logger.warning("⚠ spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            _spacy_warning_shown = True
        try:
            # Fallback to blank model (no entity recognition, but doesn't crash)
            _nlp = spacy.blank("en")
            logger.info("✓ Using blank spaCy model (limited features)")
            return _nlp
        except Exception:
            return None
    except Exception as e:
        if not _spacy_warning_shown:
            logger.error(f"❌ Failed to load spaCy: {e}")
            _spacy_warning_shown = True
        return None


def is_spacy_available() -> bool:
    """Check if spaCy is available without loading it.
    
    Returns:
        True if spaCy can be used, False otherwise
    """
    return spacy is not None


def load_spacy_model():
    """Load the spaCy model, downloading it if necessary (not possible in this env, but good practice).
    
    DEPRECATED: Use get_nlp() instead for safer loading.
    """
    return get_nlp()

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
