import discord
from discord.ext import commands
from discord.utils import format_dt

from ...Functions import download_asset, color_thief



class JoinModHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(member.guild.id, "JOIN_MOD_LOG"))
        if channel is None:
            return

        # Get dominant color of pfp
        data = await download_asset(member.display_avatar.url)
        hex_color = color_thief(data)

        # Embed flags
        embed = discord.Embed(title="Member Joined", color=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{member.name} | {member.id}')
        embed.set_thumbnail(url=member.display_avatar.url)

        profile_info = f"> **Profile** - {member.mention}\n"
        member_count_info = f"> **Members** - {len(member.guild.members)}\n"
        created_at_info = f"> **Account Created** - {format_dt(member.created_at, style='R')}\n"
        automod_info = f"> **Auto Mod** - User is Okay :white_check_mark:\n"
        if (discord.utils.utcnow() - member.created_at).days < 30:
            automod_info = "> **Auto Mod** - Account is under a month old :warning:\n"
        if member.public_flags.spammer:
            automod_info = "> **Auto Mod** - Marked by Discord as a spammer :warning:\n"

        embed_body = f"{member_count_info}{profile_info}{created_at_info}{automod_info}"

        invite = await self.bot.invite_tracker.fetch_invite(member)
        if invite is not None:
            embed_body += f"\n> **Inviter** - {invite.inviter.mention}\n> **Invite Used** - [{invite.code}]({invite.url})\n"
        else:
            vanity_code = member.guild.vanity_url_code
            if vanity_code:
                embed_body += f"\n> **Invite Used** - [{vanity_code}](https://discord.gg/{vanity_code})\n"

        embed.description = embed_body
        await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(JoinModHandler(bot))
