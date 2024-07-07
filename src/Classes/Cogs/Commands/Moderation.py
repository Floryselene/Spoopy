import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt

from ...Utils.ModHelperFuncs import *



class ModerationCog(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot


    # Credits for the original version of this go to TalonFloof
    async def punishment_helper(self, ctx, punishment_type, member, expiration, reason, punishment_func):
        if member.id == ctx.author.id:
            embed = discord.Embed(title=self.bot.user.name, description=f"You are not allowed to {punishment_type} yourself.", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
            return None

        ret = await punishment_func(self.bot, ctx.guild, member, ctx.author, expiration, reason)

        embed = discord.Embed(title="Punishment Report", colour=discord.Colour.green(), description=f"**Punishment** {punishment_type}\n**Reason** {reason}", timestamp=discord.utils.utcnow())

        emoji = ""
        if ret == 0:
            emoji = ":white_check_mark:"
        elif ret == 1:
            emoji = ":x:"
        elif ret == 2:
            emoji = ":no_entry_sign:"

        embed.add_field(name="", value=f"{emoji} {member.name} `{member.id}`", inline=False)
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    @commands.guild_only()
    @commands.hybrid_command(name="mute", description="Mutes a user for the specified time")
    @app_commands.describe(member="The member to mute", duration="How long to mute them for - (EG: 1s, 1m, 1h, 1d)", reason="The reason you're muting them")
    @app_commands.default_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason: str):
        duration_seconds = convert_duration_to_seconds(duration)
        if duration_seconds is None:
            embed = discord.Embed(title=self.bot.user.name, description="Invalid duration format. Please use a valid format like `1d`, `1h`, `1m`, or `1s`.", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
            return
        await self.punishment_helper(ctx, "mute", member, duration_seconds[1], reason, user_mute)


    @commands.guild_only()
    @commands.hybrid_command(name="unmute", description="Unmutes a user")
    @app_commands.describe(member="The member to unmute", reason="The reason you're unmuting them")
    @app_commands.default_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str):
        await self.punishment_helper(ctx, "unmute", member, 0, reason, user_unmute)


    @commands.guild_only()
    @commands.hybrid_command(name="kick", description="Kicks a user out of a guild")
    @app_commands.describe(member="The member to kick", reason="The reason you're kicking them")
    @app_commands.default_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        async def kick_func(bot, guild, user, author, expiration, final):
            await user.kick(reason=final)
            return await punishment_update(bot, guild, user, author, expiration, final, "kick")

        await self.punishment_helper(ctx, "kick", member, 0, reason, kick_func)


    @commands.guild_only()
    @commands.hybrid_command(name="ban", description="Bans a user out of a guild")
    @app_commands.describe(member="The member to ban", reason="The reason you're banning them")
    @app_commands.default_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, *, reason: str):
        async def ban_func(bot, guild, user, author, expiration, final):
            await ctx.guild.ban(user, reason=final)
            return await punishment_update(bot, guild, user, author, expiration, final, "ban")

        await self.punishment_helper(ctx, "ban", member, 0, reason, ban_func)


    @commands.guild_only()
    @commands.hybrid_command(name="unban", description="Unbans a user from a guild")
    @app_commands.describe(member="The member to unban", reason="The reason you're unbanning them")
    @app_commands.default_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason: str):
        async def unban_func(bot, guild, user, author, expiration, final):
            await ctx.guild.unban(user, reason=final)
            return await punishment_update(bot, guild, user, author, expiration, final, "unban")

        await self.punishment_helper(ctx, "unban", member, 0, reason, unban_func)


    @commands.guild_only()
    @commands.hybrid_command(name="mutelist", description="Displays all active mutes for the current guild")
    @app_commands.default_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def mutelist(self, ctx):
        mute_records = await self.bot.database.get_mutes(ctx.guild.id)

        if mute_records:
            embed = discord.Embed(title=f"Active Mutes - {ctx.guild.name}", timestamp=discord.utils.utcnow())
            embed_body = ""

            for user_id, expiration, reason in mute_records:
                user = ctx.guild.get_member(user_id)
                timestamp = format_dt(datetime.datetime.fromtimestamp(expiration), style="R")
                embed_body += f"> **User** - {user.mention} | {user.id}\n> **Expiration** - {timestamp}\n> **Reason** - `{reason}`\n\n"

            embed.description = embed_body
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
        else:
            embed = discord.Embed(title=self.bot.user.name, description="No active mutes in this guild", colour=discord.Colour.red())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)



async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
