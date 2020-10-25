from PyQt5 import Qt, QtWidgets, QtCore
import pandas as pd
from manimlib.imports import *
from math import cos, sin, pi
from sklearn.feature_extraction.text import TfidfVectorizer
import FilePicker
from os import listdir
from os.path import join, isfile
from PdfConverter import PdfConverter
from Article import Article


class TfidfVectorizerWidget(Qt.QFrame):
    def __init__(self):
        super(TfidfVectorizerWidget, self).__init__()

        self.folder_path = ""

        self.layout = QtWidgets.QVBoxLayout()
        self.setAutoFillBackground(True)

        self.table_layout = QtWidgets.QVBoxLayout()

        self.graph_plot = Qt.QLabel()
        self.graph_plot.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )
        self.run_btn = Qt.QPushButton()
        self.run_btn.setText("Run")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.start_thread)

        self.folder_viewer_layout = QtWidgets.QHBoxLayout()
        self.folder_label = Qt.QLabel()
        self.folder_label.setText("Directory of the PDF(s) : ")
        self.folder_text_edit = Qt.QTextEdit()
        self.folder_text_edit.setFixedHeight(20)
        self.folder_text_edit.setEnabled(False)
        self.folder_browser_btn = Qt.QPushButton()
        self.folder_browser_btn.setText("Choose Folder")
        self.folder_viewer_layout.addWidget(self.folder_label, 1)
        self.folder_viewer_layout.addWidget(self.folder_text_edit, 3)
        self.folder_viewer_layout.addWidget(self.folder_browser_btn, 1)
        self.folder_browser_btn.clicked.connect(self.set_folder_path)

        self.layout.addLayout(self.folder_viewer_layout, 1)
        self.layout.addLayout(self.table_layout, 15)
        self.layout.addWidget(self.graph_plot, 15)
        self.layout.addWidget(self.run_btn, 2)

        self.setLayout(self.layout)
        self.setObjectName("Frame")
        self.setStyleSheet(
            "#Frame {background : #cfcfcf; border : 3px solid #9496cb; border-radius : 10px}"
        )
        self.Vectorizer = Vectorizer_Thread()
        self.Vectorizer.top_words_signal.connect(self.get_result)

    def get_result(self, result: pd.DataFrame):
        model = PandasModel(result)
        self.TableWidget = QtWidgets.QTableView()
        self.TableWidget.setModel(model)
        self.TableWidget.resizeColumnsToContents()
        self.TableWidget.horizontalHeader().setSectionResizeMode(
            Qt.QHeaderView.Stretch
        )
        self.table_layout.addWidget(self.TableWidget)
        self.TableWidget.clicked.connect(self.show_plot)
        self.graph_plot.setPixmap(
            Qt.QPixmap.fromImage(self.Vectorizer.Articles[0].frequency_plot)
        )

    def set_folder_path(self):
        filepicker = FilePicker.FolderPicker()
        self.folder_path = filepicker.getFolderPath()
        self.folder_text_edit.setText(self.folder_path)
        self.Vectorizer.Pdf_Files_Location = self.folder_path
        if self.folder_path != "":
            self.run_btn.setEnabled(True)

    def show_plot(self, item):
        article = self.Vectorizer.Articles[item.column()]
        self.graph_plot.setPixmap(Qt.QPixmap.fromImage(article.frequency_plot))

    def start_thread(self):
        self.Vectorizer.run()


class Vectorizer_Thread(Qt.QThread):
    top_words_signal = QtCore.pyqtSignal(pd.DataFrame, name="listSignal")
    plot_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(Vectorizer_Thread, self).__init__()
        self.Pdf_Files_Location = None
        self.Articles = []
        self.computed_df = pd.DataFrame()

    def run(self):

        pdf_text = []
        pdf_names = []
        for pdf_file in listdir(self.Pdf_Files_Location):
            pdf_names.append(pdf_file)
            converted_pdf = PdfConverter(
                join(self.Pdf_Files_Location, pdf_file)
            )
            single_pdf_txt = converted_pdf.convert_pdf_to_txt()

            article = Article(pdf_file.split(".")[0], single_pdf_txt)

            self.Articles.append(article)

            pdf_text.append(single_pdf_txt)

        vectorizer = TfidfVectorizer(
            max_df=0.65, min_df=1, stop_words=None, use_idf=True, norm=None
        )
        doc_vec = vectorizer.fit_transform(pdf_text)

        transformed_documents_as_array = doc_vec.toarray()

        final_df = pd.DataFrame()

        for counter, doc in enumerate(transformed_documents_as_array):
            # construct a dataframe
            tf_idf_tuples = list(zip(vectorizer.get_feature_names(), doc))
            one_doc_as_df = (
                pd.DataFrame.from_records(
                    tf_idf_tuples, columns=["term", "score"]
                )
                .sort_values(by="score", ascending=False)
                .reset_index(drop=True)
            )
            one_doc_as_df = one_doc_as_df.drop("score", 1)
            final_df[pdf_names[counter].split(".")[0]] = one_doc_as_df[
                "term"
            ].values

        self.computed_df = final_df
        self.top_words_signal.emit(final_df)


class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if (
            orientation == QtCore.Qt.Horizontal
            and role == QtCore.Qt.DisplayRole
        ):
            return self._data.columns[col]
        return None
