import json
import os
import re
import sys
import threading
import time
import sqlite3
import tkinter as tk
import tkinter.font
import unicodedata
from datetime import datetime
from tkinter import Menu, StringVar, ttk
import tktooltip  # pip install tkinter-tooltip https://github.com/gnikit/tkinter-tooltip
import sv_ttk
import undetected_chromedriver
from scrape_tpp_gui.helper_functions import callback, str2bool
from scrape_tpp_gui.source.version.version_module import file_exists
from misc import url_list, url_list_base_page, dir_path
from FirstPage import FirstPage
from classes.ShowInfo import ShowInfo
from classes.ToplevelAbout import ToplevelAbout
from classes.ToplevelSocial import ToplevelSocial
from classes.ToplevelDonate import ToplevelDonate
from classes.ToplevelAboutTpp import ToplevelAboutTpp
from classes.AskUpdate import AskUpdate
from scrape_tpp_gui.trace_error import trace_error
from source.version.version_module import check_online_version, check_new_version
from classes.search_software import InstalledSoftware
from classes.WarningDoesNotExists import WarningDoesNotExists
from classes.settings import SettingsTopLevel
from source.classes.loading import LoadingWindow


class App:
    """Main App"""
    x = 1600
    y = 500
    base_url = "https://thepressproject.gr/"
    page_dict = {}  # Holds the FirstPage objects
    # Holds the number of the page inserted in each notebook tab (FirstPage).
    treeview_tab_page_counter = {}  # Default: {'Newsroom: 1'} (as, it loads the news up to the first page)

    def __init__(self, root, to_bypass, debug):
        self.loading_tk = None
        self.dir_path = self.find_current_dir_path()
        self.transparency = None
        self.help_menu = None
        self.tpp_menu = None
        self.theme_menu = None
        self.edit_menu = None
        self.load_more_news = None
        self.load_more_news_bypass = None
        self.context = None
        self.f_time = None
        self.time = None
        self.loading_status = True
        self.settings_dict = {}
        self.check_updates_at_startup = False  # It changes after reading and setting the variables from the json file.
        self.set_class_variables_from_settings_after_reading()
        root.geometry(f'{App.x}x{App.y}')
        self.root = root
        self.bypass = to_bypass
        self.debug = debug
        # Show the loading window
        self.loading_window()
        self.root.title('The Press Project news feed')
        self.time_widgets()
        self.note = ttk.Notebook(self.root)
        self.note.pack(side='bottom', fill='both', expand=True)
        self.create_the_notebook_pages()
        self.top_label = ttk.Label(self.root, text='The Press Project', cursor='hand2', font='Arial 20')
        self.top_label.pack(side='top', pady=15)
        self.top_label.bind("<Button-1>", lambda e: callback(App.base_url))
        tktooltip.ToolTip(self.top_label, msg='Click to open ThePressProject site in the browser', delay=0.5)
        self.empty_label_between_top_and_notebook = ttk.Label(self.root, text=" ", font='Arial 16')
        self.empty_label_between_top_and_notebook.pack(side='top')
        # Main menu
        self.main_menu = Menu(self.root, font='Arial 16',
                              tearoff=0)  # Tearoff has to be 0, so as the command to start being posted in position 0.
        self.root.config(menu=self.main_menu)
        # Create the rest menus
        self.create_menu()
        # Check for updates at startup
        self.check_for_updates(startup=self.check_updates_at_startup, from_menu=False)

        # Load transparency settings at startup from LoadingWindow!

    def loading_window(self):
        """
        Just calls the LoadingWindow, a new Toplevel.

        :return: None


        It can be also implemented with a tk.Tk() instance. You have to put this code in the init() of the App class.
        You should also change the LoadingWindow to inherit from tk.Tk.
                thr = threading.Thread(target=self.loading_window)
                thr.start()

        See here: https://stackoverflow.com/a/67097216
        """
        # LoadingWindow can inherit either from tk.TK() or tk.Toplevel.
        # If tk.Tk() is chosen, call loading_tk.mainloop().
        self.loading_tk = LoadingWindow(root=self.root, controller=self)
        print("App>loading_window called")
        if isinstance(self.loading_tk, tk.Tk):
            self.loading_tk.mainloop()

    def create_the_notebook_pages(self):
        """
        Creates the notebook pages. After each creation, it updates the progress bar in the Loading Window.
        """
        # For the 1st page of Newsroom: list(url_list.values())[0][0]
        self.notebook_pages(url=list(url_list.values())[0][0], note=self.note, controller=self, name='Newsroom')
        # Update the progress bar in the Toplevel loading window.
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[1][0], note=self.note, controller=self, name='Politics')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[2][0], note=self.note, controller=self, name='Economy')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[3][0], note=self.note, controller=self, name='International')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[4][0], note=self.note, controller=self, name='Reportage')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[5][0], note=self.note, controller=self, name='Analysis')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[6][0], note=self.note, controller=self, name='tpp.tv')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[7][0], note=self.note, controller=self, name='tpp.radio')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[8][0], note=self.note, controller=self, name='Anaskopisi')
        self.loading_tk.progress()
        self.notebook_pages(url=list(url_list.values())[9][0], note=self.note, controller=self, name='Culture')
        self.loading_tk.progress()

    def notebook_pages(self, url, note, controller, name):
        """
        Initiates and stores all the pages of the notebook (FirstPage class) in App.page_dict
        """
        App.page_dict[name] = FirstPage(note=note, name=name, controller=self, url=url, to_bypass=self.bypass,
                                        debug=self.debug, root=self.root)
        if name not in App.treeview_tab_page_counter:
            App.treeview_tab_page_counter[name] = 1

    def create_menu(self):
        """
        Creates all the menus. Base menu is self.main_menu.
        :return: None
        """
        # Menu named "Menu" for main tk Window
        self.context = Menu(self.main_menu, font='Arial 10',
                            tearoff=0)
        # 'Load more news' Menu. It's a submenu of self.context
        self.load_more_news = Menu(self.context, font='Arial 10', tearoff=0)
        self.load_more_news.add_command(label='Newsroom', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Newsroom'))
        self.load_more_news.add_command(label='Politics', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Politics'))
        self.load_more_news.add_command(label='Economy', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Economy'))
        self.load_more_news.add_command(label='International', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='International'))
        self.load_more_news.add_command(label='Reportage', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Reportage'))
        self.load_more_news.add_command(label='Analysis', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Analysis'))
        self.load_more_news.add_command(label='tpp.tv', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='tpp.tv'))
        self.load_more_news.add_command(label='tpp.radio', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='tpp.radio'))
        self.load_more_news.add_command(label='Anaskopisi', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Anaskopisi'))
        self.load_more_news.add_command(label='Culture', font='Arial 10',
                                        command=lambda: self.insert_news_for_a_particular_tab(name='Culture'))
        # "Load more news (bypass)" Menu. It's a submenu of self.context
        self.load_more_news_bypass = Menu(self.context, font='Arial 10', tearoff=0)
        self.load_more_news_bypass.add_command(label='Newsroom', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Newsroom',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='Politics', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Politics',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='Economy', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Economy',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='International', font='Arial 10',
                                               command=lambda:
                                               self.insert_news_for_a_particular_tab(name='International', bypass=True))
        self.load_more_news_bypass.add_command(label='Reportage', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Reportage',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='Analysis', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Analysis',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='tpp.tv', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='tpp.tv',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='tpp.radio', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='tpp.radio',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='Anaskopisi', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Anaskopisi',
                                                                                                     bypass=True))
        self.load_more_news_bypass.add_command(label='Culture', font='Arial 10',
                                               command=lambda: self.insert_news_for_a_particular_tab(name='Culture',
                                                                                                     bypass=True))
        # Add the self.load_more_news to self.context
        self.context.add_command(label='Renew titles', font='Arial 10', command=self.call_renew_feed)
        self.context.add_cascade(label='Load more news', menu=self.load_more_news, underline=0, font='Arial 10')
        # Add more commands
        self.context.add_separator()
        self.context.add_command(label='Renew titles (bypass)', font='Arial 10', command=self.call_renew_feed_bypass)
        self.context.add_cascade(label='Load more news (bypass)', menu=self.load_more_news_bypass, underline=0,
                                 font='Arial 10')
        # Settings
        self.context.add_separator()
        self.context.add_command(label='Settings', font='Arial 10',
                                 command=lambda: SettingsTopLevel(root=self.root, controller=self))
        # Save to db
        self.context.add_separator()
        self.context.add_command(label='Save to db', font='Arial 10', command=self.save_dataclasses_to_sqlite)
        # Exit
        self.context.add_separator()
        self.context.add_command(label='Exit', font='Arial 10', command=self.exit_the_program)
        # Add the cascade here. The submenu has to be built first and then be added to the main menu
        self.main_menu.add_cascade(label='Menu', menu=self.context)
        # Edit menu
        self.edit_menu = Menu(self.main_menu, tearoff=0)
        # Change theme menu
        self.theme_menu = Menu(self.edit_menu, tearoff=0)
        self.theme_menu.add_command(label='Azure', command=lambda: self.change_theme('azure'))
        # self.theme_menu.add_command(label="Sun valley", command=self.change_theme_sun_valley)
        self.theme_menu.add_command(label='Adapta', command=lambda: self.change_theme('adapta'))
        self.theme_menu.add_command(label='Aquativo',
                                    # https://ttkthemes.readthedocs.io/en/latest/themes.html#radiance-ubuntu
                                    command=self.change_theme_aquativo)
        self.theme_menu.add_command(label='Radiance', command=lambda: self.change_theme('radiance'))
        self.theme_menu.add_command(label='Plastik', command=lambda: self.change_theme('plastik'))
        self.theme_menu.add_command(label='Yaru', command=lambda: self.change_theme('yaru'))
        self.theme_menu.add_command(label='Arc', command=lambda: self.change_theme('arc'))
        self.theme_menu.add_command(label='XP native', command=lambda: self.change_theme('xpnative'))
        self.edit_menu.add_cascade(label='Change theme', font='Arial 10', menu=self.theme_menu, underline=0)
        self.edit_menu.add_command(label='Save theme', font='Arial 10', command=self.save_theme, underline=0)
        # TPP menu
        self.tpp_menu = Menu(self.main_menu, tearoff=0)
        self.tpp_menu.add_command(label='About ThePressProject', font='Arial 10',
                                  command=lambda: ToplevelAboutTpp(self, root=self.root))
        self.tpp_menu.add_command(label='Social media', font='Arial 10',
                                  command=lambda: ToplevelSocial(self, root=self.root, dir_path=dir_path))
        self.tpp_menu.add_command(label='Donate', font='Arial 10',
                                  command=lambda: ToplevelDonate(self, root=self.root, dir_path=dir_path))
        self.tpp_menu.add_command(label='Subscribe to Newsletter', font='Arial 10',
                                  command=lambda: callback('http://eepurl.com/dGNy2H'))
        # Create the Help menu on top of main menu
        self.help_menu = Menu(self.main_menu, tearoff=0)
        self.help_menu.add_command(label='About...', font='Arial 10', command=lambda: ToplevelAbout(self, self.root))
        self.help_menu.add_command(label='Check for updates', font='Arial 10',
                                   command=self.check_for_updates)
        # Add the rest menus as cascades menus on top of main menu
        self.main_menu.add_cascade(label='Edit', menu=self.edit_menu, underline=0)
        self.main_menu.add_cascade(label='TPP', menu=self.tpp_menu, underline=0)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu, underline=0)

    def insert_news_for_a_particular_tab(self, name, bypass=False):
        """
        Saves the number of pages loaded in the particular category to App.treeview_tab_page_counter[name]
        and loads the App.treeview_tab_page_counter[name] + 1.
        :param bypass: To use webdriver or not.
        :param name: The name of the category as a strings
        :return: None
        """
        print("App>insert_news_for_a_particular_tab")
        if bypass:  # Need to check here.
            if self.check_for_chrome_and_chromedriver() is False:  # If it returns False (=>Either does not exists)
                return  # Just break the function
        App.treeview_tab_page_counter[name] += 1  # Add 1 to the default counter
        if name not in ('Anaskopisi', 'anaskopisi'):
            url_to_scrape = str(url_list_base_page[name]) + str(App.treeview_tab_page_counter[name])
        else:  # name == Anaskopisi
            suffix = (App.treeview_tab_page_counter[name] - 1) * 20  # The second page needs n=20
            url_to_scrape = str(url_list_base_page[name]) + str(suffix)
        print(f"News [counter {App.treeview_tab_page_counter[name]}] will be added to the category {name} "
              f"from url: {url_to_scrape}")
        App.page_dict[name].insert_news_from_page(url=url_to_scrape, category=name, bypass=bypass)

    def call_renew_feed(self):
        """Recalls the site and renew the treeview for all tabs"""
        FirstPage.news_total.clear()  # Clear needs to be called here, just once. Not in Firstpage via renew_feed()
        for dictio in App.page_dict.values():
            dictio.renew_feed()
        self.f_time.destroy()
        self.time_widgets()
        print(f'App>call_renew_feed()')

    def call_renew_feed_bypass(self):
        """
        Renews the treeview for all tabs by using Chromedriver
        """
        if self.check_for_chrome_and_chromedriver() is False:
            return  # Break the function
        print(f'App>call_renew_feed_bypass()')
        FirstPage.news_total.clear()  # Clear needs to be called here, just once. Not in Firstpage via renew_feed()
        for dictio in App.page_dict.values():
            dictio.renew_feed_bypass()
        self.f_time.destroy()
        self.time_widgets()
        print(f'Notebooks renewed')

    def check_for_chrome_and_chromedriver(self):
        """
        Checks if Chrome is installed and then, checks if chromedriver is in PATH.
        :return:
        """
        program_to_find = InstalledSoftware('chrome')
        if len(program_to_find.installed_programs) == 0:
            WarningDoesNotExists(root=self.root, controller=self, info="Chrome is not installed!", program='chrome')
            return False
        elif not InstalledSoftware.program_exists('chromedriver'):
            WarningDoesNotExists(root=self.root, controller=self, info="Chromedriver is not found!", x=370, y=170,
                                 program='chromedriver')
            return False

    def time_widgets(self):
        """
        Constructs the time widget at upper left of the window.
        :return:
        """
        # Time frame
        time_now = datetime.now()
        dt = str(time_now.strftime("%d-%m-%Y, %H:%M:%S"))
        dt = 'News loaded at: ' + dt
        var = StringVar()
        var.set(dt)
        self.f_time = ttk.Frame(self.root, height=40, width=160)
        self.f_time.pack(expand=False, side='top', fill="both", padx=5, pady=5)
        self.f_time.place(x=10, y=10)
        self.time = tk.Label(self.f_time, textvariable=var)
        self.time.pack(side='left')

    def check_for_updates(self, from_menu=True, startup=False):
        """
        Checks for a new version at the remote repository.
        :param from_menu:
        :param startup: Boolean: If true, calls AskUpdate at startup.
        """
        if check_new_version():
            if from_menu:
                AskUpdate(controller=self, root=self.root)
            if startup:  # Delay 8 secs the prompt window, not to be shown immediately after startup
                self.root.after(8000, lambda: AskUpdate(controller=self, root=self.root))

        else:  # There is not a new version.
            if from_menu:
                ShowInfo(controller=self, root=self.root, info='The application is up-to-date!')
            if startup:
                self.root.after(8000,
                                lambda: ShowInfo(controller=self,
                                                 root=self.root, info='The application is up-to-date!'))

    def post_settings(self):
        """
        Settings
        # TODO fill details
        :return:
        """
        pass

    def exit_the_program(self):
        """Exits the program"""
        if FirstPage.driver is not None:
            try:
                FirstPage.driver.close()
                FirstPage.driver.quit()
                print("App>exit_the_program>Driver closed")
            except Exception as err:
                print(err)
                trace_error()
        self.root.destroy()
        print(f'App>exit_the_program()')
        sys.exit()

    def find_current_dir_path(self) -> str | os.PathLike:
        """
        Finds and returns the path of the directory of the running .py script or .exe .
        """

        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            self.dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)
            print(f'Script: {self.dir_path}')
            return self.dir_path

    def save_dataclasses_to_sqlite(self):
        """
        Saves scraped dataclasses to a sqlite db.
        Currently, dataclass contains:      date: Any
                                            url: str = ''
                                            main_content: str = ''
                                            summary: str = ''
                                            title: str = ''
                                            author: str = ''
                                            author_url: str = ''
                                            date_unix: Any = 'To_change'
                                            category: str = ''
        See also:
            Official docs: https://docs.python.org/3/library/sqlite3.html
            UPSERT process: https://stackoverflow.com/a/4330694 & https://www.sqlite.org/draft/lang_UPSERT.html
        """
        db_path = os.path.join(self.dir_path, 'tpp.db')
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("""PRAGMA encoding = 'UTF-8';""")
            con.commit()
            # Do not use ID AUTO INCREMENT.
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS news(
                            id TEXT PRIMARY KEY,
                            date TEXT NOT NULL, 
                            url TEXT NOT NULL,
                            main_content BLOB,
                            summary BLOB,
                            title TEXT NOT NULL,
                            author TEXT,
                            author_url TEXT,
                            date_unix INT,
                            category TEXT);
                        """)
            con.commit()
            # https://www.sqlitetutorial.net/sqlite-update/
            # Examples for IGNORE https://database.guide/how-on-conflict-works-in-sqlite/
            # ON CONFLICT: https://stackoverflow.com/questions/69961193/how-to-get-on-conflict-ignore-working-in-sqlite
            for number, _dataclass in enumerate(FirstPage.news_total):
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
                if number <= 5:
                    print(f'FirstPage.news_total: \n\t{tuple_dataclass}')
                    print(f'tuple for the db: {tuple_dataclass[1:3:1]}')

                # On how to insert properly placeholders in SQL statements, see
                # https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries
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
            cur.execute("""SELECT * FROM news ORDER BY date_unix DESC""")
            for number, a in enumerate(cur.fetchall()):
                if number <= 5:
                    print(f'Fetched from db: {a}')

        except (sqlite3.Error, sqlite3.DatabaseError, UnicodeEncodeError, Exception) as err:
            trace_error()
            print(err)
        finally:
            con.close()

    def strip_ansi_characters(self, text=''):
        """https://stackoverflow.com/questions/48782529/exclude-ansi-escape-sequences-from-output-log-file"""
        try:
            # ansi_re = re.compile(r'[^\x00-\x7F]+')
            # return re.sub(r'[^\x00-\x7F]+', ' ', text)
            '''text = text.encode("ascii", "ignore")
                        text = text.decode()
                        print(text)
                        return text'''
            ansi_re = re.compile(r'\x1b\[[0-9;]*m')
            re.sub(ansi_re, ' ', text)
            ansi_re = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            unicodedata.normalize('NFKD', text)
            return re.sub(ansi_re, ' ', text)

        except re.error as err:
            print(err)

    ###################
    # Theme functions #
    ###################

    def change_theme(self, theme: str):
        """
        Changes the theme of the tkinter based on the theme's name passed.
        :param theme: The name of theme
        """
        toplevel_temporary_list = []
        '''# https://stackoverflow.com/questions/10343759/determining-what-tkinter-window-is-currently-on-top
        # https://python-forum.io/thread-7744.html
        stack_order = root.tk.eval('wm stackorder {}'.format(root))
        L = [x.lstrip('.') for x in stack_order.split()]
        print([(root.children[x] if x else root) for x in L])
        print(stack_order)'''
        for (child, child_widget) in self.root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.root.withdraw()  # Hide the root
        if theme == 'azure':
            self.change_theme_azure()
        elif theme == 'radiance':
            self.change_theme_radiance()
        elif theme == 'aquativo':
            self.change_theme_aquativo()
        elif theme == "plastik":
            self.change_theme_plastik()
        elif theme == "adapta":
            self.change_theme_adapta()
        elif theme == "yaru":
            self.change_theme_yaru()
        elif theme == "arc":
            self.change_theme_arc()
        elif theme == "xpnative":
            self.change_theme_xpnative()
        self.root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    def change_theme_azure(self):
        print(f'All styles: {self.root.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {self.root.tk.call("ttk::style", "theme", "use")}')
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
                # root.tk.call("ttk::style", "theme", "use", "azure-light")
            else:
                try:
                    self.root.tk.call("set_theme", "dark")
                    # root.tk.call("ttk::style", "theme", "use", "azure-dark")
                except tkinter.TclError as err:
                    print(err)
        except (tkinter.TclError, Exception) as err:
            print(err)

    def change_theme_forest(self):
        print(f'All styles: {self.root.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {self.root.tk.call("ttk::style", "theme", "use")}')
        toplevel_temporary_list = []
        for (child, child_widget) in self.root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.root.withdraw()  # Hide the root
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "forest-dark":
                self.root.tk.call("set_theme", "light")
                # root.tk.call("set_theme", "forest-light")
                # style.theme_use('forest-light')
                # root.tk.call("ttk::style", "theme", "use", "azure-light")
            else:
                try:
                    self.root.tk.call("set_theme", "dark")
                    # style.theme_use('forest-dark')
                    # root.tk.call("set_theme", "forest-dark")
                    # root.tk.call("ttk::style", "theme", "use", "forest-dark")
                except tkinter.TclError as err:
                    print(err)
        except tkinter.TclError as err:
            print(err)
        self.root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    def change_theme_sun_valley(self):
        """
        https://stackoverflow.com/questions/30371673/can-a-ttk-style-option-be-deleted
        https://tcl.tk/man/tcl/TkCmd/ttk_style.htm
        https://wiki.tcl-lang.org/page/List+of+ttk+Themes
        CANT WORK WITH AZURE
        """
        print(f'All styles: {self.root.tk.call("ttk::style", "theme", "names")}')
        print(f'Previous Style: {self.root.tk.call("ttk::style", "theme", "use")}')
        toplevel_temporary_list = []
        for (child, child_widget) in self.root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.root.withdraw()  # Hide the root
        try:
            if sv_ttk.get_theme() == "dark":
                print("Setting theme to light")
                sv_ttk.use_light_theme()
            elif sv_ttk.get_theme() == "light":
                print("Setting theme to dark")
                sv_ttk.use_dark_theme()
            else:
                print("Not Sun Valley theme")
        except tkinter.TclError as err:
            print(err)
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
                self.root.tk.call("ttk::style", "theme", "use", 'sun-valley-light')
                self.root.tk.call("set_theme", "light")

            # elif root.tk.call("ttk::style", "theme", "use") == "sun-valley-light":
            else:
                # Set dark theme
                self.root.tk.call("ttk::style", "theme", "use", 'sun-valley-dark')
                self.root.tk.call("set_theme", "dark")
        except tkinter.TclError as err:
            print(err)
        self.root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    def change_theme_xpnative(self):
        try:
            # Switch first to light theme and then to XPnative in order for the black to be eliminated.
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'vista')
        except tkinter.TclError as err:
            print(err)

    def change_theme_radiance(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'radiance')
        except tkinter.TclError as err:
            print(err)

    def change_theme_aquativo(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'aquativo')
        except tkinter.TclError as err:
            print(err)

    def change_theme_plastik(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'plastik')
        except tkinter.TclError as err:
            print(err)

    def change_theme_adapta(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'adapta')
        except tkinter.TclError as err:
            print(err)

    def change_theme_yaru(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'yaru')
        except tkinter.TclError as err:
            print(err)

    def change_theme_arc(self):
        try:
            if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                self.root.tk.call("set_theme", "light")
            self.root.tk.call("ttk::style", "theme", "use", 'arc')
        except tkinter.TclError as err:
            print(err)

    def save_theme(self):
        """Saves the preferred theme to settings.json"""

        print(self.dir_path)
        settings_file_path = os.path.join(self.dir_path, "settings.json")
        current_theme = self.root.tk.call("ttk::style", "theme", "use")
        save_settings_to_dump = {'theme': current_theme}
        if file_exists(dir_path=self.dir_path, name='settings.json'):
            json_data = ''
            with open(os.path.join(self.dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:  # To avoid empty string in the text file
                    json_data = save_settings_to_dump
                else:
                    json_data.update(save_settings_to_dump)
            with open(os.path.join(self.dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
                print(f"Theme {current_theme} saved in: {settings_file_path}")
        else:
            with open(os.path.join(self.dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json_data = {'theme': current_theme}
                json.dump(json_data, file, indent=4)
                print(f"Theme saved to {os.path.join(self.dir_path, 'settings.json')}")

    @staticmethod
    def read_theme() -> str | None:
        """Reads the preferred theme"""
        dir_path = str
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            print(f'Script: {dir_path}')
        if file_exists(name="settings.json", dir_path=dir_path):
            with open(os.path.join(dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                print(json_data)
                if 'theme' in json_data:
                    return json_data['theme']
                else:
                    return None
        return None

    def use_theme(self, theme):
        """Sets the theme passed to the function"""
        toplevel_temporary_list = []
        for (child, child_widget) in self.root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        self.root.withdraw()  # Hide the root
        if theme == 'azure-dark' or None:
            self.root.tk.call("set_theme", "dark")
        elif theme == 'azure-light':
            self.root.tk.call("set_theme", "light")
        elif theme == 'radiance':
            self.change_theme_radiance()
        elif theme == 'aquativo':
            self.change_theme_aquativo()
        elif theme == "plastik":
            self.change_theme_plastik()
        elif theme == "adapta":
            self.change_theme_adapta()
        elif theme == "yaru":
            self.change_theme_yaru()
        elif theme == "arc":
            self.change_theme_arc()
        elif theme == "vista":
            self.change_theme_xpnative()
        self.root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

    ######################
    # Settings functions #
    ######################

    def read_settings(self) -> dict | None:
        """
        Reads the settings from `settings.json`.
        :return: A dictionary with the settings.

        """

        if file_exists(name="settings.json", dir_path=self.dir_path):
            with open(os.path.join(self.dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                print(json_data)
                return json_data
        return None

    def set_class_variables_from_settings_after_reading(self) -> None:
        """
        After loading the `settings.json`, it reads all the variables.
        If the settings file is not found, it implements default values.
        :return: None
        """
        self.settings_dict = self.read_settings()
        if self.settings_dict:
            # Even if the file exists, if the dictionary key does not exist, return self.settings as None
            try:
                self.check_updates_at_startup = self.settings_dict['auto_update_at_startup']  # Boolean
                # It's a float, it does not need conversion from percentage. It depicts the proportion of transparency
                # that the user wants. It needs to be subtracted from 1 in order to be used.
                # i.e. self.root.attributes('-alpha', 1 - 0.02) => 2% transparency
                self.transparency = self.settings_dict['transparency']
                print(f"Settings passed: "
                      f"\n\tauto_update_at_startup: {self.settings_dict['auto_update_at_startup']}"
                      f"\n\ttransparency: {self.settings_dict['transparency']}")
            except KeyError:
                self.settings_dict = None
                return None
        # There is not a settings.json. Apply default settings
        else:
            # Prompt update window at startup
            self.check_updates_at_startup = True
            # 0% transparency
            self.transparency = 0.0
            # Assign the values to settings dict
            self.settings_dict = {'auto_update_at_startup': self.check_updates_at_startup,
                                  'transparency': self.transparency}

    def set_transparency(self):
        """
        Sets the transparency using the value from settings.json
        """
        self.root.attributes('-alpha', 1 - self.transparency)

    def apply_settings(self):
        """
        Apply all settings.
        :return: None
        """
        # Assure that self.settings_dict is not None.
        if self.settings_dict:
            self.set_transparency()
