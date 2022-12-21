import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tktooltip

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import file_exists, center, callback


class ToplevelDonate:
    x = 1000
    y = 500
    donation_urls = ['https://community.thepressproject.gr/product/dorea/',
                     'https://community.thepressproject.gr/product/minaia-syndromi/',
                     'https://community.thepressproject.gr/product/etisia-syndromi/']

    def __init__(self, controller, root, dir_path):
        self.controller = controller
        self.dir_path = self.find_the_path_of_main()
        self.topleveldonate = tk.Toplevel()
        self.topleveldonate.title("Donate to TPP")
        # Set a fixed size
        self.topleveldonate.minsize(width=ToplevelDonate.x, height=ToplevelDonate.y)
        self.topleveldonate.maxsize(width=ToplevelDonate.x, height=ToplevelDonate.y)
        # Disable maximize / minimize button
        self.topleveldonate.resizable(width=False, height=False)
        # First image
        self.img_dorea = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path,
                                                                    'source\\multimedia\\images\\tpp\\dorea.jpg')))
        self.label_dorea = ttk.Label(self.topleveldonate, image=self.img_dorea, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_dorea.image = self.img_dorea
        self.label_dorea.pack(expand=True, fill="both", side='left')
        self.label_dorea.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[0]))
        tktooltip.ToolTip(self.label_dorea, msg='Click to make a one-time donation', delay=0.5)
        # Second image
        self.img_monthly = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path,
                                                                      "source\\multimedia\\images\\tpp\\mhniaia.jpg")))
        self.label_monthly = ttk.Label(self.topleveldonate, image=self.img_monthly, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_monthly.image = self.img_monthly
        self.label_monthly.pack(expand=True, fill="both", side='left')
        self.label_monthly.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[1]))
        tktooltip.ToolTip(self.label_monthly, msg='Click to make a recurrent monthly donation', delay=0.5)
        # Third image
        self.img_annually = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path,
                                                                       "source\\multimedia\\images\\tpp\\ethsia.jpg")))
        self.label_annually = ttk.Label(self.topleveldonate, image=self.img_annually, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_annually.image = self.img_annually
        self.label_annually.pack(expand=True, fill="both", side='left')
        self.label_annually.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[2]))
        tktooltip.ToolTip(self.label_annually, msg='Click to make a recurrent annual donation', delay=0.5)
        center(self.topleveldonate, root)

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or the .exe
        :return: The path of the directory of main.py or the .exe
        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path = os.path.dirname(os.path.dirname(__file__))
            print("Exe:", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)  # We need the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            print(f'Script: {self.dir_path}')
            return self.dir_path


if __name__ == "__main__":
    from misc import dir_path

    root = tk.Tk()
    center(root)
    ToplevelDonate(controller=None, root=root, dir_path=dir_path)
    root.mainloop()
