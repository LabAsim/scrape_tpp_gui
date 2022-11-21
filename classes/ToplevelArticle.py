import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from ttkwidgets.font import FontSelectFrame
import tktooltip
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import file_exists, center, callback
from source.misc.help_text import text_about
from classes.AskQuit import AskQuit


class ToplevelArticle:
    x = 1200
    y = 500

    def __init__(self, newsclass, operation, root):
        self.newsclass = newsclass
        self.title = newsclass.title
        self.date = newsclass.date
        self.url = newsclass.url
        self.summary = tk.StringVar(value=newsclass.summary)
        self.operation = operation
        self.root = root
        self.toplevelarticle = tk.Toplevel()
        self.toplevelarticle.title(f'The Press Project article: {self.title}')
        self.toplevelarticle.protocol("WM_DELETE_WINDOW", lambda: AskQuit(self.toplevelarticle))
        self.toplevelarticle.geometry(f'{ToplevelArticle.x}x{ToplevelArticle.y}')
        self.font_selection = FontSelectFrame(self.toplevelarticle, callback=self.update_preview)
        self.font_selection.pack(expand=True, side='bottom')
        self.big_frame = ttk.Frame(self.toplevelarticle)
        self.big_frame.pack(expand=True, fill='both')
        self.empty_label_top = ttk.Label(self.big_frame, text=f"\n")
        self.empty_label_top.pack(expand=True)
        self.title_labelframe = ttk.Label(self.big_frame, text='Title', relief='groove', borderwidth=0.5)
        self.title_labelframe.pack(expand=True, side='top')
        self.title_label = ttk.Label(self.title_labelframe, text=f"{self.title}",
                                     cursor='hand2', font='Arial 15', wraplength=ToplevelArticle.x)
        self.title_label.pack(expand=True, fill='both')
        self.title_label.bind("<Button-1>", lambda e: callback(self.url))
        tktooltip.ToolTip(self.title_label, msg='Click to open the article in the browser', delay=0.75)
        self.empty_label = ttk.Label(self.big_frame, text=f"\n")
        self.empty_label.pack(expand=True)
        # A tk.Text inside a tk.Text
        # https://stackoverflow.com/questions/64774411/is-there-a-ttk-equivalent-of-scrolledtext-widget-tkinter
        self.note = ttk.Notebook(self.big_frame)
        self.note.pack(side='bottom', fill='both', expand=True)
        # self.frame = ttk.LabelFrame(self.toplevelarticle, text="Content")
        self.frame = ttk.Frame(self.big_frame)
        self.frame.pack(expand=True, fill='both')
        self.note.add(self.frame, text='Summary')
        self.text = tk.Text(self.frame, wrap="word", font='Arial 13')
        self.text.insert("1.0", self.newsclass.summary)
        self.frame1 = ttk.Frame(self.big_frame)
        self.note.add(self.frame1, text='Main Article')
        self.text1 = tk.Text(self.frame1, wrap="word", font='Arial 13')
        self.text1.insert("1.0", self.newsclass.main_content)
        self.vertical_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.text.xview)
        self.vertical_scrollbar1 = ttk.Scrollbar(self.frame1, orient="vertical", command=self.text1.yview)
        self.horizontal_scrollbar1 = ttk.Scrollbar(self.frame1, orient="horizontal", command=self.text1.xview)
        self.text.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        self.text1.configure(yscrollcommand=self.vertical_scrollbar1.set, xscrollcommand=self.horizontal_scrollbar1.set)
        self.vertical_scrollbar.pack(side='right', fill='y')
        self.horizontal_scrollbar.pack(side='bottom', fill='x')
        self.vertical_scrollbar1.pack(side='right', fill='y')
        self.horizontal_scrollbar1.pack(side='bottom', fill='x')
        self.text.pack(expand=True, fill='both')
        self.text1.pack(expand=True, fill='both')
        # Disable text widget, so as the reader can not delete its content. It needs to be done AFTER text.insert
        # https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
        self.text.config(state='disabled')
        self.text1.config(state='disabled')
        # Allow user to select the text (i.e. if the user wants to copy it)
        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.text1.bind("<1>", lambda event: self.text1.focus_set())
        # Create Right-click menu for copying
        self.menu = tk.Menu(self.note, tearoff=0)
        self.menu.add_command(label='Copy', font='Arial 10', command=self.copy_text_to_clipboard)
        self.text.bind('<ButtonRelease-3>', self.post_menu)  # Menu is posted in self.text
        self.text1.bind('<ButtonRelease-3>', self.post_menu)
        center(self.toplevelarticle, self.root)

    def post_menu(self, event):
        """Posts the right click menu at the cursor's coordinates"""
        self.menu.post(event.x_root, event.y_root)

    def copy_text_to_clipboard(self):
        """
        Gets the selected text from the Text and copies it to the clipboard
        https://stackoverflow.com/questions/4073468/how-do-i-get-a-selected-string-in-from-a-tkinter-text-box
        """
        text = self.big_frame.selection_get()
        pyperclip.copy(text)
        print(f"Text copied to clipboard: {text}")

    def update_preview(self, font_tuple):
        """
        Modifies the text font
        ttps://ttkwidgets.readthedocs.io/en/latest/examples/font/FontSelectFrame.html
        """
        print(font_tuple)
        selected_font = self.font_selection.font[0]
        if selected_font is not None:
            self.text.config(state='normal')  # Sets the state back to normal so as the text's font to be modified
            self.text1.config(state='normal')
            self.text.configure(font=selected_font)
            self.text1.configure(font=selected_font)
            self.text.config(state='disabled')
            self.text1.config(state='disabled')

    @staticmethod
    def toplevel_quit(widget):
        """
        how to bind a messagebox to toplevel window in python
        https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master
        """
        if widget is not None:
            widget.destroy()

    @staticmethod
    def ask_toplevel_quit(widget):
        """
        how to bind a messagebox to toplevel window in python
        https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master
        """
        if messagebox.askokcancel(title="Quit", message="Do you want to quit?", parent=widget):
            if widget is not None:
                widget.destroy()