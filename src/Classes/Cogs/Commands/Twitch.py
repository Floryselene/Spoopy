import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from ...Utils.TwitchHelper import TwitchStreamChecker
from ...Functions import download_asset, color_thief


class TwitchCog(commands.Cog, name="Twitch Commands"):
    def __init__(self, bot):
        self.bot = bot


    @commands.guild_only()
    @commands.hybrid_group(name="twitch", description="Command Group that manages Twitch integration")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def twitch(self, ctx: commands.Context):
        pass


    @commands.guild_only()
    @twitch.command(name="setup", description="Sets up the Twitch notifier")
    @app_commands.describe(
        name="The streamer to watch for (their username - EX: spoopy1x)",
        client_id="The Twitch application Client ID",
        client_secret="The Twitch application Client Secret",
        refresh_token="The Twitch application Refresh Token",
        access_token="The Twitch application Access Token",
        channel="The Channel to forward Twitch notifications to",
        role="The Role to mention for Twitch notifications",
    )
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context, name: str, client_id: str, client_secret: str, refresh_token: str, access_token: str, channel: discord.TextChannel, role: Optional[discord.Role] = None):
        # I should change this to use the new SQL system lol
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_USER", name, "str")
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_CLIENT_ID", client_id, "str")
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_CLIENT_SECRET", client_secret, "str")
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_REFRESH_TOKEN", refresh_token, "str")
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_ACCESS_TOKEN", access_token, "str")
        self.bot.config.add_entry(ctx.guild.id, "TWITCH_NOTIFY_CHANNEL", channel.id, "int")

        LAST_NOTIF = self.bot.config.get_value(ctx.guild.id, "LAST_NOTIFICATION")

        if LAST_NOTIF is not None:
            self.bot.config.remove_entry(ctx.guild.id, "LAST_NOTIFICATION")

        response = f"This guild will now get notified when {name} goes live\nNotifications will be sent to {channel.mention}"

        if role is not None:
            self.bot.config.add_entry(ctx.guild.id, "TWITCH_NOTIFY_ROLE", role.id, "int")
            response += f"\nUsers with the {role.mention} role will be notified when {name} goes live"

        embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.green(), description=response, timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    @commands.guild_only()
    @twitch.command(name="check", description="Checks if a specific streamer is live")
    @app_commands.describe(name="The streamer to check (their username - EX: spoopy1x)",)
    async def check_streamer(self, ctx: commands.Context, name: str):
        # I should change this to use the new SQL system lol
        CLIENT_ID = self.bot.config.get_value(ctx.guild.id, "TWITCH_CLIENT_ID")
        CLIENT_SECRET = self.bot.config.get_value(ctx.guild.id, "TWITCH_CLIENT_SECRET")
        REFRESH_TOKEN = self.bot.config.get_value(ctx.guild.id, "TWITCH_REFRESH_TOKEN")
        ACCESS_TOKEN = self.bot.config.get_value(ctx.guild.id, "TWITCH_ACCESS_TOKEN")

        if any(var is None for var in [CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN]):
            embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.red(), description=f"The Twitch service is not configured properly in this guild.", timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
            return None

        checker = TwitchStreamChecker(name, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN)
        streamer_info = await checker.is_streamer_live()

        if streamer_info is None:
            embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.red(), description="Could not retrieve streamer information.", timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
            return None

        if streamer_info['is_live']:
            # Get dominant color of pfp
            data = await download_asset(streamer_info['avatar'])
            hex_color = color_thief(data)

            # Format embed
            embed = discord.Embed(title=f"{checker.TWITCH_USERNAME} is live on Twitch!", colour=discord.Colour(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
            embed.description = f"{streamer_info['title']}"
            embed.url = streamer_info['url']
            embed.set_image(url=streamer_info['preview'])
            embed.set_thumbnail(url=streamer_info['avatar'])

            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        else:
            embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.red(), description=f"{name} is not live on Twitch.", timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)



async def setup(bot):
    await bot.add_cog(TwitchCog(bot))
