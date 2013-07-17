# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/radiation_damage_char_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class RadiationDamageWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("RadiationDamageWidgetLayout")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.sizePolicy().hasHeightForWidth()))

        RadiationDamageWidgetLayoutLayout = QVBoxLayout(self,10,0,"RadiationDamageWidgetLayoutLayout")

        main_vlayout = QVBoxLayout(None,0,6,"main_vlayout")

        self.rad_damage_cbx = QCheckBox(self,"rad_damage_cbx")
        main_vlayout.addWidget(self.rad_damage_cbx)

        rtwo_layout = QHBoxLayout(None,0,6,"rtwo_layout")

        label_layout = QVBoxLayout(None,0,6,"label_layout")

        self.burn_osc_start_label = QLabel(self,"burn_osc_start_label")
        label_layout.addWidget(self.burn_osc_start_label)

        self.burn_osc_interval = QLabel(self,"burn_osc_interval")
        label_layout.addWidget(self.burn_osc_interval)
        rtwo_layout.addLayout(label_layout)

        ledit_layout = QVBoxLayout(None,0,6,"ledit_layout")

        self.burn_osc_start_ledit = QLineEdit(self,"burn_osc_start_ledit")
        self.burn_osc_start_ledit.setMinimumSize(QSize(50,0))
        self.burn_osc_start_ledit.setMaximumSize(QSize(50,32767))
        ledit_layout.addWidget(self.burn_osc_start_ledit)

        self.burn_osc_interval_ledit = QLineEdit(self,"burn_osc_interval_ledit")
        self.burn_osc_interval_ledit.setMinimumSize(QSize(50,0))
        self.burn_osc_interval_ledit.setMaximumSize(QSize(50,32767))
        ledit_layout.addWidget(self.burn_osc_interval_ledit)
        rtwo_layout.addLayout(ledit_layout)
        ledit_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rtwo_layout.addItem(ledit_spacer)
        main_vlayout.addLayout(rtwo_layout)
        vspacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        main_vlayout.addItem(vspacer)
        RadiationDamageWidgetLayoutLayout.addLayout(main_vlayout)

        self.languageChange()

        self.resize(QSize(313,110).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("RadiationDamageWidget"))
        self.rad_damage_cbx.setText(self.__tr("Determine radiation damage parameters"))
        self.burn_osc_start_label.setText(self.__tr("Oscillation start for burn strategy:"))
        self.burn_osc_interval.setText(self.__tr("Oscillation interval for burn:"))


    def __tr(self,s,c = None):
        return qApp.translate("RadiationDamageWidgetLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = RadiationDamageWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
