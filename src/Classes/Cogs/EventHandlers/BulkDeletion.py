import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import Message, Attachment



class BulkDeleteHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages:
            return
        guild = messages[0].guild
        if guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(guild.id, "DELETE_LOG"))
        if channel is None:
            return

        # Create a formatted content string for all deleted messages
        content = ""
        for message in messages:
            timestamp = message.created_at.strftime("%Y/%m/%d - %H:%M:%S")
            if message.content == "":
                message.content = "NULL"
            content += f"[{timestamp}] #{message.channel.name} ({message.channel.id}) @{message.author} ({message.author.id}) [{message.id}]: {message.content}\n"

        # Save the content to a text file
        server_name = guild.name.replace(" ", "_")
        file_name = f"{server_name}_bulk_delete_{discord.utils.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
        with open(file_name, "w") as file:
            file.write(content)

        # Get the user who initiated the bulk delete event
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_bulk_delete):
            deleted_by = f"{entry.user.mention} | {entry.user.id}"
            break

        embed = discord.Embed(
            title="Bulk Deletion",
            colour=discord.Colour.red(),
            description=
            f"> **Triggered By** - {deleted_by}\n> **Deleted Messasges** - {len(messages)}\n\n> Messages created before the bot was brought online do not get logged",
            timestamp=discord.utils.utcnow())

        await channel.send(embed=embed)
        await channel.send(file=discord.File(file_name))
        os.remove(file_name)



async def setup(bot):
    await bot.add_cog(BulkDeleteHandler(bot))
