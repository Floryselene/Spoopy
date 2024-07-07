import io
import discord
from PIL import Image
from discord.ext import commands
from discord.utils import format_dt

from ...Functions import download_asset, color_thief
from ...Misc.WelcomeCard.CardMaker import ImageEditor, is_color_too_dark



class WelcomeAnnouncementHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild is None:
            return
        channel = self.bot.get_channel(self.bot.config.get_value(member.guild.id, "WELCOME_ANNOUNCE_CHANNEL"))
        if channel is None:
            return
        welcome_message = self.bot.config.get_value(member.guild.id, "WELCOME_ANNOUNCE_MESSAGE")

        editor = ImageEditor()
        profile_pic = await download_asset(member.display_avatar.url)
        dominant_color = color_thief(profile_pic)

        background_image_path = "./Classes/Misc/WelcomeCard/Images/Dark.png"
        if is_color_too_dark(dominant_color):
            background_image_path = "./Classes/Misc/WelcomeCard/Images/Light.png"

        background_image = Image.open(background_image_path).convert("RGBA")
        foreground_image = Image.open(io.BytesIO(profile_pic)).convert("RGBA")

        recolored_image = editor.recolor(background_image, dominant_color + "FF")
        circular_image = editor.add_circular_image(foreground_image, add_border=True)
        recolored_image.paste(circular_image, (30, 38), circular_image)

        member_name = member.name
        if member.discriminator != "0":
            member_name = f"{member.name}#{member.discriminator}"

        editor.add_text(recolored_image, f"{member_name} just joined the server ~ !", "./Classes/Misc/WelcomeCard/Fonts/PlusJakartaSans-ExtraBold.ttf", 25, (200, 90))
        editor.add_text(recolored_image, f"#{len(member.guild.members)} Members", "./Classes/Misc/WelcomeCard/Fonts/PlusJakartaSans-Medium.ttf", 20, (200, 120))

        image_bytes = io.BytesIO()
        recolored_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        file = discord.File(image_bytes, filename='welcome.png')

        if welcome_message is not None:
            await channel.send(welcome_message, file=file)
        else:
            await channel.send(file=file)



async def setup(bot):
    await bot.add_cog(WelcomeAnnouncementHandler(bot))
