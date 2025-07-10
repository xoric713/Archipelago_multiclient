# multiclient/main.py
import sys
import json
from tkinter import filedialog
import os

def load_paths():
    default_paths = {
        "players": "./players",
        "output": "./output"
    }

    try:
        with open("settings.json", "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "paths" in data:
                return data["paths"]
    except FileNotFoundError:
        pass

    # Try to detect folders
    paths = {}
    for key in default_paths:
        if os.path.isdir(default_paths[key]):
            paths[key] = default_paths[key]
        else:
            print(f"[WARN] Could not find '{key}' folder. Prompting user...")
            paths[key] = filedialog.askdirectory(title=f"Select {key} folder")

    return paths

def main():
    # Check for settings file before anything else
    # Always use settings.json in the multiclient folder
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
    if not os.path.isfile(settings_path):
        print("First time setup detected. No settings.json found.")
        # Look for Archipelago players folder in common install locations
        archipelago_default = os.path.expanduser("~\\Archipelago\\players")
        if os.path.isdir(archipelago_default):
            print(f"Found Archipelago players folder at {archipelago_default}")
            default_players_path = archipelago_default
        else:
            print("Could not find Archipelago 'players' folder. Please select your Archipelago install directory.")
            from tkinter import Tk
            root = Tk()
            root.withdraw()
            arch_dir = filedialog.askdirectory(title="Select Archipelago install directory")
            if not arch_dir:
                print("No directory selected. Exiting setup.")
                sys.exit(1)
            default_players_path = os.path.join(arch_dir, "players")
        # Save a minimal settings.json for future runs in the multiclient folder
        settings = {"paths": {"players": default_players_path, "output": "./output"}}
        with open(os.path.join(os.path.dirname(__file__), "settings.json"), "w") as f:
            json.dump(settings, f, indent=4)
        print(f"Settings saved to {settings_path}. Please restart the application.")
        sys.exit(0)

    if "--gui" in sys.argv:
        from multiclient.gui import MultiClientGUI
        app = MultiClientGUI()
        app.mainloop()
    else:
        print("CLI mode not implemented yet. Use '--gui' to launch GUI.")
    paths = load_paths()
    print(f"Using paths: {paths}")


if __name__ == "__main__":
    main()
