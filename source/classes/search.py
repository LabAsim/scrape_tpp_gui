import requests
from bs4 import BeautifulSoup
from scrape_tpp_gui.trace_error import trace_error
from scrape_tpp_gui.source.classes.NewsDataclass import NewsDataclass


class SearchTerm:
    """
    Scrapes the url, title, summary and date from the TPP site for the given keyword.
    """

    def __init__(self, term: str | float | int, page_number: int, debug: bool):
        self.soup = None
        self.response = None
        self.list = []
        self.base_url = "https://thepressproject.gr/page/"
        self.base_url_preterm = "/?s="
        self.page_number = str(page_number)
        self.suffix_url = "&submit=Search"
        "https://thepressproject.gr/page/2"
        self.term = str(term)
        self.final_url = self.base_url + self.page_number + self.base_url_preterm + self.term + self.suffix_url
        self.debug = debug
        # Call the functions
        self.connect_to_url()
        self.soup_the_request()
        self.scrape_data()

    def connect_to_url(self):
        """Connects to the url and gets the response"""
        try:
            self.response = requests.get(self.final_url)
        except requests.exceptions:
            trace_error()

    def soup_the_request(self):
        """Makes a soup from self.response.text"""
        self.soup = BeautifulSoup(self.response.text, "html.parser")

    def scrape_data(self):
        """
        Scrapes the title, link, date and the summary. The scraped info is appended as a dataclass to a list.
        :return: None
        """
        sample = self.soup.find_all("article")  # ("main", class_="site-main", id="main")
        for number, item in enumerate(sample):
            title = ""
            link = ""
            date = ""
            summary = ""
            for a in item.find("h2"):
                # print(f"{number}\t: {a}\n")
                link = a['href'].strip()
                title = a.text
            for p in item.find("p"):
                summary = p.text
                # print(p.text)
            for _date in item.find("div", class_="entry-meta"):
                date = _date.text.strip()
                # print(_date.text)
            # The date = "" will raise an IndexError in Newsdataclass, but we don't care about the unixtimestamp
            # in this occasion. Thus, debug is set to False. It remains True, for the rest of the program which uses
            # the Newsdataclass
            self.list.append(NewsDataclass(url=link, title=title, date=date, summary=summary, debug=False))


if __name__ == "__main__":
    to = SearchTerm('σα', 1, True)
    print(to.final_url)

    for dataclass_ in to.list:
        print(f"{dataclass_.date}:{dataclass_.title} {dataclass_.url} {dataclass_.summary}")
    print(to.list)
