"""
Test environment variables configuration for the Discord bot.
"""
import os

# Try to import dotenv, but handle the case where it's not installed
try:
    from dotenv import load_dotenv
    
    # Load environment variables
    print("Looking for environment files...")
    if os.path.exists('.env.discord'):
        print("Found .env.discord file")
        load_dotenv('.env.discord')
    else:
        print("No .env.discord file found, checking for .env")
        if os.path.exists('.env'):
            print("Found .env file")
            load_dotenv()
        else:
            print("No .env file found either")
except ImportError:
    print("Warning: python-dotenv package not installed. Cannot load .env files.")
    print("Checking for environment variables directly...")

# Print configuration values
print("\n=== Discord Bot Configuration ===")
print(f"Discord Token Present: {'Yes' if os.getenv('DISCORD_TOKEN') else 'No'}")
print(f"Command Prefix: {os.getenv('COMMAND_PREFIX', '!')}")
print(f"Hugging Face API Key Present: {'Yes' if os.getenv('HUGGINGFACE_API_KEY') else 'No'}")
print(f"PLLuM API Key Present: {'Yes' if os.getenv('PLLUM_API_KEY') else 'No'}")
print(f"PLLuM Model ID: {os.getenv('PLLUM_MODEL_ID', 'databricks/dbrx-instruct')}")
print(f"Max Tokens: {os.getenv('PLLUM_MAX_TOKENS', '1024')}")
print(f"Temperature: {os.getenv('PLLUM_TEMPERATURE', '0.7')}")
print(f"Max History Length: {os.getenv('MAX_HISTORY_LENGTH', '10')}")
print(f"Conversation Timeout: {os.getenv('CONVERSATION_TIMEOUT', '600')} seconds")
print(f"Rate Limit Global: {os.getenv('RATE_LIMIT_GLOBAL', '60')} requests/minute")
print(f"Rate Limit User: {os.getenv('RATE_LIMIT_USER', '10')} requests/minute")