"""
Run the Discord bot.
"""
import logging
import asyncio
import os
import sys
import time
import json
import aiohttp
from datetime import datetime

# Make the modules importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Function to update bot status via web API
async def async_update_bot_status(is_running=False, error=None):
    """Update bot status through the web interface API asynchronously"""
    try:
        logger.info(f"Updating bot status: running={is_running}, error={error}")
        
        # Prepare data to send
        status_data = {
            "is_running": is_running,
            "error": error
        }
        
        # Send status update to the web interface using aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:5000/api/bot-status",
                json=status_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("Successfully updated bot status")
                else:
                    logger.warning(f"Failed to update status, received status code: {response.status}")
    
    except Exception as e:
        # Don't crash if status update fails - just log it
        logger.error(f"Error updating bot status: {e}")

# Synchronous wrapper for compatibility
def update_bot_status(is_running=False, error=None):
    """Synchronous wrapper for async_update_bot_status"""
    # Create a new event loop for the async call if we're not in an async context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a task
            asyncio.create_task(async_update_bot_status(is_running, error))
        else:
            # If not, run a new event loop
            asyncio.run(async_update_bot_status(is_running, error))
    except Exception as e:
        # If we can't update status, just log the error
        logger.error(f"Error in update_bot_status: {e}")
        # Don't raise the exception - we don't want to crash the bot

# Load environment variables (try both .env and .env.discord)
try:
    from dotenv import load_dotenv
    
    # First try loading from .env.discord
    if os.path.exists('.env.discord'):
        logger.info("Loading environment variables from .env.discord")
        load_dotenv('.env.discord')
    # Then try regular .env
    elif os.path.exists('.env'):
        logger.info("Loading environment variables from .env")
        load_dotenv()
    else:
        logger.warning("No .env or .env.discord file found. Environment variables must be set manually.")
        
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables must be set manually.")

# Check for required environment variables
required_vars = ["DISCORD_TOKEN", "HUGGINGFACE_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

# If HUGGINGFACE_API_KEY is missing but PLLUM_API_KEY exists, use that instead
if "HUGGINGFACE_API_KEY" in missing_vars and os.getenv("PLLUM_API_KEY"):
    logger.info("Using PLLUM_API_KEY as HUGGINGFACE_API_KEY")
    os.environ["HUGGINGFACE_API_KEY"] = os.getenv("PLLUM_API_KEY")
    missing_vars.remove("HUGGINGFACE_API_KEY")

# Report any remaining missing variables
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    for var in missing_vars:
        logger.error(f"Required environment variable {var} is not set.")
    print(f"Error: {error_msg}")
    update_bot_status(is_running=False, error=error_msg)
    sys.exit(1)

# Check if packages are installed
packages_installed = True
try:
    import discord
    import aiohttp
    logger.info("Required packages are installed.")
except ImportError as e:
    packages_installed = False
    logger.error(f"Import error: {e}")
    print(f"Error: Missing required packages. {e}")
    print("Please make sure discord.py and aiohttp are installed.")
    print("Run: pip install discord.py aiohttp")
    
    # Update status to show the error
    update_bot_status(is_running=False, error=f"Import error: {e}")
    sys.exit(1)

# Import bot only if packages are installed
if packages_installed:
    try:
        from bot import initialize_bot
        
        async def start_bot():
            """Start the Discord bot"""
            # Log bot startup message
            logger.info("Starting PLLuM Discord Bot...")
            
            # Update status to running
            update_bot_status(is_running=True, error=None)
            
            # Check if Discord token is available
            discord_token = os.getenv("DISCORD_TOKEN")
            if not discord_token:
                error_msg = "DISCORD_TOKEN not found in environment variables. Bot cannot start."
                logger.error(error_msg)
                print(f"Error: {error_msg}")
                update_bot_status(is_running=False, error=error_msg)
                return
            
            logger.info("Discord token found, initializing bot...")
            
            try:
                # Initialize and run the bot
                bot = initialize_bot()
                await bot.start_bot()
            except Exception as e:
                error_msg = f"Error running bot: {e}"
                logger.error(error_msg, exc_info=True)
                update_bot_status(is_running=False, error=error_msg)
                raise

        # Main entry point
        if __name__ == "__main__":
            try:
                asyncio.run(start_bot())
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                update_bot_status(is_running=False, error="Bot stopped by user")
            except Exception as e:
                logger.error(f"Error running bot: {e}", exc_info=True)
                update_bot_status(is_running=False, error=f"Error running bot: {e}")
                print(f"Error running bot: {e}")
                
    except Exception as e:
        error_msg = f"Error setting up bot: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"Error: {error_msg}")
        update_bot_status(is_running=False, error=error_msg)
        sys.exit(1)