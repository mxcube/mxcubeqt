# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/radiation_damage_model_widget_layout.ui'
#
# Created: Mon Mar 25 09:56:13 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class RadiationDamageModelWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("RadiationDamageModelWidgetLayout")


        RadiationDamageModelWidgetLayoutLayout = QVBoxLayout(self,0,0,"RadiationDamageModelWidgetLayoutLayout")

        self.gbox = QGroupBox(self,"gbox")
        self.gbox.setColumnLayout(0,Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QHBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        main_hlayout = QHBoxLayout(None,0,6,"main_hlayout")

        label_vlayout = QVBoxLayout(None,0,6,"label_vlayout")

        self.beta_over_gray_label = QLabel(self.gbox,"beta_over_gray_label")
        label_vlayout.addWidget(self.beta_over_gray_label)

        self.gamma_over_gray_label = QLabel(self.gbox,"gamma_over_gray_label")
        label_vlayout.addWidget(self.gamma_over_gray_label)

        self.sensetivity_label = QLabel(self.gbox,"sensetivity_label")
        label_vlayout.addWidget(self.sensetivity_label)
        main_hlayout.addLayout(label_vlayout)

        ledit_vlayout = QVBoxLayout(None,0,6,"ledit_vlayout")

        self.beta_over_gray_ledit = QLineEdit(self.gbox,"beta_over_gray_ledit")
        self.beta_over_gray_ledit.setMinimumSize(QSize(50,0))
        self.beta_over_gray_ledit.setMaximumSize(QSize(50,32767))
        ledit_vlayout.addWidget(self.beta_over_gray_ledit)

        self.gamma_over_gray_ledit = QLineEdit(self.gbox,"gamma_over_gray_ledit")
        self.gamma_over_gray_ledit.setMinimumSize(QSize(50,0))
        self.gamma_over_gray_ledit.setMaximumSize(QSize(50,32767))
        ledit_vlayout.addWidget(self.gamma_over_gray_ledit)

        self.sensetivity_ledit = QLineEdit(self.gbox,"sensetivity_ledit")
        self.sensetivity_ledit.setMinimumSize(QSize(50,0))
        self.sensetivity_ledit.setMaximumSize(QSize(50,32767))
        ledit_vlayout.addWidget(self.sensetivity_ledit)
        main_hlayout.addLayout(ledit_vlayout)
        gboxLayout.addLayout(main_hlayout)
        RadiationDamageModelWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(218,138).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("RadiationDamageModelWidget"))
        self.gbox.setTitle(self.__tr("Radiation damage model"))
        self.beta_over_gray_label.setText(self.__trUtf8("\xce\xb2\xc3\x85\x3c\x73\x75\x70\x3e\x32\x3c\x2f\x73\x75\x70\x3e\x2f\x4d\x47\x79\x3a"))
        self.gamma_over_gray_label.setText(self.__trUtf8("\xce\xb3\x20\x31\x2f\x4d\x47\x79\x3a"))
        self.sensetivity_label.setText(self.__tr("Sensetivity:"))


    def __tr(self,s,c = None):
        return qApp.translate("RadiationDamageModelWidgetLayout",s,c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("RadiationDamageModelWidgetLayout",s,c,QApplication.UnicodeUTF8)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = RadiationDamageModelWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
