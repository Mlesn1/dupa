"""
Configuration module for the Discord bot.
"""
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import dotenv, but handle the case where it's not installed
try:
    from dotenv import load_dotenv
    
    # Check for .env.discord file first, then fall back to .env
    if os.path.exists('.env.discord'):
        logger.info("Loading environment variables from .env.discord")
        load_dotenv('.env.discord')
    else:
        logger.info("No .env.discord file found, trying .env")
        load_dotenv()
    
except ImportError:
    logger.warning("python-dotenv package not installed. Cannot load .env files.")
    logger.info("Using environment variables directly.")

# Bot configuration
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

# PLLuM AI configuration (via Hugging Face)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("PLLUM_API_KEY")

# Primary model configuration - default model
# Default is set to Mistral-7B-Instruct which is accessible via API and has good capabilities
PLLUM_MODEL_ID = os.getenv("PLLUM_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")  

# Alternative models for different use cases
PLLUM_MODELS = {
    "default": PLLUM_MODEL_ID,
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",  # Fast, versatile model
    "dbrx": "databricks/dbrx-instruct",               # High quality but slower model
    "gemma": "google/gemma-7b-it",                    # Google's instruction-tuned model
    # Original PLLuM models (may not be accessible via API)
    "pllum-small": "CYFRAGOVPL/Llama-PLLuM-8B-instruct",  # Polish model (8B)
    "pllum-large": "CYFRAGOVPL/PLLuM-12B-instruct",       # Polish model (12B)
    "pllum-chat": "CYFRAGOVPL/PLLuM-12B-chat",            # Polish chat model (12B)
    # Fallback models for testing
    "test": "gpt2",                                       # Simple test model
    "distilgpt2": "distilgpt2",                           # Even smaller test model
}

# Use the specified model or fallback if not found
ACTIVE_MODEL_ID = PLLUM_MODELS.get(os.getenv("PLLUM_MODEL_SIZE", "default").lower(), PLLUM_MODEL_ID)

# Generation parameters
PLLUM_MAX_TOKENS = int(os.getenv("PLLUM_MAX_TOKENS", "1024"))
PLLUM_TEMPERATURE = float(os.getenv("PLLUM_TEMPERATURE", "0.7"))

# Conversation settings
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "10"))
CONVERSATION_TIMEOUT = int(os.getenv("CONVERSATION_TIMEOUT", "600"))  # In seconds

# Rate limiting
RATE_LIMIT_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "60"))  # Requests per minute
RATE_LIMIT_USER = int(os.getenv("RATE_LIMIT_USER", "10"))  # Requests per minute per user

# Bot response messages
BOT_THINKING_MESSAGE = "🤔 Thinking..."
BOT_ERROR_MESSAGE = "❌ Sorry, I encountered an error. Please try again later."
BOT_RATE_LIMITED_MESSAGE = "⏳ You're sending too many requests. Please wait a moment before trying again."
