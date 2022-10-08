import tkinter as tk
from tkinter import ttk
from helper_functions import center


class ToplevelAbout:
    x = 580
    y = 280

    def __init__(self, controller, root):
        self.controller = controller
        self.toplevel = tk.Toplevel()
        self.toplevel.title = 'About ThePressProject Scrape GUI'
        self.toplevel.geometry(f'{ToplevelAbout.x}x{ToplevelAbout.y}')
        # self.empty_top_label = ttk.Label(self.toplevel, text='\n')
        # self.empty_top_label.pack(expand=True, fill='y')
        self.big_labelframe = ttk.Frame(self.toplevel)
        self.big_labelframe.pack(expand=True, fill='both')
        text = '\nThePressProject name and all of its content belongs to the ThePressProject team. ' \
               '\n\nI have no affiliation with the team. This GUI was built only for educational purposes. ' \
               '\n\nThe 3rd party packages used to build this GUΙ have their own licenses. ' \
               'The rest of the code which is written by me, it\'s released under MIT license.' \
               '\n\nDo not forget to donate monthly to ThePressProject!'
        self.text = tk.Text(self.big_labelframe, wrap="word", font='Arial 13')
        self.text.pack(expand=True, fill='both')
        self.text.insert("1.0", text)
        self.text.config(state="disabled")
        center(self.toplevel, root)
