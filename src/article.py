# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 19:57:22 2020

@author: Pina
"""

import nltk
from nltk import FreqDist
from nltk.corpus import stopwords


class Article:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        self.tokens = self.txt_to_tokens(self.text)
        self.freq = FreqDist(self.tokens)

    def print_frequencies(self, n=20):
        for key, value in self.freq.most_common(n):
            print(key, ": ", value)

    def plot_frequencies(self):
        self.freq.plot(20, cumulative=False)

    @staticmethod
    def txt_to_tokens(text):
        """Split text and filter words containing only letters"""

        tokens = [x for x in filter(lambda x: x.isalpha(), text.lower().split())]
        nltk.download("stopwords")
        sr = stopwords.words("english")
        # throwing out 'stop words'
        return [x for x in filter(lambda x: x not in sr, tokens)]
