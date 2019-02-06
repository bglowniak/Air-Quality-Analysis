# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/QtDesignerUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 185)
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 191))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.FieldRole, spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.FieldRole, spacerItem1)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.checkBox = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBox.setText("")
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.checkBox)
        self.dateTimeEdit_2 = QtWidgets.QDateTimeEdit(self.formLayoutWidget)
        self.dateTimeEdit_2.setObjectName("dateTimeEdit_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.dateTimeEdit_2)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.formLayoutWidget)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.dateTimeEdit)
        self.pushButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.pushButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Select Files:"))
        self.label_2.setText(_translate("Dialog", "Select Output Folder:"))
        self.label_3.setText(_translate("Dialog", "Use Time Range?"))
        self.pushButton.setText(_translate("Dialog", "Run"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

