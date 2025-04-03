"""
Language utilities for handling different languages in the bot.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Simple language detection patterns
POLISH_PATTERNS = [
    r'\bże\b', r'\bjest\b', r'\bsię\b', r'\bjak\b', r'\bw\b', r'\bna\b', r'\bco\b', r'\bto\b',
    r'\bnie\b', r'\bdo\b', r'\bz\b', r'\ba\b', r'\bo\b', r'\bprzez\b', r'\bpo\b', r'\bjeśli\b',
    r'\bczy\b', r'\bmożesz\b', r'\bmoże\b', r'\bjesteś\b', r'\bmam\b', r'\bmi\b', r'\bci\b',
    r'\bdziękuję\b', r'\bproszę\b', r'\bpomóż\b', r'\bdaj\b', r'\bpokaż\b', r'\bpowiedz\b',
    r'\bwyjaśnij\b', r'\bopowiedz\b', r'\bmów\b', r'\bpisz\b', r'\bczytaj\b', r'\butwórz\b',
    r'\bzrób\b', r'\bmogę\b', r'\bchcę\b', r'\bmusimy\b', r'\błudzie\b', r'\bświat\b',
    r'\bczas\b', r'\broku\b', r'\błat\b', r'\bdzień\b', r'\bgodzin\b',
    r'[ąćęłńóśźż]'  # Polish diacritics
]

POLISH_GREETING_PATTERNS = [
    r'\bcześć\b', r'\bwitaj\b', r'\bhej\b', r'\bdzień dobry\b', r'\bdobry wieczór\b', 
    r'\bsiema\b', r'\bcz\b', r'\bwitam\b', r'\bhejka\b', r'\bjak się masz\b'
]

def is_polish(text):
    """
    Detect if the text is likely in Polish based on common word patterns
    and Polish-specific characters.

    Args:
        text: The text to check

    Returns:
        True if the text is likely Polish, False otherwise
    """
    # Convert to lowercase
    text_lower = text.lower()
    
    # Check for Polish diacritics and common Polish words
    for pattern in POLISH_PATTERNS:
        if re.search(pattern, text_lower):
            logger.debug(f"Detected Polish language pattern: {pattern}")
            return True
            
    # Check if there are more Polish greeting patterns than English ones
    polish_greetings = sum(1 for pattern in POLISH_GREETING_PATTERNS if re.search(pattern, text_lower))
    english_greetings = sum(1 for pattern in ['hello', 'hi', 'hey', 'good morning', 'good evening'] 
                            if pattern in text_lower)
    
    if polish_greetings > english_greetings:
        return True
        
    return False

def format_prompt_for_translation(text, target_language="Polish"):
    """
    Format a prompt to ask the model to respond in a specific language

    Args:
        text: The original text prompt
        target_language: The language to request the model to respond in

    Returns:
        A formatted prompt that includes the translation request
    """
    return f"{text}\n\nPlease respond in {target_language}."

def get_language_instructions(text):
    """
    Get language-specific instructions based on detected language

    Args:
        text: The input text to analyze

    Returns:
        Instructions string to add to the prompt for the AI
    """
    if is_polish(text):
        return "Proszę odpowiadaj po polsku."
    else:
        return "Please respond in English."