> There are other features, but I dont feel like listing them here  
> Most of the rest are self explanatory anyways, and there's quite a good help command in the bot  
> As it also shows descriptions and usage of commands automatically

# Table of Content
- [Moderation](#moderation)
- [Event Logging](#event-logging)
- [Reaction Roles](#reaction-roles)
- [Twitch Service](#twitch-service)
- [Developer Commands](#developer-commands)

# Moderation
### Overview

Standard moderation commands that allow you to manage your guild's members

### Commands

`ban` - Bans a user from the current guild (supports shadow banning)  
`kick` - Kicks a user from the current guild  
`mute` - Mutes a user using Discord's timeout functionality  
`mutelist` - Shows a list of all active mutes in the server  
`unban` - Unbans a user from the guild  
`unmute` - Removes the mute from a user

### Usage
> <> : required arg
> 
> [] : optional arg
```plaintext
ban <member> <reason>
kick <member> <reason>
mute <member> <duration> <reason>
mutelist
unban <member> <reason>
unmute <member> <reason>
```

# Event Logging
### Overview

Standard event logging for your guild that allow you to be aware of what actions are taking place

### Events

`Bulk Deletion` - Occurs when (usually a bot) deletes a large number of messages all in the same operation  
`Join Mod Log` - Shows when a user joins, any automod flags, warns if account age is young, shows the invite they joined with, as well as who invited them  
`Leave Mod Log` - When a user leaves, shows the action that caused them to leave (IE: Kick / Ban), who invoked said action, the roles the user leaving had, when they joined, etc  
`Message Deletion` - Shows when a message gets deleted. Includes message content, the author of the message, who deleted it (if applicable), and any attachments (if applicable)  
`Message Edit` - Shows when a message gets edited. Includes formatted diff of the message content, the author of the message, timestamps for when it was sent / when it was edited, and any attachments (if applicable)  
`Role Update` - Shows when a user gets a role added, or removed. Shows which role it was, the action taken place (additon, or removal), and who invoked the action  
`Punishment Logging` - Shows when moderation action is taken against a user, as well as who invoked the action
`Welcome Annoucement` - Shows when a user joins the guild. Formats a stylized image card showing their name, and the amount of members in the guild. Can include a custom message if specified  

### Commands
`log` - Sets the event log channels for the guild  
`welcome` - Sets the welcome announcement channel / (optional message) for the guild

### Usage
> <> : required arg
> 
> [] : optional arg
```plaintext
log <typing> <channel> (will auto-suggest typing field)
welcome <channel> [message]
```

# Reaction Roles
### Overview

Allows you to add reacions to a message (by giving the message id) within a certain channel.  
Reacting / Unreacting on one of these reactions will give / take the role set to it from you.  
Supports custom emojis as long as the emoji exists within a server the bot is also in.

### Commands
`role register` - Register a reaction role  
`role remove` - Remove entries tied to a specific Message ID

### Usage
> <> : required arg
> 
> [] : optional arg
```plaintext
role register <channel> <message_id> <emoji> <role>
role remove <channel> <message_id> [emoji] (specify emoji to only remove that entry, or leave empty to remove all entries)
```

# Twitch Service
### Overview

Allows you to set notifications in the guild for when a specific streamer goes live.  
The service will check every minute to see if the streamer in question is live, and will notify (can optionally ping a role) when they are  
If the streamer is live, the service will wait 4 hours before checking again (this is to avoid spam)

### Commands
`twitch setup` - Sets up the Twitch notifier using Twitch API credentials  
`twitch check` - Checks if a specific streamer is live

### Usage
> <> : required arg
> 
> [] : optional arg
```plaintext
twitch setup <name> <client_id> <client_secret> <refresh_token> <access_token> <channel> [role]
twitch check <name>
```

# Developer Commands
### Overview

Just some developer / bot owner commands that let you manage the bot and command tree functionality

### Commands
`cmdtree` - Syncs / Unsyncs the command tree with a scope of Guild / Global  
`cog` - Allows you to manage the loaded cogs (Load, Unload, Reload)

### Usage
> <> : required arg
> 
> [] : optional arg
```plaintext
cmdtree <action> <scope> (will auto-suggest on both fields)
cog <action> <cog> (will auto-suggest on both fields)
```
