# Preprocessing part of the IML project :
Here you will find all the scripts required to gather and clean the data before going into the tf-idf, the scripts should be executed in the following order :
1. scraper.py (scraping from www.arxiv.org)
2. date_formatter.py to add the pdfs given by the prof (although I did not use them since we got tons of data)
3. preprocessing.py

Once the execution is done, the project will have the following structure :

```bash
.
├── data
│   ├── year
│   │   │── month
│   │   │   │── files.pdf
│   │   │   │
│   │   │   └──...
│   │	└──...
│   └──...
├── clean_data
│   ├── year
│   │   │── month
│   │   │   │── files.txt
│   │   │   │
│   │   │   └──...
│   │	└──...
│   └──...
└── src
├── Article.py
├── PdfConverter.py
├── date_formatter.py
├── preprocessing.py
└── scraper.py
```

Execution details :

* The **data** directory will be created when the **scraper.py** script is executed, the pdfs will not be sorted at this stage.
* Once the scraper is done, we run the **date_formatter.py** script, which will inspect the metadata of each pdf, fetch the creationDate tag and reorganise them as seen in the above dir tree.
* Now we clean the data by running **preprocessing.py**, which will remove special characters, remove numbers, lemmatize, remove stop words (in order) for every pdf file and save it as a text file (perserving it's date specified in the dir tree)


[UPDATED] Link to clean data : https://drive.google.com/file/d/1rmg6gw2-HV0fvRt89Hs4KZsx_XD6ypeL/view?usp=sharing (367 MB zipped) | (1.22 GB decompressed)
