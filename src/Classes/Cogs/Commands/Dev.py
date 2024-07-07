import discord
from discord import app_commands
from discord.ext import commands



class DevCog(commands.Cog, name="Developer Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.tree_actions = {
            "SYNC": {
                "GLOBAL": self.sync_global,
                "GUILD": self.sync_guild,
            },
            "UNSYNC": {
                "GLOBAL": self.unsync_global,
                "GUILD": self.unsync_guild,
            },
        }


    @commands.is_owner()
    @commands.hybrid_command(name="cmdtree", description="Syncs / Unsyncs the command tree")
    @app_commands.describe(action="The action to perform (sync, or unsync)", scope="The scope of the action (global, or guild)")
    @app_commands.default_permissions(administrator=True)
    async def cmdtree(self, ctx: commands.Context, action: str, scope: str):
        action_dict = self.tree_actions.get(action.upper(), None)

        if not action_dict:
            embed = discord.Embed(title=self.bot.user.name, description=f"Invalid action. Must be `Sync` or `Unsync`", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            return

        scope_func = action_dict.get(scope.upper(), None)

        if not scope_func:
            embed = discord.Embed(title=self.bot.user.name, description=f"Invalid scope. Must be `Global` or `Guild`", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            return

        await ctx.typing()
        await scope_func(ctx)


    @commands.is_owner()
    @commands.hybrid_command(name="cog", description="Manage cogs")
    @app_commands.describe(action="The action to perform (load, unload, or reload)", cog="The name of the cog")
    @app_commands.default_permissions(administrator=True)
    async def cog(self, ctx: commands.Context, action: str, cog: str):
        try:
            if action.lower() == "load":
                await self.bot.load_extension(f"{cog}")
                embed = discord.Embed(description=f"Successfully loaded `{cog}`", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
            elif action.lower() == "unload":
                await self.bot.unload_extension(f"{cog}")
                embed = discord.Embed(description=f"Successfully unloaded `{cog}`", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
            elif action.lower() == "reload":
                await self.bot.reload_extension(f"{cog}")
                embed = discord.Embed(description=f"Successfully reloaded `{cog}`", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
            else:
                embed = discord.Embed(description=f"Invalid action: `{action}`", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())
        except Exception as e:
            embed = discord.Embed(description=f"Could not {action} `{cog}`: {e}", colour=discord.Colour.red(), timestamp=discord.utils.utcnow())

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())



    async def sync_global(self, ctx: commands.Context):
        await self.bot.tree.sync()
        embed = discord.Embed(title=self.bot.user.name, description=f"Successfully synced global command tree (May take up to 48h to show up)", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    async def sync_guild(self, ctx: commands.Context):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        embed = discord.Embed(title=self.bot.user.name, description=f"Successfully synced command tree for this guild", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    async def unsync_global(self, ctx: commands.Context):
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()
        embed = discord.Embed(title=self.bot.user.name, description=f"Successfully unsynced global command tree", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    async def unsync_guild(self, ctx: commands.Context):
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        embed = discord.Embed(title=self.bot.user.name, description=f"Successfully unsynced command tree for this guild", colour=discord.Colour.green(), timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())


    @cmdtree.autocomplete("action")
    async def autocomplete_action(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        actions = ['Sync', 'Unsync']
        return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]

    @cmdtree.autocomplete("scope")
    async def autocomplete_action(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        actions = ['Global', 'Guild']
        return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]

    @cog.autocomplete("action")
    async def autocomplete_action(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        actions = ['Load', 'Unload', 'Reload']
        return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]

    @cog.autocomplete("cog")
    async def autocomplete_action(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        actions = await self.bot.fetch_cogs()
        return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]



async def setup(bot):
    await bot.add_cog(DevCog(bot))
