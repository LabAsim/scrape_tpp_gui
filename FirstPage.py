"""
A class containing the notebook tabs (ttk.notebook).
"""
import tkinter as tk
import tkinter.font
from tkinter import Menu, ttk
import undetected_chromedriver as uc  # pip install undetected-chromedriver
from helper_functions import callback, headers, sortby, date_to_unix, is_driver_open
from trace_error import trace_error
from classes.NewsDataclass import NewsDataclass
from classes.ToplevelArticle import ToplevelArticle
from PageReader import PageReader
from SubPageReader import SubPageReader
from SubPageReaderBypass import SubPageReaderBypass
from PageReaderBypass import PageReaderBypass


class FirstPage:
    """
    A class which controls the tab(s) of the ttk.notebook from the App class.
    """

    header = ('Date', 'Title', 'Summary')
    values = []  # A temporary list containing lists for each news-link in the form of [title-string, url, date]
    news_to_open_in_browser = []  # Contains all the scraped news in the form of [title-string, url, date]
    news_total = []  # Contains all the dataclasses
    driver = None  # The Chromedriver

    def __init__(self, note, name, controller, url, to_bypass, debug, root=None):
        self.font = tkinter.font.Font(size=14)  # To measure the length of the letters
        self.note = note
        self.name = name
        self.controller = controller  # The controller is the App class
        self.root = root
        self.url = url
        self.to_bypass = to_bypass
        self.debug = debug
        self.frame = ttk.Frame(self.note)
        self.frame.pack(expand=True, fill='both', padx=1, pady=1)
        self.note.add(self.frame, text=name)
        # Tree
        # News in a Listbox
        self.f1 = ttk.Frame(self.frame)
        self.f1.pack(side='top', expand=True, fill='both', padx=2, pady=2)
        self.tree = ttk.Treeview(self.f1, columns=FirstPage.header, show='headings')
        self.setup_tree()
        if not self.to_bypass:  # To use BeautifulSoup
            self.fill_the_tree()
        else:  # self.to_bypass = True ==> Uses chromedriver
            self.fill_the_tree_bypass()
        # Menu emerging on the right click only
        self.right_click_menu = Menu(font='Arial 10', tearoff=0)
        self.right_click_menu.add_command(label='Show article', command=self.show_main_article)
        self.right_click_menu.add_command(label='Show article (bypass)', command=self.show_main_article_bypass)
        self.right_click_menu.add_command(label='Open article in browser', command=self.open_article_link)
        self.right_click_menu.add_command(label='Load more news',
                                          command=lambda: self.controller.insert_news_for_a_particular_tab(self.name))
        self.right_click_menu.add_command(label='Load more news (bypass)',
                                          command=lambda: self.controller.insert_news_for_a_particular_tab(self.name,
                                                                                                           bypass=True))
        self.tree.bind('<ButtonRelease-3>', self.post_menu)
        # Bind left double click to post the menu
        self.tree.bind("<Double-1>", self.show_main_article)

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
        :return:
        """
        current = self.tree.focus()
        current_article = self.tree.item(current)['values'][1]  # [0] is the Date
        print(f'current: {current_article}')
        count = 0
        for number, class_ in enumerate(FirstPage.news_total):
            if current_article == class_.title and count == 0:
                class_.main_content.strip()
                print(f'class_.main_content ({len(class_.main_content)})')
                if len(class_.main_content) != 0:
                    print(f'FirstPage>show_main_article>Content exists: Main content: '
                          f'\n{class_.main_content}')
                    count += 1
                    ToplevelArticle(class_, operation='main_article', root=self.root)
                else:
                    print(f'SubPageReader to be called')
                    added_new = SubPageReader(url=class_.url, header=headers(), debug=self.debug, firstpage=self)
                    data = added_new.data_to_return
                    print(f'length of SubPageReader: {len(data)}'
                          f'\nData from SubPageReader: {data}')
                    newsclass = NewsDataclass(url=data[0], date=data[2],
                                              title=data[1], summary=data[3],
                                              main_content=data[4])

                    self.tree.item(current, values=(self.tree.item(current)['values'][0], newsclass.title))
                    print(f'Main content: \n{newsclass.main_content}')
                    count += 1
                    ToplevelArticle(newsclass, operation='main_article', root=self.root)
                    # Remove the Dataclass not containing main_content and summary
                    # after appending the newsclass to the same list
                    FirstPage.news_total.insert(number, newsclass)  # Insert the newsclass to same index as class_
                    FirstPage.news_total.remove(class_)

    def show_main_article_bypass(self):
        current = self.tree.focus()
        current_article = self.tree.item(current)['values'][1]  # [0] is the Date
        print(f'current: {current_article}')
        count = 0
        for number, class_ in enumerate(FirstPage.news_total):
            if current_article == class_.title and count == 0:
                print(f'class_.main_content ({len(class_.main_content)})')
                if len(class_.main_content) >= 2:  # To avoid containing a single "\n" after not scraping with BS
                    print(f'FirstPage>show_main_article_bypass>Content exists: Main content: '
                          f'\n{class_.main_content}')
                    count += 1
                    ToplevelArticle(class_, operation='main_article', root=self.root)
                else:
                    print(f'FirstPage>show_main_article_bypass>SubPageReaderBypass to be called')
                    added_new = SubPageReaderBypass(url=class_.url, header=None, firstpage=self)
                    data = added_new.data_to_return
                    print(f'length of SubPageReaderBypass: {len(data)}'
                          f'\nData from SubPageReaderBypass: {data}')
                    newsclass = NewsDataclass(url=data[0], date=data[2],
                                              title=data[1], summary=data[3],
                                              main_content=data[4])
                    self.tree.item(current, values=(self.tree.item(current)['values'][0], newsclass.title))
                    print(f'Main content: \n{newsclass.main_content}')
                    count += 1
                    # Remove the Dataclass not containing main_content and summary
                    # after appending the newsclass to the same list
                    FirstPage.news_total.insert(number, newsclass)  # Insert the newsclass to same index as class_
                    FirstPage.news_total.remove(class_)
                    ToplevelArticle(newsclass, operation='main_article', root=self.root)

    def open_article_link(self):
        #  Solution: https://stackoverflow.com/questions/30614279/tkinter-treeview-get-selected-item-values
        current = self.tree.focus()
        current_article = self.tree.item(current)['values'][1]
        print(f'current: {current_article}')
        count = 0
        for class_ in FirstPage.news_total:
            if current_article == class_.title and count == 0:
                callback(class_.url)
                print(f'Firstpage>Called: {class_} {class_.url}')
                count += 1
        '''for _ in FirstPage.news_to_open_in_browser:
            if current_article in _:
                if count == 0:  # Open just one tab, even though the link exists in more than one tuple
                    callback(_[1])  # dictionary['link']
                    count += 1
                    print(f'Called:{_} {_[1]}')'''

    def renew_feed(self):
        FirstPage.values.clear()
        FirstPage.news_to_open_in_browser.clear()
        self.fill_the_tree()
        print(f"FirstPage>renew_feed(): Tree renewed")
        # print(FirstPage.news_total)

    def setup_tree(self):
        """Fills the tree"""
        # https://riptutorial.com/tkinter/example/31885/customize-a-treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 16))
        style.configure("Treeview", font=(None, 13))
        for head in FirstPage.header[:2]:  # [:1]
            if head == "Title":
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            elif head == 'Summary':
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            elif head == 'Date':
                self.tree.heading(column=head, text=f'{head}', command=lambda c=head: sortby(self.tree, c, 0))
                self.tree.column(column=head, stretch=True)
            else:
                self.tree.heading(column=head, text=f'{head}')
                self.tree.column(column=head, stretch=True)
        # Clear the list because otherwise it will contain duplicates
        FirstPage.values = []
        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree, orient="horizontal", command=self.tree.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        self.tree.pack(expand=True, fill='both')

    def fill_the_tree(self):
        """
        Clears the treeview and then calls PageReader and fills the tree using FirstPage.values (Title, Date).
        It sorts the news based on Date (firstly, converts the date to unix timestamps).
        """
        # Clear the treeview
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
            trace_error()
        try:
            if self.name.lower() == 'anaskopisi':  # For the category "anaskopisi"
                feed = PageReader(url=self.url, header=headers(), category=self.name.lower(), debug=self.to_bypass,
                                  firstpage=self)
            else:
                feed = PageReader(url=self.url, header=headers(), debug=self.to_bypass, firstpage=self)
            title_list = [self.font.measure(d[0]) for d in FirstPage.values]
            date_list = [self.font.measure(d[2]) for d in FirstPage.values]
            print(f"date_list: {date_list}")
            self.tree.column(column='Title', minwidth=100, width=max(title_list), stretch=True)
            if self.name.lower() in ('anaskopisi', 'tpp.radio'):
                # If stretch is True, it does not have the proper width
                self.tree.column(column='Date', minwidth=150, width=max(date_list) + 30, stretch=False)
            else:
                self.tree.column(column='Date', minwidth=150, width=max(date_list), stretch=True)
            print(f"max length of date: {max(date_list)}")
            print(max(title_list))
            for number, tuple_feed in enumerate(FirstPage.values):
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_feed[2].strip(), tuple_feed[0].strip()])  # , tuple_feed[1].strip()
            # Sort the rows of column with heading "Date"
            rows = [(self.tree.set(item, 'Date').lower(), item) for item in self.tree.get_children('')]
            rows.sort(key=date_to_unix, reverse=True)
            # Move the sorted dates
            for index, (values, item) in enumerate(rows):
                self.tree.move(item, '', index)
            if self.debug:
                print(f'Treeview was filled {FirstPage.values}')
        except Exception as err:
            print(f'Loading failed! Error: {err}')
            trace_error()

    def renew_feed_bypass(self):
        FirstPage.values.clear()
        FirstPage.news_to_open_in_browser.clear()
        self.fill_the_tree_bypass()
        print(f"FirstPage>renew_feed_bypass(): Tree renewed")

    def fill_the_tree_bypass(self):
        # Clear the treeview
        driver = None
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
        try:
            # TODO: pass to webdriver all the urls simultaneously and open the urls in separate tabs to scrape faster
            # https://www.geeksforgeeks.org/python-opening-multiple-tabs-using-selenium/
            if self.name == "Newsroom":
                options = uc.ChromeOptions()
                # options.add_argument("--headless")
                # options.add_argument("start-minimized")
                # options.add_argument("--lang=en-US")
                driver = uc.Chrome(use_subprocess=True, options=options)
                FirstPage.driver = driver
                driver.implicitly_wait(6)
                driver.set_window_position(-1000, 0)  # Set Chrome off-screen
            else:
                if is_driver_open(FirstPage.driver):
                    driver = FirstPage.driver
                else:
                    options = uc.ChromeOptions()
                    # options.add_argument("--headless")
                    # options.add_argument("start-minimized")
                    # options.add_argument("--lang=en-US")
                    driver = uc.Chrome(use_subprocess=True, options=options)
                    FirstPage.driver = driver
                    driver.implicitly_wait(6)
                    driver.set_window_position(-1000, 0)  # Set Chrome off-screen
            feed = PageReaderBypass(url=self.url, name=self.name, driver=driver, firstpage=self, debug=self.debug)
            title_list = [self.font.measure(d[0]) for d in FirstPage.values]
            date_list = [self.font.measure(d[2]) for d in FirstPage.values]
            self.tree.column(column='Title', minwidth=100, width=max(title_list), stretch=True)
            self.tree.column(column='Date', minwidth=150, width=max(date_list), stretch=True)
            print(max(title_list))
            for number, tuple_feed in enumerate(FirstPage.values):
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_feed[2].strip(), tuple_feed[0].strip()])  # , tuple_feed[1].strip()
            # print(f"App.page_dict {list(App.page_dict.keys())[-1]}")  # TODO: remove it
            # Sort the rows of column with heading "Date"
            rows = [(self.tree.set(item, 'Date').lower(), item) for item in self.tree.get_children('')]
            rows.sort(key=date_to_unix, reverse=True)
            # Move the sorted dates
            for index, (values, item) in enumerate(rows):
                self.tree.move(item, '', index)
            if self.name == 'Culture':  # After the last page ("Culture"), close the chromedriver
                # list(App.page_dict.keys())[-1]:
                driver.close()
                driver.quit()
                print(f"FirstPage>fill_the_tree_bypass> {driver} closed (self.name: {self.name})")
            if self.debug:
                print(f'Treeview was filled {FirstPage.values}')
        except ValueError:  # Raised from max() in self.tree.column (empty list)
            trace_error()
        except Exception as err:
            print(f'Loading failed! Error: {err}')
            trace_error()
            try:
                # After the last page ("Culture"), close the chromedriver
                driver.close()
                driver.quit()
                print(f"FirstPage>fill_the_tree_bypass> {driver} closed")
            except Exception:
                trace_error()

    def insert_news_from_page(self, url, category=None, bypass=False):
        """
        Inserts the news from the url to the notebook tab sorted based on the Date.
        :param bypass: To use webdriver or not.
        :param url: The url to scrape
        :param category: The category to be scraped.
        """
        FirstPage.values.clear()  # Clear the temporary list
        if not bypass:
            PageReader(url=url, header=headers(), category=category, debug=self.debug, firstpage=self)
        else:  # Use webdriver
            if is_driver_open(FirstPage.driver):
                PageReaderBypass(url=url, driver=FirstPage.driver, name=self.name, category=category, firstpage=self,
                                 debug=self.debug)
            else:
                print("FirstPage>insert_news_from_page>(Re)launching webdriver")
                options = uc.ChromeOptions()
                driver = uc.Chrome(use_subprocess=True, options=options)
                FirstPage.driver = driver
                driver.set_window_position(-1000, 0)  # Set Chrome off-screen
                driver.implicitly_wait(6)
                PageReaderBypass(url=url, driver=FirstPage.driver, name=self.name, category=category, firstpage=self,
                                 debug=self.debug)
        for number, tuple_feed in enumerate(FirstPage.values):
            self.tree.insert("", tk.END,
                             values=[tuple_feed[2].strip(), tuple_feed[0].strip()])  # , tuple_feed[1].strip()
        # Sort the rows of column with heading "Date"
        rows = [(self.tree.set(item, 'Date').lower(), item) for item in self.tree.get_children('')]
        rows.sort(key=date_to_unix, reverse=True)
        for index, (values, item) in enumerate(rows):
            self.tree.move(item, '', index)

    def __repr__(self):
        return self.name
