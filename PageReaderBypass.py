import time
from typing import Any
from bs4 import BeautifulSoup
from trace_error import trace_error
from classes.NewsDataclass import NewsDataclass


class PageReaderBypass:
    """
    Reads the html from the main category (Newsroom etc.) url and stores the title, link and date to a Dataclass in
    FirstPage.news_total and in Firstpage.values.

    :param url: The url to scrape
    :param name: The name of the category
    :param driver: The webdriver object
    """
    page_values = []

    def __init__(self, url, name, driver, debug, category=None, firstpage=None):
        self.news_dict = None
        self.temp_list = None
        self.r = None
        self.name = name
        self.url = url
        self.driver = driver  # driver passed from FirstPage
        self.debug = debug
        self.category = category
        self.soup = None
        self.firstpage = firstpage
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
        if self.debug:
            print(self.firstpage.values)

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
        self.firstpage.values.append(temp_list)
        self.firstpage.news_to_open_in_browser.append(temp_list)
        self.firstpage.news_total.append(NewsDataclass(url=link, title=title, date=date))

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
        self.firstpage.values.append(temp_list)
        self.firstpage.news_to_open_in_browser.append(temp_list)
        self.firstpage.news_total.append(NewsDataclass(url=link, title=title, date=date))
        # print(temp_list)
