from date_extractor import extract_date
from os import path, listdir, path, mkdir
import time
import logging
import shutil
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError

# Using logger to check which pdf files could not be parsed
mylogger = logging.getLogger("date_formatter")
logging.basicConfig(
    level=logging.CRITICAL,
    filename="date_formatter.log",
    filemode="a+",
    format="%(asctime)-15s %(levelname)-8s %(message)s",
)

logger = logging.getLogger("pdfminer")
logger.propagate = False

# Basically we will extract the creation date of every pdf from their metadata
# and sort them accordingly
for pdf_file in listdir("../data"):
    if path.isfile(f"../data/{pdf_file}"):
        try:
            pdf_toread = PdfFileReader(open(f"../data/{pdf_file}", "rb"))
            if pdf_toread.isEncrypted:
                pdf_toread.decrypt("")
            pdf_info = pdf_toread.getDocumentInfo()
            pdf_date = pdf_info.get("/CreationDate").split(":")[1].split("+")[0]
            pdf_year = int(pdf_date[0:4])
            pdf_months = int(pdf_date[5:6])
            if (
                pdf_year > 2014 and pdf_months != None
            ):  # for now we are sticking with papers published after 2014
                if not path.isdir(f"../data/{pdf_year}"):
                    mkdir(f"../data/{pdf_year}")
                    mkdir(f"../data/{pdf_year}/{pdf_months}")
                    shutil.move(
                        f"../data/{pdf_file}",
                        f"../data/{pdf_year}/{pdf_months}/{pdf_file}",
                    )

                else:
                    if not path.isdir(f"../data/{pdf_year}/{pdf_months}"):
                        mkdir(f"../data/{pdf_year}/{pdf_months}")
                        shutil.move(
                            f"../data/{pdf_file}",
                            f"../data/{pdf_year}/{pdf_months}/{pdf_file}",
                        )
                    else:
                        shutil.move(
                            f"../data/{pdf_file}",
                            f"../data/{pdf_year}/{pdf_months}/{pdf_file}",
                        )
                        time.sleep(0.2)  # so that the CPU does not fry
        except (
            IndexError,
            AttributeError,
            PdfReadError,
            TypeError,
            KeyError,
            NotImplementedError,
            ValueError,
            AssertionError,
            FileNotFoundError,
        ):
            mylogger.critical(f"Could not parse date for {pdf_file}")
