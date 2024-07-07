import io
import discord
from discord.ext import commands
from discord.utils import format_dt

from ...Functions import download_asset, color_thief



class DeleteHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(message.guild.id, "DELETE_LOG"))
        blacklisted_targets = self.bot.config.get_value(message.guild.id, "DELETE_BLACKLIST")
        if channel is None:
            return
        if message.author.bot:
            return
        if blacklisted_targets is not None:
            if message.channel.id in blacklisted_targets or message.author.id in blacklisted_targets:
                return

        author = message.author

        # Get the audit log entries for message deletions
        async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            if entry.target.id == message.author.id and entry.created_at > message.created_at:
                # An audit log entry is found for the deletion of the message
                deleted_by = f"{entry.user.name} | {entry.user.id}"
                deleter_link = avatar_url(entry.user)
                break
            else:
                # No audit log entry found
                deleted_by = None  # No longer using Author in this case as it's not always accurate

        # Get dominant color of pfp
        data = await download_asset(author.display_avatar.url)
        hex_color = color_thief(data)

        # Embed flags
        embed = discord.Embed(title="Message Deleted",color=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{author.name} | {author.id}', icon_url=author.display_avatar.url)
        embed.add_field(name='Channel', value=message.channel.mention, inline=True)
        embed.add_field(
            name='Message ID',
            value=
            f"[{message.id}](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})",
            inline=True)

        # Check if message is empty or not
        if message.content == "":
            content = "NULL"
        else:
            content = None if len(message.content) > 1024 else message.content

        # Show when the message was created
        message_time = message.created_at
        sent_time = format_dt(message_time, style='R')
        embed.add_field(name="Sent At", value=sent_time, inline=False)

        # More embed flags
        if content != None:
            content_attachment = None
            if content != "NULL":
                embed.add_field(name='Content', value=f'```{content}```', inline=False)
        else:
            # Create a .txt file containing the bulk of the original message
            embed.add_field(name='Content', value=f'```Message exceeded embed field limit of 1024, sending as attachment instead```', inline=False)

            # Trying to think of possible exceptions with invalid characters. Use UTF-8 as the preferred
            # but if encoding fails, use latin-1 as it's able to encode practically everything (may not always be accurate though)
            try:
                content_file = io.BytesIO(message.content.encode("utf-8"))
            except UnicodeEncodeError:
                content_file = io.BytesIO(message.content.encode("latin-1"))

            content_file.seek(0)
            content_attachment = discord.File(content_file, filename=f"{message.id}.txt")

        # Check if message has stickers
        if message.stickers:
            for sticker in message.stickers:
                sticker_name = sticker.name if sticker.name else "Unnamed Sticker"
                embed.add_field(name="Sticker Name",
                                value=f'```{sticker_name}```',
                                inline=False)
                embed.set_image(url=sticker.url)

        # Check for attachments
        #
        # Unable to (consistently) log the attachment itself, but you can
        # At least see that there was one- as well as the name
        # And char / mimetype
        attachment_objs = []
        attachment_links = []
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                attachment_links.append(f"{attachment.url} - `{attachment.content_type}`")
                try:
                    attachment_objs.append(await attachment.to_file())
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    continue

        if attachment_links:
            embed.add_field(name='Attachments (Will upload a copy if applicable)', value='\n'.join(attachment_links), inline=False)

        await channel.send(embed=embed)

        if attachment_objs:
            await channel.send(files=attachment_objs)

        if content_attachment:
            await channel.send(file=content_attachment)



async def setup(bot):
    await bot.add_cog(DeleteHandler(bot))
