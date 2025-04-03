"""
Test the PLLuM API connection.
"""
import os
import asyncio

# Try to import dotenv, but handle the case where it's not installed
try:
    from dotenv import load_dotenv
    
    # Load environment variables
    if os.path.exists('.env.discord'):
        load_dotenv('.env.discord')
    else:
        load_dotenv()
except ImportError:
    print("Warning: python-dotenv package not installed. Cannot load .env files.")
    print("Checking for environment variables directly...")

# Import PLLuM API function
from utils.pllum_api import get_pllum_response

async def test_pllum_api():
    print("Testing PLLuM API connection...")
    
    # Check if API key is present
    if not os.getenv('HUGGINGFACE_API_KEY') and not os.getenv('PLLUM_API_KEY'):
        print("Error: No API key found. Please set HUGGINGFACE_API_KEY or PLLUM_API_KEY in your environment variables.")
        return
    
    # If HUGGINGFACE_API_KEY is not set but PLLUM_API_KEY is, use PLLUM_API_KEY
    if not os.getenv('HUGGINGFACE_API_KEY') and os.getenv('PLLUM_API_KEY'):
        print("Using PLLUM_API_KEY as HUGGINGFACE_API_KEY")
        api_key = os.getenv('PLLUM_API_KEY')
        if api_key is not None:
            os.environ['HUGGINGFACE_API_KEY'] = api_key
    
    try:
        # Get the current model ID from environment variables or default
        model_id = os.getenv('PLLUM_MODEL_ID', 'CYFRAGOVPL/PLLuM-12B-instruct')
        print(f"Using model: {model_id}")
        
        # For Polish models, use a Polish query
        if "CYFRAGOVPL" in model_id or "polish" in model_id.lower():
            query = "Cześć, co możesz mi powiedzieć o botach Discord?"
            print(f"Sending Polish test query: {query}")
        else:
            query = "Hello, what can you tell me about Discord bots?"
            print(f"Sending English test query: {query}")
            
        response = await get_pllum_response(query)
        print("\nAPI Response:")
        print(response)
        print("\nPLLuM API connection successful!")
    except Exception as e:
        print(f"Error connecting to PLLuM API: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your PLLUM_API_KEY or HUGGINGFACE_API_KEY environment variable has a valid API key")
        print("2. The model may need special access permissions on Hugging Face")
        print("3. The model might be too large to use directly via the API")
        print("   - PLLuM-12B models are 24GB and may exceed Hugging Face's free tier limits")
        print("   - Llama-PLLuM-70B models are 140GB and definitely exceed API limits")
        print("4. Check if you need a Hugging Face Pro account for this model")
        print("5. Try a different model:")
        print("   - For testing: try a smaller, open-source model like 'gpt2' or 'distilgpt2'")
        print("   - For Polish: search for smaller Polish language models or fine-tunes")
        print("6. The model might need to be accessed via downloadable weights not the API")
        print("   - Large models often need to be run locally with appropriate hardware")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_pllum_api())