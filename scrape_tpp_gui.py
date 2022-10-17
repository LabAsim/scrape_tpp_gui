# Version 15/10/2022
import argparse
import json
import os
import sys
import time
import tkinter as tk
import tkinter.font
from datetime import datetime
from tkinter import Menu, StringVar, ttk
import requests
from bs4 import BeautifulSoup
import tktooltip  # https://github.com/gnikit/tkinter-tooltip
import undetected_chromedriver as uc
import sv_ttk
from helper_functions import file_exists, center, callback, headers, str2bool, tkinter_theme_calling, \
    sortby
from misc import url_list, dir_path
from trace_error import trace_error
from classes.NewsDataclass import NewsDataclass
from classes.ToplevelAbout import ToplevelAbout
from classes.ToplevelSocial import ToplevelSocial
from classes.ToplevelDonate import ToplevelDonate
from classes.ToplevelAboutTpp import ToplevelAboutTpp
from classes.AskQuit import AskQuit
from classes.ToplevelArticle import ToplevelArticle


class SubPageReader:
    dict_subpage = {}
    data_to_return = []  # a list with 5 strings: Url, Title, Date, Subtitle summary, Main content

    def __init__(self, url, header):
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        SubPageReader.data_to_return.clear()
        self.connect_to_url()
        self.soup_the_request()
        self.news_dict = {}
        SubPageReader.data_to_return.append(self.url)
        self.scrape_the_title()
        PageReader.page_values = []
        self.scrape_the_date()
        self.scrape_the_summary()
        self.scrape_the_main_article_content()

    def connect_to_url(self):
        print(f"URL >>>>>>>>>>>>>>>>> {self.url}")
        try:
            if not debug:
                self.r = requests.get(self.url, headers=self.headers)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f'Error fetching the URL: {self.url}\n\tError: {err}')

    def soup_the_request(self):
        try:
            if not debug:
                self.soup = BeautifulSoup(self.r.text, "html.parser")
        except Exception as err:
            print(f'Could not parse the xml: {self.url}\n\tError: {err}')

    def scrape_the_title(self):
        """
        Scapes the title of the article
        :return:
        """
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

    def scrape_the_date(self):
        """
        Scrapes the Date of the article
        :return: None
        """
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

    def scrape_the_summary(self):
        """
        Scrapes the summary
        :return: None
        """
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

    def scrape_the_main_article_content(self):
        """
        Scrapes the content of the main article
        :return: None
        """
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

    @staticmethod
    def return_url_list(url, header):
        """
        Returns a list with 5 strings: Url, Title, Date, Subtitle summary, Main content
        :param url: The url to scrape
        :param header: A header
        :return: list: Data_to_return from SubPageReader containing all the data for the article
        """
        SubPageReader(url=url, header=header)
        return SubPageReader.data_to_return


class PageReader:
    page_values = []

    def __init__(self, url, header):
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        self.connect_to_url(url=self.url, header=self.headers)
        self.soup_the_request(request=self.r)
        self.temp_list = []
        self.news_dict = {}
        self.scrape_the_soup()

    def connect_to_url(self, url, header):
        """
        Connects to the url using header
        :param url: The url to connect to
        :param header: The headers (user-agent) for the request to url
        :return: None
        """
        try:
            if not debug:
                self.r = requests.get(url, headers=header)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f'Error fetching the URL: {url}'
                  f'\nError: {err}')

    def soup_the_request(self, request):
        """
        Makes a soup from the request using BeautifulSoup.
        :param request: The request object
        :return: None
        """
        try:
            if not debug:
                self.soup = BeautifulSoup(request.text, "html.parser")  # Otherwise, self.r.text
        except Exception as err:
            print(f'Could not parse the xml: {self.url}'
                  f'\nError: {err}')

    def scrape_the_soup(self):
        """
        Scrapes the soup
        :return: None
        """
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
        self.r = None
        self.options = None
        self.driver = None
        self.headers = header
        self.url = url
        self.soup = None
        SubPageReaderBypass.data_to_return.clear()
        self.open_url_with_Chromedriver()
        self.soup_the_page_source()
        self.news_dict = {}
        SubPageReaderBypass.data_to_return.append(self.url)
        self.scrape_the_title()
        PageReaderBypass.page_values = []
        self.scrape_the_date()
        self.scrape_the_summary()
        self.scrape_the_main_content()

    def open_url_with_Chromedriver(self):
        """
        Uses Chromedriver to open the url ang get the page source.
        :return: None
        """
        print(f"SubPageReaderBypass>URL >>>>> {self.url}")
        try:
            self.options = uc.ChromeOptions()
            # options.add_argument("--headless")
            # options.add_argument("start-minimized")
            self.options.add_argument("--lang=en-US")
            self.driver = uc.Chrome(use_subprocess=True, options=self.options)
            self.driver.set_window_position(-1000, 0)  # Set Chrome off-screen
            self.driver.get(self.url)
            time.sleep(3.5)
            self.r = self.driver.page_source
            self.driver.close()
            self.driver.quit()
        except Exception as err:
            print(f'Error fetching the URL: {self.url}\n\tError: {err}')

    def soup_the_page_source(self):
        """
        Soups the page source
        :return: None
        """
        try:
            self.soup = BeautifulSoup(self.r, "html.parser")
        except Exception as err:
            print(f'Could not parse the xml: {self.url}\n\tError: {err}')

    def scrape_the_title(self):
        """
        Scrapes the title of the article.
        :return:
        """
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

    def scrape_the_date(self):
        """
        Scrapes the Date
        :return: None
        """
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="article-date")):
                count = 0
                if number == 0:
                    print(a.text)
                    if "Αναρτήθηκε" in a.text:
                        for _a in FirstPage.values:
                            if count == 0:
                                date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                _a.append(date)
                                SubPageReaderBypass.data_to_return.append(date)
                                print(date)
                                count += 1
                    else:
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
            trace_error()
            raise err
        if len(SubPageReaderBypass.data_to_return) < 3:  # It should contain Url + Title + Date
            SubPageReaderBypass.data_to_return.append(" ")

    def scrape_the_summary(self):
        """
        Scrapes the summary
        :return: None
        """
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
            trace_error()
            raise err

    def scrape_the_main_content(self):
        """
        Scrapes the main content of the article.
        :return: None
        """
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

    @staticmethod
    def return_url_tuple(url, header):
        """Returns a list with 5 strings: Url, Title, Date, Subtitle summary, Main content"""
        SubPageReaderBypass(url=url, header=header)
        return SubPageReaderBypass.data_to_return


