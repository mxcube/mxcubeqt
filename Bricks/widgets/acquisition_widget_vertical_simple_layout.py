# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/acquisition_widget_vertical_simple_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class AcquisitionWidgetVerticalSimpleLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("AcquisitionWidgetVerticalSimpleLayout")


        AcquisitionWidgetVerticalSimpleLayoutLayout = QVBoxLayout(self,0,0,"AcquisitionWidgetVerticalSimpleLayoutLayout")

        self.acq_gbox = QGroupBox(self,"acq_gbox")
        self.acq_gbox.setColumnLayout(0,Qt.Vertical)
        self.acq_gbox.layout().setSpacing(6)
        self.acq_gbox.layout().setMargin(11)
        acq_gboxLayout = QHBoxLayout(self.acq_gbox.layout())
        acq_gboxLayout.setAlignment(Qt.AlignTop)

        col_one_vlayout = QVBoxLayout(None,0,6,"col_one_vlayout")

        self.num_images_label = QLabel(self.acq_gbox,"num_images_label")
        col_one_vlayout.addWidget(self.num_images_label)

        self.exp_time_label = QLabel(self.acq_gbox,"exp_time_label")
        col_one_vlayout.addWidget(self.exp_time_label)

        self.osc_range_label = QLabel(self.acq_gbox,"osc_range_label")
        col_one_vlayout.addWidget(self.osc_range_label)
        acq_gboxLayout.addLayout(col_one_vlayout)

        col_two_vlayout = QVBoxLayout(None,0,6,"col_two_vlayout")

        self.num_images_cbox = QComboBox(0,self.acq_gbox,"num_images_cbox")
        col_two_vlayout.addWidget(self.num_images_cbox)

        self.exp_time_ledit = QLineEdit(self.acq_gbox,"exp_time_ledit")
        self.exp_time_ledit.setMinimumSize(QSize(50,0))
        self.exp_time_ledit.setMaximumSize(QSize(50,32767))
        col_two_vlayout.addWidget(self.exp_time_ledit)

        self.osc_range_ledit = QLineEdit(self.acq_gbox,"osc_range_ledit")
        self.osc_range_ledit.setMinimumSize(QSize(50,0))
        self.osc_range_ledit.setMaximumSize(QSize(50,32767))
        col_two_vlayout.addWidget(self.osc_range_ledit)
        acq_gboxLayout.addLayout(col_two_vlayout)
        acq_box_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        acq_gboxLayout.addItem(acq_box_spacer)
        AcquisitionWidgetVerticalSimpleLayoutLayout.addWidget(self.acq_gbox)
        vspacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AcquisitionWidgetVerticalSimpleLayoutLayout.addItem(vspacer)

        self.languageChange()

        self.resize(QSize(257,117).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("AcquisitionWidgetVerticalSimple"))
        self.acq_gbox.setTitle(self.__tr("Acquisition"))
        self.num_images_label.setText(self.__tr("Number of images:"))
        self.exp_time_label.setText(self.__tr("Exposure time:"))
        self.osc_range_label.setText(self.__tr("Oscillation range:"))
        self.num_images_cbox.clear()
        self.num_images_cbox.insertItem(self.__tr("1 Image"))
        self.num_images_cbox.insertItem(self.__tr("2 Images"))
        self.num_images_cbox.insertItem(self.__tr("4 Images"))


    def __tr(self,s,c = None):
        return qApp.translate("AcquisitionWidgetVerticalSimpleLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = AcquisitionWidgetVerticalSimpleLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
