"""
PLLuM AI API integration module using Hugging Face.
"""
import aiohttp
import logging
import os
import config
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

async def get_pllum_response(prompt: str, model_id: Optional[str] = None, max_tokens: Optional[int] = None, 
                     temperature: Optional[float] = None, guild_id: Optional[str] = None) -> str:
    """
    Get a response from the PLLuM AI via Hugging Face API.
    
    Args:
        prompt: The input prompt to send to the API
        model_id: Specific model to use (defaults to ACTIVE_MODEL_ID from config)
        max_tokens: Maximum tokens to generate (uses config default if not specified)
        temperature: Temperature parameter for generation (uses config default if not specified)
        guild_id: Optional Discord server (guild) ID to get custom model settings
    
    Returns:
        The generated text response
    
    Raises:
        Exception: If the API request fails
    """
    # Check for API key
    api_key = config.HUGGINGFACE_API_KEY
    
    if not api_key:
        logger.warning("No API key found. Running in limited mode with mock responses.")
        # Provide a mock response for testing purposes
        if "Polish" in prompt or any(c in prompt for c in "ąćęłńóśźż"):
            return "Przepraszam, ale działam w trybie testowym bez dostępu do API. Potrzebuję klucza PLLUM_API_KEY, aby generować prawdziwe odpowiedzi."
        else:
            return "I'm sorry, but I'm running in test mode without API access. I need a PLLUM_API_KEY to generate real responses."
    
    # Use provided values or defaults from config
    max_tokens = max_tokens or config.PLLUM_MAX_TOKENS
    temperature = temperature or config.PLLUM_TEMPERATURE
    
    # Use custom server model if guild_id is provided
    if guild_id and not model_id:
        # Get the admin cog from the bot to check for server-specific model
        import sys
        import importlib
        
        if 'bot' in sys.modules:
            # Try to get the active bot instance if available
            bot_module = sys.modules['bot']
            if hasattr(bot_module, 'active_bot_instance') and bot_module.active_bot_instance:
                bot = bot_module.active_bot_instance
                admin_cog = bot.bot.get_cog("Admin")
                if admin_cog:
                    custom_model = admin_cog.get_model(guild_id)
                    if custom_model:
                        model_id = custom_model
                        logger.info(f"Using custom model for guild {guild_id}: {model_id}")
    
    # Fall back to default model if still not set
    model_id = model_id or config.ACTIVE_MODEL_ID
    
    logger.info(f"Using model: {model_id}")
    
    # Hugging Face Inference API endpoint - explicitly using text-generation task
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    task_url = f"https://api-inference.huggingface.co/pipeline/text-generation/models/{model_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Set format based on model type
    if "Llama-PLLuM" in model_id:
        # Format for Llama instruction-tuned models
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }
    elif "PLLuM" in model_id and "instruct" in model_id:
        # Format for PLLuM instruction models (non-Llama)
        formatted_prompt = f"Poniżej znajduje się instrukcja, która opisuje zadanie. Napisz odpowiedź, która odpowiednio odnosi się do instrukcji.\n\n### Instrukcja:\n{prompt}\n\n### Odpowiedź:"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }
    elif "PLLuM" in model_id and "chat" in model_id:
        # Format for PLLuM chat models
        formatted_prompt = f"<human>: {prompt}\n<assistant>:"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }
    elif "Mistral" in model_id:
        # Format for Mistral models
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }
    else:
        # Standard formatting for other models
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try with regular endpoint first
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Standard endpoint error: {response.status} - {error_text}")
                    
                    # Try with explicit text-generation task endpoint
                    logger.info(f"Trying with text-generation task endpoint...")
                    try:
                        async with session.post(task_url, json=payload, headers=headers) as task_response:
                            if task_response.status != 200:
                                task_error = await task_response.text()
                                logger.error(f"Task endpoint error: {task_response.status} - {task_error}")
                                
                                # Check for specific error conditions
                                if "Model models/" in task_error and "does not exist" in task_error:
                                    raise Exception(f"Model '{model_id}' is not available via the Hugging Face API. "
                                                    f"This model might be private, too large, or require special access.")
                                elif "Task not found" in error_text:
                                    raise Exception(f"Task 'text-generation' is not available for model '{model_id}'. "
                                                    f"This model might require a different task type or special configuration.")
                                else:
                                    raise Exception(f"Hugging Face API error: {task_response.status}")
                            
                            data = await task_response.json()
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error accessing task endpoint: {str(e)}")
                        raise Exception(f"Cannot access PLLuM API: Network error or service unavailable")
                else:
                    data = await response.json()
                
                # Handle various response formats from Hugging Face
                if isinstance(data, list) and len(data) > 0:
                    if "generated_text" in data[0]:
                        return data[0]["generated_text"].strip()
                    elif isinstance(data[0], str):
                        return data[0].strip()
                elif isinstance(data, dict):
                    if "generated_text" in data:
                        return data["generated_text"].strip()
                    elif "text" in data:
                        return data["text"].strip()
                
                # If we get here, the response format was unexpected
                logger.error(f"Unexpected Hugging Face API response format: {data}")
                raise Exception("Unexpected Hugging Face API response format")
    
    except aiohttp.ClientError as e:
        logger.error(f"Network error accessing Hugging Face API: {str(e)}")
        raise Exception(f"Network error accessing Hugging Face API: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting PLLuM response: {str(e)}", exc_info=True)
        raise
