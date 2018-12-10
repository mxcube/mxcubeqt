# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgets/ui_files/catswidget.ui'
#
# Created: Wed Jan 22 15:18:50 2014
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class CatsWidget(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("CatsWidget")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))

        CatsWidgetLayout = QVBoxLayout(self,11,6,"CatsWidgetLayout")

        layout14 = QVBoxLayout(None,0,6,"layout14")

        self.lvSC = QListView(self,"lvSC")
        self.lvSC.addColumn(self.__tr("Column 1"))
        lvSC_font = QFont(self.lvSC.font())
        lvSC_font.setPointSize(9)
        self.lvSC.setFont(lvSC_font)
        layout14.addWidget(self.lvSC)

        self.ckShowEmptySlots = QCheckBox(self,"ckShowEmptySlots")
        ckShowEmptySlots_font = QFont(self.ckShowEmptySlots.font())
        self.ckShowEmptySlots.setFont(ckShowEmptySlots_font)
        layout14.addWidget(self.ckShowEmptySlots)

        layout13 = QVBoxLayout(None,0,6,"layout13")
        spacer3_2 = QSpacerItem(21,6,QSizePolicy.Minimum,QSizePolicy.Fixed)
        layout13.addItem(spacer3_2)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.btLoadSample = QPushButton(self,"btLoadSample")
        btLoadSample_font = QFont(self.btLoadSample.font())
        self.btLoadSample.setFont(btLoadSample_font)
        layout8.addWidget(self.btLoadSample)

        self.btUnloadSample = QPushButton(self,"btUnloadSample")
        btUnloadSample_font = QFont(self.btUnloadSample.font())
        self.btUnloadSample.setFont(btUnloadSample_font)
        layout8.addWidget(self.btUnloadSample)
        layout13.addLayout(layout8)

        layout11 = QHBoxLayout(None,0,6,"layout11")
        layout13.addLayout(layout11)

        self.btAbort = QPushButton(self,"btAbort")
        btAbort_font = QFont(self.btAbort.font())
        self.btAbort.setFont(btAbort_font)
        layout13.addWidget(self.btAbort)
        spacer3 = QSpacerItem(21,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        layout13.addItem(spacer3)

        layout13_2 = QHBoxLayout(None,0,6,"layout13_2")

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        layout13_2.addWidget(self.textLabel1)

        self.txtState = QLineEdit(self,"txtState")
        self.txtState.setEnabled(1)
        self.txtState.setPaletteBackgroundColor(QColor(192,192,192))
        txtState_font = QFont(self.txtState.font())
        self.txtState.setFont(txtState_font)
        self.txtState.setAlignment(QLineEdit.AlignHCenter)
        self.txtState.setReadOnly(1)
        layout13_2.addWidget(self.txtState)
        layout13.addLayout(layout13_2)
        layout14.addLayout(layout13)
        CatsWidgetLayout.addLayout(layout14)

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
        self.btAbort.setText(self.__tr("Abort"))
        self.textLabel1.setText(self.__tr("State:"))


    def __tr(self,s,c = None):
        return qApp.translate("CatsWidget",s,c)
