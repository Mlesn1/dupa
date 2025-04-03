"""
Bot initialization and configuration module.
"""
import os
import logging
import discord
from discord.ext import commands
import config

# Import cogs
from cogs.commands import CommandsCog
from cogs.conversations import ConversationsCog
from cogs.admin import AdminCog

logger = logging.getLogger(__name__)

class PLLuMBot:
    def __init__(self):
        """Initialize the Discord bot with necessary configurations"""
        self.token = os.getenv("DISCORD_TOKEN")
        if not self.token:
            raise ValueError("DISCORD_TOKEN not found in environment variables. Please set it and try again.")
        
        # Set up intents
        intents = discord.Intents.default()
        # Poniższe intencje wymagają włączenia w Discord Developer Portal
        intents.message_content = True  # Uprzywilejowana intencja - potrzebujemy jej do odczytywania treści wiadomości
        intents.members = True  # Uprzywilejowana intencja - do odczytywania informacji o członkach serwera
        
        # The admin cog reference that will be set later
        self.admin_cog = None
        
        # Create bot instance with dynamic command prefix
        self.bot = commands.Bot(
            command_prefix=self.get_prefix,
            description="A Discord bot that uses PLLuM AI to respond to messages and commands",
            intents=intents,
            help_command=None  # We'll implement our own help command
        )
        
        # Register event handlers
        self.register_events()
        
        # Set up setup hook for async initialization
        @self.bot.event
        async def setup_hook():
            # Load cogs
            await self.load_cogs()
    
    def register_events(self):
        """Register event handlers for the bot"""
        
        @self.bot.event
        async def on_ready():
            """Event handler for when the bot is ready"""
            logger.info(f"Bot logged in as {self.bot.user.name} ({self.bot.user.id})")
            logger.info(f"Connected to {len(self.bot.guilds)} guilds")
            
            # Set bot activity
            activity = discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{config.COMMAND_PREFIX}help | PLLuM AI"
            )
            await self.bot.change_presence(activity=activity)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            """Global error handler for command errors"""
            if isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"⚠️ Missing required argument: {error.param.name}")
            elif isinstance(error, commands.BadArgument):
                await ctx.send(f"⚠️ Bad argument: {error}")
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"⚠️ Command on cooldown. Try again in {error.retry_after:.2f} seconds.")
            else:
                logger.error(f"Command error: {error}", exc_info=True)
                await ctx.send(f"⚠️ An error occurred: {error}")
    
    async def load_cogs(self):
        """Load all cogs for the bot"""
        await self.bot.add_cog(CommandsCog(self.bot))
        await self.bot.add_cog(ConversationsCog(self.bot))
        # Admin cog needs to be stored as a reference for the get_prefix method
        admin_cog = AdminCog(self.bot)
        self.admin_cog = admin_cog
        await self.bot.add_cog(admin_cog)
        logger.info("All cogs loaded successfully")
    
    def get_prefix(self, bot, message):
        """Get the command prefix for a server, with fallback to default"""
        # Default prefix from config
        default_prefix = config.COMMAND_PREFIX
        
        # DMs always use the default prefix
        if message.guild is None:
            return default_prefix
            
        # If admin_cog is loaded, use its prefix
        if self.admin_cog:
            return self.admin_cog.get_prefix(message.guild.id)
            
        return default_prefix
    
    async def start_bot(self):
        """Start the bot"""
        try:
            logger.info("Starting bot...")
            await self.bot.start(self.token)
        except discord.errors.LoginFailure:
            logger.error("Invalid Discord token. Please check your DISCORD_TOKEN environment variable.")
        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
        finally:
            if not self.bot.is_closed():
                await self.bot.close()

# Global reference to the active bot instance for other modules to access
active_bot_instance = None

def initialize_bot():
    """Initialize and return a new instance of the PLLuM bot"""
    global active_bot_instance
    bot = PLLuMBot()
    active_bot_instance = bot
    return bot
