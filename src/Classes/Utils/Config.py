import os
import json



class JSONConfig:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self._load_config()


    def _load_config(self):
        if not os.path.exists(self.config_file):
            self._create_default_config()
        with open(self.config_file) as file:
            config = json.load(file)
        return config


    def _create_default_config(self):
        default_config = {
            "0": {
                "PREFIX": "."
            }
        }
        with open(self.config_file, 'w') as file:
            json.dump(default_config, file, indent=4)


    def get_value(self, guild_id, key_name):
        if str(guild_id) in self.config:
            return self.config[str(guild_id)].get(key_name)
        else:
            return None


    def add_entry(self, guild_id, key_name, value, value_type):
        if not str(guild_id) in self.config:
            self.config[str(guild_id)] = {}

        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list
        }

        if value_type not in type_map:
            raise ValueError("Invalid value type. Supported types are 'str', 'int', 'float', 'bool', and 'dict'.")

        conversion_func = type_map[value_type]
        self.config[str(guild_id)][key_name] = conversion_func(value)
        self._save_config()


    def remove_entry(self, guild_id, key_name):
        if str(guild_id) in self.config:
            if key_name in self.config[str(guild_id)]:
                del self.config[str(guild_id)][key_name]
                self._save_config()


    #######################################################
    # Depreciated                                         #
    # Moved reaction role logic to the aiosqlite database #
    #######################################################
    """
    def get_reaction_value(self, guild_id, message_id, unicode_emoji):
        guild_id_str = str(guild_id)
        message_id_str = str(message_id)

        if guild_id_str in self.config and "reaction_roles" in self.config[guild_id_str]:
            reaction_roles = self.config[guild_id_str]["reaction_roles"]
            if message_id_str in reaction_roles and unicode_emoji in reaction_roles[message_id_str]:
                return reaction_roles[message_id_str][unicode_emoji]
        return None


    def add_reaction_role(self, guild_id, message_id, unicode_emoji, role_id, value_type="list"):
        key_name = "reaction_roles"
        guild_id_str = str(guild_id)
        message_id_str = str(message_id)

        if guild_id_str not in self.config:
            self.config[guild_id_str] = {}
        if key_name not in self.config[guild_id_str]:
            self.config[guild_id_str][key_name] = {}
        if not isinstance(self.config[guild_id_str][key_name], dict):
            self.config[guild_id_str][key_name] = {}
        if message_id_str not in self.config[guild_id_str][key_name]:
            self.config[guild_id_str][key_name][message_id_str] = {}

        self.config[guild_id_str][key_name][message_id_str][unicode_emoji] = role_id
        self._save_config()
    """


    def _save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)
