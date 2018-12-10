# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/sample_info_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class SampleInfoWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("SampleInfoWidgetLayout")


        SampleInfoWidgetLayoutLayout = QVBoxLayout(self,0,0,"SampleInfoWidgetLayoutLayout")

        self.gbox = QGroupBox(self,"gbox")
        self.gbox.setColumnLayout(0,Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QVBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        rone_layout = QHBoxLayout(None,0,6,"rone_layout")

        rone_content_layout = QHBoxLayout(None,0,6,"rone_content_layout")

        rone_label_layout = QVBoxLayout(None,0,6,"rone_label_layout")

        self.name_label = QLabel(self.gbox,"name_label")
        rone_label_layout.addWidget(self.name_label)

        self.data_matrix_label = QLabel(self.gbox,"data_matrix_label")
        rone_label_layout.addWidget(self.data_matrix_label)

        self.holder_length_label = QLabel(self.gbox,"holder_length_label")
        rone_label_layout.addWidget(self.holder_length_label)

        self.basket_location_label = QLabel(self.gbox,"basket_location_label")
        rone_label_layout.addWidget(self.basket_location_label)

        self.sample_location_label = QLabel(self.gbox,"sample_location_label")
        rone_label_layout.addWidget(self.sample_location_label)
        rone_content_layout.addLayout(rone_label_layout)

        rone_ledit_layout = QVBoxLayout(None,0,6,"rone_ledit_layout")

        self.name_value_label = QLabel(self.gbox,"name_value_label")
        self.name_value_label.setMinimumSize(QSize(75,0))
        self.name_value_label.setMaximumSize(QSize(75,32767))
        rone_ledit_layout.addWidget(self.name_value_label)

        self.data_matrix_value_label = QLabel(self.gbox,"data_matrix_value_label")
        self.data_matrix_value_label.setMinimumSize(QSize(75,0))
        self.data_matrix_value_label.setMaximumSize(QSize(75,32767))
        rone_ledit_layout.addWidget(self.data_matrix_value_label)

        self.holder_length_value_label = QLabel(self.gbox,"holder_length_value_label")
        self.holder_length_value_label.setMinimumSize(QSize(50,0))
        self.holder_length_value_label.setMaximumSize(QSize(50,32767))
        rone_ledit_layout.addWidget(self.holder_length_value_label)

        self.basket_location_value_label = QLabel(self.gbox,"basket_location_value_label")
        self.basket_location_value_label.setMinimumSize(QSize(50,0))
        self.basket_location_value_label.setMaximumSize(QSize(50,32767))
        rone_ledit_layout.addWidget(self.basket_location_value_label)

        self.sample_location_value_label = QLabel(self.gbox,"sample_location_value_label")
        self.sample_location_value_label.setMinimumSize(QSize(50,0))
        self.sample_location_value_label.setMaximumSize(QSize(50,32767))
        rone_ledit_layout.addWidget(self.sample_location_value_label)
        rone_content_layout.addLayout(rone_ledit_layout)
        rone_layout.addLayout(rone_content_layout)
        hspacer = QSpacerItem(248,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rone_layout.addItem(hspacer)
        gboxLayout.addLayout(rone_layout)
        SampleInfoWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(227,151).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("SampleInfo"))
        self.gbox.setTitle(self.__tr("Sample"))
        self.name_label.setText(self.__tr("Name:"))
        self.data_matrix_label.setText(self.__tr("Data matrix:"))
        self.holder_length_label.setText(self.__tr("Holder length"))
        self.basket_location_label.setText(self.__tr("Basket location"))
        self.sample_location_label.setText(self.__tr("Sample location"))


    def __tr(self,s,c = None):
        return qApp.translate("SampleInfoWidgetLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = SampleInfoWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
