import discord
from discord.ext import commands
from discord.utils import format_dt

from ...Functions import download_asset, color_thief



class LeaveModHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(member.guild.id, "LEAVE_MOD_LOG"))
        if channel is None:
            return

        # Get dominant color of pfp
        data = await download_asset(member.display_avatar.url)
        hex_color = color_thief(data)

        # Embed flags
        embed = discord.Embed(title="Member Left", color=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{member.name} | {member.id}')
        embed.set_thumbnail(url=member.display_avatar.url)

        profile_info = f"> **Profile** - {member.mention}\n"
        joined_at_info = f"> **Joined Guild** - {format_dt(member.joined_at, style='R')}\n"
        member_count_info = f"> **Members** - {len(member.guild.members)}\n"

        action = None
        action_by = None
        reason = None

        if isinstance(member, discord.Member):
            if member.guild.me.guild_permissions.view_audit_log:
                after_date = member.joined_at
                try:
                    async for entry in member.guild.audit_logs(limit=None):
                        if entry.target.id == member.id:
                            if entry.action == discord.AuditLogAction.kick and entry.created_at > after_date:
                                action = "\n> **Action** - Kicked\n"
                                action_by = f"> **Action By** - {entry.user.mention}\n"
                                reason = f"\n> **Reason** ```{entry.reason}```" if entry.reason else "\n> **Reason** ```None Provided```"
                                break
                            elif entry.action == discord.AuditLogAction.ban and entry.created_at > after_date:
                                action = "\n> **Action** - Banned\n"
                                action_by = f"> **Action By** - {entry.user.mention}\n"
                                reason = f"\n> **Reason** ```{entry.reason}```" if entry.reason else "\n> **Reason** ```None Provided```"
                                break
                except AttributeError:
                    # Handle case when there are no audit log entries
                    pass

        # Display roles (excluding @everyone) in order of hierarchy
        roles = [
            role.mention for role in sorted(
                member.roles[1:], key=lambda x: x.position, reverse=True)
        ]

        if action:
            embed_body = f"{member_count_info}{profile_info}{joined_at_info}{action}{action_by}{reason}"
        else:
            embed_body = f"{member_count_info}{profile_info}{joined_at_info}"

        if roles:
            embed_body += f"\n\n> **Roles** \n> {' '.join(roles)}"

        embed.description = embed_body
        await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(LeaveModHandler(bot))
