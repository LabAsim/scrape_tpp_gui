import os.path
import sys
import tkinter as tk
from tkinter import ttk
from helper_functions import file_exists, center, callback, headers_list, headers, str2bool
from PIL import Image, ImageTk
import PIL.Image
from misc import dir_path


class AskQuit(tk.Toplevel):
    x = 240
    y = 110

    def __init__(self, parent):
        super().__init__()
        # self.root = root
        self.geometry(f'{AskQuit.x}x{AskQuit.y}')  # Here, self is tkinter.Toplevel
        self.parent = parent
        self.grab_set()
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        center(self, self.parent)

    def initUI(self):
        self.title("Quit")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valueLabel = ttk.Label(askquit_topframe, text="Do you want to quit?")
        valueLabel.pack(side='right', expand=True)
        image = Image.open(os.path.join(dir_path, "images/questionmark.png"))
        image = image.resize(
            (int(self.winfo_width() * 25), int(self.winfo_height() * 25)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(askquit_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=10)
        image_label.image = image
        buttonsframe = ttk.Frame(self.big_frame)
        buttonsframe.pack(side='bottom', expand=True)
        okButton = ttk.Button(buttonsframe, text="Ok", command=lambda: self.toplevel_quit(self.parent))
        okButton.pack(side='left', expand=True, pady=10, padx=10)
        cancelButton = ttk.Button(buttonsframe, text="Cancel", command=self.destroy)
        cancelButton.pack(side='right', expand=True, pady=10, padx=10)

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget is tk.Tk:
                print(f'AskQuit>toplevel_quit: Root is now exiting')
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'AskQuit>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'AskQuit>toplevel_quit: {self} is now destroyed')

    def setActive(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()
