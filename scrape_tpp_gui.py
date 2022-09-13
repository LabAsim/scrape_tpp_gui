# Version 13/9/2022
import argparse
import dataclasses
import json
import os
import sys
import time
import tkinter as tk
import tkinter.font
import webbrowser
from datetime import datetime
from tkinter import messagebox, Menu, StringVar, ttk
from typing import Any
import PIL.Image
import requests
from bs4 import BeautifulSoup
import random
from PIL import Image, ImageTk
from ttkwidgets.font import FontSelectFrame
import tktooltip  # https://github.com/gnikit/tkinter-tooltip`
import undetected_chromedriver as uc
import pyperclip
from helper_functions import file_exists, center, callback, headers_list, headers, str2bool
import sv_ttk

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child)
            for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # Switch the heading, so it will be sorted  in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col,
                                                     int(not descending)))


def close_tkinter():
    if messagebox.askokcancel(title="Quit", message="Do you want to quit?"):
        root.destroy()
        print('close_tkinter(): Tkinter window is exiting')
        sys.exit()


class AskQuit(tk.Toplevel):
    x = 300
    y = 130

    def __init__(self, parent):
        super().__init__()
        self.root = root
        self.geometry(f'{AskQuit.x}x{AskQuit.y}')  # Here, self is tkinter.Toplevel
        self.parent = parent
        self.grab_set()
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        center(self, self.parent)

    def initUI(self):
        self.title("Quit")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valueLabel = ttk.Label(askquit_topframe, text="Do you want to quit?")
        valueLabel.pack(side='right', expand=True)
        image = Image.open("images/questionmark.png")
        image = image.resize(
            (int(self.winfo_width() * 25), int(self.winfo_height() * 25)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(askquit_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=10)
        image_label.image = image
        buttonsframe = ttk.Frame(self.big_frame)
        buttonsframe.pack(side='bottom', expand=True)
        okButton = ttk.Button(buttonsframe, text="Ok", command=lambda: self.toplevel_quit(self.parent))
        okButton.pack(side='left', expand=True, pady=10, padx=10)
        cancelButton = ttk.Button(buttonsframe, text="Cancel", command=self.destroy)
        cancelButton.pack(side='right', expand=True, pady=10, padx=10)

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget == root:
                print(f'AskQuit>toplevel_quit: Root is now exiting')
                sys.exit()
            else:
                widget.destroy()
                self.destroy()
                print(f'AskQuit>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'AskQuit>toplevel_quit: {self} is now destroyed')

    def setActive(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()


url_list = {"newsroom": ["https://thepressproject.gr/article_type/newsroom/",
                         "https://thepressproject.gr/article_type/newsroom/page/2/"],
            "politics": "https://thepressproject.gr/category/politics/",
            "economy": "https://thepressproject.gr/category/economy/",
            "international": "https://thepressproject.gr/category/international/",
            "report": "https://thepressproject.gr/article_type/report/",
            "analysis": "https://thepressproject.gr/article_type/analysis/"}
url_list_second_page = {"newsroom": "https://thepressproject.gr/article_type/newsroom/page/2/",
                        "politics": "https://thepressproject.gr/category/politics/page/2/",
                        "economy": "https://thepressproject.gr/category/economy/page/2/",
                        "international": "https://thepressproject.gr/category/international/page/2/",
                        "report": "https://thepressproject.gr/article_type/report/page/2/",
                        "analysis": "https://thepressproject.gr/article_type/analysis/page/2/"}


class SubPageReader:
    dict_subpage = {}
    data_to_return = []  # a list with 5 strings: Url, Title, Date, Subtitle summary, Main content

    def __init__(self, url, header):
        self.headers = header
        self.url = url
        self.soup = None
        SubPageReader.data_to_return.clear()
        print(f"URL >>>>>>>>>>>>>>>>> {url}")
        try:
            if not debug:
                self.r = requests.get(url, headers=self.headers)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f'Error fetching the URL: {url}\n\tError: {err}')
        try:
            if not debug:
                self.soup = BeautifulSoup(self.r.text, "html.parser")
        except Exception as err:
            print(f'Could not parse the xml: {self.url}\n\tError: {err}')
        self.news_dict = {}
        # print(self.soup)
        SubPageReader.data_to_return.append(self.url)
        try:
            if len(self.soup.find_all('h1', {'class': "entry-title"})) != 0:
                for a in self.soup.find_all('h1', {'class': "entry-title"}):
                    data = a.text.strip()
                    print(f'Title: {data}')
                    SubPageReader.data_to_return.append(data)
                    SubPageReader.dict_subpage[self.url] = [data]
            elif len(self.soup.find_all('h1')) != 0:
                for a in self.soup.find_all('h1'):
                    data = a.text.strip()
                    print(f'Title: {data}')
                    SubPageReader.data_to_return.append(data)
                    SubPageReader.dict_subpage[self.url] = [data]
            else:
                if len(SubPageReader.data_to_return) < 2:  # It should contain Url + Title
                    SubPageReader.data_to_return.append(" ")
        except Exception as err:
            print(f'SubReader Error in soup: {err}')
            raise err
        # print(self.soup.title)
        PageReader.page_values = []
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="article-date")):
                count = 0
                if number == 0:
                    print(a.text)
                    if "Αναρτήθηκε" in a.text:
                        # SubPageReader.dict_subpage[self.url].append(
                        #    a.text.strip().replace("\nΑναρτήθηκε", "").split(':')[0].strip())
                        for _a in FirstPage.values:
                            if count == 0:
                                date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                _a.append(date)
                                SubPageReader.data_to_return.append(date)
                                print(date)
                                count += 1
                    else:
                        # SubPageReader.dict_subpage[self.url].append(a.text.strip().split(':')[0].strip())
                        for _a in FirstPage.values:
                            if count == 0:
                                if "Αναρτήθηκε" in a.text:
                                    date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReader.data_to_return.append(date)
                                    print(date)
                                    count += 1
                                else:
                                    date = a.text.split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReader.data_to_return.append(date)
                                    print(date)
                                    count += 1
        except Exception as err:
            print(f'SubPageReader article-date Error: {err}')
            raise err
        if len(SubPageReader.data_to_return) < 3:  # It should contain Url + Title + Date
            SubPageReader.data_to_return.append(" ")
        try:
            if len(self.soup.find_all('div', class_="subtitle article-summary")) != 0:
                for number, a in enumerate(self.soup.find_all('div', class_="subtitle article-summary")):
                    if len(a.text) != 0:
                        data = a.text.strip()
                        SubPageReader.data_to_return.append(data)
            elif len(self.soup.find_all('div', class_="col-lg-7")) != 0:
                for number, a in enumerate(self.soup.find_all('div', class_="col-lg-7")):
                    if len(a.text) != 0:
                        data = a.text.strip()
                        print(f'div_col_lg_7: {data}')
                        if data not in SubPageReader.data_to_return:
                            # To avoid duplicates of title etc. (same class under div)
                            SubPageReader.data_to_return.append(data)
            else:
                if len(SubPageReader.data_to_return) < 4:  # It should contain Url + Title + Date + Summary
                    SubPageReader.data_to_return.append(" ")
        except Exception as err:
            print(f'SubPageReader subtitle article-summary Error: {err}')
            raise err
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="main-content article-content")):
                if len(a.text) != 0:
                    data = a.text.strip()
                    SubPageReader.data_to_return.append(data)
                else:
                    if len(SubPageReader.data_to_return) < 2:  # It should contain Url + Title
                        SubPageReader.data_to_return.append(" ")
        except Exception as err:
            print(f'SubPageReader main-content article-content Error: {err}')
            raise err
        if len(SubPageReader.data_to_return) < 5:  # It should contain Url + Title + Date + Summary + Main_content
            SubPageReader.data_to_return.append(" ")
        # print(len(SubPageReader.data_to_return))
        # SubPageReader.return_url_tuple()

    @staticmethod
    def return_url_tuple(url, header):
        """Returns a list with 5 strings: Url, Title, Date, Subtitle summary, Main content"""
        SubPageReader(url=url, header=header)
        return SubPageReader.data_to_return


