import aiosqlite



class DatabaseConnection:
    def __init__(self, connection: aiosqlite.Connection):
        self.connection = connection

    async def execute(self, query: str, parameters: tuple = None):
        if parameters:
            await self.connection.execute(query, parameters)
        else:
            await self.connection.execute(query)
        await self.connection.commit()

    async def fetchall(self, query: str, parameters: tuple = None):
        async with self.connection.execute(query, parameters) as cursor:
            rows = await cursor.fetchall()
        return rows

    async def fetchone(self, query: str, parameters: tuple = None):
        async with self.connection.execute(query, parameters) as cursor:
            row = await cursor.fetchone()
        return row



class DatabaseManager:
    def __init__(self, database_connection: DatabaseConnection):
        self.database_connection = database_connection


    async def add_mute(self, guild_id: int, user_id: int, expiration: int, reason: str):
        try:
            await self.database_connection.execute(
                "INSERT INTO Mutes (guild_id, user_id, expiration, reason) VALUES (?, ?, ?, ?)",
                (guild_id, user_id, expiration, reason)
            )
        except aiosqlite.IntegrityError:
            # If there's a unique constraint violation, the user is already muted in this guild
            # In this case, just update the existing mute
            await self.database_connection.execute(
                "UPDATE Mutes SET expiration = ?, reason = ? WHERE guild_id = ? AND user_id = ?",
                (expiration, reason, guild_id, user_id)
            )


    async def remove_mute(self, guild_id: int, user_id: int):
        await self.database_connection.execute(
            "DELETE FROM Mutes WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )


    async def get_mutes(self, guild_id: int):
        rows = await self.database_connection.fetchall(
            "SELECT user_id, expiration, reason FROM Mutes WHERE guild_id = ?",
            (guild_id,)
        )
        return rows


    async def add_reaction_role(self, guild_id: int, message_id: int, emoji_name: str, role_id: int):
        try:
            await self.database_connection.execute(
                "INSERT INTO ReactionRoles (guild_id, message_id, emoji_name, role_id) VALUES (?, ?, ?, ?)",
                (guild_id, message_id, emoji_name, role_id)
            )
        except aiosqlite.IntegrityError:
            await self.database_connection.execute(
                "UPDATE ReactionRoles SET role_id = ? WHERE guild_id = ? AND message_id = ? AND emoji_name = ?",
                (role_id, guild_id, message_id, emoji_name)
            )


    async def remove_reaction_role(self, guild_id: int, message_id: int, emoji_name: str = None):
        if emoji_name:
            # Remove a specific reaction role
            await self.database_connection.execute(
                "DELETE FROM ReactionRoles WHERE guild_id = ? AND message_id = ? AND emoji_name = ?",
                (guild_id, message_id, emoji_name)
            )
        else:
            # Remove all reaction roles for a given guild and message
            await self.database_connection.execute(
                "DELETE FROM ReactionRoles WHERE guild_id = ? AND message_id = ?",
                (guild_id, message_id)
            )


    async def get_reaction_role(self, guild_id: int, message_id: int, emoji_name: str):
        row = await self.database_connection.fetchone(
            "SELECT role_id FROM ReactionRoles WHERE guild_id = ? AND message_id = ? AND emoji_name = ?",
            (guild_id, message_id, emoji_name)
        )
        if row:
            return row[0]
        else:
            return None
