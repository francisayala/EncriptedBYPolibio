from chiper import generate_keys, encrypt
from ui.encrypt import Ui_MainWindow
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
from sys import argv


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.generate_keys_button.clicked.connect(self.generate_keys)
        self.encrypt_button.clicked.connect(self.encrypt)
    
    def generate_keys(self):
        open_key, secret_key = generate_keys(58)
        self.open_key.setPlainText(f'{open_key[1]} {open_key[0]}')
        self.secret_key.setPlainText(f'{secret_key[1]} {secret_key[0]}')
    
    def encrypt(self):
        open_key = list(map(int, reversed(self.open_key.toPlainText().split())))
        data = self.open_text.toPlainText()
        if not data.isascii():
            QMessageBox.warning(self, "Warning", "Must be ASCII characters")
            return
        self.encrypt_result.setText(encrypt(open_key, data))


def main():
    app = QtWidgets.QApplication(argv)
    window = App()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
