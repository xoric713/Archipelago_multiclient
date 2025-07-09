# multiclient/builder.py

import yaml
from typing import List, Dict, Any, Optional
from worlds.AutoWorld import AutoWorldRegister

def clean_empty_structs(obj, expected_types=None):
    if expected_types is None:
        expected_types = {}

    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            sub_type = expected_types.get(k) if isinstance(expected_types, dict) else None
            cleaned[k] = clean_empty_structs(v, sub_type)
        if not cleaned and expected_types == list:
            return []
        return cleaned

    elif isinstance(obj, list):
        return [clean_empty_structs(v) for v in obj]

    elif obj == {} and expected_types == list:
        return []

    else:
        return obj


class GameEntry:
    def __init__(self, folder: str, name: str):
        self.folder = folder
        self.name = name

class SlotConfig:
    def __init__(self, name: str):
        self.name = name
        self.games: List[str] = []
        self.settings: Dict[str, Dict[str, Any]] = {}

    def to_dict(self):
        return {
            "name": self.name,
            "games": self.games,
            "settings": self.settings
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        slot = SlotConfig(data["name"])
        slot.games = data.get("games", [])
        slot.settings = data.get("settings", {})
        return slot

class YAMLBuilder:
    def __init__(self):
        self.slots: List[SlotConfig] = []
        self.settings: Dict[str, Dict[str, dict]] = {}  # slot_name -> game_folder -> settings dict


    def add_slot(self, name: str):
        self.slots.append(SlotConfig(name))

    def get_slot(self, name: str) -> Optional[SlotConfig]:
        return next((slot for slot in self.slots if slot.name == name), None)

    def set_games_for_slot(self, name: str, games: List[str]):
        slot = self.get_slot(name)
        if slot:
            slot.games = games
    def get_settings_for_slot_game(self, slot_name: str, game_folder: str) -> dict:
        return self.settings.get(slot_name, {}).get(game_folder, {})

    def set_settings_for_slot_game(self, name: str, folder: str, settings: Dict[str, Any], option_types: Dict[str, type]):
        slot = self.get_slot(name)
        if slot:
            slot.settings[folder] = {
                "data": settings,
                "types": option_types
            }
    def get_games_for_slot(self, slot_name: str) -> list[str]:
        for slot in self.slots:
            if slot.name == slot_name:
                return slot.games
        return []

    def add_game_to_slot(self, slot_name: str, game: GameEntry):
        slot = self.get_slot(slot_name)
        if slot and game.folder not in slot.games:
            slot.games.append(game.folder)

    def remove_game_from_slot(self, slot_name: str, game: GameEntry):
        slot = self.get_slot(slot_name)
        if slot and game.folder in slot.games:
            slot.games.remove(game.folder)

    def export_yaml(self, filepath: str):
        from worlds.AutoWorld import AutoWorldRegister

        final_output = []

        for slot in self.slots:
            game_weights = {}
            game_name_lookup = {}

            for folder in slot.games:
                for world_type in AutoWorldRegister.world_types.values():
                    if folder in world_type.__module__:
                        game_name = world_type.game
                        game_weights[game_name] = 50  # default weight
                        game_name_lookup[folder] = game_name
                        break

            slot_yaml = {
                "name": slot.name,
                "description": f"Generated template for {slot.name}",
                "game": game_weights,
                "requires": {"version": "0.4.1"},
            }

            for folder, setting_obj in slot.settings.items():
                settings_data = setting_obj.get("data", {})
                settings_types = setting_obj.get("types", {})
                game_name = game_name_lookup.get(folder)
                if game_name:
                    slot_yaml[game_name] = clean_empty_structs(settings_data, settings_types)

            final_output.append(slot_yaml)

        # Use yaml.dump_all, but skip the first '---'
        yaml_string = yaml.dump_all(final_output, sort_keys=False, explicit_start=True)
        yaml_string = yaml_string.lstrip("---\n")  # Remove first document marker only

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_string)



    def save_config(self, filepath: str):
        data = [slot.to_dict() for slot in self.slots]
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump({"slots": data}, f, sort_keys=False)

    def load_config(self, filepath: str):
        self.slots.clear()
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            for slot_data in data.get("slots", []):
                self.slots.append(SlotConfig.from_dict(slot_data))

    def clear(self):
        self.slots.clear()
import os
import importlib.util

from worlds.AutoWorld import AutoWorldRegister

def get_game_name_map() -> dict[str, str]:
    return {
        world.__module__.split('.')[-1]: world.game
        for world in AutoWorldRegister.world_types.values()
    }


def get_available_games() -> List[GameEntry]:
    entries = []
    for world_type in AutoWorldRegister.world_types.values():
        try:
            name = world_type.game
            module = world_type.__module__
            folder = module.split(".")[1] if "." in module else module
            entries.append(GameEntry(folder=folder, name=name))
        except Exception as e:
            print(f"[ERROR] Failed to load world class: {e}")
    return sorted(entries, key=lambda g: g.name.lower())
