from PyQt5 import Qt
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QFileDialog


class FolderPicker(
    Qt.QWidget
):  # this is the file picker class used to pick the imported names or the image path
    def __init__(self):
        super().__init__()
        self.title = "Choose Directory"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.filePath = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog()
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderName = QFileDialog.getExistingDirectory(
            self,
            "select directory",
            options=options,
        )
        if folderName:
            self.folderPath = folderName

    def getFolderPath(self):
        return self.folderPath


class errorWindow(
    Qt.QWidget
):  # this is the error window class used to display runtime input errors or connection error
    def __init__(self):
        Qt.QWidget.__init__(self)
        uic.loadUi("../ui/error.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.warningImg.setScaledContents(True)
        self.warningImg.setPixmap(Qt.QPixmap("../ui/warning.png"))
        self.okBtn.clicked.connect(self.exitWindow)
        self.errorTxt.setWordWrap(True)

    def setErrorMsg(self, msg):
        self.errorTxt.setText(msg)

    def exitWindow(self):
        self.close()
