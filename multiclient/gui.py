# multiclient/gui.py
import tkinter as tk
from tkinter import ttk
from multiclient.builder import YAMLBuilder
from multiclient.builder import get_available_games
from multiclient.wizard import YAMLWizard


class MultiClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Archipelago Multi-Client Toolkit")
        self.geometry("600x400")
        self.builder = YAMLBuilder()
        # TEMP: Add test button
        test_button = ttk.Button(self, text="Add Test Slot", command=self.test_add_slot)
        test_button.pack(pady=10)
        ttk.Button(self, text="New Game", command=self.open_wizard).pack(pady=10)
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Game", command=self.open_wizard)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def open_settings(self):
        from tkinter import messagebox
        messagebox.showinfo("Settings", "Settings dialog not yet implemented.")

    def test_add_slot(self):
        self.builder.add_slot("oot", "Player1")
        print(self.builder.generate_yaml())
        print(get_available_games())


        # Example content
        label = ttk.Label(self, text="Welcome to the Archipelago Multi-Client Toolkit!")
        label.pack(pady=20)

        # TODO: Add buttons to launch Builder, Launcher, Updater, etc.
    def open_wizard(self):
        YAMLWizard(self, self.builder)


if __name__ == "__main__":
    app = MultiClientGUI()
    app.mainloop()
