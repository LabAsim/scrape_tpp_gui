import json
import os
import sys
import time
import tkinter as tk
import tkinter.font
from datetime import datetime
from tkinter import Menu, StringVar, ttk
from typing import Any
import requests
from bs4 import BeautifulSoup
import tktooltip  # pip install tkinter-tooltip https://github.com/gnikit/tkinter-tooltip
import undetected_chromedriver as uc  # pip install undetected-chromedriver
import sv_ttk
import concurrent.futures
from helper_functions import file_exists, center, callback, headers, str2bool, tkinter_theme_calling, \
    sortby, date_to_unix, parse_arguments, is_driver_open
from misc import url_list, url_list_base_page, dir_path
from trace_error import trace_error
from classes.NewsDataclass import NewsDataclass
from classes.ToplevelAbout import ToplevelAbout
from classes.ToplevelSocial import ToplevelSocial
from classes.ToplevelDonate import ToplevelDonate
from classes.ToplevelAboutTpp import ToplevelAboutTpp
from classes.AskQuit import AskQuit
from classes.ToplevelArticle import ToplevelArticle
import concurrent.futures


class SubPageReader:
    """
    Reads the url html and returns SubPageReader.data_to_return
    """
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
        """Connects to self.url"""
        print(f"URL >>>>>>>>>>>>>>>>> {self.url}")
        try:
            if not debug:
                self.r = requests.get(self.url, headers=self.headers)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f'Error fetching the URL: {self.url}\n\tError: {err}')
            trace_error()

    def soup_the_request(self):
        """
        Makes a soup from self.r.text
        """
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
    """
    Connects to the list of url (or a single url) and scrapes the title, date. After that, it appends the data to
    Firstpage.values, FirstPage.news_to_open_in_browser and FirstPage.news_total.
    """

    def __init__(self, url, header, category=None):
        self.news_dict = None
        self.temp_list = None
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        self.category = category
        self.check_url_and_iterate(self.url, self.headers)

    def check_url_and_iterate(self, url: str | list, header):
        """
        Checks if the url is a list of urls or a url and then proceeds.
        :param url: The url to connect to
        :param header:
        :return:
        """
        if isinstance(url, list):
            for __url__ in url:
                self.connect_to_url(__url__, header)
                self.soup_the_request(request=self.r)
                self.temp_list = []
                self.news_dict = {}
                self.scrape_the_soup()
        else:  # It is not a list, but an url.
            self.connect_to_url(url, header)
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
            if self.category in ('Anaskopisi', 'anaskopisi'):
                print(f"PageReader>scrape_the_soup>{self.category}")
                for div in self.soup.find_all('div', class_='m-item grid-item col-md-6'):
                    try:
                        executor.submit(self.iterate_div_for_anaskopisi, div)
                    except Exception as err:
                        print(f'SubPageReader Error: {err}')
                        trace_error()
                        raise err
            else:
                for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                    try:
                        executor.submit(self.iterate_div, div)
                    except Exception as err:
                        print(f'SubPageReader Error: {err}')
                        trace_error()
                        raise err
        if debug:
            print(FirstPage.values)

    def iterate_div(self, div: Any):
        """
        Iterates div from the soup and scrapes the data

        :param div: The div object from the soup
        :return: None
        """
        temp_list = []
        title = ""
        link = ""
        date = ""
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

    def iterate_div_for_anaskopisi(self, div: Any):
        """
        Iterates div from the soup and scrapes the data for tpp.tv

        :param div: The div object from soup
        :return: None
        """
        temp_list = []  # Contains the
        title = ""
        link = ""
        date = ""
        text_summary = ""
        for a in div.find_all('h3'):
            # print(f'a: {a.text}')
            for b in a.find_all('a', href=True):
                # <a href="https://thepressproject.gr/anaskopisi-s08e32-katataxi-eleftherias-tou-typou/">
                # ΑΝΑΣΚΟΠΗΣΗ S08E32: ΚΑΤΑΤΑΞΗ ΕΛΕΥΘΕΡΙΑΣ ΤΟΥ ΤΥΠΟΥ</a>
                link = b['href'].strip()
                #print(f"b: {b.text} {len(b.text)} {link} {len(link)}")
                title = b.text  # .replace("ΑΝΑΣΚΟΠΗΣΗ ", "").strip()
                temp_list.append(title)
                temp_list.append(link)
        for date_div in div.find_all('div', class_='art-meta'):
            # We do not need to search the span class. The only text of the date_div is the span's text.
            date = date_div.text.strip()
            #print(f"date length: {len(date)}")
            temp_list.append(date)
        for text_div in div.find_all('div', class_='art-content'):
            text_summary = text_div.text
        FirstPage.values.append(temp_list)
        FirstPage.news_to_open_in_browser.append(temp_list)
        FirstPage.news_total.append(NewsDataclass(url=link, title=title, date=date))
        # print(temp_list)


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
            if FirstPage.driver is None:
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
            else:
                self.driver = FirstPage.driver
                self.driver.get(self.url)
                time.sleep(0.75)
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
    FirstPage.news_total and in Firstpage.values.

    :param url: The url to scrape
    :param name: The name of the category
    :param driver: The webdriver object
    """
    page_values = []

    def __init__(self, url, name, driver, category=None):
        self.news_dict = None
        self.temp_list = None
        self.r = None
        self.name = name
        self.url = url
        self.driver = driver  # driver passed from FirstPage
        self.category = category
        self.soup = None
        self.check_url_and_iterate(self.url)

    def check_url_and_iterate(self, url: str | list):
        """
        Checks if the url is a list of urls or a url and then proceeds.
        :param url: The (list of) url to connect to
        """
        if isinstance(url, list):
            for __url__ in url:
                self.use_chromedriver_and_get_page_source(__url__)
                self.soup_the_page_source()
                self.temp_list = []
                self.news_dict = {}
                self.scrape_the_data()
        else:  # It is not a list, but an url.
            self.use_chromedriver_and_get_page_source(url)
            self.soup_the_page_source()
            self.temp_list = []
            self.news_dict = {}
            self.scrape_the_data()

    def use_chromedriver_and_get_page_source(self, url):
        """
        Uses the driver passed as argument and gets the page source.
        :return: None
        """
        try:
            self.driver.get(url)
            if self.name == 'Newsroom':  # Only for the first time, wait for the Chrome to open.
                time.sleep(3.5)
            else:
                time.sleep(0.75)
            self.r = self.driver.page_source
        except Exception as err:
            print(f'Error fetching the URL: {self.url}'
                  f'\nError: {err}')
            trace_error()

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
            trace_error()

    def scrape_the_data(self):
        """
        Scrapes the data from the soup of the target url
        :return: None
        """
        # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
        '''with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # For some reason, chromedriver scrapes only with 1 worker. It also does not scrape without executor at all.
            for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                try:
                    executor.submit(self.iterate_div, div)
                    # self.iterate_div(div)
                except Exception as err:
                    print(f'SubPageReader Error: {err}')
                    trace_error()
            if debug:
                print(FirstPage.values)'''
        if self.category in ('Anaskopisi', 'anaskopisi'):
            for div in self.soup.find_all('div', class_='m-item grid-item col-md-6'):
                try:
                    self.iterate_div_for_anaskopisi(div)
                except Exception as err:
                    print(f'SubPageReader Error: {err}')
                    trace_error()
        else:
            for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                try:
                    self.iterate_div(div)
                except Exception as err:
                    print(f'SubPageReader Error: {err}')
                    trace_error()
        if debug:
            print(FirstPage.values)

    def iterate_div(self, div):
        """
        Scrapes for data
        :param div: The div to iterate
        """
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

    def iterate_div_for_anaskopisi(self, div: Any):
        """
        Iterates div from the soup and scrapes the data for tpp.tv

        :param div: The div object from soup
        :return: None
        """
        temp_list = []  # Contains the
        title = ""
        link = ""
        date = ""
        text_summary = ""
        for a in div.find_all('h3'):
            # print(f'a: {a.text}')
            for b in a.find_all('a', href=True):
                # <a href="https://thepressproject.gr/anaskopisi-s08e32-katataxi-eleftherias-tou-typou/">
                # ΑΝΑΣΚΟΠΗΣΗ S08E32: ΚΑΤΑΤΑΞΗ ΕΛΕΥΘΕΡΙΑΣ ΤΟΥ ΤΥΠΟΥ</a>
                link = b['href'].strip()
                #print(f"b: {b.text} {len(b.text)} {link} {len(link)}")
                title = b.text  # .replace("ΑΝΑΣΚΟΠΗΣΗ ", "").strip()
                temp_list.append(title)
                temp_list.append(link)
        for date_div in div.find_all('div', class_='art-meta'):
            # We do not need to search the span class. The only text of the date_div is the span's text.
            date = date_div.text.strip()
            print(f"date length: {len(date)}")
            temp_list.append(date)
        for text_div in div.find_all('div', class_='art-content'):
            text_summary = text_div.text
        FirstPage.values.append(temp_list)
        FirstPage.news_to_open_in_browser.append(temp_list)
        FirstPage.news_total.append(NewsDataclass(url=link, title=title, date=date))
        # print(temp_list)


class FirstPage:
    """
    A class which controls the tab(s) of the ttk.notebook from the App class.
    """
    header = ('Date', 'Title', 'Summary')
    values = []  # A temporary list containing lists for each news-link in the form of [title-string, url, date]
    news_to_open_in_browser = []  # Contains all the scraped news in the form of [title-string, url, date]
    news_total = []  # Contains all the dataclasses
    driver = None  # The Chromedriver

    def __init__(self, note, name, controller, url, to_bypass):
        self.note = note
        self.name = name
        self.controller = controller
        self.url = url
        self.to_bypass = to_bypass
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
                                          command=lambda: App.insert_news_for_a_particular_tab(self.name))
        self.right_click_menu.add_command(label='Load more news (bypass)',
                                          command=lambda: App.insert_news_for_a_particular_tab(self.name,
                                                                                               bypass=True))
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
                feed = PageReader(url=self.url, header=headers(), category=self.name.lower())
            else:
                feed = PageReader(url=self.url, header=headers())
            title_list = [font.measure(d[0]) for d in FirstPage.values]
            date_list = [font.measure(d[2]) for d in FirstPage.values]
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
            if debug:
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
            feed = PageReaderBypass(url=self.url, name=self.name, driver=driver)
            title_list = [font.measure(d[0]) for d in FirstPage.values]
            date_list = [font.measure(d[2]) for d in FirstPage.values]
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
            if debug:
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
            PageReader(url=url, header=headers(), category=category)
        else:  # Use webdriver
            if is_driver_open(FirstPage.driver):
                PageReaderBypass(url=url, driver=FirstPage.driver, name=self.name, category=category)
            else:
                print("FirstPage>insert_news_from_page>(Re)launching webdriver")
                options = uc.ChromeOptions()
                driver = uc.Chrome(use_subprocess=True, options=options)
                FirstPage.driver = driver
                driver.set_window_position(-1000, 0)  # Set Chrome off-screen
                driver.implicitly_wait(6)
                PageReaderBypass(url=url, driver=FirstPage.driver, name=self.name, category=category)
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


class App:
    """Main App"""
    x = 1600
    y = 500
    base_url = "https://thepressproject.gr/"
    page_dict = {}  # Holds the FirstPage objects
    # Holds the number of the page inserted in each notebook tab (FirstPage).
    treeview_tab_page_counter = {}  # Default: {'Newsroom: 1'} (as, it loads the news up to the first page)

    def __init__(self, root, to_bypass):
        self.help_menu = None
        self.tpp_menu = None
        self.theme_menu = None
        self.edit_menu = None
        self.load_more_news = None
        self.load_more_news_bypass = None
        self.context = None
        self.f_time = None
        self.time = None
        root.geometry(f'{App.x}x{App.y}')
        self.root = root
        self.root.title('The Press Project news feed')
        self.time_widgets()
        self.note = ttk.Notebook(self.root)
        self.note.pack(side='bottom', fill='both', expand=True)
        # For the 1st page of Newsroom: list(url_list.values())[0][0]
        self.notebook_pages(url=list(url_list.values())[0][0], note=self.note, controller=self, name='Newsroom')
        self.notebook_pages(url=list(url_list.values())[1][0], note=self.note, controller=self, name='Politics')
        self.notebook_pages(url=list(url_list.values())[2][0], note=self.note, controller=self, name='Economy')
        self.notebook_pages(url=list(url_list.values())[3][0], note=self.note, controller=self, name='International')
        self.notebook_pages(url=list(url_list.values())[4][0], note=self.note, controller=self, name='Reportage')
        self.notebook_pages(url=list(url_list.values())[5][0], note=self.note, controller=self, name='Analysis')
        self.notebook_pages(url=list(url_list.values())[6][0], note=self.note, controller=self, name='tpp.tv')
        self.notebook_pages(url=list(url_list.values())[7][0], note=self.note, controller=self, name='tpp.radio')
        self.notebook_pages(url=list(url_list.values())[8][0], note=self.note, controller=self, name='Anaskopisi')
        self.notebook_pages(url=list(url_list.values())[9][0], note=self.note, controller=self, name='Culture')
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

    def notebook_pages(self, url, note, controller, name):
        """
        Initiates and stores all the pages of the notebook (FirstPage class) in App.page_dict
        """
        App.page_dict[name] = FirstPage(note=note, name=name, controller=self, url=url, to_bypass=bypass)
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

    @staticmethod
    def insert_news_for_a_particular_tab(name, bypass=False):
        """
        Saves the number of pages loaded in the particular category to App.treeview_tab_page_counter[name]
        and loads the App.treeview_tab_page_counter[name] + 1.
        :param bypass: To use webdriver or not.
        :param name: The name of the category as a strings
        :return: None
        """
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
        print(f'App>call_renew_feed_bypass()')
        FirstPage.news_total.clear()  # Clear needs to be called here, just once. Not in Firstpage via renew_feed()
        for dictio in App.page_dict.values():
            dictio.renew_feed_bypass()
        self.f_time.destroy()
        self.time_widgets()
        print(f'Notebooks renewed')

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
        for (child, child_widget) in root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        root.withdraw()  # Hide the root
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
        root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

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
        except (tkinter.TclError, Exception) as err:
            print(err)

    def change_theme_forest(self):
        print(f'All styles: {root.tk.call("ttk::style", "theme", "names")}')
        # NOTE: The theme's real name is azure-<mode>
        print(f'Previous Style: {root.tk.call("ttk::style", "theme", "use")}')
        toplevel_temporary_list = []
        for (child, child_widget) in root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        root.withdraw()  # Hide the root
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
        root.deiconify()  # After changing the theme, re-draw first the root
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
        print(f'All styles: {root.tk.call("ttk::style", "theme", "names")}')
        print(f'Previous Style: {root.tk.call("ttk::style", "theme", "use")}')
        toplevel_temporary_list = []
        for (child, child_widget) in root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        root.withdraw()  # Hide the root
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
        root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()

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
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # print(dir_path)
        # print(os.path.dirname(os.path.realpath(__file__)))
        # https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
        # Determine if the application is a script file or a frozen exe
        if getattr(sys, 'frozen', False):  # TODO: review this
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            print(f'Script: {dir_path}')
        print(dir_path)
        with open(os.path.join(dir_path, "tpp.json"), "w+", encoding='utf-8') as file:
            json_data = {'theme': root.tk.call("ttk::style", "theme", "use")}
            json.dump(json_data, file, indent=4)
            print(f"Theme saved to {os.path.join(dir_path, 'tpp.json')}")

    @staticmethod
    def read_theme() -> str | None:
        """Reads the preferred theme"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if file_exists(name="tpp.json", dir_path=dir_path):
            with open(os.path.join(dir_path, "tpp.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                print(json_data)
                return json_data['theme']
        return None

    @staticmethod
    def use_theme(theme):
        """Sets the theme passed to the function"""
        toplevel_temporary_list = []
        for (child, child_widget) in root.children.items():  # Withdraw the toplevel windows
            if 'toplevel' in child:
                toplevel_temporary_list.append(child_widget)  # Save temporarily the toplevel objects
                child_widget.withdraw()
        root.withdraw()  # Hide the root
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
        root.deiconify()  # After changing the theme, re-draw first the root
        for toplevel in toplevel_temporary_list:  # Then re-draw the toplevel windows.
            # Thus, the toplevel will always be on top
            toplevel.deiconify()


if __name__ == "__main__":
    args = parse_arguments()
    debug, bypass = args.debug, args.bypass
    start = time.perf_counter()
    root = tk.Tk()  # First window
    style = ttk.Style(root)
    # A solution in order to measure the length of the titles
    # https://stackoverflow.com/questions/30950925/tkinter-getting-screen-text-unit-width-not-pixels
    font = tkinter.font.Font(size=14)
    tkinter_theme_calling(root)
    myapp = App(root=root, to_bypass=bypass)
    # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    root.protocol("WM_DELETE_WINDOW", lambda: AskQuit(root, FirstPage.driver))
    preferred_theme = myapp.read_theme()  # Reads the theme from the json (if exists)
    myapp.use_theme(preferred_theme)  # Sets the theme. If None, azure-dark is the default.
    center(root)  # Centers tkinter.Tk to screen's height & length
    end = time.perf_counter()
    print(f'Current Style: {root.tk.call("ttk::style", "theme", "use")}')
    print(f'Load in {end - start}')
    root.mainloop()
