import discord
from discord import app_commands
from discord.ext import commands



class LogSetupCog(commands.Cog, name="Log Configuration"):
    def __init__(self, bot):
        self.bot = bot
        self.typing_list = ['EDIT_LOG', 'DELETE_LOG', 'JOIN_MOD_LOG', 'LEAVE_MOD_LOG', 'PUNISHMENT_LOG', 'ROLE_LOG']


    async def handle_logs(self, ctx: commands.Context, typing, value, response):
        self.bot.config.add_entry(ctx.guild.id, typing, value, "int")
        embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.blue(), description=response, timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    @commands.guild_only()
    @commands.hybrid_command(name="log", description="Sets the event log channels for the guild")
    @app_commands.describe(typing="Which event to set", channel="The channel to set the log event to")
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def log(self, ctx: commands.Context, typing: str, channel: discord.TextChannel):
        if typing.upper() not in self.typing_list: return None
        await self.handle_logs(ctx, typing, channel.id, f"{typing} channel set to {channel.mention} on this guild")


    @commands.guild_only()
    @commands.hybrid_command(name="welcome", description="Sets the welcome announcement channel / (optional message) for the guild")
    @app_commands.describe(channel="The channel to announce new joins in", message="The message to optionally add to the announcement (Input as \"None\" to remove it)")
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx: commands.Context, channel: discord.TextChannel, message: str = None):
        self.bot.config.add_entry(ctx.guild.id, 'WELCOME_ANNOUNCE_CHANNEL', channel.id, "int")
        response = f"Welcome announcement channel set to {channel.mention} on this guild"

        if message is not None and message.upper() == "NONE":
            self.bot.config.remove_entry(ctx.guild.id, 'WELCOME_ANNOUNCE_MESSAGE')
            response += f"\nResponse has been removed"
        elif message is not None and message.upper() != "NONE":
            self.bot.config.add_entry(ctx.guild.id, 'WELCOME_ANNOUNCE_MESSAGE', message, "str")
            response += f"\nResponse has been set as well"

        embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.blue(), description=response, timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    @log.autocomplete("typing")
    async def autocomplete_action(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        actions = self.typing_list
        return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]



async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))
