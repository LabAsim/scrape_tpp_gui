"""
Contains the class for the loading window
"""
import sys
import threading
import tkinter as tk
from tkinter import ttk
from scrape_tpp_gui.helper_functions import file_exists, center, callback, headers_list, headers, str2bool


class LoadingWindow(tk.Toplevel):
    """
    The class for the initial loading window

    See also: https://stackoverflow.com/a/67097216
    """
    x = 240
    y = 110

    def __init__(self, root, controller):
        super().__init__()
        self.root = root
        self.controller = controller
        self.geometry(f'{LoadingWindow.x}x{LoadingWindow.y}')
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.init_UI()
        center(self, self.root)
        self.update()
        self.check_loading_status()

    def check_loading_status(self):
        """Pass"""
        self.root.attributes('-alpha', 0.0)
        self.root.withdraw()

        print(f"LoadingWindow>check_loading_status>root withdrawn")
        while self.controller.loading_status:
            pass
        else:
            self.root.deiconify()
            # Load transparency settings at startup
            # Here, it's the first time the user's settings are applied (it will call self.set_transparency() in App)
            self.controller.apply_settings()
            print(f"LoadingWindow>check_loading_status>settings applied")
            self.attributes('-alpha', 0.0)
            self.destroy()

    def init_UI(self):
        """
        Creates the User Interface
        """
        self.title("Loading")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valueLabel = ttk.Label(askquit_topframe, text="Loading..")
        valueLabel.pack(expand=True)

    def set_active(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget is tk.Tk:
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'LoadingWindow>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'LoadingWindow>toplevel_quit: {self} is now destroyed')
