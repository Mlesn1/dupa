# PLLuM AI Discord Bot - Detailed Guide

This document provides detailed instructions for setting up and running the PLLuM AI Discord bot.

## Table of Contents

1. [Discord Bot Setup](#discord-bot-setup)
2. [Hugging Face API Setup](#hugging-face-api-setup)
3. [Bot Installation](#bot-installation)
4. [Configuration Options](#configuration-options)
5. [Running the Bot](#running-the-bot)
6. [Using the Bot](#using-the-bot)
7. [Troubleshooting](#troubleshooting)

## Discord Bot Setup

To use this bot, you first need to create a Discord application and bot user:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "PLLuM AI Bot")
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "Token" section, click "Reset Token" to generate a new token (save this token for later)
5. Under "Privileged Gateway Intents", enable ALL THREE options:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
6. Navigate to the "OAuth2" tab, then "URL Generator"
7. Select the scopes: `bot` and `applications.commands`
8. For bot permissions, select at minimum:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Application Commands
9. Copy the generated URL and open it in a browser to invite the bot to your server

## Hugging Face API Setup

The bot uses the Hugging Face API to access PLLuM AI models:

1. Create a [Hugging Face account](https://huggingface.co/join) if you don't have one
2. Go to your [Profile Settings](https://huggingface.co/settings/tokens)
3. Create a new API token with "Read" access
4. Save this token as your `HUGGINGFACE_API_KEY` or `PLLUM_API_KEY`

### Model Selection

The bot is configured by default to use `mistralai/Mistral-7B-Instruct-v0.2`, which is a fast and capable model. Other models that work well include:

- `databricks/dbrx-instruct` - For higher quality responses (but slower performance)
- `google/gemma-7b-it` - Another fast and solid model
- For additional options, see [Hugging Face Models](https://huggingface.co/models)

Note: The original intention was to use `CYFRAGOVPL/PLLuM` models (Polish language models), but these are currently not accessible through the Hugging Face API directly.

### Language Support

The bot features automatic language detection to provide responses in the appropriate language:

- Automatically detects Polish input using common phrases and special characters (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- Instructs the model to respond in Polish when Polish is detected
- Falls back to English for all other inputs
- Maintains language consistency throughout conversations

This allows users to interact with the bot in both Polish and English without needing to specify their language manually.

## Bot Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Required Libraries

Install the required Python libraries:

```bash
pip install discord.py aiohttp python-dotenv
```

## Configuration Options

The bot is configured using environment variables, which can be set in a `.env.discord` file. Here's a complete list of available options:

### Required Settings:

- `DISCORD_TOKEN`: Your Discord bot token from the Developer Portal
- `HUGGINGFACE_API_KEY` or `PLLUM_API_KEY`: Your Hugging Face API token

### Optional Settings:

- `COMMAND_PREFIX`: The prefix for bot commands (default: `!`)
- `PLLUM_MODEL_ID`: The Hugging Face model ID to use (default: `mistralai/Mistral-7B-Instruct-v0.2`)
- `PLLUM_MAX_TOKENS`: Maximum tokens to generate in responses (default: `1024`)
- `PLLUM_TEMPERATURE`: Temperature parameter for generation (default: `0.7`)
- `MAX_HISTORY_LENGTH`: Number of messages to remember in a conversation (default: `10`)
- `CONVERSATION_TIMEOUT`: Seconds before a conversation is considered inactive (default: `600`)
- `RATE_LIMIT_GLOBAL`: Maximum requests per minute for all users (default: `60`)
- `RATE_LIMIT_USER`: Maximum requests per minute per user (default: `10`)

### Server-Specific Settings

Administrators can customize the following settings for their server:

- **Custom Prefix**: Change the command prefix for your server
- **Allowed Channels**: Restrict the bot to respond only in specific channels
- **Allowed Roles**: Restrict bot usage to specific roles
- **Custom AI Model**: Select a different AI model for your server

These settings are managed through the admin commands and are stored persistently per server.

### Sample Configuration File

Create a file named `.env.discord` in the project root with these settings:

```
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!

# PLLuM AI Configuration
HUGGINGFACE_API_KEY=${PLLUM_API_KEY}
PLLUM_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
PLLUM_MAX_TOKENS=1024
PLLUM_TEMPERATURE=0.7

# Conversation Settings
MAX_HISTORY_LENGTH=10
CONVERSATION_TIMEOUT=600

# Rate Limiting
RATE_LIMIT_GLOBAL=60
RATE_LIMIT_USER=10
```

## Running the Bot

### Using the Run Script

The easiest way to run the bot is to use the provided shell script:

```bash
chmod +x run_discord_bot.sh
./run_discord_bot.sh
```

The script will check for necessary configuration files and create them if they don't exist.

### Manual Execution

You can also run the bot directly with Python:

```bash
python run_discord_bot.py
```

## Using the Bot

Once the bot is running and has joined your server, you can interact with it using the following commands:

### Basic Commands

- `!help` - Shows all available commands
- `!ask <question>` - Ask a one-time question to PLLuM AI
- `!ping` - Check the bot's latency
- `!info` - Display information about the bot

### Conversation Commands

- `!chat` - Start a new conversation with PLLuM AI
- `!end` - End your current conversation

### Admin Commands

These commands are only available to server administrators and owners:

- `!admin channels` - Manage channels where the bot can respond
  - `!admin channels add #channel` - Allow bot to respond in a channel
  - `!admin channels remove #channel` - Prevent bot from responding in a channel
  - `!admin channels list` - Show all allowed channels
  - `!admin channels reset` - Allow bot to respond in all channels
  
- `!admin roles` - Manage roles that can use the bot
  - `!admin roles add @role` - Allow a role to use the bot
  - `!admin roles remove @role` - Prevent a role from using the bot
  - `!admin roles list` - Show all allowed roles
  - `!admin roles reset` - Allow all roles to use the bot
  
- `!admin prefix <prefix>` - Set a custom command prefix for your server
  - Example: `!admin prefix $` will change the prefix to `$`
  
- `!admin model <model_key>` - Set the AI model for your server
  - Example: `!admin model dbrx` will use the dbrx-instruct model
  - Use `!admin model` without parameter to see all available models
  
- `!admin settings` - View current server settings
- `!admin reset` - Reset all server settings to defaults

### Conversation Interaction

Once you've started a conversation with `!chat`, you can continue the conversation by:

1. **Mentioning the bot**: Type `@PLLuMBot your message here`
2. **Replying to the bot's messages**: Use Discord's reply feature on any of the bot's messages

The bot will remember the context of your conversation until:
- You manually end it with `!end`
- The conversation times out after inactivity (default 10 minutes)

## Troubleshooting

### Common Issues

1. **Bot doesn't respond to commands**
   - Check that you have the correct bot token in your `.env.discord` file
   - Ensure the bot has proper permissions in your Discord server
   - Make sure all Gateway Intents are enabled in the Discord Developer Portal
   - If using a custom prefix, make sure you're using the correct one

2. **Bot starts but doesn't generate AI responses**
   - Verify your Hugging Face API key is correct
   - Check your internet connection
   - Look for error messages in the console logs
   - The model selected might not be available through the API - try a different one

3. **Bot doesn't respond in certain channels or to certain users**
   - An administrator might have restricted the bot to specific channels or roles
   - Use `!admin settings` to check current permissions (if you're an admin)
   - Ask a server administrator to check the bot's configuration

4. **Rate limit errors**
   - Adjust the rate limit settings in your `.env.discord` file
   - Wait a minute and try again

5. **"Import error" messages**
   - Make sure all required packages are installed:
     ```bash
     pip install discord.py aiohttp python-dotenv
     ```

6. **Server settings not persisting after bot restart**
   - Check that the bot has write permissions in its directory
   - The `server_settings.json` file might be corrupted - delete it and reconfigure

### Getting Help

If you encounter issues not covered here, check:
- The Discord.py documentation: https://discordpy.readthedocs.io/
- The Hugging Face API documentation: https://huggingface.co/docs/api-inference/