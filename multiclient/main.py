# multiclient/main.py
import sys

def main():
    if "--gui" in sys.argv:
        from multiclient.gui import MultiClientGUI
        app = MultiClientGUI()
        app.mainloop()
    else:
        print("CLI mode not implemented yet. Use '--gui' to launch GUI.")

if __name__ == "__main__":
    main()
