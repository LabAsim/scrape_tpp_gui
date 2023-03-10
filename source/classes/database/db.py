"""
Contains the class for the window to search the saved news from the database.
"""
import dataclasses
import os
import re
import sqlite3
import sys
import threading
import tkinter.font as font
import tkinter as tk
from tkinter import ttk
import inspect
from typing import Union

# Load modules from upper folders
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)
from SubPageReaderDB import SubPageReader

parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(os.path.dirname(parent_parent))
from helper_functions import file_exists, center, tkinter_theme_calling, callback, headers, sortby, date_to_unix, \
    is_driver_open
from trace_error import trace_error
from source.classes.generictoplevel import GenericToplevel
from source.classes.NewsDataclass import NewsDataclass
from helper import ToplevelArticleDatabase, wrapper_for_case_conversion, convert_to_case_not_sensitive, \
    converted_stressed_vowels_to_non_stressed, match_vowels
from scrape_tpp_gui.source.classes.helpers.loadingwindow import tooltip_handler_thread, loading_tooltip


class DatabaseWindow(GenericToplevel):
    """
    Creates the window for the database search
    """
    headers = ('Date', 'Title', 'Summary', 'Category')

    def __init__(self, root, controller, debug=False):
        super().__init__(root=root, controller=controller)
        # self.dir_path and self.toplevel are inherited from the GenericToplevel
        # Although this is redundant, if it is declared here, Pycharm's autofill works.
        self.toplevel: tk.Toplevel = self.toplevel
        # https://stackoverflow.com/questions/44218662/how-to-get-the-hwnd-of-a-tkinter-window-on-windows
        # Hide the window until everything is set up.
        self.toplevel.withdraw()
        self.x = 1500
        self.y = 500
        self.root = root
        self.controller = controller
        self.debug = debug
        self.toplevel.geometry(f"{self.x}x{self.y}")
        self.toplevel.title(f"News Database")
        # UI variables
        self.case_sensitive_boolean = tk.BooleanVar(value=True)
        self.case_sensitive_button = None
        self.searchbox = None
        self.text_var = tk.StringVar()
        self.combobox = None
        self.combobox_values = ('All', 'Date', 'Title', 'Summary', 'Category')
        self.upper_frame = None
        self.notebook = None
        self.big_frame = None
        self.tree = None
        self.font = font.Font(size=14)  # To measure the length of the letters
        self.fetched_news: list[tuple]  # A list with tuples: The values after loading the db.
        # The order: date, title, summary, category, id, url, main_content, author, author_url, date_unix
        #  i.e. [('Πριν 6 λεπτά', 'ΑΝΑΣΚΟΠΗΣΗ S09E14: ΚΩΝΣΤΑΝΤΙΝΟΣ', '', 'newsroom'),]
        self.tree_searched_values = []  # The values based on searched term
        self.dataclasses_list: list[{dataclasses.dataclass}] = []
        self.right_click_menu = None
        self.bar_menu = None
        self.main_menu = None
        self.database_submenu = None
        # Create GUI
        self.init_ui()
        self.fill_treeview()
        # Create the dataclasses
        self.create_dataclasses_thread()
        # Create Menu
        self.create_menu()
        # Create the binds
        self.create_binds()
        # Center the window
        center(self.toplevel, self.root)
        self.toplevel.lift()

    def init_ui(self):
        """
        Creates the user interface.
        :return: None
        """
        self.big_frame = ttk.Frame(self.toplevel)
        self.big_frame.pack(expand=True, fill='both')
        # Upper frame
        self.upper_frame = ttk.Frame(self.big_frame)
        self.upper_frame.pack(expand=False, fill='both')
        self.combobox = ttk.Combobox(self.upper_frame, values=self.combobox_values, state='readonly',
                                     justify='center')
        # https://docs.python.org/3.10/library/tkinter.ttk.html#tkinter.ttk.Combobox.current
        self.combobox.current(0)  # Set the first value as current default value
        self.combobox.pack(side='left', padx=(5, 5), pady=(5, 5))
        self.combobox.bind("<<ComboboxSelected>>", self.shift_focus_from_combobox_to_searchbox)
        self.searchbox = tk.Entry(self.upper_frame, textvariable=self.text_var, font='Arial 15', width=20)
        self.searchbox.pack(side='left', padx=(5, 5), pady=(5, 5))
        self.case_sensitive_button_save()
        # The style renamed with "Color." in front of "Switch.TCheckbutton" so as not to interfere with the rest of
        # the GUI
        self.case_sensitive_button = ttk.Checkbutton(self.upper_frame, text="Case sensitive",
                                                     command=self.case_sensitive_button_save,
                                                     variable=self.case_sensitive_boolean,
                                                     onvalue=True, offvalue=False,
                                                     style="Color.Switch.TCheckbutton")
        self.case_sensitive_button.pack(side='right', padx=15, pady=10)
        # To display the proper color for the text, It does not work without after.
        self.toplevel.after(50, self.case_sensitive_button_save)
        self.tree = ttk.Treeview(self.big_frame, columns=DatabaseWindow.headers, show='headings')
        self.setup_treeview()
        self.tree.pack(expand=True, fill='both')
        # Register quit button to the quit function
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel_quit)
        # Make everything visible again
        self.toplevel.deiconify()

    def setup_treeview(self):
        """Fills the treeview"""
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 16))
        style.configure("Treeview", font=(None, 13))
        for head in DatabaseWindow.headers:  # [:1]
            if head == "Title":
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            elif head == 'Summary':
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            elif head == 'Date':
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            elif head == 'Category':
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            else:
                self.tree.heading(column=head, text=f'{head}')
                self.tree.column(column=head, stretch=True)
        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree, orient="horizontal", command=self.tree.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

    def fill_treeview(self):
        """Fills the treeview with data from the database"""
        # Fetch from db
        self.fetched_news = self.fetch_from_db(
            query="SELECT date, title, summary, category, id, url, main_content, author, author_url, date_unix FROM "
                  "news ORDER BY date_unix DESC")
        # print(self.fetched_news)
        # Clear the treeview
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
        # Fill the treeview
        try:
            dates = []
            titles = []
            for number, tuple_news in enumerate(self.fetched_news):
                dates.append(self.font.measure(tuple_news[0]))
                titles.append(self.font.measure(tuple_news[1]))
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_news[0], tuple_news[1], tuple_news[2], tuple_news[3]])
                # values=[tuple_news[1].strip(), tuple_news[5].strip(), tuple_news[4], tuple_news[-1]])
            # Sort according to Category's name
            sortby(self.tree, 'Category', 0)
            # Fix the lengths
            self.tree.column(column='Title', minwidth=100, width=950, stretch=True)
            self.tree.column(column='Date', minwidth=150, width=int(max(dates) - 100), stretch=False)
            print(f"DatabaseWindow>fill_treeview()>news inserted")
        except tk.TclError as err:
            print(err)
            trace_error()

    def create_menu(self):
        """Creates the menu"""
        # Menu bar
        self.bar_menu = tk.Menu(self.toplevel, font='Arial 10', tearoff=0, background='black', fg='white')
        self.toplevel.config(menu=self.bar_menu)
        # Main menu
        self.main_menu = tk.Menu(self.bar_menu, font='Arial 10', tearoff=0, background='black', fg='white')
        self.bar_menu.add_cascade(label='Menu', menu=self.main_menu, background='black')
        self.database_submenu = tk.Menu(self.main_menu, font='Arial 10', tearoff=0, background='black', fg='white')
        self.main_menu.add_cascade(label='Database', menu=self.database_submenu, background='black')
        self.database_submenu.add_command(label="Reload", command=self.fill_treeview)
        self.database_submenu.add_command(label='Save', font='Arial 10  italic', background='black',
                                          command=self.save_to_db)
        self.main_menu.add_separator()
        self.main_menu.add_command(label='Exit', command=self.toplevel_quit)
        # Right click menu only for the treeview
        self.right_click_menu = tk.Menu(font='Arial 10', tearoff=0)
        # Lambda here is needed because there is no event to be passed. If no lambda is used, an error will be raised
        self.right_click_menu.add_command(label='Show article', command=lambda: self.show_main_article(event=None))

    def create_binds(self):
        """Binds events to functions"""
        # Bind the self.search to self.search_handler
        self.searchbox.bind('<KeyRelease>', self.search_handler)
        self.searchbox.bind('<Return>', self.search_handler, "+")
        # Bind left double click to post the menu
        self.tree.bind("<Double-1>", self.show_main_article)
        # Bind the right click with self.post_menu()
        self.tree.bind('<ButtonRelease-3>', self.post_menu)
        # Bind the right click on the Switch Button with the search.
        # When the user clicks on the button, a new search will initiate.
        self.case_sensitive_button.bind('<Button-1>', self.delayed_search)

    def delayed_search(self, event=None):
        """Delays a bit the search after the user has pressed the Switch button. The delay is essential because
        otherwise it will not search properly the db."""
        self.toplevel.after(250, lambda: self.search_handler(event=event))

    def post_menu(self, event):
        """
        Posts the menu at right click.
        :param event: Mouse click from bind method of the widget
        :return: None
        """
        self.right_click_menu.post(event.x_root, event.y_root)

    def show_main_article(self, event):
        """
        Shows the summary and the main article in a separate tk.Toplevel
        :param event: The event passed behind the scenes by self.tree.bind method
        :return: None
        """
        current = self.tree.focus()
        current_article = self.tree.item(current)['values'][1]  # [0] is the Date
        print(f'current: {current_article}')
        count = 0
        for number, class_ in enumerate(self.dataclasses_list):
            if current_article == class_.title and count == 0:
                class_.main_content.strip()
                print(f'class_.main_content ({len(class_.main_content)})')
                if len(class_.main_content) != 0:
                    print(f'DatabaseWindow>show_main_article>Content exists: Main content: '
                          f'\n{class_.main_content}')
                    count += 1
                    ToplevelArticleDatabase(newsclass=class_, root=self.root, controller=self.controller)
                else:
                    print(f'SubPageReader to be called')
                    # Scrape the data
                    added_new = SubPageReader(url=class_.url, header=headers(), debug=self.debug,
                                              controller=self.controller, root=self.root, newsclass=class_)
                    data = added_new.data_to_return
                    print(f'length of SubPageReader: {len(data)}'
                          f'\nData from SubPageReader: {data}')
                    # Save the data to a new Dataclass
                    newsclass = NewsDataclass(url=data[0], date=data[2],
                                              title=data[1], summary=data[3],
                                              main_content=data[4], author=data[5], author_url=data[6],
                                              category=class_.category)
                    # Modify the current (on focus) row of the treeview
                    print(f"Current contents: {self.tree.item(current)['values']}")
                    self.tree.item(current, values=(newsclass.date, newsclass.title,
                                                    newsclass.summary, newsclass.category))
                    # print(f'Main content: \n{newsclass.main_content}')
                    count += 1
                    ToplevelArticleDatabase(newsclass=newsclass, root=self.root, controller=self.controller)
                    # Remove the Dataclass not containing main_content and summary
                    # after appending the newsclass to the same list
                    self.dataclasses_list.insert(number, newsclass)  # Insert the newsclass to same index as class_
                    self.dataclasses_list.remove(class_)

    def create_dataclasses_thread(self):
        """
        Starts a thread for converting tuples to dataclasses
        :return: None
        """
        thread_data = threading.Thread(target=self.convert_tuples_to_dataclasses)
        thread_data.start()

    def convert_tuples_to_dataclasses(self):
        """
        Converts the fetched tuples to dataclasses
        :return: None
        """
        # self.fetched_news were filled in self.fill_treeview()
        for _tuple in self.fetched_news:
            # The order inside the tuple is:
            # date, title, summary, category, id, url, main_content, author, author_url, date_unix
            date_ = _tuple[0]
            title = _tuple[1]
            summary = _tuple[2]
            category = _tuple[3]
            url = _tuple[5]
            main_content = _tuple[6]
            author = _tuple[7]
            author_url = _tuple[8]
            # date_unix = _tuple[9]
            self.dataclasses_list.append(NewsDataclass(url=url, title=title, date=date_,
                                                       category=category, summary=summary,
                                                       main_content=main_content, author=author,
                                                       author_url=author_url
                                                       )
                                         )
        # print(self.dataclasses_list)

    ####################
    # Search functions #
    ####################
    def search_handler(self, event=None) -> None:
        """
        Called after a key is released in the search box. The functions grabs the values of the combobox
        and the search box, retrieves the news based on these values and fills the treeview afterwards.
        :param event: <KeyRelease>
        :return: None
        """
        # Focus on the search box
        self.searchbox.focus_set()
        # Grab the values
        term = self.text_var.get().strip()
        combobox_current_value = self.combobox.get()
        print(f'db>search_handler>Searchbox called with term {term} in category: {combobox_current_value}')
        # Search and retrieve info based on the term
        self.retrieve_info(category=combobox_current_value, term=term)
        # Display the retrieved values
        self.fill_treeview_after_search()

    @staticmethod
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

    @wrapper_for_case_conversion
    def retrieve_info(self, category, term):
        """
        Retrieves the values based on term and appends to a temporary list
        :param category: The category to search
        :param term: Based on what to search
        :return: tuple(tuples)
        """
        print(f"{__class__.__name__}>{inspect.getframeinfo(inspect.currentframe())[2]}>Term: '{term}'")
        # Clear the temp list
        self.tree_searched_values = []
        # Assure there is a category. If not, do nothing
        if term != "":
            if category == "All":
                for _tuple in self.fetched_news:
                    chopped_tuple = tuple(_tuple[:4])
                    for tuple_item in chopped_tuple:
                        # print(_tuple[0:4])
                        if not self.case_sensitive_boolean.get():  # Case not sensitive
                            # term is already converted from the wrapper function!
                            tuple_item_modified = converted_stressed_vowels_to_non_stressed(
                                match_vowels(convert_to_case_not_sensitive(tuple_item)))
                            if term in tuple_item_modified:
                                # print(f"{__class__.__name__}>{inspect.getframeinfo(inspect.currentframe())[2]}>"
                                #      f"Case-sensitive({self.case_sensitive_boolean.get()}): Term: "
                                #      f"{term}: {tuple_item_modified}")
                                if chopped_tuple not in self.tree_searched_values:
                                    self.tree_searched_values.append(chopped_tuple)
                        else:  # Case-sensitive is set to True
                            tuple_item_matched_vowels = match_vowels(tuple_item)
                            term = match_vowels(term)
                            if term in tuple_item_matched_vowels:
                                # print(f"{__class__.__name__}>{inspect.getframeinfo(inspect.currentframe())[2]}>"
                                #      f"Case-sensitive({self.case_sensitive_boolean.get()}): Term: "
                                #      f"{term}: {tuple_item_matched_vowels}")
                                if chopped_tuple not in self.tree_searched_values:
                                    self.tree_searched_values.append(chopped_tuple)
            elif category == "Category":
                for _tuple in self.fetched_news:
                    # The last obj of the tuple is the category
                    if term in _tuple[3]:
                        self.tree_searched_values.append(_tuple)
            elif category == "Title":
                for _tuple in self.fetched_news:
                    # The second obj of the tuple is the title
                    if term in _tuple[1]:
                        self.tree_searched_values.append(_tuple)
            elif category == "Date":
                for _tuple in self.fetched_news:
                    # The first obj of the tuple is the Date
                    if term in _tuple[0]:
                        self.tree_searched_values.append(_tuple)
            elif category == "Summary":
                for _tuple in self.fetched_news:
                    # The third obj of the tuple is the Summary
                    if term in _tuple[2]:
                        self.tree_searched_values.append(_tuple)
        elif category == "" and term == "":
            self.tree_searched_values = self.fetched_news
        elif term == "":
            self.tree_searched_values = self.fetched_news

    def fill_treeview_after_search(self):
        """
        Fills the treeview based on values retrieved from search box
        :return:
        """
        # First, clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Fill the treeview based on the typed entry
        if len(self.tree_searched_values) != 0:
            for number, tuple_news in enumerate(self.tree_searched_values):
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_news[0], tuple_news[1], tuple_news[2], tuple_news[3]])
        print(f"{__class__.__name__}>{inspect.getframeinfo(inspect.currentframe())[2]}> The tree filled after search")

    def case_sensitive_button_save(self):
        """
        Returns the current state (True/False) of `self.case_sensitive_boolean`.
        :return: Boolean: The current state of BooleanVar

        Strikethrough text is not displayed well in tkinter. Usage of color is better to indicate user's preference.
        """
        current_state_of_case_sensitive_button_save_variable = self.case_sensitive_boolean.get()
        if not current_state_of_case_sensitive_button_save_variable:
            self.color_config(widget_style="Color.Switch.TCheckbutton", color="red")
            print(f"DatabaseWindow>case_sensitive_button_save>Case NOT sensitive, color "
                  f"{ttk.Style().lookup('Color.Switch.TCheckbutton', option='foreground')}")
        elif current_state_of_case_sensitive_button_save_variable:
            self.color_config(widget_style="Color.Switch.TCheckbutton", color="green")
            print(f"DatabaseWindow>case_sensitive_button_save>Case sensitive, color "
                  f"{ttk.Style().lookup('Color.Switch.TCheckbutton', option='foreground')}")
        print(
            f"current_state_of_case_sensitive_button_save_variable set: value:{current_state_of_case_sensitive_button_save_variable}")
        return current_state_of_case_sensitive_button_save_variable

    def color_config(self, widget_style, color):
        """
        Configures the style of the text in the widget.

        :param widget_style: The name of the widget style.
        :param color: The color to be changed to
        :return: None

        See: https://docs.python.org/3.10/library/tkinter.ttk.html#tkinter.ttk.Style.configure
        """
        ttk.Style().configure(widget_style, foreground=color)

    def shift_focus_from_combobox_to_searchbox(self, event):
        """
        Shifts focus from combobox to search box.
        It also reapplies the selected value (otherwise the values remains highlighted)
        :param event: The trigger event
        :return: None
        """
        # Focus on search box
        self.searchbox.focus_set()
        # Reapply the combobox value
        combobox_current_value = self.combobox.get()
        self.combobox.set("")
        self.combobox.set(combobox_current_value)

    ######################
    # Database functions #
    ######################
    def save_to_db(self):
        """
        Saves the news (the dataclasses) back to the database. If there is a conflict, it updates the database.
        :return: None

        See:
            On how to insert properly placeholders in SQL statements, see
                https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries
        """
        db_path = os.path.join(self.dir_path_exe, 'tpp.db')
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("""PRAGMA encoding = 'UTF-8';""")
            con.commit()
            # https://www.sqlitetutorial.net/sqlite-update/
            # Examples for IGNORE https://database.guide/how-on-conflict-works-in-sqlite/
            # ON CONFLICT: https://stackoverflow.com/questions/69961193/how-to-get-on-conflict-ignore-working-in-sqlite
            for number, _dataclass in enumerate(self.dataclasses_list):
                tuple_dataclass = _dataclass.return_as_tuple()
                #  It needs a primary key incorporating both category and url.
                text_id = tuple_dataclass[8] + '+' + tuple_dataclass[1]
                # Create a tuple with all the values to be passed in SQL statement
                list_to_insert = [text_id]
                for a in tuple_dataclass:
                    list_to_insert.append(a)
                for a in (tuple_dataclass[0], tuple_dataclass[2], tuple_dataclass[3],
                          tuple_dataclass[5], tuple_dataclass[6], tuple_dataclass[8]):
                    list_to_insert.append(a)

                cur.execute(f"""
                                INSERT INTO news VALUES(?,?,?,?,?,?,?,?,?,?)
                                ON CONFLICT(news.id) DO UPDATE SET
                                    date = ?,
                                    main_content = ?,
                                    summary = ?,
                                    author = ?,
                                    author_url = ?,
                                    category = ?;
                                """, list_to_insert)
                # Remember to commit the transaction after executing INSERT.
                con.commit()
                if self.debug:
                    with open('example.txt', 'a+', encoding="utf-8") as file:
                        file.write(f"""
                                    INSERT INTO news VALUES('{text_id}','{tuple_dataclass[0]}','{tuple_dataclass[1]}',
                                    '{tuple_dataclass[2]}', '{tuple_dataclass[3]}', '{tuple_dataclass[4]}',
                                    '{tuple_dataclass[5]}','{tuple_dataclass[6]}','{tuple_dataclass[7]}',
                                    '{tuple_dataclass[8]})
                                    ON CONFLICT(news.url) DO UPDATE SET
                                        date = '{str(tuple_dataclass[0])}',
                                        main_content = '{str(tuple_dataclass[2])}',
                                        summary = '{str(tuple_dataclass[3])}',
                                        author = '{tuple_dataclass[5]}',,
                                        author_url = '{tuple_dataclass[6]}',
                                        category = '{tuple_dataclass[8]}';
                                    """)
            print(f"{__class__.__name__}>{inspect.getframeinfo(inspect.currentframe())[2]}>Saved to db")
            if self.debug:
                cur.execute("""SELECT * FROM news ORDER BY date_unix DESC""")
                for number, a in enumerate(cur.fetchall()):
                    if number <= 5:
                        print(f'Fetched from db: {a}')
        except (sqlite3.Error, sqlite3.DatabaseError, UnicodeEncodeError, Exception) as err:
            trace_error()
        finally:
            con.close()

    def fetch_from_db(self, query: str) -> list:
        """

        :return: Data from the database
        """

        db_path = os.path.join(self.dir_path_exe, 'tpp.db')
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("""PRAGMA encoding = 'UTF-8';""")
            con.commit()
            cur.execute(f"""{query}""")
            return cur.fetchall()
        except (sqlite3.Error, sqlite3.DatabaseError, UnicodeEncodeError, Exception):
            trace_error()
        finally:
            con.close()

    def fetchall_from_db(self):
        """
        Connects and fetches the saved news from the sqlite db.
        :return: None
        """
        db_path = os.path.join(self.dir_path_exe, 'tpp.db')
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("""PRAGMA encoding = 'UTF-8';""")
            con.commit()
            cur.execute("""SELECT * FROM news ORDER BY date_unix DESC""")
            self.fetched_news = cur.fetchall()
            print(self.fetched_news)
        except (sqlite3.Error, sqlite3.DatabaseError, UnicodeEncodeError, Exception):
            trace_error()
        finally:
            con.close()

    ##################
    # Misc functions #
    ##################

    def toplevel_quit(self):
        """
        Sets the variable of itself in self.controller as None and quits.
        :return:
        """
        if self.controller:
            self.controller.database_tk_window = None
        self.toplevel.destroy()


if __name__ == "__main__":
    # import customtkinter as ctk
    # from customtkinter import *
    # root = ctk.CTk()
    root = tk.Tk()
    center(root)
    db_window = DatabaseWindow(root=root, controller=None)
    tkinter_theme_calling(root)
    # root.tk.call("set_theme", "light")
    root.mainloop()
