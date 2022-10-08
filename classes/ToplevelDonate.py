import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from helper_functions import file_exists, center, callback


class ToplevelDonate:
    x = 1000
    y = 500
    donation_urls = ['https://community.thepressproject.gr/product/dorea/',
                     'https://community.thepressproject.gr/product/minaia-syndromi/',
                     'https://community.thepressproject.gr/product/etisia-syndromi/']

    def __init__(self, controller, root, dir_path):
        self.controller = controller
        self.dir_path = os.path.join(dir_path, 'images')
        self.topleveldonate = tk.Toplevel()
        self.topleveldonate.title("Donate to TPP")
        # First image
        self.img_dorea = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, 'dorea.jpg')))
        self.label_dorea = ttk.Label(self.topleveldonate, image=self.img_dorea, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_dorea.image = self.img_dorea
        self.label_dorea.pack(expand=True, fill="both", side='left')
        self.label_dorea.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[0]))
        # Second image
        self.img_monthly = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, "mhniaia.jpg")))
        self.label_monthly = ttk.Label(self.topleveldonate, image=self.img_monthly, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_monthly.image = self.img_monthly
        self.label_monthly.pack(expand=True, fill="both", side='left')
        self.label_monthly.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[1]))
        # Third image
        self.img_annually = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, "ethsia.jpg")))
        self.label_annually = ttk.Label(self.topleveldonate, image=self.img_annually, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_annually.image = self.img_annually
        self.label_annually.pack(expand=True, fill="both", side='left')
        self.label_annually.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[2]))
        center(self.topleveldonate, root)