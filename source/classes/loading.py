"""
Contains the class for the loading window
"""
import json
import os
import sys
import threading
import time
import tkinter
import tkinter as tk
from tkinter import ttk
from scrape_tpp_gui.helper_functions import file_exists, center, tkinter_theme_calling
from scrape_tpp_gui.trace_error import trace_error


class LoadingWindow(tk.Tk):
    """
    The class for the initial loading window

    See also: https://stackoverflow.com/a/67097216
    """
    x = 240
    y = 110

    def __init__(self, root, controller):
        super().__init__()
        # Load the themes to the new tk.Tk instance
        self.root = root
        self.controller = controller
        self.geometry(f'{LoadingWindow.x}x{LoadingWindow.y}')
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.init_UI()
        center(self)
        self.set_active()
        # Alternative use tk.Toplevel, but be careful with RuntimeError: main thread is not in main loop.
        if isinstance(self, tk.Tk):
            tkinter_theme_calling(root=self)
            preferred_theme = self.read_theme()  # Reads the theme from the json (if exists)
            self.use_theme(preferred_theme)  # Sets the theme. If None, azure-dark is the default.
            print("LoadingWindow>theme_registering")
            self.update()
        self.check_loading_status()

    def check_loading_status(self):
        """
        Checks if all the news are loaded in the tabs of ttk.Notebook
        """
        # Do not change root's attributes or withdraw here. It will raise RuntimeError: main thread is not in main loop.
        # self.attributes('-alpha', 0.0)
        # self.withdraw()
        print(f"LoadingWindow>check_loading_status>root withdrawn")
        while self.controller.loading_status:
            # If pass statement is used, it slows down the rest of the program
            time.sleep(1)
        else:
            self.root.deiconify()
            # Load transparency settings at startup
            # Here, it's the first time the user's settings are applied (it will call self.set_transparency() in App)
            self.controller.apply_settings()
            print(f"LoadingWindow>check_loading_status>settings applied")
            self.attributes('-alpha', 0.0)
            self.toplevel_quit()

    def init_UI(self):
        """
        Creates the User Interface
        """

        self.title("Loading")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valueLabel = ttk.Label(askquit_topframe, text="Loading..")
        valueLabel.pack(expand=True)

    @staticmethod
    def read_theme() -> str | None:
        """Reads the preferred theme"""
        dir_path = str
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            print(f'Script: {dir_path}')
        if file_exists(name="settings.json", dir_path=dir_path):
            with open(os.path.join(dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                print(json_data)
                if 'theme' in json_data:
                    return json_data['theme']
                else:
                    return None
        return None

    def use_theme(self, theme):
        """Sets the theme passed to the function"""
        toplevel_temporary_list = []
        for (child, child_widget) in self.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.withdraw()  # Hide the root
        if theme == 'azure-dark' or None:
            self.tk.call("set_theme", "dark")
        elif theme == 'azure-light':
            self.tk.call("set_theme", "light")
        elif theme == 'radiance':
            self.change_theme_radiance()
        elif theme == 'aquativo':
            self.change_theme_aquativo()
        elif theme == "plastik":
            self.change_theme_plastik()
        elif theme == "adapta":
            self.change_theme_adapta()
        elif theme == "yaru":
            self.change_theme_yaru()
        elif theme == "arc":
            self.change_theme_arc()
        elif theme == "vista":
            self.change_theme_xpnative()
        else:
            self.change_theme_azure()
        self.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    def change_theme(self, theme: str):
        """
        Changes the theme of the tkinter based on the theme's name passed.
        :param theme: The name of theme
        """
        toplevel_temporary_list = []
        for (child, child_widget) in self.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.withdraw()  # Hide the root
        if theme == 'azure':
            self.change_theme_azure()
        elif theme == 'radiance':
            self.change_theme_radiance()
        elif theme == 'aquativo':
            self.change_theme_aquativo()
        elif theme == "plastik":
            self.change_theme_plastik()
        elif theme == "adapta":
            self.change_theme_adapta()
        elif theme == "yaru":
            self.change_theme_yaru()
        elif theme == "arc":
            self.change_theme_arc()
        elif theme == "xpnative":
            self.change_theme_xpnative()
        self.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    def change_theme_azure(self):
        print(f'All styles: {self.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {self.tk.call("ttk::style", "theme", "use")}')
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
                # root.tk.call("ttk::style", "theme", "use", "azure-light")
            else:
                try:
                    self.tk.call("set_theme", "dark")
                    # root.tk.call("ttk::style", "theme", "use", "azure-dark")
                except tkinter.TclError as err:
                    print(err)
        except (tkinter.TclError, Exception) as err:
            print(err)

    def change_theme_xpnative(self):
        try:
            # Switch first to light theme and then to XPnative in order for the black to be eliminated.
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'vista')
        except tkinter.TclError as err:
            print(err)

    def change_theme_radiance(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'radiance')
        except tkinter.TclError as err:
            print(err)

    def change_theme_aquativo(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'aquativo')
        except tkinter.TclError as err:
            trace_error()
            print(err)

    def change_theme_plastik(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'plastik')
        except tkinter.TclError as err:
            print(err)

    def change_theme_adapta(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'adapta')
        except tkinter.TclError as err:
            print(err)

    def change_theme_yaru(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'yaru')
        except tkinter.TclError as err:
            print(err)

    def change_theme_arc(self):
        try:
            if self.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.tk.call("set_theme", "light")
            self.tk.call("ttk::style", "theme", "use", 'arc')
        except tkinter.TclError as err:
            print(err)

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
            if isinstance(widget, tk.Tk):
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'LoadingWindow>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'LoadingWindow>toplevel_quit: {self} is now destroyed')
