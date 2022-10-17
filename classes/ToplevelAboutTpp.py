import os
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from PIL import Image, ImageTk
from helper_functions import file_exists, center, callback
from source.misc.help_text import text_about
from ttkwidgets.font import FontSelectFrame
import tktooltip

class ToplevelAboutTpp:
    x = 1200
    y = 500
    url = 'https://thepressproject.gr/pos-litourgoume/'
    text = text_about

    def __init__(self, controller, root):
        self.controller = controller
        self.toplevelabouttpp = tk.Toplevel()
        self.toplevelabouttpp.title(f"About The Press Project")
        self.toplevelabouttpp.geometry(f"{ToplevelAboutTpp.x}x{ToplevelAboutTpp.y}")
        self.font_selection = FontSelectFrame(self.toplevelabouttpp, callback=self.update_preview)
        self.font_selection.pack(expand=True, side='bottom')
        self.big_frame = ttk.Frame(self.toplevelabouttpp)
        self.big_frame.pack(expand=True, fill='both')
        self.empty_label_top = ttk.Label(self.big_frame, text=f"\n")
        self.empty_label_top.pack(expand=True)
        self.title_labelframe = ttk.Label(self.big_frame, text='Title', relief='groove', borderwidth=0.5)
        self.title_labelframe.pack(expand=True, side='top')
        self.title_label = ttk.Label(self.title_labelframe, text=f"About The Press Project",
                                     cursor='hand2', font='Arial 15', wraplength=ToplevelAboutTpp.x)
        self.title_label.pack(expand=True, fill='both')
        self.title_label.bind("<Button-1>", lambda e: callback(self.url))
        tktooltip.ToolTip(self.title_label, msg='Click to open the article in the browser', delay=0.5)
        self.empty_label = ttk.Label(self.big_frame, text=f"\n")
        self.empty_label.pack(expand=True)
        # A tk.Text inside a tk.Text
        # https://stackoverflow.com/questions/64774411/is-there-a-ttk-equivalent-of-scrolledtext-widget-tkinter
        self.note = ttk.Notebook(self.big_frame)
        self.note.pack(side='bottom', fill='both', expand=True)
        # self.frame = ttk.LabelFrame(self.toplevelarticle, text="Content")
        self.frame = ttk.Frame(self.big_frame)
        self.frame.pack(expand=True, fill='both')
        self.note.add(self.frame, text='About')
        self.text = tk.Text(self.frame, wrap="word", font='Arial 13')
        self.text.insert("1.0", ToplevelAboutTpp.text)
        self.vertical_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        self.vertical_scrollbar.pack(side='right', fill='y')
        self.horizontal_scrollbar.pack(side='bottom', fill='x')
        self.text.pack(expand=True, fill='both')
        # Disable text widget, so as reader can not delete its content. It needs to be done AFTER text.insert
        # https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
        self.text.config(state='disabled')
        # Allow user to select the text (i.e. if the user wants to copy it)
        self.text.bind("<1>", lambda event: self.text.focus_set())
        # Create Right-click menu for copying
        self.menu = tk.Menu(self.note, tearoff=0)
        self.menu.add_command(label='Copy', font='Arial 10', command=self.copy_text_to_clipboard)
        self.text.bind('<ButtonRelease-3>', self.post_menu)  # Menu is posted in self.text
        center(self.toplevelabouttpp, root)

    def post_menu(self, event):
        """Posts the right click menu at the cursor's coordinates"""
        self.menu.post(event.x_root, event.y_root)

    def copy_text_to_clipboard(self):
        """Gets the selected text from the Text and copies it to the clipboard
        https://stackoverflow.com/questions/4073468/how-do-i-get-a-selected-string-in-from-a-tkinter-text-box"""
        text = self.big_frame.selection_get()
        pyperclip.copy(text)
        print(f"Text coped to clipboard: {text}")

    def update_preview(self, font_tuple):
        """Modifies the text font
           https://ttkwidgets.readthedocs.io/en/latest/examples/font/FontSelectFrame.html"""
        print(font_tuple)
        selected_font = self.font_selection.font[0]
        if selected_font is not None:
            self.text.config(state='normal')  # Sets the state back to normal so as the text's font to be modified
            self.text.configure(font=selected_font)
            self.text.config(state='disabled')

    @staticmethod
    def toplevel_quit(widget):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            widget.destroy()

    @staticmethod
    def ask_toplevel_quit(widget):
        """how to bind a messagebox to toplevel window in python
                   https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if messagebox.askokcancel(title="Quit", message="Do you want to quit?", parent=widget):
            if widget is not None:
                widget.destroy()