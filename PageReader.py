import concurrent.futures
from typing import Any
import requests
from bs4 import BeautifulSoup
from classes.NewsDataclass import NewsDataclass
from trace_error import trace_error


class PageReader:
    """
    Connects to the list of url (or a single url) and scrapes the title, date. After that, it appends the data to
    Firstpage.values, FirstPage.news_to_open_in_browser and FirstPage.news_total.
    """

    def __init__(self, url, header, category=None, debug=False, firstpage=None):
        self.news_dict = None
        self.temp_list = None
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        self.category = category
        self.debug = debug
        self.firstpage = firstpage
        self.check_url_and_iterate(self.url, self.headers)

    def check_url_and_iterate(self, url: str | list, header):
        """
        Checks if the url is a list of urls or an url and then proceeds.
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
            if not self.debug:
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
            if not self.debug:
                self.soup = BeautifulSoup(request.text, "html.parser")  # Otherwise, self.r.text
        except Exception as err:
            print(f'Could not parse the html: {self.url}'
                  f'\nError: {err}')

    def scrape_the_soup(self):
        """
        Scrapes the soup
        :return: None
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
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
                print(f"PageReader>scrape_the_soup>{self.category}")
                for div in self.soup.find_all('div', class_='col-md-8 archive-item'):
                    try:
                        executor.submit(self.iterate_div, div)
                    except Exception as err:
                        print(f'SubPageReader Error: {err}')
                        trace_error()
                        raise err
        if self.debug:
            print(self.firstpage.values)

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
        self.firstpage.values.append(temp_list)
        self.firstpage.news_to_open_in_browser.append(temp_list)
        self.firstpage.news_total.append(NewsDataclass(url=link, title=title, date=date, category=self.category))

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
                # print(f"b: {b.text} {len(b.text)} {link} {len(link)}")
                title = b.text  # .replace("ΑΝΑΣΚΟΠΗΣΗ ", "").strip()
                temp_list.append(title)
                temp_list.append(link)
        for date_div in div.find_all('div', class_='art-meta'):
            # We do not need to search the span class. The only text of the date_div is the span's text.
            date = date_div.text.strip()
            # print(f"date length: {len(date)}")
            temp_list.append(date)
        for text_div in div.find_all('div', class_='art-content'):
            text_summary = text_div.text
        self.firstpage.values.append(temp_list)
        self.firstpage.news_to_open_in_browser.append(temp_list)
        self.firstpage.news_total.append(NewsDataclass(url=link, title=title, date=date, category=self.category))
        # print(temp_list)
