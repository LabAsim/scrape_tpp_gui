"""
Main app
"""
import multiprocessing as mp
import time
import tkinter as tk
import tkinter.font
from tkinter import ttk
import App
from classes.AskQuit import AskQuit
from FirstPage import FirstPage
from helper_functions import center, tkinter_theme_calling, parse_arguments
from source.version.version_module import check_new_version

if __name__ == "__main__":
    mp.freeze_support()
    args = parse_arguments()
    debug, bypass = args.debug, args.bypass
    start = time.perf_counter()
    root = tk.Tk()  # First window
    # Hide the main window. Only thε LoadingWindow from App will be shown
    root.withdraw()
    root.attributes('-alpha', 0.0)
    style = ttk.Style(root)
    # A solution in order to measure the length of the titles
    # https://stackoverflow.com/questions/30950925/tkinter-getting-screen-text-unit-width-not-pixels
    font = tkinter.font.Font(size=14)  # font must be here, after root is initialized
    tkinter_theme_calling(root)
    myapp = App.App(root=root, to_bypass=bypass, debug=debug)
    # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    root.protocol("WM_DELETE_WINDOW", lambda: AskQuit(root, FirstPage.driver))
    preferred_theme = myapp.read_theme()  # Reads the theme from the json (if exists)
    myapp.use_theme(preferred_theme)  # Sets the theme. If None, azure-dark is the default.
    center(root)  # Centers tkinter.Tk to screen's height & length
    end = time.perf_counter()
    print(f'Current Style: {root.tk.call("ttk::style", "theme", "use")}')
    print(f'Load in {end - start}')
    root.mainloop()
