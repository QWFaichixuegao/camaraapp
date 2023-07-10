# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

import Ui_Detection1


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()

    ui = Ui_Detection1.Ui_Form()

    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

