import sys

from enum import Enum, unique
from PyQt5 import QtCore, QtWidgets
from crydi import md4, md5, sha1, sha256, hmac
from main_ui import Ui_Dialog

@unique
class InputType(Enum):
    File = 0
    Keyboard = 1

class MainDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

        self.browseFileButton.clicked.connect(self.openFileDialog)
        self.setupProcessButton()

    def setupProcessButton(self):
        menu = QtWidgets.QMenu(parent = self.processInputButton)
        menu.addAction('Procesar teclado', self.setKeyboardAsInput)
        menu.addAction('Procesar archivo', self.setFileAsIinput)

        self.setKeyboardAsInput()
        self.processInputButton.setMenu(menu)
        self.processInputButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.processInputButton.clicked.connect(self.processInput)

    def setFileAsIinput(self):
        self.input = InputType.File
        self.processInputButton.setText('Procesar archivo')

    def setKeyboardAsInput(self):
        self.input = InputType.Keyboard
        self.processInputButton.setText('Procesar teclado')

    def openFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"", "","All Files (*)", options=options)

        if not fileName:
            return

        self.filenameLine.setText(fileName)

    def clearOutputValues(self):
        self.infoLabel.setText('')
        self.md5Output.setText('')
        self.md4Output.setText('')
        self.sha1Output.setText('')
        self.sha256Output.setText('')
        self.hmacOutput.setText('')

    def processInput(self):
        self.clearOutputValues()

        if self.input == InputType.File:
            file = QtCore.QFile(self.filenameLine.text())
            if not file.open(QtCore.QIODevice.ReadOnly):
                self.infoLabel.setText('Error: no existe el archivo')
                return

            stream = QtCore.QTextStream(file)
            self.contents = stream.readAll()[:-1]
        else:
            self.contents = self.keyboardInputText.toPlainText()

        self.contents  = self.contents or ''
        self.hex_input = self.hexKeyboardCheckBox.isChecked() or self.hexFileCheckBox.isChecked()

        if self.hex_input:
            self.contents = self.contents.replace(' ' ,  '')
            self.contents = self.contents.replace('\t',  '')
            self.contents = self.contents.replace('\r', '')
            self.contents = self.contents.replace('\n',  '')

        self.key     = self.keyLine.text()
        self.hex_key = self.hexKeyCheckbox.isChecked()
        self.hash_fn = self.hashComboBox.currentText()

        self.processMD4()
        self.processMD5()
        self.processSHA1()
        self.processSHA256()
        self.processHMAC()

    def processMD4(self):
        try:
            digest = md4.digest(self.contents, self.hex_input)
        except Exception:
            self.infoLabel.setText('Error: valor hexadecimal inválido')
            return 

        self.md4Output.setText(digest)

    def processMD5(self):
        try:
            digest = md5.digest(self.contents, self.hex_input)
        except Exception:
            self.infoLabel.setText('Error: valor hexadecimal inválido')
            return

        self.md5Output.setText(digest)

    def processSHA1(self):
        try:
            digest = sha1.digest(self.contents, self.hex_input)
        except Exception:
            self.infoLabel.setText('Error: valor hexadecimal inválido')
            return

        self.sha1Output.setText(digest)

    def processSHA256(self):
        try:
            digest = sha256.digest(self.contents, self.hex_input)
        except Exception:
            self.infoLabel.setText('Error: valor hexadecimal inválido')
            return

        self.sha256Output.setText(digest)

    def processHMAC(self):
        if not self.key:
            return 

        try:
            digest = hmac.digest(self.contents, self.hash_fn, self.key, self.hex_input,
                                 self.hex_key)
        except Exception:
            self.infoLabel.setText('Error: valor hexadecimal inválido')
            return

        self.hmacOutput.setText(digest)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = MainDialog()
    dialog.show()
    sys.exit(app.exec_())