class PageReader:
    page_values = []

    def __init__(self, url, header):
        self.headers = header
        self.url = url
        self.soup = None
        try:
            if not debug:
                self.r = requests.get(url, headers=self.headers)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f'Error fetching the URL: {url}'
                  f'\nError: {err}')
        try:
            if not debug:
                self.soup = BeautifulSoup(self.r.text, "html.parser")
        except Exception as err:
            print(f'Could not parse the xml: {self.url}'
                  f'\nError: {err}')
        self.temp_list = []
        self.news_dict = {}
        try:
            for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                temp_list = []
                title = ""
                link = ""
                date = ""
                # print(div.text)
                for a in div.find_all('h3'):
                    # print(a.text)
                    for b in a.find_all('a', href=True, rel=True):
                        # print(b.text)
                        # print(f"url: {b['href']}, Title: {b['rel']}")
                        link = b['href'].strip()
                        for num, word in enumerate(b['rel']):
                            if num != 0:  # Do not include a space in front of the first word
                                title += " "
                            title += word
                        title.strip()
                        temp_list.append(title)
                        temp_list.append(link)
                for number, a in enumerate(div.find('div', class_="archive-info info-text")):
                    if number == 0:
                        # Get the label as an author
                        temp_date = div.find('div', class_="archive-info info-text")
                        date_child = list(temp_date.children)[0].strip().replace("ί", "ι")
                        date = date_child
                        print(f'PageReader> date: {date_child}')
                        temp_list.append(date_child)
                FirstPage.values.append(temp_list)
                FirstPage.news_to_open_in_browser.append(temp_list)
                FirstPage.news_total.append(NewsDataclass(url=link, title=title, date=date))
        except Exception as err:
            print(f'SubPageReader Error: {err}')
        if debug:
            print(FirstPage.values)


