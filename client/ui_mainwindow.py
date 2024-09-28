from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.createTableButton = QtWidgets.QPushButton(self.centralwidget)
        self.createTableButton.setGeometry(QtCore.QRect(150, 100, 100, 30))
        self.createTableButton.setObjectName("createTableButton")

        self.deleteTableButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteTableButton.setGeometry(QtCore.QRect(150, 150, 100, 30))
        self.deleteTableButton.setObjectName("deleteTableButton")

        self.tableNameInput = QtWidgets.QLineEdit(self.centralwidget)
        self.tableNameInput.setGeometry(QtCore.QRect(100, 50, 200, 30))
        self.tableNameInput.setObjectName("tableNameInput")

        self.fieldsInput = QtWidgets.QLineEdit(self.centralwidget)
        self.fieldsInput.setGeometry(QtCore.QRect(100, 200, 200, 30))
        self.fieldsInput.setObjectName("fieldsInput")

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DBMS Client"))
        self.createTableButton.setText(_translate("MainWindow", "Create Table"))
        self.deleteTableButton.setText(_translate("MainWindow", "Delete Table"))
