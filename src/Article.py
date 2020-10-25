# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 19:57:22 2020

@author: Pina
"""


from nltk.corpus import stopwords
from nltk import FreqDist
import nltk
import matplotlib.pyplot as plt
from PIL import Image
from PIL.ImageQt import ImageQt
from io import BytesIO

nltk.download("stopwords")


def txt_to_tokens(text):
    # splitting text and filtering words containing only letters
    tokens = [x for x in filter(lambda x: x.isalpha(), text.lower().split())]
    sr = stopwords.words("english")
    # throwing out 'stop words'
    return [x for x in filter(lambda x: x not in sr, tokens)]


def get_frequency_plot(text, name):
    fig = plt.figure()
    freq = FreqDist(text)
    vals = freq.most_common(20)
    plt.xticks(rotation=90)
    plt.bar(*zip(*vals))
    plt.tight_layout()
    ax = fig.add_subplot(111)
    fig.patch.set_visible(False)
    buf = BytesIO()
    fig.canvas.print_png(buf, format="png", transparent=True)
    buf.seek(0)
    img = Image.open(buf)
    qt_image = ImageQt(img)
    return qt_image


class Article:
    def __init__(self, pdf_name, text):
        self.text = text
        self.pdf_name = pdf_name
        self.tokens = txt_to_tokens(text)
        self.frequency_plot = get_frequency_plot(self.tokens, pdf_name)

    def print_frequencies(self, n=20):
        for key, value in self.freq.most_common(n):
            print(key, ": ", value)
