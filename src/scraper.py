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
    def __init__(self, start_date: str, end_date: str, topic: str, resume: bool):

        self.page_index = 0
        self.year_index = start_date
        self.month_index = 1
        self.pdf_count = 0

        if not isdir("../data"):
            mkdir("../data")

        self.attach_logger()

        if resume:
            self.get_variables()
        else:
            self.start_date = start_date
            self.end_date = end_date
            self.topic = topic
            with open("vars.pkl", "wb") as f:
                pickle.dump(
                    [
                        self.topic,
                        self.start_date,
                        self.end_date,
                        self.page_index,
                        self.year_index,
                        self.month_index,
                        self.pdf_count,
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
                self.topic,
                self.start_date,
                self.end_date,
                self.page_index,
                self.year_index,
                self.month_index,
                self.pdf_count,
            ) = pickle.load(f)

    def update_variables(self):
        with open("vars.pkl", "wb") as f:
            pickle.dump(
                [
                    self.topic,
                    self.start_date,
                    self.end_date,
                    self.page_index,
                    self.year_index,
                    self.month_index,
                    self.pdf_count,
                ],
                f,
            )

    def download_file(self, download_url, pdf_title):
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
            file = open(f"../data/{pdf_title}.pdf", "wb")
            file.write(req.content)
            file.close()
            self.pdf_count += 1
        except Exception as ex:
            exception_str = type(ex).__name__
            exception_args = ex.args
            self.logger.exception(
                f"{exception_str} Args : {exception_args} Paper : {pdf_title}"
            )

    def start(self):
        while self.year_index < self.end_date:
            while self.month_index < 12:
                while self.pdf_count < 100:
                    self.topic = self.topic.replace(" ", "+")
                    base_link = requests.get(
                        f"https://onlinelibrary.wiley.com/action/doSearch?field1=AllField&text1={self.topic}&Ppub=&AfterMonth={self.month_index}&AfterYear={self.year_index}&BeforeMonth={self.month_index}&BeforeYear={self.year_index}&startPage={self.page_index}",
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
                    pdf_boxes = page_soup.findAll("div", {"class": "item__body"})

                    for pdf_box in pdf_boxes:
                        access_type = pdf_box.find(
                            "div", {"class": "doi-access", "tabindex": "0"}
                        )
                        if access_type:
                            if (
                                access_type.text == "Free Access"
                                or access_type.text == "Open Access"
                            ):
                                pdf_info = pdf_box.find(
                                    "a", {"class": "publication_title visitable"},
                                )
                                pdf_title = pdf_info.text

                                download_link = (
                                    "https://onlinelibrary.wiley.com/"
                                    + pdf_info["href"].replace("/doi", "doi/pdfdirect")
                                    + "?download=true"
                                )
                                self.download_file(download_link, pdf_title)
                                time.sleep(random.randint(1, 3))
                                self.logger.info(f"[Added PDF] {pdf_title}")

                    self.page_index += 1
                    self.update_variables()

                self.month_index += 1
                self.pdf_count = 0
                self.page_index = 0
                self.update_variables()
                self.logger.warn("[NEW MONTH] : " + base_link.url)

            self.year_index += 1
            self.pdf_count = 0
            self.page_index = 0
            self.month_index = 1
            self.update_variables()
            self.logger.warn("[NEW YEAR] : " + base_link.url)


topics = [
    "Algorithms",
    "Artificial intelligence",
    "Big data",
]
for topic in topics:
    my_scraper = scraper(2015, 2020, topic, False)
    my_scraper.start()
