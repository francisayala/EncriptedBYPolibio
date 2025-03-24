from chiper import generate_keys, decrypt
from ui.decrypt import Ui_MainWindow
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
from sys import argv


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.decrypt_button.clicked.connect(self.decrypt)
    
    def decrypt(self):
        secret_key = list(map(int, reversed(self.secret_key.toPlainText().split())))
        data = self.encrypt_result.toPlainText()
        if not data.isascii():
            QMessageBox.warning(self, "Warning", "Must be ASCII characters")
            return
        try:
            self.open_text.setText(decrypt(secret_key, data))
        except:
            QMessageBox.warning(self, "ERROR", "Incorrect key may have been specified")


def main():
    app = QtWidgets.QApplication(argv)
    window = App()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
