import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
from typing import Dict, Any
from multiclient.builder import YAMLBuilder, get_available_games
from worlds.AutoWorld import AutoWorldRegister


def get_game_name_map() -> dict:
    return {
        world.__module__.split('.')[-1]: world.game
        for world in AutoWorldRegister.world_types.values()
    }


import tkinter as tk
from tkinter import ttk, filedialog
import yaml


class SettingsEditor(tk.Toplevel):
    def __init__(self, master, builder, slot_name, folder, game_name):
        super().__init__(master)
        self.title(f"{slot_name} - {game_name} Settings")
        self.builder = builder
        self.slot = slot_name
        self.folder = folder
        self.game_name = game_name
        self.entries = {}

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        raw_template = self.load_template_defaults()
        saved_data = self.builder.get_settings_for_slot_game(self.slot, self.folder)
        saved_values = saved_data.get("data", {}) if isinstance(saved_data, dict) else {}


        if not raw_template:
            from tkinter import messagebox
            messagebox.showerror("Template Error", "No template data found for this game. Please ensure the template YAML is valid and not empty.")
            self.destroy()
            return

        for key, options in raw_template.items():
            if isinstance(options, dict):
                frame = ttk.LabelFrame(self.scroll_frame, text=key)
                frame.pack(fill="x", padx=4, pady=4)
                self.entries[key] = {}

                saved_weights = saved_values.get(key, {})

                def add_option_row(opt_key="", opt_value=""):
                    row = ttk.Frame(frame)
                    row.pack(fill="x", padx=2, pady=1)
                    key_var = tk.StringVar(value=opt_key)
                    val_var = tk.StringVar(value=str(opt_value))
                    tk.Entry(row, textvariable=key_var, width=20).pack(side="left", padx=(0, 4))
                    tk.Entry(row, textvariable=val_var, width=6).pack(side="left")
                    self.entries[key][opt_key] = val_var  # ✅ Use plain string for key

                # Populate existing or template keys
                unique_keys = set(options.keys()) | set(saved_weights.keys())
                for opt_key in sorted(unique_keys, key=str):
                    add_option_row(opt_key, saved_weights.get(opt_key, 0))

                ttk.Button(frame, text="+ Add Option", command=add_option_row).pack(anchor="w", padx=4)

            else:
                label = ttk.Label(self.scroll_frame, text=key)
                label.pack(anchor="w", padx=4)
                val = tk.StringVar(value=str(saved_values.get(key, options)))
                entry = ttk.Entry(self.scroll_frame, textvariable=val)
                entry.pack(fill="x", padx=4, pady=2)
                self.entries[key] = val

        ttk.Button(self.scroll_frame, text="Save", command=self.save_settings).pack(pady=10)

    def load_template_defaults(self):
        import os, json
        # Load settings.json to get the players path
        # Always use settings.json in the multiclient folder
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        players_path = None
        templates_dir = None
        try:
            with open(settings_path, "r", encoding="utf-8") as sf:
                settings = json.load(sf)
            players_path = settings.get("paths", {}).get("players")
            if players_path:
                templates_dir = os.path.join(players_path, "templates")
        except Exception:
            pass
        if not templates_dir or not os.path.isdir(templates_dir):
            from tkinter import messagebox
            messagebox.showerror("Template Error", "Could not find templates directory. Check your settings.json paths.")
            return {}

        found_template = None
        # Iterate through all YAML files in templates_dir
        for fname in os.listdir(templates_dir):
            if fname.endswith(".yaml"):
                fpath = os.path.join(templates_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    # Look for a 'game' key at the top level
                    if isinstance(data, dict):
                        game_val = data.get("game")
                        if game_val == self.game_name:
                            found_template = fpath
                            break
                except Exception:
                    continue
        if found_template:
            with open(found_template, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            # Save the template path in settings.json
            try:
                if os.path.isfile(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as sf:
                        settings = json.load(sf)
                else:
                    settings = {}
            except Exception:
                settings = {}
            if "templates" not in settings:
                settings["templates"] = {}
            settings["templates"][self.game_name] = found_template
            # Always save settings.json in the multiclient folder
            with open(os.path.join(os.path.dirname(__file__), "settings.json"), "w", encoding="utf-8") as sf:
                json.dump(settings, sf, indent=4)
            return data.get(self.game_name, {}) if data else {}
        else:
            from tkinter import messagebox
            messagebox.showerror("Template Error", f"No template with game: {self.game_name} found in templates folder.")
            return {}


    def save_settings(self):
        final = {}
        option_types = {}

        for key, entry in self.entries.items():
            if isinstance(entry, dict):
                result = {}
                for key_var, val_var in entry.items():
                    k = key_var.get()
                    v = val_var.get()
                    try:
                        v = int(v) if v.isdigit() else v
                    except Exception:
                        pass
                    if k:
                        result[k] = v
                final[key] = result
                option_types[key] = dict
            else:
                raw = entry.get()
                try:
                    final[key] = int(raw) if raw.isdigit() else raw
                except Exception:
                    final[key] = raw
                option_types[key] = type(final[key])

        self.builder.set_settings_for_slot_game(self.slot, self.folder, final, option_types)
        self.destroy()


class YAMLWizard(tk.Toplevel):
    def __init__(self, master, builder: YAMLBuilder):
        super().__init__(master)
        self.title("New Game - YAML Wizard")
        self.builder = builder
        self.games = get_available_games()
        self.game_name_lookup = get_game_name_map()
        self.selected_slot = None
        self.slot_name_var = tk.StringVar()
        ttk.Label(self, text="New Player Name:").pack()
        ttk.Entry(self, textvariable=self.slot_name_var).pack(fill="x")

        self.slot_listbox = tk.Listbox(self)
        self.slot_listbox.pack(fill="x")
        self.slot_listbox.bind("<<ListboxSelect>>", self.refresh_games)

        ttk.Button(self, text="Add Slot", command=self.add_slot).pack(pady=5)

        self.left_list = tk.Listbox(self, selectmode=tk.SINGLE)
        self.right_list = tk.Listbox(self, selectmode=tk.SINGLE)
        self.left_list.pack(side="left", expand=True, fill="both")
        self.right_list.pack(side="right", expand=True, fill="both")

        control_frame = ttk.Frame(self)
        control_frame.pack()
        ttk.Button(control_frame, text="→", command=self.assign_game).pack()
        ttk.Button(control_frame, text="←", command=self.remove_game).pack()
        ttk.Button(control_frame, text="Edit Settings", command=self.edit_settings).pack()

        ttk.Button(self, text="Save Config", command=self.save_config).pack(side="left")
        ttk.Button(self, text="Load Config", command=self.load_config).pack(side="left")
        ttk.Button(self, text="Export Final YAML", command=self.export_yaml).pack(side="right")

    def add_slot(self):
        name = self.slot_name_var.get().strip() or f"Player{len(self.builder.slots) + 1}"
        self.builder.add_slot(name)
        self.slot_listbox.insert("end", name)
        self.slot_name_var.set("")  # Clear entry field


    def refresh_games(self, event=None):
        if self.slot_listbox.curselection():
            self.selected_slot = self.slot_listbox.get(self.slot_listbox.curselection()[0])

        all_game_folders = sorted(self.games, key=lambda g: g.name)
        current_games = self.builder.get_games_for_slot(self.selected_slot)

        self.left_list.delete(0, "end")
        self.right_list.delete(0, "end")

        for g in all_game_folders:
            if g.folder in current_games:
                self.right_list.insert("end", g.name)
            else:
                self.left_list.insert("end", g.name)
        print("Slot:", self.selected_slot)
        print("Slot Games:", current_games)
        print("All Games:", [(g.name, g.folder) for g in self.games])




    def assign_game(self):
        sel = self.left_list.curselection()
        if not sel or not self.selected_slot:
            return
        selected_name = self.left_list.get(sel[0])
        game_entry = next((g for g in self.games if g.name == selected_name), None)
        if game_entry:
            print(f"Adding {game_entry.folder} to {self.selected_slot}")
            self.builder.add_game_to_slot(self.selected_slot, game_entry)
            self.refresh_games()
            print("Games after assignment:", self.builder.get_games_for_slot(self.selected_slot))

        else:
            print(f"GameEntry not found for {selected_name}")
        self.left_list.delete(0, "end")
        self.right_list.delete(0, "end")
        self.refresh_games()




    def remove_game(self):
        sel = self.right_list.curselection()
        if not sel or not self.selected_slot:
            return
        game_name = self.right_list.get(sel[0])
        game_entry = next((g for g in self.games if g.name == game_name), None)
        if game_entry:
            self.builder.remove_game_from_slot(self.selected_slot, game_entry)
            self.refresh_games()
        self.left_list.delete(0, "end")
        self.right_list.delete(0, "end")
        self.refresh_games()


    def edit_settings(self):
        sel = self.right_list.curselection()
        if not sel or not self.selected_slot:
            return
        game_name = self.right_list.get(sel[0])
        folder = next((g.folder for g in self.games if g.name == game_name), game_name)
        SettingsEditor(self, self.builder, self.selected_slot, folder, game_name)


    def save_config(self):
        path = filedialog.asksaveasfilename(defaultextension=".yaml")
        if path:
            self.builder.export_config(path)

    def load_config(self):
        path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml")])
        if path:
            self.builder.load_config(path)
            self.slot_listbox.delete(0, "end")
            for slot in self.builder.slots:
                self.slot_listbox.insert("end", slot.name)
            self.refresh_games()

    def export_yaml(self):
        path = filedialog.asksaveasfilename(defaultextension=".yaml")
        if path:
            self.builder.export_yaml(path)
