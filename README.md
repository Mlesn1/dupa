# PLLuM AI Discord Bot

A Discord bot that leverages PLLuM AI to respond to user messages and commands, providing interactive and context-aware conversations.

## Features

- 🤖 **AI-Powered Chat** - Chat with the PLLuM AI through Discord using the power of the Hugging Face API
- 💬 **Context-Aware Conversations** - The bot remembers your conversation history for more coherent responses
- 🌐 **Multi-Language Support** - Automatically detects and responds in Polish or English based on user's input
- ⚙️ **Multiple Command Options** - Use single commands or engage in full conversations with the bot
- ⏲️ **Rate Limiting** - Prevents abuse with customizable rate limits per user and globally
- 🧹 **Automatic Cleanup** - Inactive conversations are automatically cleaned up to save resources

## Bot Commands

- `!help` - Shows the help message with all available commands
- `!ask <question>` - Ask PLLuM AI a one-time question
- `!chat` - Start a conversation with PLLuM AI
- `!end` - End your current conversation
- `!ping` - Check the bot's latency
- `!info` - Get information about the bot

## Getting Started

### Prerequisites

- Python 3.8+
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Hugging Face API Key (or PLLUM_API_KEY)

### Required Packages

```bash
pip install discord.py aiohttp python-dotenv
```

### Configuration

Create a `.env.discord` file in the root directory with the following content:

```
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!

# PLLuM AI Configuration
HUGGINGFACE_API_KEY=${PLLUM_API_KEY}
PLLUM_MODEL_ID=CYFRAGOVPL/PLLuM
PLLUM_MAX_TOKENS=1024
PLLUM_TEMPERATURE=0.7

# Conversation Settings
MAX_HISTORY_LENGTH=10
CONVERSATION_TIMEOUT=600

# Rate Limiting
RATE_LIMIT_GLOBAL=60
RATE_LIMIT_USER=10
```

Replace `your_discord_bot_token_here` with your actual Discord bot token.

### Running the Bot

#### Using the run script (recommended)

```bash
# Make the script executable
chmod +x run_discord_bot.sh

# Run the script
./run_discord_bot.sh
```

#### Manual execution

```bash
python run_discord_bot.py
```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Enable the following Privileged Gateway Intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
4. Generate a bot token and add it to your `.env.discord` file
5. Use the OAuth2 URL Generator to generate an invite link with the `bot` scope and appropriate permissions
6. Invite the bot to your server

## Project Structure

```
.
├── bot.py                  # Main bot initialization and configuration
├── config.py               # Configuration loading and defaults
├── main.py                 # Web interface for the bot
├── run_discord_bot.py      # Entry point for running the bot
├── run_discord_bot.sh      # Shell script for easy execution
├── cogs/
│   ├── commands.py         # Bot commands implementation
│   └── conversations.py    # Conversation handling and memory
└── utils/
    ├── language_utils.py   # Language detection and multi-language support
    ├── logger.py           # Logging configuration
    ├── pllum_api.py        # PLLuM AI Hugging Face API integration
    └── rate_limiter.py     # Rate limiting functionality
```

## Customization

### Changing the AI Model

You can change the AI model by modifying the `PLLUM_MODEL_ID` in your `.env.discord` file. 

**Recommended models:**
- `mistralai/Mistral-7B-Instruct-v0.2` - A smaller, faster model that works well for most use cases
- `databricks/dbrx-instruct` - A more powerful but resource-intensive model

The default is set to the Mistral model which has better performance on Replit.

### Language Support

The bot is designed to automatically detect and respond in Polish or English based on the language of the user's input. This is achieved through:

- Automatic language detection of user queries
- Adding language-specific instructions to the model prompts
- Support for special Polish characters and common phrases

You can modify the language detection patterns in `utils/language_utils.py` to improve accuracy or add support for additional languages.

### Adjusting Rate Limits

Modify the `RATE_LIMIT_GLOBAL` and `RATE_LIMIT_USER` values in your `.env.discord` file to adjust the rate limits.

### Conversation Settings

- `MAX_HISTORY_LENGTH`: Number of messages to remember in conversation history
- `CONVERSATION_TIMEOUT`: Time in seconds before a conversation is considered inactive and cleaned up

## License

This project is open source and available under the MIT License.

## Note on PLLuM AI

This bot uses the PLLuM AI (Programmable Large Language Model) via the Hugging Face API. You need a valid Hugging Face API token to use this functionality. The bot will look for a `PLLUM_API_KEY` environment variable if `HUGGINGFACE_API_KEY` is not explicitly set.