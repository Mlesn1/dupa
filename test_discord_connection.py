"""
Test the Discord bot connection without fully starting the bot.
"""
import os
import asyncio
import sys

# Try to import needed packages but handle the case where they're not installed
try:
    import discord
except ImportError:
    print("Error: discord.py package not installed.")
    print("Please install it with: pip install discord.py")
    sys.exit(1)

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

async def test_discord_connection():
    print("Testing Discord connection...")
    
    # Get Discord token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
        print("Please make sure you've created a .env.discord file with your Discord bot token")
        return
    
    # Create a test client
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"Successfully connected to Discord as {client.user}")
        print(f"Bot is in {len(client.guilds)} servers")
        if len(client.guilds) > 0:
            print("\nServers the bot is in:")
            for guild in client.guilds:
                print(f"- {guild.name} (ID: {guild.id})")
        print("\nDiscord connection test successful!")
        await client.close()
    
    try:
        print("Attempting to connect to Discord...")
        await client.start(token)
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token. Please check your DISCORD_TOKEN in .env.discord")
    except Exception as e:
        print(f"Error connecting to Discord: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_discord_connection())