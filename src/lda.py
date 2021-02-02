import pandas as pd
import numpy as np
import gensim
from gensim import corpora
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.models.callbacks import PerplexityMetric
from gensim.test.utils import common_corpus, common_dictionary
from gensim import corpora, models
from gensim.test.utils import datapath
from src.pyLDAvis_local import gensim_local
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt
from matplotlib import pylab as pl
from wordcloud import WordCloud

from smart_open import smart_open
import os
import itertools
import pyLDAvis.gensim

# import pickle
# import pyLDAvis.gensim


class ReadFilesDir(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for filename in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, filename)):
                yield simple_preprocess(line)


class ReadFilesDir2(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for year in os.listdir(self.dirname):
            for month in os.listdir(os.path.join(self.dirname, year)):
                for filename in os.listdir(os.path.join(self.dirname, year, month)):
                    for line in open(os.path.join(self.dirname, year, month, filename)):
                        yield simple_preprocess(line)
                print(year + " " + month)


class BoWCorpus(object):
    def __init__(self, path, dictionary):
        self.filepath = path
        self.dictionary = dictionary

    def __iter__(self):
        global mydict
        for line in smart_open(self.filepath):
            tokenized_list = simple_preprocess(line, deacc=True)

            bow = self.dictionary.doc2bow(tokenized_list, allow_update=True)

            mydict.merge_with(self.dictionary)

            yield bow


def create_dictionary(path):
    dictionary = Dictionary()
    for year in os.listdir(path):
        for month in os.listdir(os.path.join(path, year)):
            dict_temp = corpora.Dictionary(ReadFilesDir(os.path.join(path, year, month)))
            dictionary.merge_with(dict_temp)
            print(month)
    return dictionary


def create_corpus(dict, path):
    gensim_corpus = [dict.doc2bow(token, allow_update=True) for token in
                     ReadFilesDir2(path)]
    # Save the corpus
    corpora.MmCorpus.serialize("corpus_all_docs", gensim_corpus)
    return gensim_corpus


def build_lda_model(corpus: list, dictionary: gensim.corpora.dictionary.Dictionary, NUM_TOPICS: int):
    lda_model = gensim.models.ldamodel.LdaModel(corpus,
                                                num_topics=NUM_TOPICS,
                                                id2word=dictionary,
                                                passes=10,
                                                update_every=1,
                                                chunksize=1000)
    # if you want to save the model
    # lda_model.save('model5.gensim')
    return lda_model


def compute_coherence_values(dictionary, corpus, limit, start=2, step=3):
    """
    Compute u_mass coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = models.LdaMulticore(gensim_corpus, id2word=dictionary, num_topics=num_topics, workers=2)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, corpus=corpus, dictionary=dictionary, coherence='u_mass')
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values


def format_topics_sentences(ldamodel, corpus: list):
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num),
                                                                  round(prop_topic, 4),
                                                                  topic_keywords]),
                                                       ignore_index=True)
            else:
                break
        # Show the progress
        if i % 100 == 0:
            print(i)
    sent_topics_df.columns = ['Dominant_Topic', 'Frac_Contribution', 'Topic_Keywords']
    return sent_topics_df


def get_doc_names(path):
    doc_names = []
    years = []
    months = []
    for year in os.listdir(path):
        for month in os.listdir(os.path.join(path, year)):
            for filename in os.listdir(os.path.join(path, year, month)):
                doc_names.append(filename)
                years.append(year)
                months.append(month)
    return doc_names, years, months


def topics_by_time(doc_df: pd.DataFrame):
    topics_time = (doc_df
                   .groupby(by=["Year", "Month", "Dominant_Topic"])
                   .size()
                   .reset_index(name='counts'))
    topics_time[["Year", "Month", "Dominant_Topic"]] = (topics_time[["Year",
                                                                    "Month",
                                                                    "Dominant_Topic"]]
                                                        .astype(int))
    topics_time['Date'] = pd.to_datetime(topics_time[['Year', 'Month']].assign(DAY=1))
    topics_time = topics_time.sort_values(by=["Year", "Month"])
    topics_time = topics_time.drop(["Year", "Month"], axis=1)
    return topics_time


def topics_by_time2(doc_df: pd.DataFrame):
    topics_time = (doc_df
                   .groupby(by=["Year", "Dominant_Topic"])
                   .size()
                   .reset_index(name='counts'))
    topics_time[["Year", "Dominant_Topic"]] = (topics_time[["Year", "Dominant_Topic"]].astype(int))
    topics_time['Date'] = pd.to_datetime(topics_time[['Year']].assign(DAY=1, MONTH=1))
    topics_time = topics_time.sort_values(by=["Year"])
    topics_time = topics_time.drop(["Year"], axis=1)
    return topics_time


def plot_topics_over_time(topics: pd.DataFrame, num_topics: int):
    colors = ["darkblue", "chartreuse", "fuchsia", "red", "lime"]
    for i in range(5):
        for j in range(5*i, 5*(i+1), 1):
            data = topics[topics.Dominant_Topic == j]
            plt.plot(data.Date, data.counts, color=colors[j % 5])
        plt.title("Documents in Topics over Time")
        plt.xlabel("Time")
        plt.ylabel("Number of Documents in Topics")
        plt.legend(range(5*i, 5*(i+1), 1), loc="best")
        plt.savefig(f"Topics{5*i}-{5*(i+1)-1}")
        plt.close()


def plot_topics_over_years(topics: pd.DataFrame):
    colors = ["darkblue", "chartreuse", "fuchsia", "red", "lime"]
    for i in range(5):
        for j in range(5 * i, 5 * (i + 1), 1):
            data = topics[topics.Dominant_Topic == j]
            plt.plot([str(date.year) for date in data.Date], data.counts, color=colors[j % 5])
        plt.title("Documents in Topics over Time")
        plt.xlabel("Time")
        plt.ylabel("Number of Documents in Topics")
        plt.legend(range(5 * i, 5 * (i + 1), 1), loc="best")
        plt.savefig(f"Topics_years_{5 * i}-{5 * (i + 1) - 1}")
        plt.close()


def create_word_clouds(lda_model):
    for t in range(lda_model.num_topics):
        plt.figure()
        plt.imshow(WordCloud(background_color="white").fit_words(dict(lda_model.show_topic(t, 200))))
        plt.axis("off")
        plt.title("Topic #" + str(t))
        plt.savefig(f"Topic_{t}_WordCloud")


if __name__ == "__main__":
    print("Loading path...")
    path = os.path.join(os.path.dirname(os.getcwd()), "clean_data")

    print("Loading dictionary...")
    dictionary = Dictionary()
    dictionary = dictionary.load("dictionary_all_docs")

    print("Loading corpus...")
    gensim_corpus = corpora.MmCorpus("corpus_all_docs")

    # Build the model for the first time (first example is very slow, with 10 topics.
    # HINT: Use the second multicore model with the number of workers that is the number of your cores
    # of the processor minus 1.

    # lda_model_all_docs = build_lda_model(gensim_corpus, dictionary, 10)

    # Multicore model with 3 workers, 25 number of topics a priori, 2000 sized training set
    # the model goes through particular document 10 times (passes argument)
    # lda = models.LdaMulticore(gensim_corpus, id2word=dictionary, num_topics=25, workers=3, chunksize=2000, passes=10)
    # lda.save("model_multicore_25topics")

    print("Loading model...")
    lda = models.LdaMulticore.load("model_multicore_25topics")

    # Print out the topics
    topics = lda.print_topics(num_words=5, num_topics=-1)
    for topic in topics:
        print(topic)



    # # Calculate log perplexity of the model
    # print('\nPerplexity: ', lda.log_perplexity(gensim_corpus))
    # Perplexity:  -8.861996532967312 (for 20 topics)

    # # Use pyLDAvis to show the result of the model and distance map of the topics
    # lda_display = gensim_local.prepare(lda, gensim_corpus, dictionary)
    # # pyLDAvis.show(lda_display)
    # pyLDAvis.save_html(lda_display, 'lda_pyLDAvis_25_topics.html')

    # # Calculating word frequencies in the corpus
    # word_frequencies = [[(mydict[id], frequence) for id, frequence in couple] for couple in gensim_corpus]

    # # Using coherence model to optimize LDA model by number of topics
    # # Starting from 5 to 40 topics by 5 topics
    # model_list, coherence_values = compute_coherence_values(dictionary=dictionary,
    #                                                         corpus=gensim_corpus,
    #                                                         start=5,
    #                                                         limit=40,
    #                                                         step=5)
    # max_value = max(coherence_values)
    # max_index = coherence_values.index(max_value)
    #
    # best_model = model_list[max_index]
    # best_model.save("best_coherence_2_50_5")

    # # Show the graph of relationship between the number of topics and u_mass coherence
    # limit = 40
    # start = 5
    # step = 5
    # x = range(start, limit, step)
    # plt.plot(x, coherence_values)
    # plt.xlabel("Num Topics")
    # plt.ylabel("Coherence score")
    # plt.legend(("coherence_values"), loc='best')
    # plt.show()

    # Finding dominant topic in each sentence

    #####################################################
    # print("Finding dominant topic in each document...")
    # df_topic_sents_keywords = format_topics_sentences(ldamodel=lda, corpus=gensim_corpus)
    #
    # # Format
    # df_dominant_topic = df_topic_sents_keywords.reset_index()
    # df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords']
    #
    # # Save results
    # df_dominant_topic.to_csv("dominant_topics_25")

    ######################################################

    # Merging titles, year and month from the documents with the obtained data set (dominant topics for the particular
    # document)

    df_dominant_topic = pd.read_csv("dominant_topics_25")
    doc_names, years, months = get_doc_names(path)
    df_dominant_topic["Document_Title"] = doc_names
    df_dominant_topic["Year"] = years
    df_dominant_topic["Month"] = months
    df_dominant_topic = df_dominant_topic[["Year",
                                           "Month",
                                           "Document_No",
                                           "Document_Title",
                                           "Dominant_Topic",
                                           "Topic_Perc_Contrib",
                                           "Keywords"]]

    #########################################################################

    # Show how the number of documents for specific topic changes by months
    topics_count = topics_by_time(df_dominant_topic[df_dominant_topic.Year != "2020"])
    topics_count.to_html("topics_count_over_time.html")
    plot_topics_over_time(topics_count, 25)

    # Show how the number of documents for specific topic changes by years
    topics_count2 = topics_by_time2(df_dominant_topic[df_dominant_topic.Year != "2020"])
    topics_count2.to_html("topics_count_over_years.html")
    plot_topics_over_years(topics_count2)


    #########################################################################

    # Create Workclouds for the topics
    create_word_clouds(lda)
