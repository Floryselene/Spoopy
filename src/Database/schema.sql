/* Credits to original table structuring go to TalonFloof */
CREATE TABLE IF NOT EXISTS 'Mutes' (
    'guild_id' INTEGER,
    'user_id' INTEGER,
    'expiration' INTEGER,
    'reason' TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS 'MuteIndex' ON 'Mutes' (
    'guild_id',
    'user_id'
);

CREATE TABLE IF NOT EXISTS 'ReactionRoles' (
    'guild_id' INTEGER,
    'message_id' INTEGER,
    'emoji_name' TEXT,
    'role_id' INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS 'ReactionRoleIndex' ON 'ReactionRoles' (
    'guild_id',
    'message_id',
    'emoji_name'
);
