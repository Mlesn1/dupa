"""
Commands cog for the Discord bot.
Contains basic command handlers.
"""
import discord
from discord.ext import commands
import logging
import config
from utils.pllum_api import get_pllum_response
from utils.rate_limiter import RateLimiter
from utils.language_utils import get_language_instructions

logger = logging.getLogger(__name__)

class CommandsCog(commands.Cog, name="Commands"):
    """Handles all command-related functionality for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.rate_limiter = RateLimiter(config.RATE_LIMIT_USER)
        
    async def cog_check(self, ctx):
        """Check permissions before executing commands"""
        # DMs are always allowed
        if ctx.guild is None:
            return True
            
        # Check server permissions through AdminCog
        admin_cog = self.bot.get_cog("Admin")
        if admin_cog:
            return await admin_cog.check_message_permissions(ctx.message)
            
        # If AdminCog is not available, allow the command
        return True
    
    @commands.command(name="help")
    async def help_command(self, ctx):
        """Shows the help message with all available commands"""
        # Get the custom prefix for this server if available
        prefix = config.COMMAND_PREFIX
        if ctx.guild:
            admin_cog = self.bot.get_cog("Admin")
            if admin_cog:
                prefix = admin_cog.get_prefix(ctx.guild.id)
                
        embed = discord.Embed(
            title="PLLuM AI Bot Help",
            description=f"Prefix: `{prefix}`",
            color=discord.Color.blue()
        )
        
        # Commands category
        embed.add_field(
            name="📋 Commands",
            value=(
                f"`{prefix}help` - Shows this help message\n"
                f"`{prefix}ask <question>` - Ask PLLuM AI a question\n"
                f"`{prefix}chat` - Start a conversation with PLLuM AI\n"
                f"`{prefix}ping` - Check the bot's latency\n"
                f"`{prefix}info` - Get information about the bot"
            ),
            inline=False
        )
        
        # Admin commands for administrators
        if ctx.guild and ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="🔧 Admin Commands",
                value=(
                    f"`{prefix}admin channels` - Manage allowed channels\n"
                    f"`{prefix}admin roles` - Manage allowed roles\n"
                    f"`{prefix}admin prefix` - Set custom command prefix\n"
                    f"`{prefix}admin model` - Set AI model\n"
                    f"`{prefix}admin settings` - View current settings\n"
                    f"`{prefix}admin reset` - Reset server settings"
                ),
                inline=False
            )
        
        # Conversations explanation
        embed.add_field(
            name="💬 Conversations",
            value=(
                f"To talk to the AI, either use the `{prefix}chat` command to start a conversation, "
                f"or mention the bot with your message like `@PLLuMBot hello!`\n\n"
                f"Conversations timeout after {config.CONVERSATION_TIMEOUT//60} minutes of inactivity."
            ),
            inline=False
        )
        
        # Rate limiting information
        embed.add_field(
            name="⚠️ Rate Limits",
            value=(
                f"• {config.RATE_LIMIT_USER} requests per minute per user\n"
                f"• {config.RATE_LIMIT_GLOBAL} requests per minute for the entire bot"
            ),
            inline=False
        )
        
        embed.set_footer(text="PLLuM AI Bot | Powered by discord.py")
        await ctx.send(embed=embed)
    
    @commands.command(name="ask")
    async def ask_command(self, ctx, *, question: str):
        """Ask a one-time question to PLLuM AI"""
        # Check rate limit
        if not self.rate_limiter.check_rate_limit(ctx.author.id):
            await ctx.send(config.BOT_RATE_LIMITED_MESSAGE)
            return
        
        async with ctx.typing():
            try:
                # Send thinking message
                thinking_msg = await ctx.send(config.BOT_THINKING_MESSAGE)
                
                # Get language instructions based on the question
                language_instructions = get_language_instructions(question)
                
                # Get response from PLLuM AI with language instructions
                prompt = f"User: {question}\n\n{language_instructions}\n\nAI:"
                guild_id = str(ctx.guild.id) if ctx.guild else None
                response = await get_pllum_response(prompt, guild_id=guild_id)
                
                # Create response embed
                embed = discord.Embed(
                    title="PLLuM AI Response",
                    description=response,
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                
                # Delete thinking message and send response
                await thinking_msg.delete()
                await ctx.send(embed=embed)
                
                logger.info(f"Answered question for user {ctx.author.id}: {question[:50]}...")
                
            except Exception as e:
                logger.error(f"Error in ask command: {str(e)}", exc_info=True)
                await ctx.send(config.BOT_ERROR_MESSAGE)
    
    @commands.command(name="ping")
    async def ping_command(self, ctx):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")
    
    @commands.command(name="info")
    async def info_command(self, ctx):
        """Display information about the bot"""
        embed = discord.Embed(
            title="PLLuM AI Bot Information",
            description="A Discord bot that leverages PLLuM AI to respond to messages and commands",
            color=discord.Color.blue()
        )
        
        # Bot stats
        embed.add_field(
            name="📊 Bot Stats",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Commands:** {len(self.bot.commands)}\n"
                f"**Latency:** {round(self.bot.latency * 1000)}ms"
            ),
            inline=True
        )
        
        # PLLuM AI Info
        embed.add_field(
            name="🤖 PLLuM AI",
            value=(
                f"**Max Tokens:** {config.PLLUM_MAX_TOKENS}\n"
                f"**Temperature:** {config.PLLUM_TEMPERATURE}"
            ),
            inline=True
        )
        
        # Get the custom prefix for this server if available
        prefix = config.COMMAND_PREFIX
        if ctx.guild:
            admin_cog = self.bot.get_cog("Admin")
            if admin_cog:
                prefix = admin_cog.get_prefix(ctx.guild.id)
                
        embed.set_footer(text=f"Prefix: {prefix} | Use {prefix}help for commands")
        await ctx.send(embed=embed)
