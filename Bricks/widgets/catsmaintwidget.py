# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/catsmaintwidget.ui'
#
# Created: Thu Jan 30 15:00:32 2014
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class CatsMaintWidget(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("CatsMaintWidget")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))

        CatsMaintWidgetLayout = QVBoxLayout(self,11,6,"CatsMaintWidgetLayout")

        self.groupBox5 = QGroupBox(self,"groupBox5")
        self.groupBox5.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.groupBox5.sizePolicy().hasHeightForWidth()))
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QHBoxLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        self.btPowerOn = QPushButton(self.groupBox5,"btPowerOn")
        self.btPowerOn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btPowerOn.sizePolicy().hasHeightForWidth()))
        groupBox5Layout.addWidget(self.btPowerOn)

        self.btPowerOff = QPushButton(self.groupBox5,"btPowerOff")
        self.btPowerOff.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btPowerOff.sizePolicy().hasHeightForWidth()))
        groupBox5Layout.addWidget(self.btPowerOff)
        CatsMaintWidgetLayout.addWidget(self.groupBox5)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QVBoxLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        self.btLid1Open = QPushButton(self.groupBox2,"btLid1Open")
        btLid1Open_font = QFont(self.btLid1Open.font())
        self.btLid1Open.setFont(btLid1Open_font)
        groupBox2Layout.addWidget(self.btLid1Open)

        self.btLid1Close = QPushButton(self.groupBox2,"btLid1Close")
        btLid1Close_font = QFont(self.btLid1Close.font())
        self.btLid1Close.setFont(btLid1Close_font)
        groupBox2Layout.addWidget(self.btLid1Close)
        layout7.addWidget(self.groupBox2)

        self.groupBox2_2 = QGroupBox(self,"groupBox2_2")
        self.groupBox2_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2_2.layout().setSpacing(6)
        self.groupBox2_2.layout().setMargin(11)
        groupBox2_2Layout = QVBoxLayout(self.groupBox2_2.layout())
        groupBox2_2Layout.setAlignment(Qt.AlignTop)

        self.btLid2Open = QPushButton(self.groupBox2_2,"btLid2Open")
        btLid2Open_font = QFont(self.btLid2Open.font())
        self.btLid2Open.setFont(btLid2Open_font)
        groupBox2_2Layout.addWidget(self.btLid2Open)

        self.btLid2Close = QPushButton(self.groupBox2_2,"btLid2Close")
        btLid2Close_font = QFont(self.btLid2Close.font())
        self.btLid2Close.setFont(btLid2Close_font)
        groupBox2_2Layout.addWidget(self.btLid2Close)
        layout7.addWidget(self.groupBox2_2)

        self.groupBox2_2_2 = QGroupBox(self,"groupBox2_2_2")
        self.groupBox2_2_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2_2_2.layout().setSpacing(6)
        self.groupBox2_2_2.layout().setMargin(11)
        groupBox2_2_2Layout = QVBoxLayout(self.groupBox2_2_2.layout())
        groupBox2_2_2Layout.setAlignment(Qt.AlignTop)

        self.btLid3Open = QPushButton(self.groupBox2_2_2,"btLid3Open")
        btLid3Open_font = QFont(self.btLid3Open.font())
        self.btLid3Open.setFont(btLid3Open_font)
        groupBox2_2_2Layout.addWidget(self.btLid3Open)

        self.btLid3Close = QPushButton(self.groupBox2_2_2,"btLid3Close")
        btLid3Close_font = QFont(self.btLid3Close.font())
        self.btLid3Close.setFont(btLid3Close_font)
        groupBox2_2_2Layout.addWidget(self.btLid3Close)
        layout7.addWidget(self.groupBox2_2_2)
        CatsMaintWidgetLayout.addLayout(layout7)

        self.groupBox13 = QGroupBox(self,"groupBox13")
        self.groupBox13.setColumnLayout(0,Qt.Vertical)
        self.groupBox13.layout().setSpacing(6)
        self.groupBox13.layout().setMargin(11)
        groupBox13Layout = QHBoxLayout(self.groupBox13.layout())
        groupBox13Layout.setAlignment(Qt.AlignTop)

        self.btResetError = QPushButton(self.groupBox13,"btResetError")
        self.btResetError.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btResetError.sizePolicy().hasHeightForWidth()))
        btResetError_font = QFont(self.btResetError.font())
        self.btResetError.setFont(btResetError_font)
        groupBox13Layout.addWidget(self.btResetError)

        self.btBack = QPushButton(self.groupBox13,"btBack")
        self.btBack.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btBack.sizePolicy().hasHeightForWidth()))
        btBack_font = QFont(self.btBack.font())
        self.btBack.setFont(btBack_font)
        groupBox13Layout.addWidget(self.btBack)

        self.btSafe = QPushButton(self.groupBox13,"btSafe")
        self.btSafe.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btSafe.sizePolicy().hasHeightForWidth()))
        btSafe_font = QFont(self.btSafe.font())
        self.btSafe.setFont(btSafe_font)
        groupBox13Layout.addWidget(self.btSafe)
        CatsMaintWidgetLayout.addWidget(self.groupBox13)

        self.languageChange()

        self.resize(QSize(878,408).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.setTabOrder(self.btPowerOn,self.btPowerOff)
        self.setTabOrder(self.btPowerOff,self.btLid1Open)
        self.setTabOrder(self.btLid1Open,self.btLid1Close)
        self.setTabOrder(self.btLid1Close,self.btLid2Open)
        self.setTabOrder(self.btLid2Open,self.btLid2Close)
        self.setTabOrder(self.btLid2Close,self.btLid3Open)
        self.setTabOrder(self.btLid3Open,self.btLid3Close)
        self.setTabOrder(self.btLid3Close,self.btResetError)
        self.setTabOrder(self.btResetError,self.btBack)
        self.setTabOrder(self.btBack,self.btSafe)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.groupBox5.setTitle(self.__tr("Arm Power"))
        self.btPowerOn.setText(self.__tr("Power On"))
        self.btPowerOff.setText(self.__tr("Power Off"))
        self.groupBox2.setTitle(self.__tr("Lid 1"))
        self.btLid1Open.setText(self.__tr("Open"))
        self.btLid1Close.setText(self.__tr("Close"))
        self.groupBox2_2.setTitle(self.__tr("Lid 2"))
        self.btLid2Open.setText(self.__tr("Open"))
        self.btLid2Close.setText(self.__tr("Close"))
        self.groupBox2_2_2.setTitle(self.__tr("Lid 3"))
        self.btLid3Open.setText(self.__tr("Open"))
        self.btLid3Close.setText(self.__tr("Close"))
        self.groupBox13.setTitle(self.__tr("Recovery Commands"))
        self.btResetError.setText(self.__tr("Reset Error"))
        self.btBack.setText(self.__tr("Back"))
        self.btSafe.setText(self.__tr("Safe"))


    def __tr(self,s,c = None):
        return qApp.translate("CatsMaintWidget",s,c)
