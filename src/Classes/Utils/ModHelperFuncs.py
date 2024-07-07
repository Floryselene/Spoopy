import discord
import datetime
from discord.ext import commands
from ..Functions import download_asset, color_thief
from .TimeFormatter import convert_duration_to_seconds



# Credits for most of this to TalonFloof
async def punishment_update(bot: commands.Bot, guild: discord.Guild, user: discord.User, invoker, timeout, reason: str, type: str, test_punish: bool = False, points: int = 0, id: str = ""):
    ret = 0
    embed = discord.Embed(title="Punishment Update", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
    embed.set_author(name=f"{user.name} | {user.id}", icon_url=user.display_avatar.url)

    if isinstance(timeout, int) and timeout == 0:
        timeout = datetime.datetime.now()

    punish = {
        "ban": "🔨 Banned",
        "kick": "👢 Kicked",
        "unban": "🎉 Unbanned",
        "unmute": "🎉 Unmuted",
        "forgive": f"🎉 Forgiven Warning `{id}`",
        "mute": f"🔇 Muted, will be unmuted <t:{int(timeout.timestamp())}:R>",
        "tempban": f"🔨 Temp Banned. Will be unbanned <t:{int(timeout.timestamp())}:R>",
        "warn": f":warning: Warned ({points} point{'s' if points != 1 else ''}, expires <t:{int(timeout.timestamp())}:R>, ID `{id}`)"
    }.get(type, "")

    embed.add_field(name=f"{guild.name} | {punish}", value="Reason: " + reason + "", inline=True)
    embed.set_thumbnail(url=guild.icon.url)

    try:
        await user.send(embed=embed)
    except (discord.errors.HTTPException, discord.errors.Forbidden):
        if len(user.mutual_guilds) == 0:
            ret = 1
        else:
            ret = 2
    if test_punish:
        return 0
    if bot.config.get_value(guild.id, "PUNISHMENT_LOG") is None:
        return ret

    log_channel = bot.get_channel(bot.config.get_value(guild.id, "PUNISHMENT_LOG"))
    data = await download_asset(user.display_avatar.url)
    hex_color = color_thief(data)
    embed = discord.Embed(title="Punishment Log", colour=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
    embed.set_author(name=f"{user.name} | {user.id}")
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name=punish, value="Reason: " + reason + "", inline=True)

    if invoker is not None:
        embed.set_footer(text=f"{invoker.name} | {invoker.id}", icon_url=invoker.display_avatar.url)

    await log_channel.send(embed=embed)
    return ret



async def user_mute(bot, guild: discord.Guild, member: discord.Member, invoker, duration: int, reason: str):
    await member.timeout(datetime.timedelta(seconds=min(2419200, duration)), reason=reason)
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration)
    ret = await punishment_update(bot, guild, member, invoker, expiration, reason, "mute")
    await bot.database.add_mute(guild.id, member.id, expiration.timestamp(), reason)
    return ret


async def user_unmute(bot, guild: discord.Guild, member: discord.Member, invoker, placeholder, reason: str):
    await member.timeout(None, reason=reason)
    ret = await punishment_update(bot, guild, member, invoker, 0, reason, "unmute")
    await bot.database.remove_mute(guild.id, member.id)
    return ret
