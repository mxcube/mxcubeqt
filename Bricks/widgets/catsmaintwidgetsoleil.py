# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/soleilcatsmaintwidget7.ui'
#
# Created: Tue Nov 18 18:40:05 2014
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class CatsMaintWidgetSoleil(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("CatsMaintWidgetSoleil")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))

        CatsMaintWidgetSoleilLayout = QVBoxLayout(self,11,6,"CatsMaintWidgetSoleilLayout")

        self.groupBox5 = QGroupBox(self,"groupBox5")
        self.groupBox5.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.groupBox5.sizePolicy().hasHeightForWidth()))
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QHBoxLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        self.lblPowerState = QLabel(self.groupBox5,"lblPowerState")
        self.lblPowerState.setAlignment(QLabel.AlignCenter)
        groupBox5Layout.addWidget(self.lblPowerState)

        self.btPowerOn = QPushButton(self.groupBox5,"btPowerOn")
        self.btPowerOn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btPowerOn.sizePolicy().hasHeightForWidth()))
        groupBox5Layout.addWidget(self.btPowerOn)

        self.btPowerOff = QPushButton(self.groupBox5,"btPowerOff")
        self.btPowerOff.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btPowerOff.sizePolicy().hasHeightForWidth()))
        groupBox5Layout.addWidget(self.btPowerOff)
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox5)

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
        CatsMaintWidgetSoleilLayout.addLayout(layout7)

        self.groupBox6 = QGroupBox(self,"groupBox6")
        self.groupBox6.setColumnLayout(0,Qt.Vertical)
        self.groupBox6.layout().setSpacing(6)
        self.groupBox6.layout().setMargin(11)
        groupBox6Layout = QHBoxLayout(self.groupBox6.layout())
        groupBox6Layout.setAlignment(Qt.AlignTop)

        self.lblMessage = QLabel(self.groupBox6,"lblMessage")
        groupBox6Layout.addWidget(self.lblMessage)
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox6)

        self.groupBox11 = QGroupBox(self,"groupBox11")
        self.groupBox11.setColumnLayout(0,Qt.Vertical)
        self.groupBox11.layout().setSpacing(6)
        self.groupBox11.layout().setMargin(11)
        groupBox11Layout = QHBoxLayout(self.groupBox11.layout())
        groupBox11Layout.setAlignment(Qt.AlignTop)

        self.btHome = QPushButton(self.groupBox11,"btHome")
        self.btHome.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btHome.sizePolicy().hasHeightForWidth()))
        btHome_font = QFont(self.btHome.font())
        self.btHome.setFont(btHome_font)
        groupBox11Layout.addWidget(self.btHome)

        self.btDry = QPushButton(self.groupBox11,"btDry")
        self.btDry.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btDry.sizePolicy().hasHeightForWidth()))
        btDry_font = QFont(self.btDry.font())
        self.btDry.setFont(btDry_font)
        groupBox11Layout.addWidget(self.btDry)

        self.btSoak = QPushButton(self.groupBox11,"btSoak")
        self.btSoak.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btSoak.sizePolicy().hasHeightForWidth()))
        btSoak_font = QFont(self.btSoak.font())
        self.btSoak.setFont(btSoak_font)
        groupBox11Layout.addWidget(self.btSoak)
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox11)

        self.groupBox14 = QGroupBox(self,"groupBox14")
        self.groupBox14.setColumnLayout(0,Qt.Vertical)
        self.groupBox14.layout().setSpacing(6)
        self.groupBox14.layout().setMargin(11)
        groupBox14Layout = QHBoxLayout(self.groupBox14.layout())
        groupBox14Layout.setAlignment(Qt.AlignTop)

        self.btMemoryClear = QPushButton(self.groupBox14,"btMemoryClear")
        self.btMemoryClear.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btMemoryClear.sizePolicy().hasHeightForWidth()))
        btMemoryClear_font = QFont(self.btMemoryClear.font())
        self.btMemoryClear.setFont(btMemoryClear_font)
        groupBox14Layout.addWidget(self.btMemoryClear)

        self.btToolOpen = QPushButton(self.groupBox14,"btToolOpen")
        self.btToolOpen.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btToolOpen.sizePolicy().hasHeightForWidth()))
        btToolOpen_font = QFont(self.btToolOpen.font())
        self.btToolOpen.setFont(btToolOpen_font)
        groupBox14Layout.addWidget(self.btToolOpen)

        self.btToolcal = QPushButton(self.groupBox14,"btToolcal")
        self.btToolcal.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btToolcal.sizePolicy().hasHeightForWidth()))
        btToolcal_font = QFont(self.btToolcal.font())
        self.btToolcal.setFont(btToolcal_font)
        groupBox14Layout.addWidget(self.btToolcal)
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox14)

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
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox13)

        self.groupBox5_2 = QGroupBox(self,"groupBox5_2")
        self.groupBox5_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.groupBox5_2.sizePolicy().hasHeightForWidth()))
        self.groupBox5_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox5_2.layout().setSpacing(6)
        self.groupBox5_2.layout().setMargin(11)
        groupBox5_2Layout = QHBoxLayout(self.groupBox5_2.layout())
        groupBox5_2Layout.setAlignment(Qt.AlignTop)

        self.lblRegulationState = QLabel(self.groupBox5_2,"lblRegulationState")
        self.lblRegulationState.setAlignment(QLabel.AlignCenter)
        groupBox5_2Layout.addWidget(self.lblRegulationState)

        self.btRegulationOn = QPushButton(self.groupBox5_2,"btRegulationOn")
        self.btRegulationOn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.btRegulationOn.sizePolicy().hasHeightForWidth()))
        groupBox5_2Layout.addWidget(self.btRegulationOn)
        CatsMaintWidgetSoleilLayout.addWidget(self.groupBox5_2)

        self.languageChange()

        self.resize(QSize(552,668).expandedTo(self.minimumSizeHint()))
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
        self.setTabOrder(self.btSafe,self.btHome)
        self.setTabOrder(self.btHome,self.btDry)
        self.setTabOrder(self.btDry,self.btSoak)
        self.setTabOrder(self.btSoak,self.btMemoryClear)
        self.setTabOrder(self.btMemoryClear,self.btToolOpen)
        self.setTabOrder(self.btToolOpen,self.btToolcal)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.groupBox5.setTitle(self.__tr("Arm Power"))
        self.lblPowerState.setText(self.__tr("Power"))
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
        self.groupBox6.setTitle(self.__tr("CATS message"))
        self.lblMessage.setText(self.__tr("Dummy message"))
        self.groupBox11.setTitle(self.__tr("Commands"))
        self.btHome.setText(self.__tr("Home"))
        self.btDry.setText(self.__tr("Dry"))
        self.btSoak.setText(self.__tr("Soak"))
        self.groupBox14.setTitle(QString.null)
        self.btMemoryClear.setText(self.__tr("Clear Memory"))
        self.btToolOpen.setText(self.__tr("Open Tool"))
        self.btToolcal.setText(self.__tr("Calibrate"))
        self.groupBox13.setTitle(QString.null)
        self.btResetError.setText(self.__tr("Reset Error"))
        self.btBack.setText(self.__tr("Back"))
        self.btSafe.setText(self.__tr("Safe"))
        self.groupBox5_2.setTitle(self.__tr("LN2 Regulation"))
        self.lblRegulationState.setText(self.__tr("Regulation"))
        self.btRegulationOn.setText(self.__tr("Regulation On"))


    def __tr(self,s,c = None):
        return qApp.translate("CatsMaintWidgetSoleil",s,c)
