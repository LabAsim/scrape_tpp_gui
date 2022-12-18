import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc  # pip install undetected-chromedriver
from trace_error import trace_error
from PageReaderBypass import PageReaderBypass


class SubPageReaderBypass:
    """
    Reads the url html and returns SubPageReaderBypass.data_to_return
    """
    dict_subpage = {}
    data_to_return = []  # A list with 7 strings: Url, Title, Date, Subtitle summary, Main content, Author, Author's url

    def __init__(self, url, header, firstpage):
        self.r = None
        self.options = None
        self.driver = None
        self.headers = header
        self.url = url
        self.soup = None
        self.firstpage = firstpage
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
        self.scrape_author()

    def open_url_with_Chromedriver(self):
        """
        Uses Chromedriver to open the url ang get the page source.
        :return: None
        """
        print(f"SubPageReaderBypass>URL >>>>> {self.url}")
        try:
            if self.firstpage.driver is None:
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
                self.driver = self.firstpage.driver
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
                        for _a in self.firstpage.values:
                            if count == 0:
                                date = a.text.replace("\nΑναρτήθηκε", "").split(':')[0].strip()
                                _a.append(date)
                                SubPageReaderBypass.data_to_return.append(date)
                                print(date)
                                count += 1
                    else:
                        for _a in self.firstpage.values:
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
                        SubPageReaderBypass.data_to_return.append(author)
                        SubPageReaderBypass.data_to_return.append('None')
                    # There is an author.
                    else:
                        for b in author_list:
                            print(f'b:{b}'
                                  f'\nb author:{b.text.strip()}'
                                  f'\nb[href]: {b["href"].strip()}'
                                  f"\nb['rel']: {b['rel']}")
                            author = b.text
                            author_url = b["href"].strip()
                            SubPageReaderBypass.data_to_return.append(author)
                            SubPageReaderBypass.data_to_return.append(author_url)
        except Exception as err:
            print(err)
            trace_error()

    @staticmethod
    def return_url_tuple(url, header):
        """Returns a list with 5 strings: Url, Title, Date, Subtitle summary, Main content"""
        SubPageReaderBypass(url=url, header=header)
        return SubPageReaderBypass.data_to_return

    #TODO: add author / author url