class SubPageReaderBypass:
    """
    Reads the url html and returns SubPageReaderBypass.data_to_return
    """
    dict_subpage = {}
    data_to_return = []  # a list with 5 strings: Url, Title, Date, Subtitle summary, Main content

    def __init__(self, url, header):
        self.headers = header
        self.url = url
        self.soup = None
        SubPageReaderBypass.data_to_return.clear()
        print(f"SubPageReaderBypass>URL >>>>> {url}")
        try:
            options = uc.ChromeOptions()
            # options.add_argument("--headless")
            # options.add_argument("start-minimized")
            options.add_argument("--lang=en-US")
            driver = uc.Chrome(use_subprocess=True, options=options)
            driver.get(self.url)
            time.sleep(5)
            self.r = driver.page_source
            driver.close()
            driver.quit()
        except Exception as err:
            print(f'Error fetching the URL: {url}\n\tError: {err}')
        try:
            self.soup = BeautifulSoup(self.r, "html.parser")
        except Exception as err:
            print(f'Could not parse the xml: {self.url}\n\tError: {err}')
        self.news_dict = {}
        # print(self.soup)
        SubPageReaderBypass.data_to_return.append(self.url)
        try:
            if len(self.soup.find_all('h1', {'class': "entry-title"})) != 0:
                for a in self.soup.find_all('h1', {'class': "entry-title"}):
                    data = a.text.strip()
                    print(f'Title: {data}')
                    SubPageReaderBypass.data_to_return.append(data)
                    SubPageReaderBypass.dict_subpage[self.url] = [data]
            elif len(self.soup.find_all('h1')) != 0:
                for a in self.soup.find_all('h1'):
                    data = a.text.strip()
                    print(f'Title: {data}')
                    SubPageReaderBypass.data_to_return.append(data)
                    SubPageReaderBypass.dict_subpage[self.url] = [data]
            else:
                if len(SubPageReaderBypass.data_to_return) < 2:  # It should contain Url + Title
                    SubPageReaderBypass.data_to_return.append(" ")
        except Exception as err:
            print(f'SubReader Error in soup: {err}')
        # print(self.soup.title)
        PageReaderBypass.page_values = []
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="article-date")):
                count = 0
                if number == 0:
                    print(a.text)
                    if "Αναρτήθηκε" in a.text:
                        # SubPageReader.dict_subpage[self.url].append(
                        #    a.text.strip().replace("\nΑναρτήθηκε", "").split(':')[0].strip())
                        for _a in FirstPage.values:
                            if count == 0:
                                date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                _a.append(date)
                                SubPageReaderBypass.data_to_return.append(date)
                                print(date)
                                count += 1
                    else:
                        # SubPageReader.dict_subpage[self.url].append(a.text.strip().split(':')[0].strip())
                        for _a in FirstPage.values:
                            if count == 0:
                                if "Αναρτήθηκε" in a.text:
                                    date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReaderBypass.data_to_return.append(date)
                                    print(date)
                                    count += 1
                                else:
                                    date = a.text.split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReaderBypass.data_to_return.append(date)
                                    print(date)
                                    count += 1
        except Exception as err:
            print(f'SubPageReader article-date Error: {err}')
            raise err
        if len(SubPageReaderBypass.data_to_return) < 3:  # It should contain Url + Title + Date
            SubPageReaderBypass.data_to_return.append(" ")
        try:
            if len(self.soup.find_all('div', class_="subtitle article-summary")) != 0:
                for number, a in enumerate(self.soup.find_all('div', class_="subtitle article-summary")):
                    if len(a.text) != 0:
                        data = a.text.strip()
                        SubPageReaderBypass.data_to_return.append(data)
            elif len(self.soup.find_all('div', class_="col-lg-7")) != 0:
                for number, a in enumerate(self.soup.find_all('div', class_="col-lg-7")):
                    if len(a.text) != 0:
                        data = a.text.strip()
                        print(f'div_col_lg_7: {data}')
                        if data not in SubPageReaderBypass.data_to_return:
                            # To avoid duplicates of title etc. (same class under div)
                            SubPageReaderBypass.data_to_return.append(data)
            else:
                if len(SubPageReaderBypass.data_to_return) < 4:  # It should contain Url + Title + Date + Summary
                    SubPageReaderBypass.data_to_return.append(" ")
        except Exception as err:
            print(f'SubPageReader subtitle article-summary Error: {err}')
            raise err
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="main-content article-content")):
                if len(a.text) != 0:
                    data = a.text.strip()
                    SubPageReaderBypass.data_to_return.append(data)
                else:
                    if len(SubPageReaderBypass.data_to_return) < 2:  # It should contain Url + Title
                        SubPageReaderBypass.data_to_return.append(" ")
        except Exception as err:
            print(f'SubPageReader main-content article-content Error: {err}')
            raise err
        if len(SubPageReaderBypass.data_to_return) < 5:  # It should contain Url + Title + Date + Summary + Main_content
            SubPageReaderBypass.data_to_return.append(" ")
        # print(len(SubPageReader.data_to_return))
        # SubPageReader.return_url_tuple()

    @staticmethod
    def return_url_tuple(url, header):
        """Returns a list with 5 strings: Url, Title, Date, Subtitle summary, Main content"""
        # newsclass = NewsDataclass(url=SubPageReader.data_to_return[0], date=SubPageReader.data_to_return[2],
        #                          title=SubPageReader.data_to_return[1], summary=SubPageReader.data_to_return[3],
        #                          main_content=SubPageReader.data_to_return[4])
        # FirstPage.news_total.append(newsclass)
        SubPageReaderBypass(url=url, header=header)
        return SubPageReaderBypass.data_to_return


