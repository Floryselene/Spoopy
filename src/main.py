import re
import os
import discord
import platform
import aiosqlite
from dotenv import load_dotenv
from discord.ext import commands

from Classes.Utils.Config import JSONConfig
from Database.Database import DatabaseManager, DatabaseConnection
from Classes.Utils.InviteTracker import InviteTracker



intents = discord.Intents.default()
intents.message_content = True
intents.members = True



class TestingBot(commands.AutoShardedBot):
    config = JSONConfig(f"./config.json")


    def __init__(self, intents):
        super().__init__(command_prefix=commands.when_mentioned_or(self.config.get_value(0, "PREFIX")), intents=intents, help_command=None)
        self.database = None
        self.invite_tracker = InviteTracker(self)


    async def init_db(self):
        db_name = "Database.db"
        async with aiosqlite.connect(f"./Database/{db_name}") as db:
            with open(f"./Database/schema.sql") as file:
                await db.executescript(file.read())
            await db.commit()

        connection = DatabaseConnection(await aiosqlite.connect(f"./Database/{db_name}"))
        self.database = DatabaseManager(connection)


    async def fetch_cogs(self):
        path = f"./Classes/Cogs"
        cogs = []

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                for file in os.listdir(item_path):
                    if file.endswith(".py"):
                        # Forget if windows uses \\ in this or not, so to be safe, just replace it as well
                        relative_path = re.sub(r'[/\\]', '.', os.path.join("Classes", "Cogs", item, file)[:-3])
                        cogs.append(relative_path)

        return cogs


    async def load_cogs(self):
        cogs = await self.fetch_cogs()

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded extension '{cog}'")
            except Exception as e:
               exception = f"{type(e).__name__}: {e}"
               print(exception)


    async def setup_hook(self):
        print(f'Logged in as {self.user.name}#{self.user.discriminator}')
        print(f"discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")
        await self.init_db()
        await self.load_cogs()


    async def on_ready(self):
        self.uptime = discord.utils.utcnow()
        print("Ready!")


    async def on_command_error(self, ctx: commands.Context, error):
        error_messages = {
            commands.CommandNotFound: None,
            commands.MissingRequiredArgument: "A required argument is missing. Please provide it, or check the help command for further reference",
            commands.MissingPermissions: "You do not have adequate permissions to run this command",
            commands.errors.NoPrivateMessage: "This command can only be run in a guild",
            commands.errors.NotOwner: "This command can only be run by the bot's owner"
        }

        for error_type, message in error_messages.items():
            if isinstance(error, error_type):
                if message is not None:
                    embed = discord.Embed(
                        title=self.user.name,
                        description=message,
                        colour=discord.Colour.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
                return

        embed = discord.Embed(
            title=self.user.name,
            description=f"An internal error occurred while processing this command\n```\n{str(error)}\n```",
            colour=discord.Colour.red(),
            timestamp=discord.utils.utcnow()
        )
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        await super().on_command_error(ctx, error)



load_dotenv()

bot = TestingBot(intents=intents)
bot.run(os.getenv("TOKEN"))
