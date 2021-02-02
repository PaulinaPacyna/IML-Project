# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 19:56:26 2020

@author: Pina
"""

from tika import parser


def convert_pdf_to_string(file_path):

    rawText = parser.from_file(file_path)
    rawList = rawText["content"]
    return rawList
