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


class ToplevelDonate:
    x = 1000
    y = 500
    donation_urls = ['https://community.thepressproject.gr/product/dorea/',
                     'https://community.thepressproject.gr/product/minaia-syndromi/',
                     'https://community.thepressproject.gr/product/etisia-syndromi/']

    def __init__(self, controller, root):
        self.controller = controller
        self.dir_path = self.find_the_path_of_main()
        self.topleveldonate = tk.Toplevel()
        self.topleveldonate.protocol("WM_DELETE_WINDOW", self.toplevel_quit)
        self.topleveldonate.title("Donate to TPP")
        # Set a fixed size
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

    def bring_focus_back(self):
        """
        Maximizes the toplevel window and forces the focus on it.
        """
        self.topleveldonate.deiconify()
        self.topleveldonate.lift()
        self.topleveldonate.focus_force()

    def toplevel_quit(self):
        """It closes the window and set the controller variable back to None"""
        # Set the variable of this toplevel in the controller class back to None
        if self.controller:
            self.controller.topleveldonate = None
        # Destroy the toplevel
        self.topleveldonate.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    ToplevelDonate(controller=None, root=root)
    root.mainloop()
