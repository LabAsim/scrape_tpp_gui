import requests
from bs4 import BeautifulSoup
from trace_error import trace_error
from PageReader import PageReader


class SubPageReader:
    """
    Reads the url html and returns SubPageReader.data_to_return
    """
    dict_subpage = {}
    data_to_return = []  # A list with 7 strings: Url, Title, Date, Subtitle summary, Main content, Author, Author's url

    def __init__(self, url, header, firstpage, debug):
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        self.firstpage = firstpage
        self.debug = debug
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
        self.scrape_author()

    def connect_to_url(self):
        """Connects to self.url"""
        print(f"URL >>>>>>>>>>>>>>>>> {self.url}")
        try:
            if not self.debug:
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
            if not self.debug:
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
                        for _a in self.firstpage.values:
                            if count == 0:
                                date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                _a.append(date)
                                SubPageReader.data_to_return.append(date)
                                print(f'SubPageReader>scrape_the_date>date: {date}')
                                count += 1
                    else:
                        # SubPageReader.dict_subpage[self.url].append(a.text.strip().split(':')[0].strip())
                        for _a in self.firstpage.values:
                            if count == 0:
                                if "Αναρτήθηκε" in a.text:
                                    date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReader.data_to_return.append(date)
                                    print(f'SubPageReader>scrape_the_date>date: {date}')
                                    count += 1
                                else:
                                    date = a.text.split(':')[0].strip()
                                    _a.append(date)
                                    SubPageReader.data_to_return.append(date)
                                    print(f'SubPageReader>scrape_the_date>date: {date}')
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

    def scrape_author(self) -> None:

        """
        Scrapes the author and the author's url, if it exists (otherwise, it's an empty string).
        :return: None

        Example scraped:
            b:<a class="author url fn" href="https://thepressproject.gr/author/panos/" rel="author" title="Posts by Παναγιώτης Παπαδομανωλάκης">Παναγιώτης Παπαδομανωλάκης</a>
            b author:Παναγιώτης Παπαδομανωλάκης
            b[href]: https://thepressproject.gr/author/panos/
            b['rel']: ['author']
        """
        author = ''
        author_url = ''
        try:
            for number, a in enumerate(self.soup.find_all('div', class_="article-author")):
                count = 0
                if number == 0:
                    print(f'a class: {a}'
                          f'\na class text: {a.text.strip()}')
                    author_list = a.find_all('a', href=True, rel=True)
                    # For the pages that they do not contain a particular author (only 'The Press Project').
                    if len(author_list) == 0:
                        author = a.text.strip()
                        SubPageReader.data_to_return.append(author)
                        SubPageReader.data_to_return.append('None')
                    # There is an author.
                    else:
                        for b in author_list:
                            print(f'b:{b}'
                                  f'\nb author:{b.text.strip()}'
                                  f'\nb[href]: {b["href"].strip()}'
                                  f"\nb['rel']: {b['rel']}")
                            author = b.text
                            author_url = b["href"].strip()
                            SubPageReader.data_to_return.append(author)
                            SubPageReader.data_to_return.append(author_url)
        except Exception as err:
            print(err)
            trace_error()

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
