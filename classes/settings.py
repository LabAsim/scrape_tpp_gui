"""
The settings class
"""
import json
import os
import sys
import tkinter as tk
from tkinter import ttk

from scrape_tpp_gui.helper_functions import tkinter_theme_calling, center
from scrape_tpp_gui.source.version.version_module import file_exists


class SettingsTopLevel(tk.Toplevel):
    """
    A toplevel for settings
    """

    def __init__(self, root, controller, x=500, y=500):
        super().__init__()
        self.button_frame = None
        self.apply_button = None
        self.apply_button_frame = None
        self.transparency_text_label = None
        self.transparency_scale = None
        self.transparency_progressbar = None
        self.transparency_frame = None
        self.dir_path = self.find_the_path_of_main()
        self.save_button = None
        self.save_button_frame = None
        self.check_update_button = None
        self.checkbutton_frame = None
        self.big_frame = None
        self.check_update_button_variable = tk.BooleanVar(value=True)
        self.transparency_percentage = tk.IntVar()
        self.settings_from_file = None
        self.root = root
        self.controller = controller
        self.x = x
        self.y = y
        self.create_ui()
        self.set_class_variables_from_settings()
        # self.grab_set()
        self.set_active()
        center(self, self.root)
        # Apply the loaded settings
        self.apply_settings()
        # Assure that the transparency of this Toplevel is 0%
        self.attributes('-alpha', 1)

    def create_ui(self):
        """
        Constructs the User Interface  for the Settings window.
        :return: None
        """

        self.title("Settings")
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.button_frame = ttk.Frame(self.big_frame)
        self.button_frame.pack(side='bottom', fill='both')
        # Apply button
        self.apply_button_frame = ttk.Frame(self.button_frame)
        self.apply_button_frame.pack(side='left')
        self.apply_button = ttk.Button(self.apply_button_frame, text=f"Apply", command=self.apply_settings)
        self.apply_button.pack(pady=10, padx=(50, 0))
        # Save button
        self.save_button_frame = ttk.Frame(self.button_frame)
        self.save_button_frame.pack(side='right')
        self.save_button = ttk.Button(self.save_button_frame, text=f"Save", command=self.save_all_settings)
        self.save_button.pack(pady=10, padx=(0, 50))
        # Check buttons
        # This style applies only in Azure ttk Theme
        self.checkbutton_frame = ttk.LabelFrame(self.big_frame, text="Update", padding=(20, 10))
        self.checkbutton_frame.pack(padx=(20, 10), pady=(20, 10), side='top')
        self.check_update_button = ttk.Checkbutton(self.checkbutton_frame, text="Check for updates at startup",
                                                   command=self.check_button_save,
                                                   variable=self.check_update_button_variable,
                                                   onvalue=True, offvalue=False,
                                                   style="Switch.TCheckbutton")
        self.check_update_button.pack(padx=5, pady=10)
        # Transparency frame, scale, progressbar, label with text
        self.transparency_frame = ttk.LabelFrame(self.big_frame, text="Transparency")
        self.transparency_frame.pack(side='bottom', pady=5, padx=5)
        self.transparency_scale = ttk.Scale(self.transparency_frame,
                                            from_=100, to=0,
                                            variable=self.transparency_percentage,
                                            command=self.update_transparency_scale)
        self.transparency_scale.pack(side='left', padx=(20, 10), pady=(10, 10))
        self.transparency_progressbar = ttk.Progressbar(self.transparency_frame,
                                                        maximum=100, variable=self.transparency_percentage,
                                                        value=0,
                                                        mode="determinate")
        self.transparency_progressbar.pack(side='right', padx=(10, 20), pady=(10, 10))
        self.transparency_text_label = ttk.Label(self.transparency_frame, text=self.get_scale_value())
        self.transparency_text_label.pack(side='bottom')

    def update_transparency_scale(self, event):
        """
        Sets the `self.transparency_percentage` based on the scale's value.
        :param event: Moving the scale.
        :return: None.
        """
        current_percentage_of_scale = int(self.transparency_scale.get())
        self.transparency_percentage.set(current_percentage_of_scale)
        self.transparency_text_label['text'] = self.get_scale_value()

    def get_scale_value(self):
        """
        Returns the string to be displayed in the label below the scale-progressbar.
        :return: The percentage of transparency based on the scale (determined by the user).
        """
        print(f"Transparency: {int(self.transparency_scale['value'])}%")
        return f"{int(self.transparency_scale['value'])}%"

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
        :return: None
        """
        dir_path = str
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            # Current file in /scrape_tpp_gui/classes/ but the setting have to /scrape_tpp_gui
            dir_path = os.path.dirname(dir_path)
            print(f'Script: {dir_path}')
        print(dir_path)
        # Saves transparency as a decimal (not percentage)
        save_settings_to_dump = {'auto_update_at_startup': self.check_button_save(),
                                 'transparency': int(self.transparency_scale.get()) / 100}
        # TODO: read the 'transparency' from main App and implement its value
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

    def set_class_variables_from_settings(self):
        """
        Reads the file and sets all the class variables and their user-defined values from the file.
        :return: None
        """
        self.settings_from_file = self.read_settings_from_file()

        # Assure that it is not None.
        if self.settings_from_file:
            # Even if the file exists, if the dictionary key does not exist, return self.settings as None
            try:
                self.check_update_button_variable.set(self.settings_from_file['auto_update_at_startup'])
                # Sets the IntVar the percentage from the settings
                self.transparency_percentage.set(self.settings_from_file['transparency'] * 100)
                # Updates the text in the label
                self.update_transparency_scale(event=None)
                print(f"{self.check_update_button_variable.set(self.settings_from_file['auto_update_at_startup'])}"
                      f"\n{self.transparency_scale['value']}")
            except KeyError:
                self.settings_from_file = None
                return None

    def apply_settings(self):
        """
        This functions applies the loaded settings (saved as class variables).
        :return: None
        """
        # The setting for auto-update does not need to be applied here. It makes no difference.
        # Sets the transparency of the root. Convert to decimal (i.e. 67% = 1 - 67/100 = 0.33)
        self.root.attributes('-alpha', (1 - int(self.transparency_percentage.get()) / 100))

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
    top = SettingsTopLevel(controller=None, root=root)
    root.mainloop()