class PageReaderBypass:
    """
    Reads the html from the main category (Newsroom etc.) url and stores the title, link and date to a Dataclass in
    FirstPage.news_total
    """
    page_values = []

    def __init__(self, url, name, driver):
        self.name = name
        self.url = url
        self.driver = driver
        self.soup = None
        try:
            self.driver.get(self.url)
            if self.name == 'Newsroom':  # Only for the first time, wait for the Chrome to open.
                time.sleep(3.5)
            else:
                time.sleep(0.75)
            self.r = driver.page_source
        except Exception as err:
            print(f'Error fetching the URL: {url}'
                  f'\nError: {err}')
        try:
            self.soup = BeautifulSoup(self.r, "html.parser")
        except Exception as err:
            print(f'Could not parse the html: {self.url}'
                  f'\nError: {err}')
        self.temp_list = []
        self.news_dict = {}
        try:
            for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                temp_list = []
                title = ""
                link = ""
                date = ""
                # print(div.text)
                for a in div.find_all('h3'):
                    # print(a.text)
                    for b in a.find_all('a', href=True, rel=True):
                        # print(b.text)
                        # print(f"url: {b['href']}, Title: {b['rel']}")
                        link = b['href'].strip()
                        for num, word in enumerate(b['rel']):
                            if num != 0:  # Do not include a space in front of the first word
                                title += " "
                            title += word
                        title.strip()
                        temp_list.append(title)
                        temp_list.append(link)
                for number, a in enumerate(div.find('div', class_="archive-info info-text")):
                    if number == 0:
                        # Get the label as an author
                        temp_date = div.find('div', class_="archive-info info-text")
                        date_child = list(temp_date.children)[0].strip().replace("ί", "ι")
                        date = date_child
                        print(f'PageReaderBypass> date: {date_child}')
                        temp_list.append(date_child)
                FirstPage.values.append(temp_list)
                FirstPage.news_to_open_in_browser.append(temp_list)
                FirstPage.news_total.append(NewsDataclass(url=link, title=title, date=date))
        except Exception as err:
            print(f'PageReaderBypass Error: {err}')
        if debug:
            print(FirstPage.values)


@dataclasses.dataclass
class NewsDataclass:
    date: Any
    url: str = ''
    main_content: str = ''
    summary: str = ''
    title: str = ''

    def __str__(self):
        return f'Name:"{self.url}"'


class FirstPage:
    header = ('Date', 'Title', 'Summary')
    values = []  # A temporary list containing lists for each news-link in the form of [title-string, url, date]
    news_to_open_in_browser = []  # Contains all the scraped news in the form of [title-string, url, date]
    news_total = []  # Contains all the dataclasses
    driver = ""  # The Chromedriver

    def __init__(self, note, name, controller, url):
        self.note = note
        self.name = name
        self.controller = controller
        self.url = url
        self.frame = ttk.Frame(self.note)
        self.frame.pack(expand=True, fill='both', padx=1, pady=1)
        self.note.add(self.frame, text=name)
        # Tree
        # News in a Listbox
        self.f1 = ttk.Frame(self.frame)
        self.f1.pack(side='top', expand=True, fill='both', padx=2, pady=2)
        self.tree = ttk.Treeview(self.f1, columns=FirstPage.header, show='headings')
        self.setup_tree()
        self.fill_the_tree()
        # Menu emerging on the right click only
        self.right_click_menu = Menu(font='Arial 10',
                                     tearoff=0)
        self.right_click_menu.add_command(label='Show article', command=self.show_main_article)
        self.right_click_menu.add_command(label='Show article (bypass)', command=self.show_main_article_bypass)
        self.right_click_menu.add_command(label='Open article in browser', command=self.open_article_link)
        self.tree.bind('<ButtonRelease-3>', self.post_menu)

    def post_menu(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def show_main_article(self):
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
                    ToplevelArticle(class_, operation='main_article')
                else:
                    print(f'SubPageReader to be called')
                    added_new = SubPageReader(url=class_.url, header=headers())
                    data = added_new.data_to_return
                    print(f'length of SubPageReader: {len(data)}'
                          f'\nData from SubPageReader: {data}')
                    newsclass = NewsDataclass(url=data[0], date=data[2],
                                              title=data[1], summary=data[3],
                                              main_content=data[4])

                    self.tree.item(current, values=(self.tree.item(current)['values'][0], newsclass.title))
                    print(f'Main content: \n{newsclass.main_content}')
                    count += 1
                    ToplevelArticle(newsclass, operation='main_article')
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
                    ToplevelArticle(class_, operation='main_article')
                else:
                    print(f'FirstPage>show_main_article_bypass>SubPageReaderBypass to be called')
                    added_new = SubPageReaderBypass(url=class_.url, header=None)
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
                    ToplevelArticle(newsclass, operation='main_article')

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
        # Clear the treeview
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
        try:
            feed = PageReader(url=self.url, header=headers())
            title_list = [font.measure(d[0]) for d in FirstPage.values]
            date_list = [font.measure(d[2]) for d in FirstPage.values]
            self.tree.column(column='Title', minwidth=100, width=max(title_list), stretch=True)
            self.tree.column(column='Date', minwidth=150, width=max(date_list), stretch=True)
            print(max(title_list))
            for number, tuple_feed in enumerate(FirstPage.values):
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_feed[2].strip(), tuple_feed[0].strip()])  # , tuple_feed[1].strip()
            if debug:
                print(f'Treeview was filled {FirstPage.values}')
        except Exception as err:
            print(f'Loading failed! Error: {err}')

    def renew_feed_bypass(self):
        FirstPage.values.clear()
        FirstPage.news_to_open_in_browser.clear()
        self.fill_the_tree_bypass()
        print(f"FirstPage>renew_feed_bypass(): Tree renewed")

    def fill_the_tree_bypass(self):
        # Clear the treeview
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            print('Tree was erased')
        except Exception as err:
            print(f'Error in deleting the Tree: {err}')
        try:
            if self.name == "Newsroom":
                options = uc.ChromeOptions()
                # options.add_argument("--headless")
                # options.add_argument("start-minimized")
                # options.add_argument("--lang=en-US")
                driver = uc.Chrome(use_subprocess=True, options=options)
                FirstPage.driver = driver
                # driver.set_window_position(-1000, 0)  # Set Chrome off screen
            else:
                driver = FirstPage.driver
            feed = PageReaderBypass(url=self.url, name=self.name, driver=driver)
            title_list = [font.measure(d[0]) for d in FirstPage.values]
            date_list = [font.measure(d[2]) for d in FirstPage.values]
            self.tree.column(column='Title', minwidth=100, width=max(title_list), stretch=True)
            self.tree.column(column='Date', minwidth=150, width=max(date_list), stretch=True)
            print(max(title_list))
            for number, tuple_feed in enumerate(FirstPage.values):
                self.tree.insert("", tk.END, iid=str(number),
                                 values=[tuple_feed[2].strip(), tuple_feed[0].strip()])  # , tuple_feed[1].strip()
            print(f"App.page_dict {list(App.page_dict.keys())[-1]}")  # TODO: remove it
            if self.name == list(App.page_dict.keys())[-1]:  # After the last page ("Analysis"), close the chromedriver
                driver.close()
                driver.quit()
                print(f"FirstPage>fill_the_tree_bypass> {driver} closed")
            if debug:
                print(f'Treeview was filled {FirstPage.values}')
        except Exception as err:
            print(f'Loading failed! Error: {err}')

    def __repr__(self):
        return self.name


