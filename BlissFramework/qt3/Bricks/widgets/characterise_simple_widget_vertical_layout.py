# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/characterise_simple_widget_vertical_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class CharacteriseSimpleWidgetVerticalLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("CharacteriseSimpleWidgetVerticalLayout")


        CharacteriseSimpleWidgetVerticalLayoutLayout = QHBoxLayout(self,0,0,"CharacteriseSimpleWidgetVerticalLayoutLayout")

        main_vlayout = QVBoxLayout(None,0,6,"main_vlayout")

        self.characterisation_gbox = QGroupBox(self,"characterisation_gbox")
        self.characterisation_gbox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.characterisation_gbox.sizePolicy().hasHeightForWidth()))
        self.characterisation_gbox.setAcceptDrops(0)
        self.characterisation_gbox.setColumnLayout(0,Qt.Vertical)
        self.characterisation_gbox.layout().setSpacing(6)
        self.characterisation_gbox.layout().setMargin(11)
        characterisation_gboxLayout = QHBoxLayout(self.characterisation_gbox.layout())
        characterisation_gboxLayout.setAlignment(Qt.AlignTop)

        characterisation_vlayout = QVBoxLayout(None,0,6,"characterisation_vlayout")

        rone_hlayout = QHBoxLayout(None,0,6,"rone_hlayout")

        ctwo_rone_hlayout = QHBoxLayout(None,0,6,"ctwo_rone_hlayout")

        self.strat_comp_label = QLabel(self.characterisation_gbox,"strat_comp_label")
        ctwo_rone_hlayout.addWidget(self.strat_comp_label)

        self.start_comp_cbox = QComboBox(0,self.characterisation_gbox,"start_comp_cbox")
        ctwo_rone_hlayout.addWidget(self.start_comp_cbox)
        rone_hlayout.addLayout(ctwo_rone_hlayout)
        rtwo_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rone_hlayout.addItem(rtwo_spacer)
        characterisation_vlayout.addLayout(rone_hlayout)

        rwo_hlayout = QHBoxLayout(None,0,6,"rwo_hlayout")

        checkbox_layout = QVBoxLayout(None,0,6,"checkbox_layout")

        self.account_rad_dmg_cbx = QCheckBox(self.characterisation_gbox,"account_rad_dmg_cbx")
        checkbox_layout.addWidget(self.account_rad_dmg_cbx)

        self.optimised_sad_cbx = QCheckBox(self.characterisation_gbox,"optimised_sad_cbx")
        checkbox_layout.addWidget(self.optimised_sad_cbx)

        self.induced_burn_cbx = QCheckBox(self.characterisation_gbox,"induced_burn_cbx")
        checkbox_layout.addWidget(self.induced_burn_cbx)
        rwo_hlayout.addLayout(checkbox_layout)
        cone_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rwo_hlayout.addItem(cone_spacer)
        characterisation_vlayout.addLayout(rwo_hlayout)
        characterisation_gboxLayout.addLayout(characterisation_vlayout)
        main_vlayout.addWidget(self.characterisation_gbox)
        crystal_hspacer = QSpacerItem(20,0,QSizePolicy.Minimum,QSizePolicy.Expanding)
        main_vlayout.addItem(crystal_hspacer)
        CharacteriseSimpleWidgetVerticalLayoutLayout.addLayout(main_vlayout)

        self.languageChange()

        self.resize(QSize(324,158).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("CharacteriseWidgetVerticalSimple"))
        self.characterisation_gbox.setTitle(self.__tr("Characterisation"))
        self.strat_comp_label.setText(self.__tr("Strategy complexity:"))
        self.start_comp_cbox.clear()
        self.start_comp_cbox.insertItem(self.__tr("Single subwedge"))
        self.start_comp_cbox.insertItem(self.__tr("Few subwedges"))
        self.start_comp_cbox.insertItem(self.__tr("Many subwedges"))
        self.account_rad_dmg_cbx.setText(self.__tr("Account for radiation damage"))
        self.optimised_sad_cbx.setText(self.__tr("Optimised SAD"))
        self.induced_burn_cbx.setText(self.__tr("Induced burn"))


    def __tr(self,s,c = None):
        return qApp.translate("CharacteriseSimpleWidgetVerticalLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = CharacteriseSimpleWidgetVerticalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
