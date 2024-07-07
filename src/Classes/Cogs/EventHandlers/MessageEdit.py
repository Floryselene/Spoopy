import discord
import difflib
from discord.ext import commands
from discord.utils import format_dt
from discord.ext.commands import Context
from discord import Message, Attachment

from ...Functions import download_asset, color_thief



class EditHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before is None or after is None:
            return
        if before.guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(before.guild.id, "EDIT_LOG"))
        blacklisted_targets = self.bot.config.get_value(before.guild.id, "EDIT_BLACKLIST")
        if channel is None:
            return
        if before.author.bot:
            return
        if blacklisted_targets is not None:
            if before.channel.id in blacklisted_targets or before.author.id in blacklisted_targets:
                return

        if before.content == after.content and before.attachments == after.attachments and before.stickers == after.stickers:
            return

        author = before.author
        data = await download_asset(author.display_avatar.url)
        hex_color = color_thief(data)

        embed = discord.Embed(title="Message Edited",
                              color=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{author.name} | {author.id}', icon_url=author.display_avatar.url)

        # Channel and Message ID on the top row
        embed.add_field(name='Channel', value=before.channel.mention, inline=True)
        embed.add_field(
            name='Message ID',
            value=
            f"[{before.id}](https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id})",
            inline=True)

        # Define timestamps
        created_time = before.created_at
        sent_timestamp = format_dt(created_time, style='R')
        edited_time = after.edited_at
        edit_timestamp = format_dt(edited_time, style='R')

        # Filler lol
        embed.add_field(name="", value="", inline=False)

        # Add time fields
        embed.add_field(name="Sent At", value=sent_timestamp, inline=True)
        embed.add_field(name="Edited At", value=edit_timestamp, inline=True)

        if before.content == "":
            og_content = "NULL"
        else:
            og_content = None if len(before.content) > 1024 else before.content
            alt_content = None if len(after.content) > 1024 else after.content

        diff = difflib.ndiff(before.content.splitlines(keepends=True), after.content.splitlines(keepends=True))
        diff_text = '\n'.join(diff)

        # Main content field
        if og_content or alt_content != None:
            embed.add_field(name='Diff',
                            value=f'```diff\n{diff_text}```',
                            inline=False)
        else:
            file_content = diff_text
            # Trying to think of possible exceptions with invalid characters. Use UTF-8 as the preferred
            # but if encoding fails, use latin-1 as it's able to encode practically everything
            try:
                content_file = BytesIO(file_content.encode("utf-8"))
            except UnicodeEncodeError:
                content_file = BytesIO(file_content.encode("latin-1"))

            content_file.seek(0)
            content_attachment = discord.File(content_file, filename=f"{after.id}.txt")
            after.attachments.append(content_attachment)

        # Log stickers
        if before.stickers == after.stickers:
            if before.stickers:
                sticker = before.stickers[0]
                sticker_name = sticker.name if sticker.name else "Unnamed Sticker"
                embed.add_field(name="Sticker Name",
                                value=f'```{sticker_name}```',
                                inline=False)
                embed.set_image(url=sticker.url)

        # Dont even think you can change stickers so I'm not gonna
        # Include extra logic for handling that event

        # Handle attachments
        before_attachments = before.attachments
        after_attachments = after.attachments

        if before_attachments or after_attachments:
            attachment_links = []
            attachments = []

            # Save and prepare attachments from the before message if there haven't been any changes in attachments
            if before_attachments and before_attachments == after_attachments:
                for attachment in before_attachments:
                    attachments.append(await attachment.to_file())
                    attachment_links.append(attachment.url)

            # Save and prepare attachments from the after message if there have been changes in attachments
            elif after_attachments:
                for attachment in after_attachments:
                    try:
                        attachments.append(await attachment.to_file())
                        attachment_links.append(attachment.url)
                    # to_file() wont work if we're creating the attachment
                    # so initialize as discord.File(), and send directly
                    except AttributeError:
                        attachments.append(attachment)

            # Check if attachments have been removed
            if len(after_attachments) < len(before_attachments):
                removed_attachments = [
                    attachment for attachment in before_attachments
                    if attachment not in after_attachments
                ]
                removed_attachment_links = [
                    attachment.url for attachment in removed_attachments
                ]
                embed.add_field(name='Attachments Removed',
                                value='\n'.join(removed_attachment_links),
                                inline=False)

                # Save and upload the removed attachments
                for attachment in removed_attachments:
                    attachments.append(await attachment.to_file())

            # If no attachments were removed, display the "Attachments" field
            if len(attachment_links) > 0 and len(after_attachments) >= len(
                    before_attachments):
                attachment_urls = '\n'.join(attachment_links)
                embed.add_field(name='Attachments',
                                value=attachment_urls,
                                inline=False)

            await channel.send(embed=embed)

            if len(attachments) > 0:
                await channel.send(files=attachments)
        else:
            await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(EditHandler(bot))
