"""
Admin cog for the Discord bot.
Contains administrative commands for server owners and administrators.
"""
import discord
from discord.ext import commands
import logging
import json
import os
import config
from typing import Optional

logger = logging.getLogger(__name__)

class AdminCog(commands.Cog, name="Admin"):
    """Handles administrative commands for server owners and administrators"""

    def __init__(self, bot):
        self.bot = bot
        self.server_settings = {}
        self.settings_path = "server_settings.json"
        self.load_settings()
    
    def load_settings(self):
        """Load server settings from disk"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    self.server_settings = json.load(f)
                logger.info(f"Loaded settings for {len(self.server_settings)} servers")
            else:
                logger.info("No settings file found, starting with empty settings")
                self.server_settings = {}
        except Exception as e:
            logger.error(f"Error loading server settings: {e}", exc_info=True)
            self.server_settings = {}
    
    def save_settings(self):
        """Save server settings to disk"""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.server_settings, f, indent=4)
            logger.info(f"Saved settings for {len(self.server_settings)} servers")
        except Exception as e:
            logger.error(f"Error saving server settings: {e}", exc_info=True)
    
    def get_server_setting(self, guild_id, key, default=None):
        """Get a setting for a specific server"""
        guild_id = str(guild_id)  # Convert to string for JSON storage
        if guild_id not in self.server_settings:
            self.server_settings[guild_id] = {}
        return self.server_settings[guild_id].get(key, default)
    
    def set_server_setting(self, guild_id, key, value):
        """Set a setting for a specific server"""
        guild_id = str(guild_id)  # Convert to string for JSON storage
        if guild_id not in self.server_settings:
            self.server_settings[guild_id] = {}
        self.server_settings[guild_id][key] = value
        self.save_settings()
    
    async def cog_check(self, ctx):
        """Check if user has permission to run admin commands"""
        if ctx.guild is None:
            await ctx.send("❌ Admin commands can only be used in servers, not in DMs.")
            return False
        
        # Check if user is the server owner, an administrator, or has the manage server permission
        if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild:
            return True
        
        await ctx.send("❌ You don't have permission to use this command. You need to be a server administrator.")
        return False
    
    @commands.group(name="admin", invoke_without_command=True)
    async def admin_group(self, ctx):
        """Admin commands group - displays help if no subcommand is specified"""
        embed = discord.Embed(
            title="Admin Commands",
            description="Administrative commands for managing the bot on your server",
            color=discord.Color.blue()
        )
        
        command_list = [
            f"`{config.COMMAND_PREFIX}admin channels` - Manage allowed channels",
            f"`{config.COMMAND_PREFIX}admin roles` - Manage allowed roles",
            f"`{config.COMMAND_PREFIX}admin prefix` - Set custom command prefix",
            f"`{config.COMMAND_PREFIX}admin settings` - View current settings",
            f"`{config.COMMAND_PREFIX}admin model` - Set AI model",
            f"`{config.COMMAND_PREFIX}admin reset` - Reset server settings"
        ]
        
        embed.add_field(
            name="Available Commands",
            value="\n".join(command_list),
            inline=False
        )
        
        embed.set_footer(text="Only server admins can use these commands")
        await ctx.send(embed=embed)
    
    @admin_group.command(name="settings")
    async def admin_settings(self, ctx):
        """View current server settings"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.server_settings:
            self.server_settings[guild_id] = {}
        
        settings = self.server_settings[guild_id]
        
        embed = discord.Embed(
            title="Server Settings",
            description=f"Current settings for {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        # Get allowed channels
        allowed_channels = settings.get("allowed_channels", [])
        channels_str = "All channels allowed" if not allowed_channels else ", ".join([f"<#{ch}>" for ch in allowed_channels])
        
        # Get allowed roles
        allowed_roles = settings.get("allowed_roles", [])
        roles_str = "All roles allowed" if not allowed_roles else ", ".join([f"<@&{r}>" for r in allowed_roles])
        
        # Get custom prefix
        custom_prefix = settings.get("prefix", config.COMMAND_PREFIX)
        
        # Get selected model
        model = settings.get("model", config.ACTIVE_MODEL_ID)
        
        embed.add_field(name="Prefix", value=f"`{custom_prefix}`", inline=False)
        embed.add_field(name="AI Model", value=f"`{model}`", inline=False)
        embed.add_field(name="Allowed Channels", value=channels_str, inline=False)
        embed.add_field(name="Allowed Roles", value=roles_str, inline=False)
        
        await ctx.send(embed=embed)
    
    @admin_group.command(name="channels")
    async def admin_channels(self, ctx, action: str = None, channel: Optional[discord.TextChannel] = None):
        """Manage allowed channels for the bot"""
        if action is None or action.lower() not in ["add", "remove", "list", "reset"]:
            await ctx.send(f"❌ Invalid action. Use `{config.COMMAND_PREFIX}admin channels add #channel`, `{config.COMMAND_PREFIX}admin channels remove #channel`, `{config.COMMAND_PREFIX}admin channels list`, or `{config.COMMAND_PREFIX}admin channels reset`.")
            return
        
        action = action.lower()
        
        if action == "list":
            # List current allowed channels
            allowed_channels = self.get_server_setting(ctx.guild.id, "allowed_channels", [])
            if not allowed_channels:
                await ctx.send("✅ The bot is allowed to respond in all channels.")
                return
            
            channels_str = ", ".join([f"<#{ch}>" for ch in allowed_channels])
            await ctx.send(f"Allowed channels: {channels_str}")
            return
        
        if action == "reset":
            # Reset allowed channels
            self.set_server_setting(ctx.guild.id, "allowed_channels", [])
            await ctx.send("✅ Reset channel settings. The bot is now allowed to respond in all channels.")
            return
        
        # For add/remove we need a channel parameter
        if channel is None:
            await ctx.send(f"❌ Please specify a channel. Example: `{config.COMMAND_PREFIX}admin channels {action} #general`")
            return
        
        allowed_channels = self.get_server_setting(ctx.guild.id, "allowed_channels", [])
        
        if action == "add":
            if str(channel.id) in allowed_channels:
                await ctx.send(f"❌ <#{channel.id}> is already in the allowed channels list.")
                return
            
            allowed_channels.append(str(channel.id))
            self.set_server_setting(ctx.guild.id, "allowed_channels", allowed_channels)
            await ctx.send(f"✅ Added <#{channel.id}> to allowed channels.")
        
        elif action == "remove":
            if str(channel.id) not in allowed_channels:
                await ctx.send(f"❌ <#{channel.id}> is not in the allowed channels list.")
                return
            
            allowed_channels.remove(str(channel.id))
            self.set_server_setting(ctx.guild.id, "allowed_channels", allowed_channels)
            await ctx.send(f"✅ Removed <#{channel.id}> from allowed channels.")
    
    @admin_group.command(name="roles")
    async def admin_roles(self, ctx, action: str = None, role: Optional[discord.Role] = None):
        """Manage allowed roles for the bot"""
        if action is None or action.lower() not in ["add", "remove", "list", "reset"]:
            await ctx.send(f"❌ Invalid action. Use `{config.COMMAND_PREFIX}admin roles add @role`, `{config.COMMAND_PREFIX}admin roles remove @role`, `{config.COMMAND_PREFIX}admin roles list`, or `{config.COMMAND_PREFIX}admin roles reset`.")
            return
        
        action = action.lower()
        
        if action == "list":
            # List current allowed roles
            allowed_roles = self.get_server_setting(ctx.guild.id, "allowed_roles", [])
            if not allowed_roles:
                await ctx.send("✅ The bot is allowed to respond to all roles.")
                return
            
            roles_str = ", ".join([f"<@&{r}>" for r in allowed_roles])
            await ctx.send(f"Allowed roles: {roles_str}")
            return
        
        if action == "reset":
            # Reset allowed roles
            self.set_server_setting(ctx.guild.id, "allowed_roles", [])
            await ctx.send("✅ Reset role settings. The bot is now allowed to respond to all roles.")
            return
        
        # For add/remove we need a role parameter
        if role is None:
            await ctx.send(f"❌ Please specify a role. Example: `{config.COMMAND_PREFIX}admin roles {action} @role`")
            return
        
        allowed_roles = self.get_server_setting(ctx.guild.id, "allowed_roles", [])
        
        if action == "add":
            if str(role.id) in allowed_roles:
                await ctx.send(f"❌ {role.name} is already in the allowed roles list.")
                return
            
            allowed_roles.append(str(role.id))
            self.set_server_setting(ctx.guild.id, "allowed_roles", allowed_roles)
            await ctx.send(f"✅ Added {role.name} to allowed roles.")
        
        elif action == "remove":
            if str(role.id) not in allowed_roles:
                await ctx.send(f"❌ {role.name} is not in the allowed roles list.")
                return
            
            allowed_roles.remove(str(role.id))
            self.set_server_setting(ctx.guild.id, "allowed_roles", allowed_roles)
            await ctx.send(f"✅ Removed {role.name} from allowed roles.")
    
    @admin_group.command(name="prefix")
    async def admin_prefix(self, ctx, new_prefix: Optional[str] = None):
        """Set a custom command prefix for this server"""
        if new_prefix is None:
            # Show current prefix
            custom_prefix = self.get_server_setting(ctx.guild.id, "prefix", config.COMMAND_PREFIX)
            await ctx.send(f"Current prefix: `{custom_prefix}`")
            await ctx.send(f"To change it, use `{config.COMMAND_PREFIX}admin prefix <new_prefix>`")
            return
        
        # Validate prefix length
        if len(new_prefix) > 5:
            await ctx.send("❌ Prefix is too long. Maximum length is 5 characters.")
            return
        
        # Set new prefix
        self.set_server_setting(ctx.guild.id, "prefix", new_prefix)
        await ctx.send(f"✅ Command prefix set to `{new_prefix}`")
        await ctx.send(f"Example: `{new_prefix}help`")
    
    @admin_group.command(name="model")
    async def admin_model(self, ctx, model_key: Optional[str] = None):
        """Set the AI model to use for this server"""
        if model_key is None:
            # List available models
            embed = discord.Embed(
                title="Available AI Models",
                description="Choose a model with `!admin model <key>`",
                color=discord.Color.blue()
            )
            
            # Current model
            current_model = self.get_server_setting(ctx.guild.id, "model", config.ACTIVE_MODEL_ID)
            embed.add_field(
                name="Current Model",
                value=f"`{current_model}`",
                inline=False
            )
            
            # Available models
            model_list = []
            for key, model_id in config.PLLUM_MODELS.items():
                model_list.append(f"`{key}`: {model_id}")
            
            embed.add_field(
                name="Available Models",
                value="\n".join(model_list),
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        # Check if model exists
        model_key = model_key.lower()
        if model_key not in config.PLLUM_MODELS:
            await ctx.send(f"❌ Unknown model key: `{model_key}`. Use `{config.COMMAND_PREFIX}admin model` to see available models.")
            return
        
        # Set model
        model_id = config.PLLUM_MODELS[model_key]
        self.set_server_setting(ctx.guild.id, "model", model_id)
        await ctx.send(f"✅ AI model set to `{model_id}`")
    
    @admin_group.command(name="reset")
    async def admin_reset(self, ctx):
        """Reset all server settings to defaults"""
        # Ask for confirmation
        confirmation_msg = await ctx.send("⚠️ This will reset ALL server settings to default values. Are you sure? Reply with `yes` to confirm or `no` to cancel.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]
        
        try:
            # Wait for confirmation
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            if msg.content.lower() == "yes":
                # Reset settings
                if str(ctx.guild.id) in self.server_settings:
                    del self.server_settings[str(ctx.guild.id)]
                    self.save_settings()
                
                await ctx.send("✅ All server settings have been reset to defaults.")
            else:
                await ctx.send("❌ Reset cancelled.")
                
        except Exception as e:
            logger.error(f"Error in reset command: {e}", exc_info=True)
            await ctx.send("❌ Reset cancelled or timed out.")

    async def check_message_permissions(self, message):
        """Check if a message should be processed based on channel and role restrictions"""
        # DMs are always allowed
        if message.guild is None:
            return True
        
        guild_id = str(message.guild.id)
        if guild_id not in self.server_settings:
            return True  # No restrictions set
        
        settings = self.server_settings[guild_id]
        
        # Check channels
        allowed_channels = settings.get("allowed_channels", [])
        if allowed_channels and str(message.channel.id) not in allowed_channels:
            return False
        
        # Check roles
        allowed_roles = settings.get("allowed_roles", [])
        if allowed_roles:
            # Check if user has any of the allowed roles
            user_roles = [str(role.id) for role in message.author.roles]
            if not any(role_id in allowed_roles for role_id in user_roles):
                return False
        
        return True
    
    def get_prefix(self, guild_id):
        """Get custom prefix for a server"""
        return self.get_server_setting(guild_id, "prefix", config.COMMAND_PREFIX)
    
    def get_model(self, guild_id):
        """Get custom model for a server"""
        return self.get_server_setting(guild_id, "model", config.ACTIVE_MODEL_ID)