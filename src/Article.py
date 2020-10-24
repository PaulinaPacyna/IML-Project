# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 19:57:22 2020

@author: Pina
"""


from nltk.corpus import stopwords
from nltk import FreqDist


class Article:
    def __init__(self,text):
        self.text=text  
        #splitting text and filtering words containing only letters
        tokens=[x for x in filter(lambda x: x.isalpha(),text.lower().split())]  
        sr= stopwords.words('english')
        #throwing out 'stop words'
        self.tokens = [x for x in filter(lambda x: x not in sr,tokens )]
        self.freq = FreqDist(self.tokens)
    def print_frequencies (self,n=20):
        for key,value in self.freq.most_common(n):
            print(key,': ',value)
        
    def plot_frequencies(self):
        self.freq.plot(20, cumulative=False) 