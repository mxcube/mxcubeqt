# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/sad_char_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class SADWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("SADWidgetLayout")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.sizePolicy().hasHeightForWidth()))

        SADWidgetLayoutLayout = QVBoxLayout(self,10,0,"SADWidgetLayoutLayout")

        self.sad_bgroup = QButtonGroup(self,"sad_bgroup")
        self.sad_bgroup.setFrameShape(QButtonGroup.NoFrame)
        self.sad_bgroup.setColumnLayout(0,Qt.Vertical)
        self.sad_bgroup.layout().setSpacing(0)
        self.sad_bgroup.layout().setMargin(0)
        sad_bgroupLayout = QHBoxLayout(self.sad_bgroup.layout())
        sad_bgroupLayout.setAlignment(Qt.AlignTop)

        main_vlayout = QVBoxLayout(None,0,6,"main_vlayout")

        self.automatic_resolution_radio = QRadioButton(self.sad_bgroup,"automatic_resolution_radio")
        main_vlayout.addWidget(self.automatic_resolution_radio)

        rtwo_hlayout = QHBoxLayout(None,0,6,"rtwo_hlayout")

        self.optimal_sad_radio = QRadioButton(self.sad_bgroup,"optimal_sad_radio")
        rtwo_hlayout.addWidget(self.optimal_sad_radio)

        self.sad_resolution_ledit = QLineEdit(self.sad_bgroup,"sad_resolution_ledit")
        self.sad_resolution_ledit.setMinimumSize(QSize(50,0))
        self.sad_resolution_ledit.setMaximumSize(QSize(50,32767))
        rtwo_hlayout.addWidget(self.sad_resolution_ledit)
        hspacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rtwo_hlayout.addItem(hspacer)
        main_vlayout.addLayout(rtwo_hlayout)
        sad_bgroupLayout.addLayout(main_vlayout)
        SADWidgetLayoutLayout.addWidget(self.sad_bgroup)
        vspacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        SADWidgetLayoutLayout.addItem(vspacer)

        self.languageChange()

        self.resize(QSize(422,76).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("SADWidget"))
        self.sad_bgroup.setTitle(QString.null)
        self.automatic_resolution_radio.setText(self.__trUtf8("\x52\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x20\x73\x65\x6c\x65\x63\x74\x65\x64\x20\x61\x75\x74\x6f\x6d\x61\x74\x69\x63\x61\x6c\x6c\x79\x2c\x20\x72\x6f\x74\x61\x74\x69\x6f\x6e\x20\x69\x6e\x74\x65\x72\x76\x61\x6c\x3a\x20\x33\x36\x30\xc2\xb0"))
        self.optimal_sad_radio.setText(self.__tr("Optimal SAD for given resolution:"))


    def __tr(self,s,c = None):
        return qApp.translate("SADWidgetLayout",s,c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("SADWidgetLayout",s,c,QApplication.UnicodeUTF8)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = SADWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
