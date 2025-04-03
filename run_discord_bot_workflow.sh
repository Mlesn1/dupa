#!/bin/bash

echo "Setting up Discord Bot Workflow..."

# Workflow name
WORKFLOW_NAME="Run Discord Bot"

# Create workflow directory structure if it doesn't exist
mkdir -p .replit/workflows

# Create workflow configuration
cat > .replit/workflows/run_discord_bot.json << 'EOF'
{
  "name": "Run Discord Bot",
  "command": "python run_discord_bot.py",
  "restartOn": {
    "files": ["**/*.py"],
    "exclude": ["**/*.pyc", "**/__pycache__/**"]
  }
}
EOF

echo "Workflow '$WORKFLOW_NAME' has been created."
echo "To run the Discord bot, use the workflow panel or restart the repl."