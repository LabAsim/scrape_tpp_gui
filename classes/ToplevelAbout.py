import tkinter as tk
from tkinter import ttk
import sys
import os
import tktooltip

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import callback, center


class ToplevelAbout:
    x = 580
    y = 280

    def __init__(self, controller, root):
        self.controller = controller
        self.toplevel = tk.Toplevel()
        self.title = 'About this project'
        self.url = 'https://github.com/LabAsim/scrape_tpp_gui'
        self.toplevel.title = 'About ThePressProject Scrape GUI'
        self.toplevel.geometry(f'{ToplevelAbout.x}x{ToplevelAbout.y}')
        self.big_labelframe = ttk.Frame(self.toplevel)
        self.big_labelframe.pack(expand=True, fill='both')
        self.empty_label_top = ttk.Label(self.big_labelframe, text=f"\n")
        self.empty_label_top.pack(expand=True)
        self.title_labelframe = ttk.Label(self.big_labelframe, text='Title', relief='groove', borderwidth=0.5)
        self.title_labelframe.pack(expand=True, side='top')
        self.title_label = ttk.Label(self.title_labelframe, text=f"{self.title}",
                                     cursor='hand2', font='Arial 15', wraplength=ToplevelAbout.x)
        self.title_label.pack(expand=True, fill='both')
        self.title_label.bind("<Button-1>", lambda e: callback(self.url))
        tktooltip.ToolTip(self.title_label, msg='Click to open the article in the browser', delay=0.5)
        self.empty_label = ttk.Label(self.big_labelframe, text=f"\n")
        self.empty_label.pack(expand=True)
        text = '\nThePressProject name and all of its content belong to the ThePressProject team. ' \
               '\n\nI have no affiliation with the team. This GUI was built only for educational purposes. ' \
               '\n\nThe 3rd party packages used to build this GUΙ have their own licenses. ' \
               'The rest of the code which is written by me, it\'s released under MIT license.' \
               '\n\nDo not forget to donate monthly to ThePressProject!'
        self.text = tk.Text(self.big_labelframe, wrap="word", font='Arial 13')
        self.vertical_scrollbar = ttk.Scrollbar(self.big_labelframe, orient="vertical", command=self.text.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(self.big_labelframe, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        self.vertical_scrollbar.pack(side='right', fill='y')
        self.horizontal_scrollbar.pack(side='bottom', fill='x')
        self.text.pack(expand=True, fill='both')
        self.text.insert("1.0", text)
        self.text.config(state="disabled")
        center(self.toplevel, root)


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    ToplevelAbout(controller=None, root=root)
    root.mainloop()
