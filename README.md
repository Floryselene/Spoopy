Originally requested to be written by me for a friend-    
You're free to host an instance of this bot for yourself.

# Table of Content
- [Features (Overview)](#features-overview)
- [Installation](#installation)
- [Features (More Detail](/Docs/FEATURES.md)
- [License](/LICENSE)

## Features (Overview)
- Moderation
- Event Logging
- Custom Welcome Announcement (When a member joins the guild)
- Reaction Roles
- Automated Twitch Notification Service (requires API credentials)

And more!

## Installation
- Get your bot's token (not explaining that here, but you can do it [here](https://discord.com/developers/applications))
- Open [.env.example](/src/.env.example), add your token to where it says `TOKEN_GOES_HERE`, and remove `.example` leaving you with just the `.env` file
- To install dependencies you can do `python -m pip install -r requirements.txt` (`requirements.txt` can be found [here](/src/requirements.txt))
- To run simply do `python main.py` (must be inside the [src](/src) directory as this project has relative imports / file handling)
- Enjoy!

### Note!
The bot's default prefix is `.` - though all commands are hybrid (meaning they support both application and prefix invocation)  
You may change the default prefix in `config.json` after it is generated for the first time.  
(You can also ping the bot instead of the prefix, like `@ping help`)


> Created with ♥ by Floryselene
