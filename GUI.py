import os
from PyQt5 import QtCore, QtWidgets
from .ui.MainWindow import Ui_MainWindow
from .ui.about import Ui_Form as Ui_aboutWindow
from .ui.input import Ui_Form as Ui_inputWindow
from .ui.help import Ui_Form as Ui_helpWindow
import pyqtgraph as pg
import pyqtgraph.exporters
import matplotlib.pyplot as plt
from .fit import *
import configparser

language_path = os.path.realpath(__file__)[:-6] + "language\\"


class Mainwindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, rawVariables=None):
        super(Mainwindow, self).__init__(parent)
        self.setupUi(self)
        self.show()

        # 设置图像框
        self.graphWidget = pg.PlotWidget()
        self.gridLayout_3.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)
        self.Xlabel = None
        self.Ylabel = None

        # 设置帮助、关于以及输入窗口，以及设置各种信号的连接
        self.rawVariables = rawVariables
        self.showvars()
        self.aboutwindow = Aboutwindow()
        self.helpwindow = Helpwindow()
        self.inputwindow_title = Inputwindow()
        self.inputwindow_title.pushButton.clicked.connect(self.inputtitleback)
        self.inputwindow_xlabel = Inputwindow()
        self.inputwindow_xlabel.pushButton.clicked.connect(self.inputXlabelback)
        self.inputwindow_ylabel = Inputwindow()
        self.inputwindow_ylabel.pushButton.clicked.connect(self.inputYlabelback)
        self.signalchannels()

        # 设置拟合选项comboBox
        self.comboBox_3.setCurrentIndex(4)
        self.stackedWidget.setCurrentIndex(4)
        self.findcombo = {'0': [self.lineEdit_2, self.lineEdit_3, self.textEdit_2], '1': self.comboBox_5,
                          '2': self.comboBox_6, '3': self.comboBox_7, '4': self.comboBox_4, '5': self.comboBox_8,
                          '6': [self.comboBox_9, self.comboBox_10], '7': self.comboBox_11}
        self.findlabel = {'1': self.label_11, '2': self.label_13, '3': self.label_15, '5': self.label_19,
                          '6': self.label_22, '7': self.label_26}

        # 设置翻译
        self.translator = QtCore.QTranslator()
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + '\curvefitting.ini')
        self.language = config['DEFAULT'].get('language', "en")
        if self.language == 'en':
            self.translate("en", nomatter=True)
        else:
            self.action_English.setIconVisibleInMenu(False)

        # 自动拟合的设置
        if config['DEFAULT'].get('autofit', "False") == "False":
            self.autofit = False
            self.action_12.setIconVisibleInMenu(False)
        else:
            self.autofit = True
            self.checkBox.setChecked(True)

    def signalchannels(self):
        # 各种信号槽的搭建
        self.comboBox.currentIndexChanged.connect(self.plot)
        self.comboBox.currentIndexChanged.connect(self.renew_xylabel)
        self.comboBox_2.currentIndexChanged.connect(self.plot)
        self.comboBox_2.currentIndexChanged.connect(self.renew_xylabel)
        self.pushButton.clicked.connect(self.goodfit)
        self.checkBox.stateChanged.connect(self.setCheckBox)
        self.pushButton_2.setDisabled(True)
        self.pushButton_4.clicked.connect(self.printfigure)
        self.action_3.triggered.connect(self.printfigure)
        self.pushButton_5.clicked.connect(self.savefigure)
        self.action_7.triggered.connect(self.savefigure)
        self.action_5.triggered.connect(self.close)
        self.action_Chinese.triggered.connect(lambda: self.translate("zh_CN"))
        self.action_English.triggered.connect(lambda: self.translate("en"))
        self.action_11.triggered.connect(self.aboutwindow.show)
        self.action_10.triggered.connect(self.helpwindow.show)
        self.action_12.triggered.connect(self.action_autofit)
        self.action_8.triggered.connect(self.inputtitle)
        self.actionX.triggered.connect(self.inputXlabel)
        self.actionY.triggered.connect(self.inputYlabel)
        self.action.triggered.connect(self.clear)
        self.pushButton_2.clicked.connect(self.stopfitting)
        self.comboBox_3.currentIndexChanged.connect(self.showfitoption)
        self.comboBox_5.currentIndexChanged.connect(self.showfunction)
        self.comboBox_6.currentIndexChanged.connect(self.showfunction)
        self.comboBox_7.currentIndexChanged.connect(self.showfunction)
        self.comboBox_8.currentIndexChanged.connect(self.showfunction)
        self.comboBox_9.currentIndexChanged.connect(self.showfunction)
        self.comboBox_10.currentIndexChanged.connect(self.showfunction)
        self.comboBox_11.currentIndexChanged.connect(self.showfunction)
        self.pushButton_3.clicked.connect(self.printresult)
        self.action_2.triggered.connect(self.printresult)

    def translate(self, language, nomatter=False):
        if (self.language != language) or nomatter:
            self.translator.load(language_path + "MainWindow_{}.qm".format(language))
            _app = QtWidgets.QApplication.instance()
            _app.installTranslator(self.translator)
            self.retranslateUi(self)
            self.aboutwindow.translate(language)
            self.helpwindow.translate(language)
            self.inputwindow_title.translate(language)
            self.inputwindow_xlabel.translate(language)
            self.inputwindow_ylabel.translate(language)
            self.language = language
        if language == "en":
            self.action_English.setIconVisibleInMenu(True)
            self.action_Chinese.setIconVisibleInMenu(False)
        elif language == "zh_CN":
            self.action_English.setIconVisibleInMenu(False)
            self.action_Chinese.setIconVisibleInMenu(True)

    def showvars(self):
        # 负责筛选合适的变量，并显示在comboBox中
        keys_ = list(self.rawVariables.keys())
        variables = []
        for i_ in keys_:
            if not i_.startswith('_') and str(type(self.rawVariables[i_]))[8:-2] in ['int', 'float', 'list', 'tuple',
                                                                                     'numpy.ndarray'] \
                    and not i_ in ['In', 'variables']:
                variables.append(i_)
        del i_, keys_
        text1 = self.comboBox.currentText()
        text2 = self.comboBox_2.currentText()
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.comboBox.addItems(variables)
        self.comboBox_2.addItems(variables)
        self.comboBox.setCurrentText(text1)
        self.comboBox_2.setCurrentText(text2)

    def plot(self):
        # 绘制散点图
        text1 = self.comboBox.currentText()
        text2 = self.comboBox_2.currentText()
        try:
            x, y = eval(text1, self.rawVariables), eval(text2, self.rawVariables)
            if type(x) != type(y):
                self.messege(
                    "无法绘制！\nX与Y的数据类型不同" if self.language == "zh_CN" else "Cannot plot!\nX and Y have different data types")
            elif len(x) != len(y):
                self.messege(
                    "无法绘制！\nX与Y的维度不同" if self.language == "zh_CN" else "Cannot plot!\nX and Y have different dimensions")
            else:
                self.graphWidget.clear()
                scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=1, color='k'), symbol='o', size=4)
                self.graphWidget.addItem(scatter)
                pos = [{'pos': [x[i], y[i]]} for i in range(len(x))]
                scatter.setData(pos)

                if self.autofit:
                    self.goodfit()
        except Exception as e:
            self.messege(repr(e))

    def messege(self, e):
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', e)
        msg_box.exec_()

    def setCheckBox(self):
        # checkBox状态发生变化时进行的设置
        combos = (self.comboBox_3, self.comboBox_4, self.comboBox_5, self.comboBox_6, self.comboBox_7,
                  self.comboBox_8, self.comboBox_9, self.comboBox_10, self.comboBox_11)
        if self.checkBox.isChecked():
            self.autofit = True
            self.plot()
            self.pushButton.setDisabled(True)
            self.pushButton_2.setDisabled(True)
            for combo in combos:
                combo.currentIndexChanged.connect(self.plot)
            self.action_12.setIconVisibleInMenu(True)
        else:
            self.autofit = False
            self.pushButton.setDisabled(False)
            for combo in combos:
                combo.currentIndexChanged.disconnect(self.plot)
            self.action_12.setIconVisibleInMenu(False)

    def findfitmod(self):
        # 生成fit输入参数
        index = self.comboBox_3.currentIndex()
        if index == 0:
            edits = self.findcombo['0']
            value = [edits[0].text(), edits[1].text(), edits[2].toPlainText()]
        elif index == 6:
            value = [i.currentIndex() for i in self.findcombo['6']]
        elif index == 8:
            value = 0
        else:
            value = self.findcombo[str(index)].currentIndex()
        self.fitmod = (index, value)

    def goodfit(self):
        # 拟合接口函数
        if not self.autofit:
            self.pushButton.setDisabled(True)
            self.plot()
        self.pushButton_2.setDisabled(False)
        self.text1 = self.comboBox.currentText()
        self.text2 = self.comboBox_2.currentText()

        try:
            self.findfitmod()
            self.x, self.y = eval(self.text1, self.rawVariables), eval(self.text2, self.rawVariables)

            # 激发线程
            self.workthread = WorkThread([self])
            self.workthread.trigger.connect(self.goodfitback)
            self.workthread.start()
        except Exception as e:
            self.messege(repr(e))

    def goodfitback(self):
        # 把fit操作放在一个线程里，结束后触发的恢复按钮状态的操作
        if self.successfit:
            try:
                pen = pg.mkPen(color='b', width=4)
                xx = (self.x.min(), self.x.max())
                self.graphWidget.plot(np.linspace(xx[0], xx[1], 200),
                                      self.p(np.linspace(xx[0], xx[1], 200), *self.para),
                                      name=self.lineEdit.text(), pen=pen)

                self.textEdit.setText("")
                text = give_reflect(self.x, self.y, self.p, self.para, self.para_names, self.fitmod, self.language)
                for i in text:
                    self.textEdit.append(i)
            except Exception as e:
                self.messege(repr(e))
        else:
            self.messege(self.e)
        if not self.autofit:
            self.pushButton.setDisabled(False)
        self.pushButton_2.setDisabled(True)

    def stopfitting(self):
        # 停止拟合
        self.workthread.terminate()
        self.workthread.wait()
        if not self.autofit:
            self.pushButton.setDisabled(False)
        self.pushButton_2.setDisabled(True)

    def showfitoption(self):
        # 将stackedWidget与相应拟合模式相绑定
        self.stackedWidget.setCurrentIndex(self.comboBox_3.currentIndex())

    def showfunction(self):
        # 设置label为表示当前方程的字符串
        self.findfitmod()
        text = show_function(self.fitmod)[7:]
        label = self.findlabel[str(self.fitmod[0])]
        label.setToolTip(text)
        room = int(label.width() / 5.5)
        if len(text) > room:
            text = text[:room - 4] + '...'
        label.setText(text)

    def printresult(self):
        # 输出拟合结果
        if self.fitmod[0] == 0:
            text_func = "f({}) = ".format(self.fitmod[1][1]) + self.fitmod[1][2]
        else:
            text_func = show_function(self.fitmod)
        if self.fitmod[0] == 4:
            for i in range(self.fitmod[1] + 2):
                text_func = text_func.replace("p{}".format(i + 1), str(round(self.p[self.fitmod[1] + 1 - i], 2)))
        else:
            for i in range(len(self.para)):
                text_func = text_func.replace(self.para_names[i], str(round(self.para[i], 2)))
        print(text_func)

    def printfigure(self):
        try:
            if self.language == "zh_CN":
                plt.rcParams['font.sans-serif'] = 'SimHei'
                plt.rcParams['axes.unicode_minus'] = False
            xx = (self.x.min(), self.x.max())
            plt.plot(np.linspace(xx[0], xx[1], 200), self.p(np.linspace(xx[0], xx[1], 200), *self.para))
            plt.scatter(self.x, self.y, c='k')
            plt.gcf().set_facecolor(np.ones(3) * 240 / 255)
            plt.grid()
            if self.Xlabel:
                self.text1 = self.Xlabel
            if self.Ylabel:
                self.text2 = self.Ylabel
            plt.legend([self.lineEdit.text(), "{} vs. {}".format(self.text2, self.text1)])
            plt.title(self.lineEdit.text())
            plt.xlabel(self.text1)
            plt.ylabel(self.text2)
            plt.show()
        except Exception as e:
            self.messege(repr(e))

    def savefigure(self):
        fileName, fileType = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                   "保存文件" if self.language == "zh_CN" else "Save file",
                                                                   os.getcwd(),
                                                                   "Portable Network Graphics(*.png);;Joint Photographic Group(*.jpg);;All Files(*)")
        if fileName:
            ex = pyqtgraph.exporters.ImageExporter(self.graphWidget.plotItem)
            ex.parameters()['width'] = 2000
            ex.export(fileName)

    def action_autofit(self):
        if self.checkBox.isChecked():
            self.checkBox.setChecked(False)
            self.action_12.setIconVisibleInMenu(False)
        else:
            self.checkBox.setChecked(True)
            self.action_12.setIconVisibleInMenu(True)

    def closeEvent(self, event):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {"language": self.language, "autofit": str(self.checkBox.isChecked())}
        with open(os.path.expanduser('~') + '\curvefitting.ini', 'w') as configfile:
            config.write(configfile)
        event.accept()

    def inputtitle(self):
        self.inputwindow_title.lineEdit.setText(self.lineEdit.text())
        self.inputwindow_title.show()

    def inputtitleback(self):
        title = self.inputwindow_title.inputvalue
        if title:
            self.lineEdit.setText(title)

    def inputXlabel(self):
        if self.Xlabel:
            self.inputwindow_xlabel.lineEdit.setText(self.Xlabel)
        else:
            self.inputwindow_xlabel.lineEdit.setText(self.comboBox.currentText())
        self.inputwindow_xlabel.show()

    def inputXlabelback(self):
        xlabel = self.inputwindow_xlabel.inputvalue
        if xlabel:
            self.Xlabel = xlabel

    def inputYlabel(self):
        if self.Ylabel:
            self.inputwindow_ylabel.lineEdit.setText(self.Ylabel)
        else:
            self.inputwindow_ylabel.lineEdit.setText(self.comboBox_2.currentText())
        self.inputwindow_ylabel.show()

    def inputYlabelback(self):
        ylabel = self.inputwindow_ylabel.inputvalue
        if ylabel:
            self.Ylabel = ylabel

    def renew_xylabel(self):
        self.Xlabel = None
        self.Ylabel = None

    def clear(self):
        self.comboBox.setCurrentIndex(0)
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_4.setCurrentIndex(0)
        self.graphWidget.clear()
        self.renew_xylabel()
        self.translate(self.language, nomatter=True)
        del self.x, self.y, self.p, self.text1, self.text2


