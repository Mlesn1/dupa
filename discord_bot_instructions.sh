#!/bin/bash

# Display Discord Bot Structure and Instructions
echo "==================================================================="
echo "                    PLLuM AI Discord Bot                           "
echo "==================================================================="
echo 
echo "Project Structure:"
find . -type f -name "*.py" | sort
echo 
echo "==================================================================="
echo "Running the Discord Bot:"
echo "==================================================================="
echo "1. Configure your Discord Token in .env.discord file"
echo "2. Make sure you have PLLUM_API_KEY set (for Hugging Face)"
echo "3. Run the bot with: ./run_discord_bot.sh"
echo 
echo "Missing required dependencies (discord.py, aiohttp, python-dotenv)?"
echo "You can install them with:"
echo "pip install discord.py aiohttp python-dotenv"
echo 
echo "==================================================================="
echo "Sample Bot Configuration (.env.discord):"
echo "==================================================================="
echo "DISCORD_TOKEN=your_discord_bot_token_here"
echo "COMMAND_PREFIX=!"
echo "HUGGINGFACE_API_KEY=\${PLLUM_API_KEY}"
echo "PLLUM_MODEL_ID=databricks/dbrx-instruct"
echo "PLLUM_MAX_TOKENS=1024"
echo "PLLUM_TEMPERATURE=0.7"
echo "MAX_HISTORY_LENGTH=10"
echo "CONVERSATION_TIMEOUT=600"
echo "RATE_LIMIT_GLOBAL=60"
echo "RATE_LIMIT_USER=10"
echo 
echo "==================================================================="
echo "Bot Features:"
echo "==================================================================="
echo "- AI-Powered Chat using PLLuM AI via Hugging Face"
echo "- Context-Aware Conversations with memory"
echo "- Multiple Command Options (like !ask, !chat, etc.)"
echo "- Rate Limiting to prevent abuse"
echo "- Conversation Cleanup for inactive conversations"
echo 
echo "==================================================================="