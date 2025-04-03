#!/bin/bash

echo "==================================================================="
echo "                Starting PLLuM AI Discord Bot                      "
echo "==================================================================="

# Check for required environment files
if [ ! -f .env.discord ] && [ ! -f .env ]; then
    echo "Warning: No .env.discord or .env file found."
    echo "Creating a sample .env.discord file..."
    
    # Create a sample .env.discord file if it doesn't exist
    cat > .env.discord << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
COMMAND_PREFIX=!

# PLLuM AI Configuration
HUGGINGFACE_API_KEY=\${PLLUM_API_KEY}
PLLUM_MODEL_ID=CYFRAGOVPL/PLLuM
PLLUM_MAX_TOKENS=1024
PLLUM_TEMPERATURE=0.7

# Conversation Settings
MAX_HISTORY_LENGTH=10
CONVERSATION_TIMEOUT=600

# Rate Limiting
RATE_LIMIT_GLOBAL=60
RATE_LIMIT_USER=10
EOF
    
    echo "Sample .env.discord file created. Please edit it with your Discord bot token."
    echo "Hint: If you already have a PLLUM_API_KEY set, it will be used as the Hugging Face API key."
    echo "==================================================================="
    exit 1
fi

# Check if PLLUM_API_KEY is set
if [ -z "$PLLUM_API_KEY" ]; then
    echo "Warning: PLLUM_API_KEY environment variable is not set."
    echo "This API key is needed for the PLLuM AI functionality."
    echo "Please set it or add it to your .env or .env.discord file."
    echo "==================================================================="
fi

# Run the Discord bot
echo "Starting the Discord bot..."
python run_discord_bot.py