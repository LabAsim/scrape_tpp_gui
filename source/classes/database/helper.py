"""
This module contains classes and functions assisting Database creation
"""
import functools
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Union
import pyperclip
from ttkwidgets.font import FontSelectFrame
import tktooltip

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(os.path.dirname(parent_parent))
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import file_exists, center, callback


def match_vowels(term: str):
    """
    Search the `term` for the vowels in the dictionary and converts the vowels
    (key is the match and value the converted one).
    Note that it does NOT recognize ".", ":" etc and thus, the passing term is stripped of them.

    :param term: The text to convert
    :return: An utf-8 string

    See below for docs:

        Find spaces:
                        https://stackoverflow.com/a/43037651

        Unicode tables:
                        https://www.utf8-chartable.de/unicode-utf8-table.pl
                        https://www.utf8-chartable.de/unicode-utf8-table.pl?start=896&names=-&utf8=string-literal
        Official docs:
                        https://docs.python.org/3.10/library/re.html?highlight=finditer#re.finditer
    """
    # print(f"{term.encode('utf-8')}")
    # res = (re.sub('.', lambda x: ' \\u%04X' % ord(x.group()), term))
    # print("The unicode converted String : " + str(res))
    vowels = {
        b"\xce\xb1\xcc\x81": "ά".encode('utf-8'),
        b"\xce\xb5\xcc\x81": "έ".encode('utf-8'),
        b"\xce\xb7\xcc\x81": "ή".encode('utf-8'),
        b"\xce\xb9\xcc\x81": "ί".encode('utf-8'),
        b"\xce\xbf\xcc\x81": "ό".encode('utf-8'),
        b"\xcf\x85\xcc\x81": "ύ".encode('utf-8'),
        b"\xcf\x89\xcc\x81": "ώ".encode('utf-8'),
    }
    # This pattern depicts the keys of the dictionary above.
    vowels_pattern = re.compile(b"[\xce\xcf][\xb7\xb1\xb5\xb9\xbf\x85\x89]?\xcc\x81[\xcf\x82]?")
    # All greek letters or a space and at most one special character (to create a stressed vowel).
    # examples: "Χρυσής Αυγή εισαγγελέας"
    greek_letters_utf8 = re.compile("[\u0370-\u03ff\u1f00-\u1fff\s][\u0300-\u0301]?")
    greek_english_letters_numbers_utf8 = re.compile(
        "[0-9\u0040-\u007e\u0370-\u03ff\u1f00-\u1fff\s][\u0300-\u0301]{0,1}")
    term_to_return = bytes()
    # print(f"term:{term}")
    # TODO: remove it
    if not isinstance(term, Union[str, bytes]):
        raise TypeError(f"term: {term} is type: {type(term)} not Union[str, bytes]")
    for match in greek_english_letters_numbers_utf8.finditer(term):
        # print(match.group())
        # Convert the match (str) to bytes
        match_byte = match.group(0).encode('utf-8')
        space = re.search(re.compile('\s'), match.group(0))
        # Match the letter bytes to the pattern consisting of vowel bytes
        if re.match(vowels_pattern, match_byte):
            # print(re.match(vowels_pattern, match_byte).group())
            for match_vowel in vowels_pattern.finditer(match.group(0).encode('utf-8')):
                # print(f'Converted {match_vowel.group(0)}:{match_vowel.group(0).decode("utf-8")}')
                # Append the bytes from the dictionary above
                term_to_return += vowels[match_vowel.group(0)]
        elif match_byte.decode('utf-8').isspace():
            # print(f"Space found!:{match.group()}")
            term_to_return += space.group(0).encode('utf-8')
        # Not a match => Append the bytes to the variable
        else:
            term_to_return += match_byte
    # print(f"{term.encode('utf-8')} converted to {term_to_return}")
    return term_to_return.decode('utf-8')


def converted_stressed_vowels_to_non_stressed(term: str) -> str:
    """
    Converts the Greek stressed vowels to non-stressed. It converts the Greek letter "ς" to "σ".
    :param term: The string to be converted
    :return: The converted strings
    """
    conversion_letters = {"Σ": "σ",
                          "ς": "σ",
                          "έ": "ε",
                          "ό": "ο",
                          "ί": "ι",
                          "ή": "η",
                          "ύ": "υ",
                          "ά": "α",
                          "ώ": "ω"}

    term_to_return = ""
    for letter in term:
        if letter in conversion_letters:
            # Swap the letter =
            term_to_return += conversion_letters[letter]
        else:
            # Just add the letter
            term_to_return += letter

    return term_to_return


