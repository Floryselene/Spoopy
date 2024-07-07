import discord
from discord.ext import commands

from ...Functions import download_asset, color_thief



class RoleHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_updates = {}  # Dictionary to track role updates


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(self.bot.config.get_value(before.guild.id, "ROLE_LOG"))
        if channel is None:
            return

        data = await download_asset(after.display_avatar.url)
        hex_color = color_thief(data)
        embed = discord.Embed(title="Role Update",
                              color=discord.Color(int(hex_color[1:], 16)), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{after.name} | {after.id}', icon_url=after.display_avatar.url)

        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [
                role for role in before.roles if role not in after.roles
            ]

            # Check if the user has an existing role update entry
            if after.id in self.role_updates:
                # Remove duplicates from added and removed roles
                added_roles = list(
                    set(self.role_updates[after.id]["added_roles"] + added_roles))
                removed_roles = list(
                    set(self.role_updates[after.id]["removed_roles"] + removed_roles))
                # Update the entry with the deduplicated roles
                self.role_updates[after.id]["added_roles"] = added_roles
                self.role_updates[after.id]["removed_roles"] = removed_roles
            else:
                # Create a new entry for the user's role update
                self.role_updates[after.id] = {
                    "added_roles": added_roles,
                    "removed_roles": removed_roles
                }

        # Get the audit log entries for role updates
        async for entry in after.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id and entry.created_at > after.joined_at:
                updater = entry.user
                break
        else:
            updater = None
            updater_link = None

        if updater:
            embed.set_footer(text=f"{updater.name} | {updater.id}",
                             icon_url=updater.display_avatar.url)

        description = f"> **Profile** - {after.mention}\n"

        # Check if the user has an existing role update entry
        if after.id in self.role_updates:
            role_update = self.role_updates.pop(
                after.id)  # Retrieve and remove the entry

            added_roles = role_update["added_roles"]
            removed_roles = role_update["removed_roles"]

            if added_roles:
                added_mentions = ', '.join(
                    list(set([role.mention for role in added_roles])))
                description += f"> **Added Roles** - {added_mentions}\n"

            if removed_roles:
                removed_mentions = ', '.join(
                    list(set([role.mention for role in removed_roles])))
                description += f"> **Removed Roles** - {removed_mentions}"

            if description != "> **Profile** - {after.mention}":
                embed.description = description
                await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(RoleHandler(bot))
