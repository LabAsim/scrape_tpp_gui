"""
A toplevel to display some info
"""

import os.path
import sys
import tkinter as tk
from tkinter import ttk
import PIL.Image

parent_folder = os.path.dirname(__file__)
parent_of_parent_folder = os.path.dirname(parent_folder)
#sys.path.append(parent_of_parent_folder)

from helper_functions import center
from PIL import Image, ImageTk


class ShowInfo(tk.Toplevel):
    """
    A toplevel window for displaying info
    """
    x = 290
    y = 120

    def __init__(self, controller, root, info):
        super().__init__()
        self.geometry(f'{ShowInfo.x}x{ShowInfo.y}')  # Here, self is tkinter.Toplevel
        # Set fixed size
        self.maxsize(width=ShowInfo.x, height=ShowInfo.y)
        # Disable maximize / minimize button
        self.resizable(width=False, height=False)
        self.controller = controller
        self.root = root
        self.info = info
        self.grab_set()
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        center(self, self.root)
        dir_path = os.path.dirname(os.path.realpath(__file__))  # The relative is like this: ./classes
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            print(f'Script: {dir_path}')
        self.dir_path = dir_path  # The directory containing the executable. See above for the real folder.
        print(self.dir_path)

    def initUI(self):
        """
        Constructs the window.
        """
        self.title("Up-to-date")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valuelabel = ttk.Label(askquit_topframe, text=f"{self.info}")
        valuelabel.pack(side='right', expand=True)
        image = Image.open(os.path.join(parent_of_parent_folder, "multimedia\\images\\exclamation_mark.png"))
        image = image.resize(
            (int(self.winfo_width() * 60), int(self.winfo_height() * 60)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(askquit_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=1)
        image_label.image = image
        buttons_frame = ttk.Frame(self.big_frame)
        buttons_frame.pack(side='bottom', expand=True)
        ok_button = ttk.Button(buttons_frame, text="Ok", command=self.toplevel_quit)
        ok_button.pack(expand=True, pady=10, padx=10)

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget is tk.Tk:
                print(f'ShowInfo>toplevel_quit: Root is now exiting')
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'ShowInfo>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'ShowInfo>toplevel_quit: {self} is now destroyed')

    def setActive(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    ShowInfo(controller=None, root=root, info='The application is up-to-date!')
    root.mainloop()
