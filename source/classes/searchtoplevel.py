import threading
import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from scrape_tpp_gui.source.classes.database.SubPageReaderDB import SubPageReader
from scrape_tpp_gui.source.classes.database.helper import ToplevelArticleDatabase
from scrape_tpp_gui.source.classes.generictoplevel import GenericToplevel
from scrape_tpp_gui.trace_error import trace_error
from NewsDataclass import NewsDataclass
from scrape_tpp_gui.helper_functions import sortby, center, headers


class ToplevelSearch(GenericToplevel):
    """Contains the scraped results from the search in the TPP site"""
    headers = ('Date', 'Title')  # , 'Summary')

    def __init__(self, controller, root: tk.Tk, results: list[NewsDataclass]):
        super().__init__(controller=controller, root=root)
        self.toplevel: tk.Toplevel = self.toplevel
        self.controller = controller
        self.root = root
        self.x = 1000
        self.y = 400
        self.fetched_news: list[NewsDataclass] = results
        self.toplevel.geometry(f"{self.x}x{self.y}")
        self.title = "Search"
        self.toplevel.title(self.title)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel_quit)
        self.font = font.Font(size=14)
        self.big_frame = None
        self.tree = None
        self.right_click_menu = None
        self.create_menu()
        self.create_ui()
        self.setup_treeview()
        self.fill_treeview()
        self.create_binds()
        center(self.toplevel, self.root)
        self.toplevel.lift()

    def create_menu(self):
        """Creates the menu bar"""
        # Menu bar
        self.bar_menu = tk.Menu(self.toplevel, font='Arial 10', tearoff=0, background='black', fg='white')
        self.toplevel.config(menu=self.bar_menu)
        # Main menu
        self.main_menu = tk.Menu(self.bar_menu, font='Arial 10', tearoff=0, background='black', fg='white')
        self.bar_menu.add_cascade(label='Menu', menu=self.main_menu, background='black')
        self.main_menu.add_command(label='Load more results', command=self.controller.search_site_load_more)
        # Right click menu only for the treeview
        self.right_click_menu = tk.Menu(font='Arial 10', tearoff=0)
        # Lambda here is needed because there is no event to be passed. If no lambda is used, an error will be raised
        self.right_click_menu.add_command(label='Show article', command=lambda: self.show_main_article(event=None))

    def create_ui(self):
        """Constructs the user interface"""
        self.big_frame = ttk.Frame(self.toplevel)
        self.big_frame.pack(expand=True, fill='both')
        self.topframe = ttk.Label(self.big_frame, text=" ")
        self.topframe.pack(side='top')
        self.tree = ttk.Treeview(self.big_frame, columns=ToplevelSearch.headers, show="headings")
        self.tree.pack(expand=True, fill='both')

    def setup_treeview(self):
        """Fills the treeview"""
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 16))
        style.configure("Treeview", font=(None, 13))
        for head in ToplevelSearch.headers:
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
        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree, orient="horizontal", command=self.tree.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

    def fill_treeview(self):
        """Fills the treeview with the fetched results from the search in the site"""
        # Clear the treeview
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('ToplevelSearch>fill_treeview()>Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
        if len(self.fetched_news) != 0:
            dates_length = []
            titles_length = []
            for number, _dataclass in enumerate(self.fetched_news):
                dates_length.append(self.font.measure(_dataclass.date))
                titles_length.append(self.font.measure(_dataclass.title))
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[_dataclass.date, _dataclass.title])
            # Fix the lengths
            self.tree.column(column='Title', minwidth=100, width=int(max(titles_length)), stretch=True)
            self.tree.column(column='Date', minwidth=150, width=int(max(dates_length)), stretch=False)
            # Adjust the x axis after the scraped data is loaded in the treeview
            self.x = int(max(titles_length)) + int(max(dates_length)) + 150
            self.toplevel.geometry(f"{self.x}x{self.y}")
            print(f"ToplevelSearch>fill_treeview()>news inserted")

    def create_binds(self):
        """Binds events to functions"""
        # Bind left double click to post the menu
        self.tree.bind("<Double-1>", self.show_main_article)
        # Bind the right click with self.post_menu()
        self.tree.bind('<ButtonRelease-3>', self.post_menu)

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
        for number, class_ in enumerate(self.fetched_news):
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
                    added_new = SubPageReader(url=class_.url, header=headers(), debug=False,
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
                    self.fetched_news.insert(number, newsclass)  # Insert the newsclass to same index as class_
                    self.fetched_news.remove(class_)

    def toplevel_quit(self):
        """It closes the window and set the controller variable back to None"""
        if self.controller:
            self.controller.searchtoplevel = None
        # Destroy the toplevel
        self.toplevel.destroy()


# Test
if __name__ == "__main__":
    root = tk.Tk()
    from scrape_tpp_gui.helper_functions import center, tkinter_theme_calling, parse_arguments
    from scrape_tpp_gui.trace_error import trace_error
    from search import SearchTerm
    center(root)
    tkinter_theme_calling(root)
    results = SearchTerm(term="κουλης", page_number=1, debug=False)
    ToplevelSearch(root=root, controller=None, results=results.list)
    root.mainloop()
