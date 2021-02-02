import requests
import logging
from bs4 import BeautifulSoup
import urllib
from os.path import isdir, isfile
from os import mkdir
import pickle
import time
import random


class scraper:
    """
    This class is responsible for scraping all the dataset,
    the script was running for weeks to scrape the resulting
    dataset

    Target website          : http://export.arxiv.org/
    Delay between requests  : 1s
    Data dumped in          : ../data
    Logger                  : scraper.log
    Variables               : vars.pkl
    """

    def __init__(self, start_date: str, end_date: str, resume: bool):
        """
        start_date : which year to start with
        end_year   : which year to end with
        resume     : use variables saved in pkl and resume
                     from that point
        """

        # Initialising variables
        self.year_index = start_date
        self.month_index = 1
        self.pdf_count = 0

        # Creating a folder to hold all the data
        if not isdir("../data"):
            mkdir("../data")

        # Attaching logger
        self.attach_logger()

        if resume:
            self.get_variables()
        else:
            self.start_date = start_date
            self.end_date = end_date
            with open("vars.pkl", "wb") as f:

                # Saving variables
                pickle.dump(
                    [
                        self.start_date,
                        self.end_date,
                        self.year_index,
                        self.month_index,
                    ],
                    f,
                )

    def attach_logger(self):
        self.logger = logging.getLogger("scraper")
        logging.basicConfig(
            level=logging.INFO,
            filename="scraper.log",
            filemode="a+",
            format="%(asctime)-15s %(levelname)-8s %(message)s",
        )

    def get_variables(self):
        with open("vars.pkl", "rb") as f:
            (
                self.start_date,
                self.end_date,
                self.year_index,
                self.month_index,
            ) = pickle.load(f)

    def update_variables(self):
        with open("vars.pkl", "wb") as f:
            pickle.dump(
                [
                    self.start_date,
                    self.end_date,
                    self.year_index,
                    self.month_index,
                ],
                f,
            )

    def download_file(self, download_url, pdf_title, path):
        """
        download_url : automatic download link
        pdf_title    : name of the file that will be saved
        path         : exact path to use (year/month)
        """

        try:
            req = requests.get(
                download_url,
                headers={
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                },
            )
            file = open(f"{path}/{pdf_title}.pdf", "wb")
            file.write(req.content)
            file.close()
            self.pdf_count += 1
        except Exception as ex:
            exception_str = type(ex).__name__
            exception_args = ex.args
            self.logger.exception(
                f"[Arxiv] {exception_str} Args: {exception_args} Paper : {pdf_title}"
            )

    def start(self):
        """
        Start scraping using the specified parameters
        """

        print(self.year_index)
        print(type(self.year_index))
        print(self.end_date)
        print(type(self.end_date))

        while self.year_index < self.end_date:

            if not isdir(f"../data/{self.year_index}"):
                mkdir(f"../data/{self.year_index}")

            while self.month_index < 13:

                if not isdir(f"../data/{self.year_index}/{self.month_index}"):
                    mkdir(f"../data/{self.year_index}/{self.month_index}")

                year_str = str(self.year_index)[2] + str(self.year_index)[3]
                base_link = requests.get(
                    f"http://export.arxiv.org/list/cs/{year_str}{self.month_index:02}?skip=0&show=500",
                    headers={
                        "Accept-Encoding": "gzip, deflate, sdch",
                        "Accept-Language": "en-US,en;q=0.8",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Cache-Control": "max-age=0",
                        "Connection": "keep-alive",
                    },
                )
                self.logger.warn("[NEW PAGE] : " + base_link.url)
                page_soup = BeautifulSoup(base_link.text, "html.parser")
                pdf_titles = page_soup.findAll("dd")
                pdf_links = page_soup.findAll("dt")
                for title, link in zip(pdf_titles, pdf_links):

                    pdf_link = link.find("a", {"title": "Download PDF"})
                    pdf_title = (
                        title.text.split("Title: ")[1].split("Authors")[0]
                    )[:-3]
                    if pdf_link and not isfile(
                        f"../data/{self.year_index}/{self.month_index}/{pdf_title}.pdf"
                    ):
                        download_link = (
                            "http://export.arxiv.org/" + pdf_link["href"]
                        )
                        self.download_file(
                            download_link,
                            pdf_title,
                            path=f"../data/{self.year_index}/{self.month_index}",
                        )
                        time.sleep(random.randint(1, 3))
                        self.logger.info(
                            f"[Arxiv] [Added PDF] ({self.pdf_count}) {pdf_title}"
                        )
                    self.pdf_count += 1

                self.month_index += 1
                self.pdf_count = 0
                self.update_variables()
                self.logger.warn("[Arxiv] [NEW MONTH] : " + base_link.url)

            self.year_index += 1
            self.pdf_count = 0
            self.month_index = 1
            self.update_variables()
            self.logger.warn("[Arxiv] [NEW YEAR] : " + base_link.url)


my_scraper = scraper(2015, 2020, True)
my_scraper.start()