class App:
    """Main App"""
    x = 1600
    y = 500
    base_url = "https://thepressproject.gr/"
    page_dict = {}

    def __init__(self, root):
        self.f_time = None
        self.time = None
        root.geometry(f'{App.x}x{App.y}')
        self.root = root
        self.root.title('The Press Project news feed')
        self.widgets()
        self.note = ttk.Notebook(self.root)
        self.note.pack(side='bottom', fill='both', expand=True)
        self.notebook_pages(url=list(url_list.values())[0][0], note=self.note, controller=self, name='Newsroom')
        self.notebook_pages(url=list(url_list.values())[1], note=self.note, controller=self, name='Politics')
        self.notebook_pages(url=list(url_list.values())[2], note=self.note, controller=self, name='Economy')
        self.notebook_pages(url=list(url_list.values())[3], note=self.note, controller=self, name='International')
        self.notebook_pages(url=list(url_list.values())[4], note=self.note, controller=self, name='Reportage')
        self.notebook_pages(url=list(url_list.values())[5], note=self.note, controller=self, name='Analysis')
        self.top_label = ttk.Label(self.root, text='The Press Project', cursor='hand2', font='Arial 20')
        self.top_label.pack(side='top', pady=15)
        self.top_label.bind("<Button-1>", lambda e: callback(App.base_url))
        tktooltip.ToolTip(self.top_label, msg='Click to open ThePressProject site in the browser', delay=0.75)
        # Main menu
        self.main_menu = Menu(self.root, font='Arial 16',
                              tearoff=0)  # Tearoff has to be 0, in order the command to start being posted in position 0.
        self.root.config(menu=self.main_menu)
        # Emerging Menu for main tk Window
        self.context = Menu(self.main_menu, font='Arial 10',
                            tearoff=0)
        self.context.add_command(label='Renew titles', font='Arial 10', command=self.call_renew_feed)
        self.context.add_command(label='Renew titles (bypass)', font='Arial 10', command=self.call_renew_feed_bypass)
        self.context.add_separator()
        self.context.add_command(label='Exit', font='Arial 10', command=self.exit_the_program)
        # Add the cascade here. The submenu has to be built first and then be added to the main menu
        self.main_menu.add_cascade(label='Menu', menu=self.context)
        # Edit menu
        self.edit_menu = Menu(self.main_menu, tearoff=0)
        # Change theme menu
        self.theme_menu = Menu(self.edit_menu, tearoff=0)
        self.theme_menu.add_command(label='Azure', command=self.change_theme_azure)
        # self.theme_menu.add_command(label="Sun valley", command=self.change_theme_sun_valley)
        self.theme_menu.add_command(label='Adapta', command=self.change_theme_adapta)
        self.theme_menu.add_command(label='Aquativo',
                                    command=self.change_theme_aquativo)  # https://ttkthemes.readthedocs.io/en/latest/themes.html#radiance-ubuntu
        self.theme_menu.add_command(label='Radiance', command=self.change_theme_radiance)
        self.theme_menu.add_command(label='Plastik', command=self.change_theme_plastik)
        self.theme_menu.add_command(label='Yaru', command=self.change_theme_yaru)
        self.theme_menu.add_command(label='Arc', command=self.change_theme_arc)
        self.theme_menu.add_command(label='XP native', command=self.change_theme_xpnative)
        self.edit_menu.add_cascade(label='Change theme', font='Arial 10', menu=self.theme_menu, underline=0)
        self.edit_menu.add_command(label='Save theme', font='Arial 10', command=App.save_theme, underline=0)
        # TPP menu
        self.tpp_menu = Menu(self.main_menu, tearoff=0)
        self.tpp_menu.add_command(label='Social media', font='Arial 10', command=lambda: ToplevelSocial(self))
        self.tpp_menu.add_command(label='Donate', font='Arial 10', command=lambda: ToplevelDonate(self))
        self.tpp_menu.add_command(label='Subscribe to Newsletter', font='Arial 10',
                                  command=lambda: callback('http://eepurl.com/dGNy2H'))
        # Create the Help menu
        self.help_menu = Menu(self.main_menu, tearoff=0)
        self.help_menu.add_command(label='About...', font='Arial 10', command=lambda: ToplevelAbout(self))
        # add the Help menu to the menubar
        self.main_menu.add_cascade(label='Edit', menu=self.edit_menu, underline=0)
        self.main_menu.add_cascade(label='TPP', menu=self.tpp_menu, underline=0)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu, underline=0)

    def notebook_pages(self, url, note, controller, name):
        """
        Stores all the pages of the notebook in App.page_dict
        :param url:
        :param note:
        :param controller:
        :param name:
        :return:
        """
        App.page_dict[name] = FirstPage(note=note, name=name, controller=self, url=url)

    def call_renew_feed(self):
        """Recalls the site and renew the treeview for all tabs"""
        FirstPage.news_total.clear()  # Clear needs to be called here, just once. Not in Firstpage via renew_feed()
        for dictio in App.page_dict.values():
            dictio.renew_feed()
        self.f_time.destroy()
        self.widgets()
        print(f'App>call_renew_feed()')

    def call_renew_feed_bypass(self):
        """
        Renews the treeview for all tabs by using Chromedriver
        """
        print(f'App>call_renew_feed_bypass()')
        FirstPage.news_total.clear()  # Clear needs to be called here, just once. Not in Firstpage via renew_feed()
        for dictio in App.page_dict.values():
            dictio.renew_feed_bypass()
        self.f_time.destroy()
        self.widgets()
        print(f'Notebooks renewed')

    def widgets(self):
        # Time frame
        time_now = datetime.now()
        dt = str(time_now.strftime("%d-%m-%Y, %H:%M:%S"))
        dt = 'News loaded at: ' + dt
        var = StringVar()
        var.set(dt)
        self.f_time = ttk.Frame(root, height=40, width=160)
        self.f_time.pack(expand=False, side='top', fill="both", padx=5, pady=5)
        self.f_time.place(x=10, y=10)
        self.time = tk.Label(self.f_time, textvariable=var)
        self.time.pack(side='left')

    @staticmethod
    def exit_the_program():
        """Exits the program"""
        root.destroy()
        print(f'App>exit_the_program()')
        sys.exit()

    def change_theme_azure(self):
        print(f'All styles: {root.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {root.tk.call("ttk::style", "theme", "use")}')
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
                # root.tk.call("ttk::style", "theme", "use", "azure-light")
            else:
                try:
                    root.tk.call("set_theme", "dark")
                    # root.tk.call("ttk::style", "theme", "use", "azure-dark")
                except tkinter.TclError as err:
                    print(err)
        except tkinter.TclError as err:
            print(err)

    def change_theme_forest(self):
        print(f'All styles: {root.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {root.tk.call("ttk::style", "theme", "use")}')
        try:
            if root.tk.call("ttk::style", "theme", "use") == "forest-dark":
                root.tk.call("set_theme", "light")
                # root.tk.call("set_theme", "forest-light")
                # style.theme_use('forest-light')
                # root.tk.call("ttk::style", "theme", "use", "azure-light")
            else:
                try:
                    root.tk.call("set_theme", "dark")
                    # style.theme_use('forest-dark')
                    # root.tk.call("set_theme", "forest-dark")
                    # root.tk.call("ttk::style", "theme", "use", "forest-dark")
                except tkinter.TclError as err:
                    print(err)
        except tkinter.TclError as err:
            print(err)

    def change_theme_sun_valley(self):
        """
        https://stackoverflow.com/questions/30371673/can-a-ttk-style-option-be-deleted
        https://tcl.tk/man/tcl/TkCmd/ttk_style.htm
        https://wiki.tcl-lang.org/page/List+of+ttk+Themes
        CANT WORK WITH AZURE
        """
        print(f'All styles: {root.tk.call("ttk::style", "theme", "names")}')
        print(f'Previous Style: {root.tk.call("ttk::style", "theme", "use")}')
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
            if root.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
                root.tk.call("ttk::style", "theme", "use", 'sun-valley-light')
                root.tk.call("set_theme", "light")

            # elif root.tk.call("ttk::style", "theme", "use") == "sun-valley-light":
            else:
                # Set dark theme
                root.tk.call("ttk::style", "theme", "use", 'sun-valley-dark')
                root.tk.call("set_theme", "dark")
        except tkinter.TclError as err:
            print(err)

    def change_theme_xpnative(self):
        try:
            # Switch first to light theme and then to XPnative in order for the black to be eliminated.
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'vista')
        except tkinter.TclError as err:
            print(err)

    def change_theme_radiance(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'radiance')
        except tkinter.TclError as err:
            print(err)

    def change_theme_aquativo(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'aquativo')
        except tkinter.TclError as err:
            print(err)

    def change_theme_plastik(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'plastik')
        except tkinter.TclError as err:
            print(err)

    def change_theme_adapta(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'adapta')
        except tkinter.TclError as err:
            print(err)

    def change_theme_yaru(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'yaru')
        except tkinter.TclError as err:
            print(err)

    def change_theme_arc(self):
        try:
            if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
                root.tk.call("set_theme", "light")
            root.tk.call("ttk::style", "theme", "use", 'arc')
        except tkinter.TclError as err:
            print(err)

    @staticmethod
    def save_theme():
        """Saves the preferred theme"""
        with open("tpp.json", "w+", encoding='utf-8') as file:
            json_data = {'theme': root.tk.call("ttk::style", "theme", "use")}
            json.dump(json_data, file, indent=4)
            print(f"Theme saved to tpp.json")

    @staticmethod
    def read_theme():
        """Reads the preferred theme"""
        if file_exists(name="tpp.json", dir_path=dir_path):
            with open("tpp.json", "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                return json_data['theme']
        return None

    @staticmethod
    def use_theme(theme):
        """Sets the theme passed to the function"""
        if theme == 'azure-dark' or None:
            root.tk.call("set_theme", "dark")
        elif theme == 'azure-light':
            root.tk.call("set_theme", "light")
        elif theme == 'radiance':
            myapp.change_theme_radiance()
        elif theme == 'aquativo':
            myapp.change_theme_aquativo()
        elif theme == "plastik":
            myapp.change_theme_plastik()
        elif theme == "adapta":
            myapp.change_theme_adapta()
        elif theme == "yaru":
            myapp.change_theme_yaru()
        elif theme == "arc":
            myapp.change_theme_arc()
        elif theme == "vista":
            myapp.change_theme_xpnative()


class ToplevelArticle:
    x = 1200
    y = 500

    def __init__(self, newsclass, operation):
        self.newsclass = newsclass
        self.title = newsclass.title
        self.date = newsclass.date
        self.url = newsclass.url
        self.summary = tk.StringVar(value=newsclass.summary)
        self.operation = operation
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
        # Disable text widget, so as reader can not delete its content. It needs to be done AFTER text.insert
        # https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
        self.text.config(state='disabled')
        self.text1.config(state='disabled')
        # Allow user to select the text (i.e. if the user wants to copy it)
        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.text1.bind("<1>", lambda event: self.text1.focus_set())
        # Create Right-click menu for copying
        self.menu = Menu(self.note, tearoff=0)
        self.menu.add_command(label='Copy', font='Arial 10', command=self.copy_text_to_clipboard)
        self.text.bind('<ButtonRelease-3>', self.post_menu)  # Menu is posted in self.text
        self.text1.bind('<ButtonRelease-3>', self.post_menu)
        center(self.toplevelarticle, root)

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
            self.text1.config(state='normal')
            self.text.configure(font=selected_font)
            self.text1.configure(font=selected_font)
            self.text.config(state='disabled')
            self.text1.config(state='disabled')

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


class ToplevelDonate:
    x = 1000
    y = 500
    donation_urls = ['https://community.thepressproject.gr/product/dorea/',
                     'https://community.thepressproject.gr/product/minaia-syndromi/',
                     'https://community.thepressproject.gr/product/etisia-syndromi/']

    def __init__(self, controller):
        self.controller = controller
        self.dir_path = os.path.join(dir_path, 'images')
        self.topleveldonate = tk.Toplevel()
        self.topleveldonate.title("Donate to TPP")
        # First image
        self.img_dorea = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, 'dorea.jpg')))
        self.label_dorea = ttk.Label(self.topleveldonate, image=self.img_dorea, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_dorea.image = self.img_dorea
        self.label_dorea.pack(expand=True, fill="both", side='left')
        self.label_dorea.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[0]))
        # Second image
        self.img_monthly = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, "mhniaia.jpg")))
        self.label_monthly = ttk.Label(self.topleveldonate, image=self.img_monthly, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_monthly.image = self.img_monthly
        self.label_monthly.pack(expand=True, fill="both", side='left')
        self.label_monthly.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[1]))
        # Third image
        self.img_annually = ImageTk.PhotoImage(Image.open(os.path.join(self.dir_path, "ethsia.jpg")))
        self.label_annually = ttk.Label(self.topleveldonate, image=self.img_annually, cursor='hand2')
        # Image needs to re declared. See notes from the first answer.
        # https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window
        self.label_annually.image = self.img_annually
        self.label_annually.pack(expand=True, fill="both", side='left')
        self.label_annually.bind('<Button-1>', lambda e: callback(ToplevelDonate.donation_urls[2]))
        center(self.topleveldonate, root)


