"""
The settings class
"""
import json
import os
import sys
import tkinter as tk
from tkinter import ttk
from typing import AnyStr

from scrape_tpp_gui.helper_functions import str2bool, tkinter_theme_calling, center
from scrape_tpp_gui.source.version.version_module import file_exists


class SettingsTopLevel(tk.Toplevel):
    """
    A toplevel for settings
    """

    def __init__(self, root, controller, x=500, y=500):
        super().__init__()
        self.dir_path = self.find_the_path_of_main()
        self.save_button = None
        self.save_button_frame = None
        self.check_update_button = None
        self.checkbutton_frame = None
        self.big_frame = None
        self.check_update_button_variable = tk.BooleanVar(value=True)
        self.settings_from_file = None
        self.root = root
        self.controller = controller
        self.x = x
        self.y = y
        self.set_variables_from_settings()
        self.create_ui()
        # self.grab_set()
        self.set_active()
        center(self, self.root)

    def create_ui(self):
        """
        Constructs the User Interface
        :return:
        """

        self.title("Settings")
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        # Save button
        self.save_button_frame = ttk.Frame(self.big_frame)
        self.save_button_frame.pack(side='bottom')
        self.save_button = ttk.Button(self.save_button_frame, text=f"Save", command=self.save_all_settings)
        self.save_button.pack(side='bottom', expand=True, pady=10, padx=10, )
        # Check buttons
        # This style applies only in Azure ttk Theme
        self.checkbutton_frame = ttk.LabelFrame(self.big_frame, text="Update", padding=(20, 10))
        self.checkbutton_frame.pack(padx=(20, 10), pady=(20, 10), side='top')
        self.check_update_button = ttk.Checkbutton(self.checkbutton_frame, text="Prompt auto-update at startup",
                                                   command=self.check_button_save,
                                                   variable=self.check_update_button_variable,
                                                   onvalue=True, offvalue=False,
                                                   style="Switch.TCheckbutton")

        self.check_update_button.pack(padx=5, pady=10)

    def check_button_save(self):
        """
        Returns the current state (True/False) of `self.check_update_button_variable`.
        :return: Boolean: The current state of BooleanVar
        """
        current_state_of_check_update_button_variable = self.check_update_button_variable.get()
        print(f"check_update_button_variable set: value:{current_state_of_check_update_button_variable}")
        return current_state_of_check_update_button_variable

    def set_active(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()

    def save_all_settings(self):
        """
        Saves all settings to `settings.json`.
        :return:
        """
        dir_path = str
        if getattr(sys, 'frozen', False):  # TODO: review this
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            # Current file in /scrape_tpp_gui/classes/ but the setting have to /scrape_tpp_gui
            dir_path = os.path.dirname(dir_path)
            print(f'Script: {dir_path}')
        print(dir_path)
        save_settings_to_dump = {'auto_update_at_startup': self.check_button_save()}
        if file_exists(name="settings.json", dir_path=dir_path):
            json_data = ''
            with open(os.path.join(dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:  # To avoid empty string in the text file
                    json_data = save_settings_to_dump
                else:
                    json_data.update(save_settings_to_dump)
            with open(os.path.join(dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
                print(f"Settings saved in: {os.path.join(dir_path, 'settings.json')}")
        else:  # Settings.json does not exist.
            with open(os.path.join(dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json_data = save_settings_to_dump
                json.dump(json_data, file, indent=4)
                print(f"Settings saved in: {os.path.join(dir_path, 'settings.json')}")

    def read_settings_from_file(self):
        """
        Reads the settings from `settings.json`.
        :return: A dictionary with the settings.

        """

        if file_exists(name="settings.json", dir_path=self.dir_path):
            with open(os.path.join(self.dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:
                    return None  # To avoid empty string in the text file
                print(json_data)
                return json_data
        return None

    def set_variables_from_settings(self):
        """
        Reads the file and sets all the variables and their user-defined values from the file.
        :return: None
        """
        self.settings_from_file = self.read_settings_from_file()
        if self.settings_from_file:  # It is not None, thus
            self.check_update_button_variable.set(self.settings_from_file['auto_update_at_startup'])

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or the .exe
        :return: The path of the directory of main.py or the .exe
        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            self.dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)  # We need the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            print(f'Script: {self.dir_path}')
            return self.dir_path


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_theme_calling(root)
    SettingsTopLevel(controller=None, root=root)
    root.mainloop()