def convert_to_case_not_sensitive(term) -> str:
    """
    Converts all letters to lowercase and returns the new string
    :param term: The term to be converted
    :return: The term with its vowels converted

    See utf-8 table: https://www.utf8-chartable.de/unicode-utf8-table.pl?start=896&names=-&utf8=string-literal
    The regex pattern for all greek letters: https://stackoverflow.com/a/48468106
    Official regex docs:
    match: https://docs.python.org/3.10/library/re.html?highlight=re#re.Match.group
    re.compile: https://docs.python.org/3.10/library/re.html#re.compile
    """

    # All greek letters and at most one space.
    vowels_utf8 = re.compile("[\u0370-\u03ff\u1f00-\u1fff]?[\\s]?")
    greek_english_letters_numbers_utf8 = re.compile(
        "[0-9\u0040-\u007e\u0370-\u03ff\u1f00-\u1fff\s][\u0300-\u0301]{0,1}")

    term_to_return = str()
    for match in greek_english_letters_numbers_utf8.finditer(term):
        term_to_return += match.group(0).lower()

    return term_to_return


def wrapper_for_case_conversion(func):
    """
    A wrapper function for converting the searched term (and searched news) based on the
    user's preference of case sensitivity
    """

    def inner(*args, **kwargs):
        """
        Inner wrapper function
        Checks for the user's preference of case sensitivity and returns accordingly the function
        """
        # Args[0] is self (The instance of the Class)
        # kwargs is a dictionary with keys containing the variables name and values the variables' values.
        self = args[0]
        term = kwargs["term"]
        category = kwargs["category"]
        # self.casecase_sensitive_boolean is a tk.BooleanVar, so get() needs to called here.
        if self.case_sensitive_boolean.get() is False:
            kwargs["term"] = converted_stressed_vowels_to_non_stressed(match_vowels(convert_to_case_not_sensitive(term)))

            return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return inner


class ToplevelArticleDatabase:
    """
    A toplevel window containing the article's summary and main article
    """
    x = 1200
    y = 500

    def __init__(self, newsclass, root, controller):
        self.newsclass = newsclass
        self.title = newsclass.title
        self.date = newsclass.date
        self.url = newsclass.url
        self.summary = tk.StringVar(value=newsclass.summary)
        # Create the UI
        self.root = root
        self.toplevelarticle = tk.Toplevel()
        self.toplevelarticle.title(f'The Press Project article: {self.title}')
        self.toplevelarticle.geometry(f'{ToplevelArticleDatabase.x}x{ToplevelArticleDatabase.y}')
        self.right_click_menu_for_title_label = None
        self.horizontal_scrollbar1 = None
        self.vertical_scrollbar1 = None
        self.horizontal_scrollbar = None
        self.vertical_scrollbar = None
        self.text1 = None
        self.frame1 = None
        self.text = None
        self.frame = None
        self.note = None
        self.empty_label = None
        self.title_label = None
        self.title_labelframe = None
        self.empty_label_top = None
        self.big_frame = None
        self.font_selection = None
        # Create the user interface
        self.create_ui()
        # Create the binds
        self.create_binds()
        # Center the window
        center(self.toplevelarticle, self.root)

    def create_ui(self):
        """Creates the UI"""
        self.font_selection = FontSelectFrame(self.toplevelarticle, callback=self.update_preview)
        self.font_selection.pack(expand=True, side='bottom')
        self.big_frame = ttk.Frame(self.toplevelarticle)
        self.big_frame.pack(expand=True, fill='both')
        self.empty_label_top = ttk.Label(self.big_frame, text=f"\n")
        self.empty_label_top.pack(expand=True)
        self.title_labelframe = ttk.Label(self.big_frame, text='Title', relief='groove', borderwidth=0.5)
        self.title_labelframe.pack(expand=True, side='top')
        self.title_label = ttk.Label(self.title_labelframe, text=f"{self.title}",
                                     cursor='hand2', font='Arial 15', wraplength=ToplevelArticleDatabase.x)
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
        # Create Right-click menu for copying
        self.menu = tk.Menu(self.note, tearoff=0)
        self.menu.add_command(label='Copy', font='Arial 10', command=self.copy_text_to_clipboard)
        # Create the right click menu for the Title Label
        self.create_right_click_menu()

    def post_menu(self, event):
        """Posts the right click menu at the cursor's coordinates"""
        self.menu.post(event.x_root, event.y_root)

    def post_title_menu(self, event):
        """Posts the right click menu of the Title Label at the cursor's coordinates"""
        self.right_click_menu_for_title_label.post(event.x_root, event.y_root)

    def create_right_click_menu(self):
        """Creates the menu for the title label"""

        self.right_click_menu_for_title_label = tk.Menu(self.title_label, tearoff=0)
        self.right_click_menu_for_title_label.add_command(label='Copy link', font='Arial 10',
                                                          command=lambda: pyperclip.copy(self.url))

    def create_binds(self):
        """Creates the binds for the menus"""
        self.title_label.bind('<ButtonRelease-3>', self.post_title_menu)  # Menu is posted in self.text
        self.text.bind('<ButtonRelease-3>', self.post_menu)  # Menu is posted in self.text
        self.text1.bind('<ButtonRelease-3>', self.post_menu)
        # Allow user to select the text (i.e. if the user wants to copy it)
        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.text1.bind("<1>", lambda event: self.text1.focus_set())

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
