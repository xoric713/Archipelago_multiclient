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
    def destroy(self):
        super().destroy()
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

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")

        # Windows and MacOS
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # Linux (event.num 4=up, 5=down)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # Use slot name for temp file
        import os, json
        self._template = self.load_template_with_comments_attached()
        temp_file_name = f"{self.slot}.temp"
        temp_file_path = os.path.join(os.path.dirname(__file__), temp_file_name)
        self.temp_file_path = temp_file_path
        # Load or initialize [slot name].temp as a master dict of games
        if os.path.exists(temp_file_path):
            try:
                with open(temp_file_path, "r", encoding="utf-8") as f:
                    temp_data = json.load(f)
            except Exception:
                temp_data = {}
        else:
            temp_data = {}

        if not isinstance(temp_data, dict):
            temp_data = {}

        # Use game_name as the key for this game's working data
        game_key = self.game_name
        # Only operate within the game's own dict in temp file
        if game_key not in temp_data or not isinstance(temp_data[game_key], dict):
            saved_data = self.builder.get_settings_for_slot_game(self.slot, self.folder)
            saved_values = saved_data.get("data", {}) if isinstance(saved_data, dict) else {}
            def extract_values(template, saved):
                if isinstance(template, dict):
                    result = {}
                    for k, v in template.items():
                        if k == '__HEADER__':
                            continue
                        elif isinstance(v, dict) and 'value' not in v:
                            result[k] = extract_values(v, saved.get(k, {}))
                        elif isinstance(v, dict) and 'value' in v:
                            result[k] = saved.get(k, v['value'])
                        else:
                            result[k] = saved.get(k, v)
                    for k, v in saved.items():
                        if k not in result:
                            result[k] = v
                    return result
                else:
                    return saved if saved else template
            temp_data[game_key] = extract_values(self._template, saved_values)
            with open(temp_file_path, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, indent=2)
        # All operations from here on are scoped to this game's dict only
        self.temp_data = temp_data
        self.game_key = game_key
        self.working_data = self.temp_data[self.game_key]

        def save_working_data():
            self.temp_data[self.game_key] = self.working_data
            with open(self.temp_file_path, "w", encoding="utf-8") as f:
                json.dump(self.temp_data, f, indent=2)

        # Show header comment if present
        header_comment = self._template.get('__HEADER__')
        if header_comment:
            header_label = ttk.Label(self.scroll_frame, text=header_comment, foreground="#888888", wraplength=600, justify="left")
            header_label.pack(anchor="w", padx=4, pady=(6, 12))



        def render_options(parent, template, values):
            # Clear previous widgets
            for widget in parent.winfo_children():
                widget.destroy()
            for group_key, group_values in values.items():
                frame = ttk.LabelFrame(parent, text=group_key)
                frame.pack(fill="x", padx=4, pady=4)
                def render_group(gkey, gvalues, gframe):
                    # If gvalues is an empty dict, treat as value (show entry box with {})
                    if isinstance(gvalues, dict) and not gvalues:
                        row = ttk.Frame(gframe)
                        row.pack(fill="x", padx=2, pady=1)
                        val_var = tk.StringVar(value="{}")
                        val_entry = tk.Entry(row, textvariable=val_var, width=40)
                        val_entry.pack(side="left", padx=(0, 4))
                        def on_val_change(*_):
                            val = val_var.get()
                            import json
                            try:
                                val_cast = json.loads(val)
                            except Exception:
                                val_cast = val
                            if values is self.temp_data[self.game_key]:
                                self.temp_data[self.game_key][gkey] = val_cast
                            else:
                                self.temp_data[self.game_key][gkey] = val_cast
                            values = val_cast
                            with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                json.dump(self.temp_data, f, indent=2)
                        val_var.trace_add('write', on_val_change)
                        return
                    if isinstance(gvalues, dict):
                        for opt_key in list(gvalues.keys()):
                            opt_key_str = str(opt_key)
                            if opt_key_str == 'comment':
                                comment_label = ttk.Label(gframe, text=gvalues[opt_key], foreground="#888888", wraplength=600, justify="left")
                                comment_label.pack(anchor="w", padx=4, pady=(0,6))
                            else:
                                row = ttk.Frame(gframe)
                                row.pack(fill="x", padx=2, pady=1)
                                # Use a closure to keep track of the current key for this row
                                def make_option_row(opt_key):
                                    current_key = [opt_key]  # mutable reference
                                    key_var = tk.StringVar(value=str(opt_key))
                                    val_var = tk.StringVar(value=str(gvalues[opt_key]))
                                    # Only user-defined options (new_option_) are editable
                                    if str(opt_key).startswith("new_option_"):
                                        key_entry = tk.Entry(row, textvariable=key_var, width=16)
                                        key_entry.pack(side="left", padx=(0, 4))
                                        def on_label_change(*_):
                                            new_label = key_var.get()
                                            # Validation: not empty, not 'comment', not duplicate, not unchanged
                                            if (
                                                new_label == current_key[0]
                                                or not new_label
                                                or new_label == 'comment'
                                                or new_label in gvalues
                                            ):
                                                # Revert UI if invalid
                                                key_var.set(current_key[0])
                                                return
                                            # Only rename if old key exists
                                            if current_key[0] in gvalues:
                                                gvalues[new_label] = gvalues.pop(current_key[0])
                                                # Also update temp_data, but only pop if key exists
                                                if gvalues is self.temp_data[self.game_key]:
                                                    if current_key[0] in self.temp_data[self.game_key]:
                                                        self.temp_data[self.game_key][new_label] = self.temp_data[self.game_key].pop(current_key[0])
                                                    else:
                                                        self.temp_data[self.game_key][new_label] = gvalues[new_label]
                                                else:
                                                    if current_key[0] in self.temp_data[self.game_key][gkey]:
                                                        self.temp_data[self.game_key][gkey][new_label] = self.temp_data[self.game_key][gkey].pop(current_key[0])
                                                    else:
                                                        self.temp_data[self.game_key][gkey][new_label] = gvalues[new_label]
                                                current_key[0] = new_label
                                                # Update value entry to point to new key
                                                val_var.set(str(gvalues[new_label]))
                                                val_entry.config(textvariable=val_var)
                                                with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                                    import json
                                                    json.dump(self.temp_data, f, indent=2)
                                            else:
                                                # Key already changed/removed, revert UI
                                                key_var.set(current_key[0])
                                        key_var.trace_add('write', on_label_change)
                                    else:
                                        # Pre-defined: show as read-only label
                                        key_entry = ttk.Label(row, text=str(opt_key), width=16, anchor="w")
                                        key_entry.pack(side="left", padx=(0, 4))
                                    val_entry = tk.Entry(row, textvariable=val_var, width=12)
                                    val_entry.pack(side="left", padx=(0, 4))
                                    def remove_row(row=row, opt_key_ref=current_key):
                                        row.destroy()
                                        if opt_key_ref[0] in gvalues and opt_key_ref[0] != "comment":
                                            del gvalues[opt_key_ref[0]]
                                        with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                            import json
                                            json.dump(self.temp_data, f, indent=2)
                                    remove_btn = ttk.Button(row, text="✕", width=2, command=remove_row)
                                    remove_btn.pack(side="left", padx=(2, 0))
                                    def on_val_change(*_):
                                        val = val_var.get()
                                        try:
                                            if '.' in val:
                                                val_cast = float(val)
                                            else:
                                                val_cast = int(val)
                                        except Exception:
                                            val_cast = val
                                        if gvalues is self.temp_data[self.game_key]:
                                            self.temp_data[self.game_key][current_key[0]] = val_cast
                                        else:
                                            self.temp_data[self.game_key][gkey][current_key[0]] = val_cast
                                        gvalues[current_key[0]] = val_cast
                                        with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                            import json
                                            json.dump(self.temp_data, f, indent=2)
                                    val_var.trace_add('write', on_val_change)
                                make_option_row(opt_key)
                    else:
                        # gvalues is not a dict: treat as a single value (list, dict, or other)
                        row = ttk.Frame(gframe)
                        row.pack(fill="x", padx=2, pady=1)
                        val_var = tk.StringVar(value=str(gvalues))
                        val_entry = tk.Entry(row, textvariable=val_var, width=40)
                        val_entry.pack(side="left", padx=(0, 4))
                        def on_val_change(*_):
                            val = val_var.get()
                            # Try to parse as JSON for lists/dicts, fallback to string
                            import json
                            try:
                                val_cast = json.loads(val)
                            except Exception:
                                val_cast = val
                            if values is self.temp_data[self.game_key]:
                                self.temp_data[self.game_key][gkey] = val_cast
                            else:
                                self.temp_data[self.game_key][gkey] = val_cast
                            values = val_cast
                            with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                json.dump(self.temp_data, f, indent=2)
                        val_var.trace_add('write', on_val_change)
                    # Only show add option button if gvalues is a dict and all values are not lists or dicts
                    if isinstance(gvalues, dict):
                        if not any(isinstance(v, (list, dict)) for k, v in gvalues.items() if k != 'comment'):
                            def add_empty_option():
                                idx = 1
                                while True:
                                    new_key = f"new_option_{idx}"
                                    if new_key not in gvalues and new_key != "comment":
                                        break
                                    idx += 1
                                gvalues[new_key] = ""
                                with open(self.temp_file_path, "w", encoding="utf-8") as f:
                                    import json
                                    json.dump(self.temp_data, f, indent=2)
                                render_options(parent, template, values)
                            add_btn = ttk.Button(gframe, text="+ Add Option", command=add_empty_option)
                            add_btn._is_add_option_button = True
                            add_btn.pack(anchor="w", padx=4)
                render_group(group_key, group_values, frame)

        render_options(self.scroll_frame, self._template, self.working_data)

        # Add Save Settings button
        def save_settings_button_action():
            from tkinter import filedialog, messagebox
            # Suggest filename as [user desired name].[game_name].sav
            default_name = f"{self.slot}.{self.game_name}.sav"
            file_path = filedialog.asksaveasfilename(defaultextension=".sav", initialfile=default_name, filetypes=[("Save Files", "*.sav")], title="Save Settings As")
            if file_path:
                self.temp_data[self.game_key] = self.working_data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.temp_data, f, indent=2)
                messagebox.showinfo("Settings Saved", f"Settings for {self.game_name} saved to {file_path}")

        save_btn = ttk.Button(self, text="Save Settings", command=save_settings_button_action)
        save_btn.pack(side="bottom", pady=8)

        # Add Load Settings button
        def load_settings_button_action():
            from tkinter import filedialog, messagebox
            # Only show files for this game
            filetypes = [(f"{self.game_name} Save Files", f"*.{self.game_name}.sav")]
            file_path = filedialog.askopenfilename(defaultextension=".sav", filetypes=filetypes, title="Load Settings")
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        loaded_data = json.load(f)
                    # Only update the current game's data
                    if self.game_key in loaded_data:
                        self.temp_data[self.game_key] = loaded_data[self.game_key]
                        self.working_data = self.temp_data[self.game_key]
                        with open(self.temp_file_path, "w", encoding="utf-8") as f2:
                            json.dump(self.temp_data, f2, indent=2)
                        render_options(self.scroll_frame, self._template, self.working_data)
                        messagebox.showinfo("Settings Loaded", f"Settings for {self.game_name} loaded from {file_path}")
                    else:
                        messagebox.showerror("Load Failed", f"No settings for {self.game_name} found in {file_path}")
                except Exception as e:
                    messagebox.showerror("Load Failed", f"Could not load settings: {e}")

        load_btn = ttk.Button(self, text="Load Settings", command=load_settings_button_action)
        load_btn.pack(side="bottom", pady=4)

    def load_template_with_comments_attached(self):
        import os, json, re
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
            return {}

        found_template = None
        for fname in os.listdir(templates_dir):
            if fname.endswith(".yaml"):
                fpath = os.path.join(templates_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    game_val = None
                    for line in lines:
                        m = re.match(r"^game:\s*['\"]?([^'\"\n]+)['\"]?", line)
                        if m:
                            game_val = m.group(1)
                            break
                    if game_val == self.game_name:
                        found_template = fpath
                        break
                except Exception:
                    continue
        if not found_template:
            return {}

        with open(found_template, "r", encoding="utf-8") as f:
            lines = f.readlines()
        data = yaml.safe_load("".join(lines))
        def simple_template_with_group_comments(yaml_dict, lines):
            # Attach only group-level comments that appear immediately AFTER the group key
            game_section = yaml_dict.get(self.game_name, {})
            result = {}
            group_comments = {}
            idx = 0
            while idx < len(lines):
                raw = lines[idx].rstrip('\n')
                m = re.match(r'^([^:\n]+):(.*)', raw)
                if m:
                    key = m.group(1).strip()
                    if key in game_section:
                        # This is a group key
                        comment_lines = []
                        j = idx + 1
                        while j < len(lines):
                            next_raw = lines[j].rstrip('\n')
                            if not next_raw.strip():
                                j += 1
                                continue
                            if next_raw.strip().startswith('#'):
                                comment_lines.append(next_raw.strip().lstrip('#').strip())
                                j += 1
                            else:
                                break
                        if comment_lines:
                            group_comments[key] = '\n'.join(comment_lines)
                idx += 1
            # Build result: {key: {comment: ..., option1: value1, ...}} or {key: value}
            for key, values in game_section.items():
                # If this is an option-typed dict (empty dict, or has only type/comment), treat as value
                if isinstance(values, dict):
                    # If empty dict, treat as value
                    if not values:
                        result[key] = {}
                        continue
                    # If only 'comment' or 'type' keys, treat as value
                    nonmeta = [k for k in values if k not in ('comment', 'type')]
                    if not nonmeta:
                        result[key] = dict(values)  # preserve comment/type if present
                        continue
                    # Otherwise, treat as group
                    group = {}
                    if key in group_comments:
                        group['comment'] = group_comments[key]
                    for opt, val in values.items():
                        group[opt] = val
                    result[key] = group
                else:
                    result[key] = values
            return result

        return simple_template_with_group_comments(data, lines)

    # _update_temp_file removed: temp files are only written on config load or direct field change
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from multiclient.builder import YAMLBuilder, get_available_games

# YAMLWizard class restored to latest version
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

        self.left_list.bind("<Double-Button-1>", self._on_game_double_click)
        self.right_list.bind("<Double-Button-1>", self._on_game_double_click)

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

    def assign_game(self):
        sel = self.left_list.curselection()
        if not sel or not self.selected_slot:
            return
        selected_name = self.left_list.get(sel[0])
        game_entry = next((g for g in self.games if g.name == selected_name), None)
        if game_entry:
            self.builder.add_game_to_slot(self.selected_slot, game_entry)
            self._update_temp_file_for_slot(self.selected_slot)
            self.refresh_games()
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
            self._update_temp_file_for_slot(self.selected_slot)
            self.refresh_games()
        self.left_list.delete(0, "end")
        self.right_list.delete(0, "end")
        self.refresh_games()

    def _update_temp_file_for_slot(self, slot_name, from_config=False, config_data=None):
        import os, json
        temp_dir = os.path.dirname(__file__)
        temp_file = os.path.join(temp_dir, f"{slot_name}.temp")
        if from_config and config_data is not None:
            # Write an exact copy of the slot's dict from config_data
            slot_dict = config_data.get(slot_name, {})
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(slot_dict, f, indent=2)
        else:
            # Write the current builder state (from settings editor/UI)
            slot_data = self.builder.get_settings_for_slot(slot_name)
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(slot_data, f, indent=2)

    def edit_settings(self):
        sel = self.right_list.curselection()
        if not sel or not self.selected_slot:
            return
        game_name = self.right_list.get(sel[0])
        folder = next((g.folder for g in self.games if g.name == game_name), game_name)
        SettingsEditor(self, self.builder, self.selected_slot, folder, game_name)

    def save_config(self):
        import os, json
        # Ask user for a .Yconfig file path
        path = filedialog.asksaveasfilename(defaultextension=".Yconfig", filetypes=[("Yconfig (JSON)", "*.Yconfig"), ("JSON", "*.json"), ("All Files", "*.*")], title="Save Combined Config As")
        if not path:
            return
        # Find all .temp files in the multiclient directory
        temp_dir = os.path.dirname(__file__)
        temp_files = [f for f in os.listdir(temp_dir) if f.endswith(".temp")]
        combined = {}
        for temp_file in temp_files:
            slot_name = temp_file[:-5]  # Remove .temp
            temp_path = os.path.join(temp_dir, temp_file)
            try:
                with open(temp_path, "r", encoding="utf-8") as f:
                    slot_data = json.load(f)
                combined[slot_name] = slot_data
            except Exception:
                continue
        # Save as JSON to the chosen path
        try:
            with open(path, "w", encoding="utf-8") as outf:
                json.dump(combined, outf, indent=2)
            messagebox.showinfo("Config Saved", f"Combined config saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save config: {e}")

    def load_config(self):
        import os, json
        # Allow loading both .json and .Yconfig files
        path = filedialog.askopenfilename(filetypes=[("Yconfig (JSON)", "*.Yconfig"), ("JSON files", "*.json"), ("All Files", "*.*")], title="Load Config File")
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext == ".yconfig" or ext == ".json":
            # Load combined config, restore per-slot .temp files, and update builder/GUI
            try:
                with open(path, "r", encoding="utf-8") as f:
                    combined = json.load(f)
                if not isinstance(combined, dict):
                    messagebox.showerror("Load Failed", "Yconfig file format invalid.")
                    return
                temp_dir = os.path.dirname(__file__)
                self.builder.clear()  # Remove all slots/games from builder
                self.slot_listbox.delete(0, "end")
                for slot_name, slot_data in combined.items():
                    # Write temp file for slot (exact copy from config)
                    self._update_temp_file_for_slot(slot_name, from_config=True, config_data=combined)
                    self.builder.add_slot(slot_name)
                    self.slot_listbox.insert("end", slot_name)
                    # Add all games for this slot
                    if isinstance(slot_data, dict):
                        for game_name in slot_data.keys():
                            game_entry = next((g for g in self.games if g.name == game_name), None)
                            if game_entry:
                                self.builder.add_game_to_slot(slot_name, game_entry)
                # After all slots/games are added, update the game lists for the selected slot
                if self.slot_listbox.size() > 0:
                    self.slot_listbox.selection_clear(0, 'end')
                    self.slot_listbox.selection_set(0)
                    self.selected_slot = self.slot_listbox.get(0)
                    self.refresh_games()
                # Update all temp files to match builder state (from config)
                for slot_name in combined.keys():
                    self._update_temp_file_for_slot(slot_name, from_config=True, config_data=combined)
                messagebox.showinfo("Config Loaded", f"Loaded config and restored per-slot settings from {path}")
                self.refresh_games()
            except Exception as e:
                messagebox.showerror("Load Failed", f"Could not load Yconfig: {e}")
        else:
            # Fallback to legacy YAML config loading
            import yaml
            self.builder.load_config(path)
            self.slot_listbox.delete(0, "end")
            for slot in self.builder.slots:
                self.slot_listbox.insert("end", slot.name)
            # Update all temp files to match builder state
            for slot in self.builder.slots:
                self._update_temp_file_for_slot(slot.name, from_config=False)
            self.refresh_games()

    def export_yaml(self):
        path = filedialog.asksaveasfilename(defaultextension=".yaml")
        if path:
            self.builder.export_yaml(path)

    def _on_game_double_click(self, event):
        widget = event.widget
        sel = widget.curselection()
        if not sel or not self.selected_slot:
            return
        game_name = widget.get(sel[0])
        folder = next((g.folder for g in self.games if g.name == game_name), game_name)
        SettingsEditor(self, self.builder, self.selected_slot, folder, game_name)
