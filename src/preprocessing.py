from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from os import listdir, mkdir
from os.path import join, isfile, isdir
import PdfConverter
from Article import Article
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from pathlib import Path
import nltk
from nltk.corpus import wordnet, stopwords
from timeit import default_timer as timer
from collections import Counter
import time
import re

DATA_PATH = "../data"
CLEAN_DATA_PATH = "../clean_data"

porter = PorterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()
stops = set(stopwords.words("english"))
stopwords_dict = Counter(
    stops
)  # Using a hashmap makes computation considerably faster


def remove_special_characters(text):
    pat = r"[^a-zA-z0-9.,!?/:;\"\'\s]"
    return re.sub(pat, "", text)


def remove_numbers(text):
    pattern = r"[^a-zA-z.,!?/:;\"\'\s]"
    return re.sub(pattern, "", text)


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }

    return tag_dict.get(tag, wordnet.NOUN)


def lemmatize_text(text):
    token_words = word_tokenize(text)
    lemmatized_text = []
    for word in token_words:
        lemmatized_text.append(
            wordnet_lemmatizer.lemmatize(word, get_wordnet_pos(word))
        )
        lemmatized_text.append(" ")
    return "".join(lemmatized_text)


def lemmatize_pdfs():
    if not (isdir("../clean_data")):
        mkdir("../clean_data")
    for year in listdir(DATA_PATH):
        if not (isdir(f"../clean_data/{year}")):
            mkdir(f"../clean_data/{year}")

        for month in listdir(join(DATA_PATH, year)):
            if not (isdir(f"../clean_data/{year}/{month}")):
                mkdir(f"../clean_data/{year}/{month}")

            for pdf_file in listdir(join(join(DATA_PATH, year), month)):
                cleaned_pdf_path = Path(
                    join(join(join(CLEAN_DATA_PATH, year), month), pdf_file)
                ).with_suffix(".txt")
                if not isfile(cleaned_pdf_path):
                    try:
                        pdf_path = join(
                            join(join(DATA_PATH, year), month), pdf_file
                        )
                        single_pdf_txt = PdfConverter.convert_pdf_to_string(
                            pdf_path
                        ).lower()
                        single_pdf_txt = remove_special_characters(
                            single_pdf_txt
                        )

                        single_pdf_txt = remove_numbers(single_pdf_txt)

                        lemmatized_pdf = lemmatize_text(single_pdf_txt)

                        cleaned_pdf = " ".join(
                            [
                                word
                                for word in lemmatized_pdf.split()
                                if word not in stopwords_dict
                            ]
                        )

                        with open(cleaned_pdf_path, "w+") as text_file:
                            text_file.write(cleaned_pdf)

                    except Exception as e:
                        print(e.__cause__)


lemmatize_pdfs()
