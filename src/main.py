from PyQt5 import Qt, QtWidgets, uic, QtCore
import sys
import TfidfVectorizer


class main(Qt.QMainWindow):
    def __init__(self):
        super(main, self).__init__()
        uic.loadUi("../ui/main.ui", self)

        self.TfidfVectorizer = TfidfVectorizer.TfidfVectorizerWidget()

        self.MenuLayout = Qt.QVBoxLayout()
        self.CentralLayout = Qt.QGridLayout()

        self.MenuWidget = Qt.QListWidget(objectName="MenuBar")
        self.MenuLayout.addWidget(self.MenuWidget)

        self.CentralLayout.addWidget(self.TfidfVectorizer)

        self.setStyleSheets()
        self.horizontalLayout.addLayout(self.MenuLayout, 1)
        self.horizontalLayout.addLayout(self.CentralLayout, 4)
        self.show()

    def resizeEvent(self, event):
        Qt.QMainWindow.resizeEvent(self, event)
        VLsize = Qt.QSize(
            event.size().width() - 20, event.size().height() - 20
        )

        self.horizontalLayoutWidget.resize(VLsize)

    def setStyleSheets(self):
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setStyleSheet("#centralwidget{background : #444444;}")
        self.MenuWidget.setStyleSheet(
            "background: #616161;border : 1px solid #8f8f8f; border-radius : 10px"
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main()
    app.exec_()  # execute application
