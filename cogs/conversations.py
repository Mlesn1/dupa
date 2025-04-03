"""
Conversations cog for the Discord bot.
Handles ongoing conversations with users.
"""
import asyncio
import discord
from discord.ext import commands, tasks
import logging
import time
from datetime import datetime
from collections import defaultdict
import config
from utils.pllum_api import get_pllum_response
from utils.rate_limiter import RateLimiter
from utils.language_utils import get_language_instructions

logger = logging.getLogger(__name__)

class ConversationsCog(commands.Cog, name="Conversations"):
    """Handles all conversation-related functionality for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = defaultdict(list)  # user_id -> list of messages
        self.conversation_last_activity = defaultdict(float)  # user_id -> timestamp
        self.rate_limiter = RateLimiter(config.RATE_LIMIT_USER)
        self.cleanup_task = None
        
    async def cog_load(self):
        """Called when the cog is loaded"""
        # Start background task to clean up inactive conversations
        self.cleanup_task = self.bot.loop.create_task(self.cleanup_inactive_conversations())

    def cog_unload(self):
        """Called when the cog is unloaded"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
    
    async def cleanup_inactive_conversations(self):
        """Background task to clean up inactive conversations"""
        try:
            while not self.bot.is_closed():
                current_time = time.time()
                
                # Find inactive conversations
                inactive_users = []
                for user_id, last_activity in self.conversation_last_activity.items():
                    if current_time - last_activity > config.CONVERSATION_TIMEOUT:
                        inactive_users.append(user_id)
                
                # Remove inactive conversations
                for user_id in inactive_users:
                    del self.active_conversations[user_id]
                    del self.conversation_last_activity[user_id]
                    logger.info(f"Cleaned up inactive conversation for user {user_id}")
                
                # Sleep for a minute before checking again
                await asyncio.sleep(60)
        
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            pass
        except Exception as e:
            logger.error(f"Error in conversation cleanup task: {e}", exc_info=True)
    
    @commands.command(name="chat")
    async def chat_command(self, ctx):
        """Start a conversation with PLLuM AI"""
        user_id = ctx.author.id
        
        # Reset the conversation history
        self.active_conversations[user_id] = []
        self.conversation_last_activity[user_id] = time.time()
        
        embed = discord.Embed(
            title="New Conversation Started",
            description=(
                "I'm PLLuM AI, ready to chat! Just mention me or reply to my messages.\n"
                f"Your conversation will timeout after {config.CONVERSATION_TIMEOUT//60} minutes of inactivity.\n"
                f"Type `{config.COMMAND_PREFIX}end` to end the conversation manually."
            ),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="end")
    async def end_command(self, ctx):
        """End the current conversation"""
        user_id = ctx.author.id
        
        if user_id in self.active_conversations:
            del self.active_conversations[user_id]
            del self.conversation_last_activity[user_id]
            await ctx.send("✅ Conversation ended.")
        else:
            await ctx.send("❓ You don't have an active conversation.")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle user messages for conversations"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Check if message mentions the bot or is a reply to the bot's message
        is_mention = self.bot.user in message.mentions
        is_reply = message.reference and message.reference.resolved and message.reference.resolved.author.id == self.bot.user.id
        
        if not (is_mention or is_reply):
            return
        
        # Get the context
        ctx = await self.bot.get_context(message)
        
        # If this is a command, don't handle it here
        if ctx.valid:
            return
            
        # Check server permissions (if in a guild)
        if message.guild is not None:
            admin_cog = self.bot.get_cog("Admin")
            if admin_cog and not await admin_cog.check_message_permissions(message):
                # Message doesn't meet the server's permission requirements
                return
        
        user_id = message.author.id
        
        # Check rate limit
        if not self.rate_limiter.check_rate_limit(user_id):
            await message.channel.send(config.BOT_RATE_LIMITED_MESSAGE)
            return
        
        # Update last activity timestamp
        self.conversation_last_activity[user_id] = time.time()
        
        # Get user message content
        content = message.content
        
        # Remove bot mention from message if present
        if is_mention:
            content = content.replace(f'<@{self.bot.user.id}>', '').strip()
        
        # Add message to conversation history
        self.active_conversations[user_id].append({"role": "user", "content": content})
        
        # Trim history if it gets too long
        if len(self.active_conversations[user_id]) > config.MAX_HISTORY_LENGTH * 2:
            # Keep first message (for context) and the most recent messages
            self.active_conversations[user_id] = [
                self.active_conversations[user_id][0],
                *self.active_conversations[user_id][-(config.MAX_HISTORY_LENGTH*2-1):]
            ]
        
        async with message.channel.typing():
            try:
                # Send thinking message
                thinking_msg = await message.channel.send(config.BOT_THINKING_MESSAGE)
                
                # Build the prompt from conversation history
                prompt = ""
                for msg in self.active_conversations[user_id]:
                    role_prefix = "User: " if msg["role"] == "user" else "AI: "
                    prompt += f"{role_prefix}{msg['content']}\n"
                
                # Get language instructions for the latest user message
                latest_user_message = content
                language_instructions = get_language_instructions(latest_user_message)
                
                # Add language instructions to the prompt
                prompt += f"\n{language_instructions}\n\nAI: "
                
                # Get response from PLLuM AI
                guild_id = str(message.guild.id) if message.guild else None
                response = await get_pllum_response(prompt, guild_id=guild_id)
                
                # Add response to conversation history
                self.active_conversations[user_id].append({"role": "assistant", "content": response})
                
                # Delete thinking message
                await thinking_msg.delete()
                
                # Send the response
                await message.reply(response)
                
                logger.info(f"Replied to conversation message for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error in conversation: {str(e)}", exc_info=True)
                await message.channel.send(config.BOT_ERROR_MESSAGE)