class PageReaderBypass:
    """
    Reads the html from the main category (Newsroom etc.) url and stores the title, link and date to a Dataclass in
    FirstPage.news_total
    """
    page_values = []

    def __init__(self, url, name, driver):
        """
        
        :param url:
        :param name:
        :param driver:
        """
        self.name = name
        self.url = url
        self.driver = driver  # driver passed from FirstPage
        self.soup = None
        self.use_chromedriver_and_get_page_source()
        self.soup_the_page_source()
        self.temp_list = []
        self.news_dict = {}
        self.scrape_the_data()

    def use_chromedriver_and_get_page_source(self):
        """
        Uses the driver passed as argument and gets the page source.
        :return: None
        """
        try:
            self.driver.get(self.url)
            if self.name == 'Newsroom':  # Only for the first time, wait for the Chrome to open.
                time.sleep(3.5)
            else:
                time.sleep(0.75)
            self.r = self.driver.page_source
        except Exception as err:
            print(f'Error fetching the URL: {self.url}'
                  f'\nError: {err}')

    def soup_the_page_source(self):
        """
        Soups the page source
        :return:
        """
        try:
            self.soup = BeautifulSoup(self.r, "html.parser")
        except Exception as err:
            print(f'Could not parse the html: {self.url}'
                  f'\nError: {err}')

    def scrape_the_data(self):
        """
        Scrapes the data from the soup of the target url
        :return:
        """
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
        # Bind left double click to post the menu
        self.tree.bind("<Double-1>", self.show_main_article)

    def post_menu(self, event):
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
                    ToplevelArticle(class_, operation='main_article', root=root)
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
                    ToplevelArticle(newsclass, operation='main_article', root=root)
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
                    ToplevelArticle(class_, operation='main_article', root=root)
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
                    ToplevelArticle(newsclass, operation='main_article', root=root)

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
                driver.set_window_position(-1000, 0)  # Set Chrome off screen
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
        self.tpp_menu.add_command(label='About ThePressProject', font='Arial 10',
                                  command=lambda: ToplevelAboutTpp(self, root=root))
        self.tpp_menu.add_command(label='Social media', font='Arial 10',
                                  command=lambda: ToplevelSocial(self, root=root, dir_path=dir_path))
        self.tpp_menu.add_command(label='Donate', font='Arial 10',
                                  command=lambda: ToplevelDonate(self, root=root, dir_path=dir_path))
        self.tpp_menu.add_command(label='Subscribe to Newsletter', font='Arial 10',
                                  command=lambda: callback('http://eepurl.com/dGNy2H'))
        # Create the Help menu on top of main menu
        self.help_menu = Menu(self.main_menu, tearoff=0)
        self.help_menu.add_command(label='About...', font='Arial 10', command=lambda: ToplevelAbout(self, root))
        # Add the rest menus as cascades menus on top of main menu
        self.main_menu.add_cascade(label='Edit', menu=self.edit_menu, underline=0)
        self.main_menu.add_cascade(label='TPP', menu=self.tpp_menu, underline=0)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu, underline=0)

    def notebook_pages(self, url, note, controller, name):
        """
        Stores all the pages of the notebook in App.page_dict
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
        with open(os.path.join(dir_path, "tpp.json"), "w+", encoding='utf-8') as file:
            json_data = {'theme': root.tk.call("ttk::style", "theme", "use")}
            json.dump(json_data, file, indent=4)
            print(f"Theme saved to tpp.json")

    @staticmethod
    def read_theme() -> str | None:
        """Reads the preferred theme"""
        if file_exists(name="tpp.json", dir_path=dir_path):
            with open(os.path.join(dir_path, "tpp.json"), "r+", encoding='utf-8') as file:
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


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(add_help=True)
    my_parser.add_argument('--debug', type=str2bool, action='store', const=True, nargs='?', required=False,
                           default=False, help='If True, it does not load the news.')
    args = my_parser.parse_args()
    debug = args.debug
    start = time.time()
    root = tk.Tk()  # First window
    style = ttk.Style(root)
    # A solution in order to measure the length of the titles
    # https://stackoverflow.com/questions/30950925/tkinter-getting-screen-text-unit-width-not-pixels
    font = tkinter.font.Font(size=14)
    tkinter_theme_calling(root)
    myapp = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: AskQuit(
        root))  # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    preferred_theme = myapp.read_theme()  # Reads the theme from the json (if exists)
    myapp.use_theme(preferred_theme)  # Sets the theme. If None, azure-dark is the default.
    center(root)  # Centers tkinter.Tk to screen's height & length
    end = time.time()
    print(f'Current Style: {root.tk.call("ttk::style", "theme", "use")}')
    print(f'Load in {end - start}')
    root.mainloop()
