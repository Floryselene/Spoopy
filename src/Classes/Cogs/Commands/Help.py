import discord
from discord import app_commands
from discord.ext import commands
from collections import OrderedDict

from ...Views.EmbedPages import EmbedPageView



class HelpCog(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name="help", description="Displays this message")
    @app_commands.describe(command_name="Optional command name to specify for specific information")
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        prefix = ctx.prefix
        config_prefix = self.bot.config.get_value(0, "PREFIX")

        if f"<@{self.bot.user.id}>" in prefix:
            prefix = f"@ping " # Could do the bot's name, but that can get a bit long
                               # So use "@ping" for simplicity

        if command_name:
            # Retrieve information about a specific command
            command = self.bot.get_command(command_name)
            if command:
                if isinstance(command, commands.Group):
                    await self.send_group_help(ctx, prefix, command)
                else:
                    await self.send_command_help(ctx, prefix, command)
            else:
                embed = discord.Embed(title=self.bot.user.name, description=f"Unknown command - `{command_name}`",
                                      colour=discord.Colour.red())
                await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        else:
            categories = await self.get_command_categories(ctx)

            embeds = []
            for category, commands_list in categories.items():
                category_name = category.replace("Cog", "") # If no name is given to Cog via `name`, derive one from our structure (EG: HelpCog -> Help)
                commands_chunks = [commands_list[i:i + 7] for i in range(0, len(commands_list), 7)]
                for i, commands_chunk in enumerate(commands_chunks):
                    embed = discord.Embed(
                        title=f"Command Category - `{category_name}" + (f" ({i + 1})" if i > 0 else "") + "`",
                        description="Here are the available commands:\n\n", color=discord.Color.blue())
                    for command in commands_chunk:
                        if command.hidden:
                            continue
                        embed.description += f"> `{prefix}{command.qualified_name}` - {command.description}\n\n"

                    embed.description += f"Prefix: `{config_prefix}` or ping\nSlash commands exist too!"
                    embeds.append(embed)

            view = EmbedPageView(embeds)
            view.message = await ctx.reply(embed=embeds[0], view=view, allowed_mentions=discord.AllowedMentions.none())


    async def send_command_help(self, ctx, prefix, command):
        try:
            await command.can_run(ctx)
        except commands.CheckFailure:
            embed = discord.Embed(title=self.bot.user.name, description="You don't have permission to view usage for this command",
                                  colour=discord.Colour.red())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            return

        field_name = f"Command Help - `{command.name}`"
        aliases = command.aliases
        if aliases:
            alias_list = ', '.join(aliases)
            field_name += f"\nAliases - `{alias_list}`"

        embed = discord.Embed(title=field_name, description=command.description, color=discord.Color.blue())

        usage = self.get_command_usage(command, prefix, include_group_name=bool(command.parent))
        if usage:
            embed.add_field(name="Usage", value=f"```{usage}```", inline=False)

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())


    async def send_group_help(self, ctx, prefix, group):
        embeds = []
        filtered_commands = []
        _commands = sorted([command for command in group.commands if not command.hidden], key=lambda c: c.name)

        for command in _commands:
            try:
                await command.can_run(ctx)
                filtered_commands.append(command)
            except commands.CheckFailure:
                pass

        command_chunks = [filtered_commands[i:i + 6] for i in range(0, len(filtered_commands), 6)]

        for i, command_chunk in enumerate(command_chunks):
            embed = discord.Embed(
                title=f"Command Group Help - `{group.name}" + (f" ({i + 1})" if i > 0 else "") + "`",
                description=group.description, color=discord.Color.blue())

            for command in command_chunk:
                usage = self.get_command_usage(command, prefix, include_group_name=True)
                field_name = f"Command - `{command.name}`"

                aliases = command.aliases
                if aliases:
                    alias_list = ', '.join(aliases)
                    field_name += f"\nAliases - `{alias_list}`"

                embed.add_field(name=field_name, value=f"```{usage}```", inline=False)

            embeds.append(embed)

        if embeds:
            view = EmbedPageView(embeds)
            view.message = await ctx.reply(embed=embeds[0], view=view, allowed_mentions=discord.AllowedMentions.none())
        else:
            embed = discord.Embed(title=self.bot.user.name, description="You don't have permission to view usage for this group",
                                  colour=discord.Colour.red())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            return


    @staticmethod
    def get_command_usage(command, prefix, include_group_name=False):
        usage = prefix

        if include_group_name:
            usage += f"{command.full_parent_name.lower()} "

        usage += f"{command.name} "
        params = command.clean_params.values()
        params = [param for param in params if param.name not in ["self", "ctx"]]

        for param in params:
            if param.default != param.empty:
                usage += f"[{param.name}] "
            else:
                usage += f"<{param.name}> "

        return usage.strip()


    async def get_command_categories(self, ctx):
        commands_list = sorted(self.bot.commands, key=lambda c: (c.cog_name or "", c.name))
        categories = OrderedDict()

        for command in commands_list:
            cog_name = command.cog_name or "No Category"

            if cog_name == "Help":
                continue  # Exclude help, because there's only one command, and it's self-explanatory

            if isinstance(command, commands.Group):
                subcommands = sorted(command.commands, key=lambda c: c.name)  # Sort subcommands alphabetically
                filtered_subcommands = []
                for subcommand in subcommands:
                    try:
                        await subcommand.can_run(ctx)
                        filtered_subcommands.append(subcommand)
                    except commands.CheckFailure:
                        pass
                categories.setdefault(cog_name, []).extend(filtered_subcommands)
            else:
                try:
                    await command.can_run(ctx)
                    categories.setdefault(cog_name, []).append(command)
                except commands.CheckFailure:
                    pass

        categories = OrderedDict(sorted(categories.items(), key=lambda x: x[0]))
        return categories



async def setup(bot):
    await bot.add_cog(HelpCog(bot))
