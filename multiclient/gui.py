# multiclient/gui.py
import tkinter as tk
from tkinter import ttk

class MultiClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Archipelago Multi-Client Toolkit")
        self.geometry("600x400")

        # Example content
        label = ttk.Label(self, text="Welcome to the Archipelago Multi-Client Toolkit!")
        label.pack(pady=20)

        # TODO: Add buttons to launch Builder, Launcher, Updater, etc.

if __name__ == "__main__":
    app = MultiClientGUI()
    app.mainloop()