class WorkThread(QtCore.QThread):
    # 专为拟合而生的线程
    trigger = QtCore.pyqtSignal()

    def __init__(self, myui):
        super(WorkThread, self).__init__()
        [self.ui] = myui

    def run(self):
        self.ui.successfit = False
        try:
            self.ui.p, self.ui.para, self.ui.para_names = fit(self.ui.x, self.ui.y, mod=self.ui.fitmod)
        except Exception as e:
            self.ui.e = repr(e)
        else:
            self.ui.successfit = True
        self.trigger.emit()


class Aboutwindow(QtWidgets.QWidget, Ui_aboutWindow):
    def __init__(self, parent=None):
        super(Aboutwindow, self).__init__(parent)
        self.setupUi(self)
        self.translator = QtCore.QTranslator()

    def translate(self, language):
        self.translator.load(language_path + "about_{}.qm".format(language))
        _app = QtWidgets.QApplication.instance()
        _app.installTranslator(self.translator)
        self.retranslateUi(self)


class Helpwindow(QtWidgets.QWidget, Ui_helpWindow):
    def __init__(self, parent=None):
        super(Helpwindow, self).__init__(parent)
        self.setupUi(self)
        self.translator = QtCore.QTranslator()

    def translate(self, language):
        self.translator.load(language_path + "help_{}.qm".format(language))
        _app = QtWidgets.QApplication.instance()
        _app.installTranslator(self.translator)
        self.retranslateUi(self)


class Inputwindow(QtWidgets.QWidget, Ui_inputWindow):
    def __init__(self, parent=None):
        super(Inputwindow, self).__init__(parent)
        self.setupUi(self)
        self.translator = QtCore.QTranslator()
        self.inputvalue = None
        self.pushButton.clicked.connect(self.OK)
        self.pushButton_2.clicked.connect(self.close)

    def OK(self):
        self.inputvalue = self.lineEdit.text()
        self.close()

    def translate(self, language):
        self.translator.load(language_path + "input_{}.qm".format(language))
        _app = QtWidgets.QApplication.instance()
        _app.installTranslator(self.translator)
        self.retranslateUi(self)