class ToplevelSocial:
    """Contains the links to TPP's social media"""
    x = 1000
    y = 500
    social_media_urls = ['https://www.facebook.com/ThePressProject',
                         'https://www.facebook.com/anaskopisi',
                         'https://twitter.com/intent/follow?screen_name=ThePressProject&tw_p=followbutton',
                         'https://libretooth.gr/@thepressproject']

    def __init__(self, controller):
        # https://stackoverflow.com/questions/69293836/tkinter-how-do-i-resize-an-image-to-fill-its-labelframe-and-have-that-labelfram
        self.controller = controller
        self.dir_path = os.path.join(dir_path, 'images')
        self.toplevelsocial = tk.Toplevel()
        self.toplevelsocial.title('TPP social media')
        self.bigframe = ttk.Frame(self.toplevelsocial)
        self.bigframe.pack(expand=True, fill='both')
        self.topframe = ttk.Frame(self.bigframe)
        self.topframe.pack(expand=True, fill='both', side='top', padx=80, pady=10)
        self.middleframe = ttk.Frame(self.bigframe)
        self.middleframe.pack(expand=True, fill='both', side='top', padx=80, pady=10)
        self.bottomframe = ttk.Frame(self.bigframe)
        self.bottomframe.pack(expand=True, fill='both', side='bottom', padx=80, pady=10)
        # First image
        self.img_facebook = Image.open(os.path.join(self.dir_path, 'facebook.png'))
        self.img_facebook = self.img_facebook.resize((900, 175), Image.ANTIALIAS)
        # (int(self.toplevelsocial.winfo_width() * 200), int(self.toplevelsocial.winfo_height() * 200)),

        self.img_facebook_tk = ImageTk.PhotoImage(self.img_facebook)
        self.label_facebook = ttk.Label(self.topframe, image=self.img_facebook_tk, cursor='hand2')
        self.label_facebook.image = self.img_facebook_tk
        self.label_facebook.pack(expand=True, fill='both')
        self.label_facebook.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[0]))
        # 2nd image
        self.img_twitter = Image.open(os.path.join(self.dir_path, 'twitter.png'))
        self.img_twitter = self.img_twitter.resize((900, 175), Image.ANTIALIAS)
        # (int(self.toplevelsocial.winfo_width()/3), int(self.toplevelsocial.winfo_height()/3)),
        # Image.ANTIALIAS)
        self.img_twitter_tk = ImageTk.PhotoImage(self.img_twitter)
        self.label_twitter = ttk.Label(self.middleframe, image=self.img_twitter_tk, cursor='hand2')
        self.label_twitter.image = self.img_twitter_tk
        self.label_twitter.pack(expand=True, fill='both')
        self.label_twitter.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[2]))
        # 3rd image
        self.img_mastodon = Image.open(os.path.join(self.dir_path, 'mastodon.png'))
        self.img_mastodon = self.img_mastodon.resize((900, 175), Image.ANTIALIAS)
        self.img_mastodon_tk = ImageTk.PhotoImage(self.img_mastodon)
        self.label_mastodon = ttk.Label(self.bottomframe, image=self.img_mastodon_tk, cursor='hand2')
        self.label_mastodon.image = self.img_mastodon_tk
        self.label_mastodon.pack(expand=True, fill='both')
        self.label_mastodon.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[3]))
        center(window=self.toplevelsocial, parent_window=root)
        # self.toplevelsocial.bind('<Configure>', func=self.resize_images)
        print((int(self.bigframe.winfo_width()), int(self.bigframe.winfo_height())))
        print((int(self.toplevelsocial.winfo_width()), int(self.toplevelsocial.winfo_height())))

    def resize_images(self, event):
        # self.img_facebook = Image.open(os.path.join(self.dir_path, 'Facebook_wikimedia.png'))
        img_facebook = self.img_facebook.resize(
            (int(self.toplevelsocial.winfo_width() / 3), int(self.toplevelsocial.winfo_height() / 3)))
        self.img_facebook_tk = ImageTk.PhotoImage(img_facebook)
        self.label_facebook.config(image=self.img_facebook_tk)
        # self.img_twitter = Image.open(os.path.join(self.dir_path, 'twitter_tpp.png'))
        img_twitter = self.img_twitter.resize(
            (int(self.bigframe.winfo_width() / 3), int(self.bigframe.winfo_height() / 3)),
            Image.ANTIALIAS)
        self.img_twitter_tk = ImageTk.PhotoImage(img_twitter)
        self.label_twitter.config(image=self.img_twitter_tk)
        self.label_twitter.image = img_twitter


