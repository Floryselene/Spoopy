import discord
from discord.utils import format_dt
from discord.ext import commands, tasks
from datetime import datetime, timezone

from ...Utils.TwitchHelper import TwitchStreamChecker
from ...Functions import download_asset, color_thief



class TwitchServiceCog(commands.Cog, name="Twitch Notification Service"):
    def __init__(self, bot):
        self.bot = bot
        self.stream_check_loop.start()


    def cog_unload(self):
        self.stream_check_loop.cancel()


    @tasks.loop(minutes=1)
    async def stream_check_loop(self):
        TIME = datetime.now(timezone.utc).timestamp()
        WAIT_FACTOR = 4 * 60 * 60
        for guild in self.bot.guilds:
            # I should change this to use the new SQL system lol
            TWITCH_USERNAME = self.bot.config.get_value(guild.id, "TWITCH_USER")
            CLIENT_ID = self.bot.config.get_value(guild.id, "TWITCH_CLIENT_ID")
            CLIENT_SECRET = self.bot.config.get_value(guild.id, "TWITCH_CLIENT_SECRET")
            REFRESH_TOKEN = self.bot.config.get_value(guild.id, "TWITCH_REFRESH_TOKEN")
            ACCESS_TOKEN = self.bot.config.get_value(guild.id, "TWITCH_ACCESS_TOKEN")
            NOTIFY_CHANNEL = self.bot.get_channel(self.bot.config.get_value(guild.id, "TWITCH_NOTIFY_CHANNEL"))
            NOTIFY_ROLE = guild.get_role(self.bot.config.get_value(guild.id, "TWITCH_NOTIFY_ROLE"))
            LAST_NOTIF = self.bot.config.get_value(guild.id, "LAST_NOTIFICATION")

            if any(var is None for var in [TWITCH_USERNAME, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN, NOTIFY_CHANNEL]):
                continue

            if LAST_NOTIF is None or (TIME - LAST_NOTIF) >= WAIT_FACTOR:
                checker = TwitchStreamChecker(TWITCH_USERNAME, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN)

                streamer_info = await checker.is_streamer_live()
                if streamer_info is None:
                    continue

                if streamer_info['is_live']:
                    if NOTIFY_CHANNEL is not None:
                        # Get dominant color of pfp
                        data = await download_asset(streamer_info['avatar'])
                        hex_color = color_thief(data)

                        # Format embed
                        embed = discord.Embed(title=f"{checker.TWITCH_USERNAME} is live on Twitch!", colour=discord.Colour(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
                        embed.description = f"{streamer_info['title']}"
                        embed.description += f"\n\nWill check again {format_dt(datetime.fromtimestamp(TIME + WAIT_FACTOR), style='R')}"
                        embed.url = streamer_info['url']
                        embed.set_image(url=streamer_info['preview'])
                        embed.set_thumbnail(url=streamer_info['avatar'])
                        self.bot.config.add_entry(guild.id, "LAST_NOTIFICATION", TIME, "float")

                        if NOTIFY_ROLE is not None:
                            await NOTIFY_CHANNEL.send(NOTIFY_ROLE.mention, embed=embed)
                        else:
                            await NOTIFY_CHANNEL.send(embed=embed)


    @stream_check_loop.before_loop
    async def before_stream_check_loop(self):
        await self.bot.wait_until_ready()



async def setup(bot):
    await bot.add_cog(TwitchServiceCog(bot))
