# -*- coding: utf-8 -*-
#!/usr/bin/env python

from Article import Article
from PdfConverter import PdfConverter

if __name__ == "__main__":
    pdf = PdfConverter("..\data\poland.pdf")
    article_pl = Article(pdf.convert_pdf_to_txt())
    article_pl.plot_frequencies()
    article_pl.print_frequencies()
