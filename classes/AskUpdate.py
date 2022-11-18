import os.path
import sys
import tkinter as tk
from tkinter import ttk
from scrape_tpp_gui.helper_functions import center
from PIL import Image, ImageTk
import PIL.Image
from scrape_tpp_gui.misc import dir_path
from scrape_tpp_gui.source.updater.updater import download_update


class AskUpdate(tk.Toplevel):
    """
    A toplevel window for updating the application.
    """
    x = 270
    y = 110

    def __init__(self, parent, driver=None):
        super().__init__()
        # self.root = root
        self.driver = driver
        self.geometry(f'{AskUpdate.x}x{AskUpdate.y}')  # Here, self is tkinter.Toplevel
        self.parent = parent
        self.grab_set()
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        center(self, self.parent)

    def initUI(self):
        """
        Constructs the window.
        """
        self.title("Quit")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valueLabel = ttk.Label(askquit_topframe, text="Do you want to download the update?")
        valueLabel.pack(side='right', expand=True)
        image = Image.open(os.path.join(dir_path, "images/questionmark.png"))
        image = image.resize(
            (int(self.winfo_width() * 25), int(self.winfo_height() * 25)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(askquit_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=10)
        image_label.image = image
        buttons_frame = ttk.Frame(self.big_frame)
        buttons_frame.pack(side='bottom', expand=True)
        ok_button = ttk.Button(buttons_frame, text="Ok", command=lambda: self.download_and_quit(dir_path))
        ok_button.pack(side='left', expand=True, pady=10, padx=10)
        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side='right', expand=True, pady=10, padx=10)

    def download_and_quit(self, path):
        """
        Downloads the update to the specific path
        :param path: The path
        :return: None
        """
        download_update(path)
        self.toplevel_quit(widget=self.parent)

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


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    AskUpdate(parent=None)
    root.mainloop()
