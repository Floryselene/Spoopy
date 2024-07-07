import os
import psutil
import discord
from typing import Optional
from discord import app_commands
from discord.ext import commands

from ...Functions import download_asset, color_thief



class MiscCog(commands.Cog, name="Miscellaneous"):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())


    @commands.hybrid_command(name="botinfo", description="Returns some info about the bot!")
    async def botinfo(self, ctx: commands.Context):
        latency = self.bot.latency * 1000.0
        ram_usage = self.process.memory_full_info().rss / 1024**2
        difference = discord.utils.utcnow() - self.bot.uptime            

        days, remainder = divmod(difference.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        data = await download_asset(self.bot.user.display_avatar)
        hex_color = color_thief(data)

        embed = discord.Embed(
            title=f"{self.bot.user.name} - Invite Me!",
            description="Here's some information about the bot.",
            colour=int(hex_color[1:], 16),
            timestamp=discord.utils.utcnow()
        )
        embed.url = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot+applications.commands&permissions=8"

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Servers", value=f"`{len(ctx.bot.guilds)}`", inline=True)
        embed.add_field(name="Latency", value=f"`{latency:.2f} ms`", inline=True)
        embed.add_field(name="RAM Usage", value=f"`{ram_usage:.2f} MiB`", inline=True)
        embed.add_field(name="Built With", value=f"`discord.py {discord.__version__}`", inline=True)
        embed.add_field(name="Running On", value=f"`{platform.release()}`", inline=True)
        embed.add_field(name="Uptime", value=f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s", inline=True)
        embed.set_footer(text="Made with ♥ by Floramene")

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())


    # Credits for the original version of this command go to TalonFloof
    @commands.guild_only()
    @commands.hybrid_command(name="embed", description="Generates an embed message", default_permission=False)
    @app_commands.describe(
        channel="The channel to send the embed to",
        title="The title for the embed",
        description="The description for the embed (Type \"\\n\" to do a linebreak)",
        color="The color for the embed (EX: #FF0000)",
        url="The URL for the embed",
        thumbnail="The thumbnail for the embed",
        image="The image for the embed",
        footer="The footer for the embed"
    )
    @app_commands.default_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def embed(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        title: str,
        description: str,
        color: Optional[str] = None,
        url: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        footer: Optional[str] = None
    ):

        embed = discord.Embed()

        attributes = {
            "title": title,
            "description": description.replace("\\n", "\n"),
            "color": discord.Color(int(color.replace("#", ""), 16)) if color and color.lower() not in ["none", ""] else None,
            "url": url if url and url.lower() not in ["none", ""] else None,
            "thumbnail": thumbnail,
            "image": image,
            "footer": footer
        }

        for attribute, value in attributes.items():
            if value is not None:
                if attribute == "thumbnail":
                    # It NEEDS a URL, else it raises an error
                    # You can avoid that by giving a dummy URL, also doesnt put any image
                    if value.lower() == "none": value = "https://example.com"
                    embed.set_thumbnail(url=value)
                elif attribute == "image":
                    if value.lower() == "none": value = "https://example.com"
                    embed.set_image(url=value)
                elif attribute == "footer":
                    if value.lower() == "none": value = ""
                    embed.set_footer(text=value)
                else:
                    setattr(embed, attribute, value)

        await ctx.reply("Embed Sent!", ephemeral=True)
        destination = ctx.channel if channel is None else channel
        await destination.send(embed=embed)



async def setup(bot):
    await bot.add_cog(MiscCog(bot))
