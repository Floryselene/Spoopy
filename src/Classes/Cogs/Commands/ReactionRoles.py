import discord
from discord.ext import commands
from discord import PartialEmoji, app_commands



class ReactionRolesCog(commands.Cog, name="Reaction Role Configuration"):
    def __init__(self, bot):
        self.bot = bot


    @commands.guild_only()
    @commands.hybrid_group(name="role", description="Command Group that manages reaction roles")
    @commands.has_permissions(manage_roles=True)
    @app_commands.default_permissions(manage_roles=True)
    async def role(self, ctx: commands.Context):
        pass


    @commands.guild_only()
    @role.command(name="register", description="Register a reaction role")
    @app_commands.describe(channel="The channel to look in", message_id="The message ID to look for", emoji="The emoji to use", role="The role to give")
    @app_commands.default_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def register_role(self, ctx, channel: discord.TextChannel, message_id: str, emoji, role: discord.Role):
        message = await channel.fetch_message(message_id)
        emoji_obj = PartialEmoji.from_str(emoji)
        await message.add_reaction(emoji_obj)
        await self.bot.database.add_reaction_role(ctx.guild.id, message_id, emoji, role.id)
        embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.blurple(), description=f"Set {emoji_obj} to give {role.mention} on the selected message", timestamp=discord.utils.utcnow())
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    @commands.guild_only()
    @role.command(name="remove", description="Remove entries tied to a specific Message ID")
    @app_commands.describe(channel="The channel to look in", message_id="The message ID to look for", emoji="The emoji to remove (If none is provided, will remove ALL of them)")
    @app_commands.default_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def remove_role_entries(self, ctx, channel: discord.TextChannel, message_id: str, emoji=None):
        message = await channel.fetch_message(message_id)

        if emoji:
            emoji_obj = PartialEmoji.from_str(emoji)
            await self.bot.database.remove_reaction_role(ctx.guild.id, message_id, emoji)
            await message.clear_reaction(emoji_obj)
            embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.blurple(), description=f"Removed {emoji_obj} as an option on the selected message", timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)
        else:
            await self.bot.database.remove_reaction_role(ctx.guild.id, message_id)
            for reaction in message.reactions:
                await message.clear_reaction(reaction.emoji)
            embed = discord.Embed(title=self.bot.user.name, colour=discord.Colour.blurple(), description=f"Removed all options on the selected message", timestamp=discord.utils.utcnow())
            await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


    # Derived from Arthurdw/Reaction-Role
    # Rewritten to work with sqlite
    # Thank youuu!!
    async def process_reaction(self, payload: discord.RawReactionActionEvent, r_type=None) -> None:
        if payload.user_id == self.bot.user.id:
            return None

        guild_id = payload.guild_id
        message_id = payload.message_id
        emoji_name = str(payload.emoji)

        role_id = await self.bot.database.get_reaction_role(guild_id, message_id, emoji_name)

        if role_id is not None:
            guild = self.bot.get_guild(guild_id)
            user = await guild.fetch_member(payload.user_id)
            role = guild.get_role(role_id)

            if role is None:
                pass
            elif r_type == "add":
                await user.add_roles(role)
            elif r_type == "remove":
                await user.remove_roles(role)
            else:
                pass


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.process_reaction(payload, "add")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.process_reaction(payload, "remove")



async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))
