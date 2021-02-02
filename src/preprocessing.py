"""
Place unzipped clean_data folder in IML-Project/ folder and run this script
to perform simple preprocessing on txt files.
"""
import itertools
import os
import re
import shutil
import num2words
from spacy.lang.en.stop_words import STOP_WORDS


def move(destination):
    """Flatten a directory."""
    all_files = []
    for root, _dirs, files in itertools.islice(os.walk(destination), 1, None):
        for filename in files:
            all_files.append(os.path.join(root, filename))
    for filename in all_files:
        shutil.move(filename, destination)


def flatten(path=os.path.join(os.path.dirname(os.getcwd()), "clean_data")):
    """In the dataset provided by Marcel, sometimes a file which contain a '$' in the name
    is saved as a directory with the file inside. This function fixes this error.
    Input: path - path to clean_data folder"""

    for year in os.listdir(path):
        year_path = os.path.join(path, year)
        if os.path.isdir(year_path):
            for month in os.listdir(os.path.join(path, year)):
                month_path = os.path.join(path, year, month)
                if os.path.isdir(month_path):
                    for folder in os.listdir(month_path):
                        if os.path.isdir(os.path.join(path, year, month, folder)):
                            move(os.path.join(path, year, month, folder))
                            shutil.rmtree(
                                os.path.join(path, year, month, folder),
                                ignore_errors=True,
                            )


def preprocess_txt(path=os.path.join(os.path.dirname(os.getcwd()), "clean_data")):
    """Remove non letters, words shorter than 3 letters or longer
    than 20 letters, and multiple spaces.
    Input: path - path to clean_data folder"""
    for year in os.listdir(path):
        year_path = os.path.join(path, year)
        if os.path.isdir(year_path):
            for month in os.listdir(os.path.join(path, year)):
                month_path = os.path.join(path, year, month)
                if os.path.isdir(month_path):
                    for file in os.listdir(month_path):
                        f = open(os.path.join(path, year, month, file), "r")
                        letters_only = re.sub(r"[^a-zA-Z\s]", " ", f.read())
                        no_singletons = re.sub(r"\b\w{1,2}\b", " ", letters_only)
                        no_long_words = re.sub(r"\b[a-zA-Z]{20,}\b", " ", no_singletons)
                        single_spaces = re.compile(r"\s{2,}").sub(" ", no_long_words)
                        no_stop_words = " ".join(
                            filter(
                                lambda x: x not in STOP_WORDS,
                                single_spaces.split(sep=" "),
                            )
                        )
                        w = open(os.path.join(path, year, month, file), "w")
                        w.write(no_stop_words)
                        f.close()
                        w.close()


STOP_WORDS |= set([num2words.num2words(x) for x in range(100)])
flatten()
preprocess_txt()
