# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 19:56:26 2020

@author: Pina
"""
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


class PdfConverter:
    def __init__(self, file_path):
        self.file_path = file_path

    def convert_pdf_to_txt(self):
        """Convert pdf file to a string which has space between words"""

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = "utf-8"  # 'utf16','utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        with open(self.file_path, "rb") as fp:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()
            for page in PDFPage.get_pages(
                fp,
                pagenos,
                maxpages=maxpages,
                password=password,
                caching=caching,
                check_extractable=True,
            ):
                interpreter.process_page(page)
        device.close()
        str_ret = retstr.getvalue()
        retstr.close()
        return str_ret

    def save_convert_pdf_to_txt(self):
        """Convert pdf file text to string and save as a text_pdf.txt file"""

        content = self.convert_pdf_to_txt()
        txt_pdf = open("text_pdf.txt", "wb")
        txt_pdf.write(content.encode("utf-8"))
        txt_pdf.close()
