# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Bricks/widgets/ui_files/scwidget.ui'
#
# Created: Mon Sep 2 11:54:00 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class SCWidget(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("SCWidget")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))


        LayoutWidget = QWidget(self,"layout14")
        LayoutWidget.setGeometry(QRect(0,0,370,850))
        layout14 = QVBoxLayout(LayoutWidget,11,6,"layout14")

        self.lvSC = QListView(LayoutWidget,"lvSC")
        self.lvSC.addColumn(self.__tr("Column 1"))
        lvSC_font = QFont(self.lvSC.font())
        lvSC_font.setPointSize(9)
        self.lvSC.setFont(lvSC_font)
        layout14.addWidget(self.lvSC)

        self.ckShowEmptySlots = QCheckBox(LayoutWidget,"ckShowEmptySlots")
        ckShowEmptySlots_font = QFont(self.ckShowEmptySlots.font())
        ckShowEmptySlots_font.setPointSize(10)
        self.ckShowEmptySlots.setFont(ckShowEmptySlots_font)
        layout14.addWidget(self.ckShowEmptySlots)

        layout19 = QHBoxLayout(None,0,6,"layout19")
        spacer1 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout19.addItem(spacer1)

        self.lbImage = QLabel(LayoutWidget,"lbImage")
        self.lbImage.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.lbImage.sizePolicy().hasHeightForWidth()))
        self.lbImage.setMinimumSize(QSize(320,240))
        self.lbImage.setMaximumSize(QSize(320,240))
        self.lbImage.setFrameShape(QLabel.Box)
        self.lbImage.setFrameShadow(QLabel.Plain)
        self.lbImage.setMargin(0)
        self.lbImage.setMidLineWidth(0)
        self.lbImage.setScaledContents(1)
        self.lbImage.setAlignment(QLabel.AlignTop | QLabel.AlignLeft)
        layout19.addWidget(self.lbImage)
        spacer1_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout19.addItem(spacer1_2)
        layout14.addLayout(layout19)

        layout13 = QVBoxLayout(None,0,6,"layout13")
        spacer3_2 = QSpacerItem(21,6,QSizePolicy.Minimum,QSizePolicy.Fixed)
        layout13.addItem(spacer3_2)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.btLoadSample = QPushButton(LayoutWidget,"btLoadSample")
        btLoadSample_font = QFont(self.btLoadSample.font())
        btLoadSample_font.setPointSize(10)
        self.btLoadSample.setFont(btLoadSample_font)
        layout8.addWidget(self.btLoadSample)

        self.btUnloadSample = QPushButton(LayoutWidget,"btUnloadSample")
        btUnloadSample_font = QFont(self.btUnloadSample.font())
        btUnloadSample_font.setPointSize(10)
        self.btUnloadSample.setFont(btUnloadSample_font)
        layout8.addWidget(self.btUnloadSample)
        layout13.addLayout(layout8)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.btOperMode = QPushButton(LayoutWidget,"btOperMode")
        btOperMode_font = QFont(self.btOperMode.font())
        btOperMode_font.setPointSize(10)
        self.btOperMode.setFont(btOperMode_font)
        layout11.addWidget(self.btOperMode)

        self.btChargeMode = QPushButton(LayoutWidget,"btChargeMode")
        btChargeMode_font = QFont(self.btChargeMode.font())
        btChargeMode_font.setPointSize(10)
        self.btChargeMode.setFont(btChargeMode_font)
        layout11.addWidget(self.btChargeMode)
        layout13.addLayout(layout11)

        self.btAbort = QPushButton(LayoutWidget,"btAbort")
        btAbort_font = QFont(self.btAbort.font())
        btAbort_font.setPointSize(10)
        self.btAbort.setFont(btAbort_font)
        layout13.addWidget(self.btAbort)
        spacer3 = QSpacerItem(21,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        layout13.addItem(spacer3)

        layout13_2 = QHBoxLayout(None,0,6,"layout13_2")

        self.textLabel1 = QLabel(LayoutWidget,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        textLabel1_font.setPointSize(10)
        self.textLabel1.setFont(textLabel1_font)
        layout13_2.addWidget(self.textLabel1)

        self.txtState = QLineEdit(LayoutWidget,"txtState")
        self.txtState.setEnabled(1)
        self.txtState.setPaletteBackgroundColor(QColor(192,192,192))
        txtState_font = QFont(self.txtState.font())
        txtState_font.setPointSize(10)
        self.txtState.setFont(txtState_font)
        self.txtState.setAlignment(QLineEdit.AlignHCenter)
        self.txtState.setReadOnly(1)
        layout13_2.addWidget(self.txtState)
        layout13.addLayout(layout13_2)
        layout14.addLayout(layout13)

        self.languageChange()

        self.resize(QSize(370,859).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.lvSC.header().setLabel(0,self.__tr("Column 1"))
        self.lvSC.clear()
        item = QListViewItem(self.lvSC,None)
        item.setText(0,self.__tr("New Item"))

        self.ckShowEmptySlots.setText(self.__tr("Show empty slots"))
        self.btLoadSample.setText(self.__tr("Load"))
        self.btUnloadSample.setText(self.__tr("Unload"))
        self.btOperMode.setText(self.__tr("Operating Mode"))
        self.btChargeMode.setText(self.__tr("Charging Mode"))
        self.btAbort.setText(self.__tr("Abort"))
        self.textLabel1.setText(self.__tr("State:"))


    def __tr(self,s,c = None):
        return qApp.translate("SCWidget",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = SCWidget()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