class ToplevelAbout:
    x = 580
    y = 280

    def __init__(self, controller):
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


dir_path = os.path.dirname(os.path.realpath(__file__))

themes_paths = {"azure": os.path.join(dir_path, 'source/azure/azure.tcl'),
                "plastik": os.path.join(dir_path, 'source/plastik/plastik.tcl'),
                "radiance": os.path.join(dir_path, 'source/radiance/radiance.tcl'),
                "aquativo": os.path.join(dir_path, 'source/aquativo/aquativo.tcl'),
                "adapta": os.path.join(dir_path, 'source/adapta/adapta.tcl'),
                "yaru": os.path.join(dir_path, 'source/yaru/yaru.tcl'),
                "arc": os.path.join(dir_path, 'source/arc/arc.tcl')}

if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(add_help=True)
    my_parser.add_argument('--debug', type=str2bool, action='store', const=True, nargs='?', required=False,
                           default=True, help='If True, it does not load the news.')
    args = my_parser.parse_args()
    debug = args.debug
    start = time.time()
    root = tk.Tk()  # First window
    style = ttk.Style(root)
    # A solution in order to measure the length of the titles
    # https://stackoverflow.com/questions/30950925/tkinter-getting-screen-text-unit-width-not-pixels
    font = tkinter.font.Font(size=14)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # https://rdbende.github.io/tkinter-docs/tutorials/how-to-use-themes.html
    root.tk.call('source', themes_paths["azure"])  # https://github.com/rdbende/Azure-ttk-theme
    root.tk.call('source', themes_paths["plastik"])
    root.tk.call('source', themes_paths['radiance'])
    root.tk.call('source', themes_paths['aquativo'])
    root.tk.call('source', themes_paths['adapta'])
    root.tk.call('source', themes_paths['yaru'])
    root.tk.call('source', themes_paths['arc'])
    root.tk.call("set_theme", "dark")
    myapp = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: AskQuit(
        root))  # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    preferred_theme = myapp.read_theme()  # Reads the theme from the json (if exists)
    myapp.use_theme(preferred_theme)  # Sets the theme. If None, azure-dark is the default.
    center(root)
    end = time.time()
    print(f'Current Style: {root.tk.call("ttk::style", "theme", "use")}')
    print(f'Load in {end - start}')
    root.mainloop()
