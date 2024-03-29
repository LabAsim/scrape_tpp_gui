import os.path
import sys
import tkinter as tk
from tkinter import ttk
from scrape_tpp_gui.helper_functions import file_exists, center, callback, headers_list, headers, str2bool
from PIL import Image, ImageTk
import PIL.Image
from scrape_tpp_gui.misc import dir_path


class AskQuit(tk.Toplevel):
    """
    A class for asking the user if he/she wants to quit and close the current window.
    """
    x = 240
    y = 110

    def __init__(self, parent, driver=None, controller=None):
        super().__init__()
        # self.root = root
        self.controller = controller
        self.images_dir_path = None
        self.path_of_images()
        self.driver = driver
        self.geometry(f'{AskQuit.x}x{AskQuit.y}')  # Here, self is tkinter.Toplevel
        # Set a fixed size
        self.minsize(width=AskQuit.x, height=AskQuit.y)
        self.maxsize(width=AskQuit.x, height=AskQuit.y)
        # Disable maximize / minimize button
        self.resizable(width=False, height=False)
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
        image = Image.open(self.images_dir_path)
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
                if self.driver is not None:  # Do not forget to close webdriver
                    self.driver.close()
                    self.driver.quit()
                sys.exit()
            else:
                if self.controller:
                    # Set the Flag to true to terminate the thread
                    self.controller.autosave_db_thread_stop_flag = True
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

    def path_of_images(self):
        """
        Finds the path to the question-mark file.
        """
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_of_current_dir = os.path.dirname(current_dir_path)
        self.images_dir_path = os.path.join(parent_of_current_dir, "multimedia\\images\\questionmark.png")
