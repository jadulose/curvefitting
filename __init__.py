__author__ = "Fan Peilin"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2020 Fan Peilin"
__license__ = "MIT"

__all__ = ['cftool']

import os
import sys
from PyQt5 import QtCore, QtWidgets
from .GUI import Mainwindow
import configparser

if not os.path.exists(os.path.expanduser('~')+'\curvefitting.ini'):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {"language": "en", "autofit": "False"}
    with open(os.path.expanduser('~')+'\curvefitting.ini', 'w') as configfile:
        config.write(configfile)


def cftool(rawVariables):
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    Mainwindow(rawVariables=rawVariables)
    app.exec_()
