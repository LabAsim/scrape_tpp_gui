import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tktooltip

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(parent_parent)
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import file_exists, center, callback


class GenericToplevel:
    """
    A generic Toplevel class to be used from other windows. It contains useful functions.
    """
    x = 1000
    y = 500

    def __init__(self, controller, root):
        self.controller = controller
        self.dir_path = self.find_the_path_of_main()
        self.toplevel = tk.Toplevel()
        center(self.toplevel, root)

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or the .exe
        :return: The path of the directory of main.py or the .exe


        Note that if the current class is import in App.py as
        'from scrape_tpp_gui.source.classes.ToplevelSocial import ToplevelSocial',
        the path will contain scrape_tpp_gui\\, which does not exist in temporary directories.
        Thus, in this situation, you need the parent folder.
        It's easier to use 'source.classes.ToplevelSocial import ToplevelSocial' to avoid that
        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            # If the path until this step contains \\scrape_tpp_gui, get the parent dir, which is a temp dir(MEIPP).
            # self.dir_path = os.path.dirname(self.dir_path)
            print("Exe:", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            print(f'Script: {self.dir_path}')
            return self.dir_path

    def bring_focus_back(self) -> None:
        """
        Maximizes the toplevel window and forces the focus on it.
        """
        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    @property
    def name_of_class(self):
        """
        :return: The name of the class in lower case.
        """
        return self.__class__.__name__.lower()
