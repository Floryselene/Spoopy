import discord
from discord.ext import commands, tasks

from ...Utils.ModHelperFuncs import *



class ModServiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation_loop.start()


    def cog_unload(self):
        self.moderation_loop.cancel()


    # Credits to TalonFloof for the original version of this task
    @tasks.loop(seconds=5)
    async def moderation_loop(self):
        for guild in self.bot.guilds:
            mute_records = await self.bot.database.get_mutes(guild.id)
            for user_id, expiration, reason in mute_records:
                member = await guild.fetch_member(user_id)
                if int(datetime.datetime.now(datetime.timezone.utc).timestamp()) > expiration:
                    await user_unmute(self.bot, guild, member, self.bot.user, 0, "Mute time has expired")
                elif (member.timed_out_until is not None and (datetime.datetime.fromtimestamp(expiration, datetime.timezone.utc) - discord.utils.utcnow()).days > 27 and (member.timed_out_until - discord.utils.utcnow()).days < 27):
                    await member.timeout(datetime.timedelta(days=28), reason="Timeout extension to match mute time")


    @moderation_loop.before_loop
    async def before_moderation_loop(self):
        await self.bot.wait_until_ready()



async def setup(bot):
    await bot.add_cog(ModServiceCog(bot))
