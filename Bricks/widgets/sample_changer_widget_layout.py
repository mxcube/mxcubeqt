# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/sample_changer_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class SampleChangerWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("SampleChangerWidgetLayout")


        SampleChangerWidgetLayoutLayout = QHBoxLayout(self,0,6,"SampleChangerWidgetLayoutLayout")

        self.gbox = QGroupBox(self,"gbox")
        self.gbox.setColumnLayout(0,Qt.Vertical)
        self.gbox.layout().setSpacing(2)
        self.gbox.layout().setMargin(11)
        gboxLayout = QHBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        layout6 = QVBoxLayout(None,0,6,"layout6")

        rone_layout = QHBoxLayout(None,0,6,"rone_layout")

        filter_hlayout = QHBoxLayout(None,0,22,"filter_hlayout")

        self.filter_label = QLabel(self.gbox,"filter_label")
        filter_hlayout.addWidget(self.filter_label)

        self.filter_cbox = QComboBox(0,self.gbox,"filter_cbox")
        filter_hlayout.addWidget(self.filter_cbox)
        rone_layout.addLayout(filter_hlayout)
        hspacer_right = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rone_layout.addItem(hspacer_right)

        self.details_button = QPushButton(self.gbox,"details_button")
        self.details_button.setMinimumSize(QSize(110,0))
        rone_layout.addWidget(self.details_button)
        layout6.addLayout(rone_layout)

        layout5 = QHBoxLayout(None,0,6,"layout5")

        self.centring_label = QLabel(self.gbox,"centring_label")
        layout5.addWidget(self.centring_label)

        self.centring_cbox = QComboBox(0,self.gbox,"centring_cbox")
        layout5.addWidget(self.centring_cbox)
        rthree_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout5.addItem(rthree_spacer)

        self.synch_button = QPushButton(self.gbox,"synch_button")
        layout5.addWidget(self.synch_button)
        layout6.addLayout(layout5)
        gboxLayout.addLayout(layout6)
        SampleChangerWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(347,89).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("SampleChangerWidget"))
        self.gbox.setTitle(self.__tr("Sample list"))
        self.filter_label.setText(self.__tr("Show:"))
        self.filter_cbox.clear()
        self.filter_cbox.insertItem(self.__tr("All samples"))
        self.filter_cbox.insertItem(self.__tr("Mounted sample"))
        self.filter_cbox.insertItem(self.__tr("Use as free pin"))
        self.details_button.setText(self.__tr("Show SC-details"))
        self.centring_label.setText(self.__tr("Centring:"))
        self.centring_cbox.clear()
        self.centring_cbox.insertItem(self.__tr("Manual"))
        self.centring_cbox.insertItem(self.__tr("Automatic loop centring"))
        self.centring_cbox.insertItem(self.__tr("Automatic crystal centring"))
        self.synch_button.setText(self.__tr("S"))


    def __tr(self,s,c = None):
        return qApp.translate("SampleChangerWidgetLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = SampleChangerWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
