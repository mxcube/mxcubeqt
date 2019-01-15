# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/diffraction_plan_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class DiffractionPlanWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("DiffractionPlanWidgetLayout")

        DiffractionPlanWidgetLayoutLayout = QHBoxLayout(
            self, 11, 6, "DiffractionPlanWidgetLayoutLayout"
        )

        self.diffraction_plan_gb = QGroupBox(self, "diffraction_plan_gb")
        self.diffraction_plan_gb.setColumnLayout(0, Qt.Vertical)
        self.diffraction_plan_gb.layout().setSpacing(6)
        self.diffraction_plan_gb.layout().setMargin(11)
        diffraction_plan_gbLayout = QHBoxLayout(self.diffraction_plan_gb.layout())
        diffraction_plan_gbLayout.setAlignment(Qt.AlignTop)

        rone_hlayout = QHBoxLayout(None, 0, 20, "rone_hlayout")

        left_col_hlayout = QHBoxLayout(None, 0, 6, "left_col_hlayout")

        col_one_vlayout = QVBoxLayout(None, 0, 6, "col_one_vlayout")

        self.space_group_label = QLabel(self.diffraction_plan_gb, "space_group_label")
        col_one_vlayout.addWidget(self.space_group_label)

        self.exp_time_label = QLabel(self.diffraction_plan_gb, "exp_time_label")
        col_one_vlayout.addWidget(self.exp_time_label)

        self.max_exp_time_label = QLabel(self.diffraction_plan_gb, "max_exp_time_label")
        col_one_vlayout.addWidget(self.max_exp_time_label)

        self.osc_range_label = QLabel(self.diffraction_plan_gb, "osc_range_label")
        col_one_vlayout.addWidget(self.osc_range_label)

        self.aimed_res_label = QLabel(self.diffraction_plan_gb, "aimed_res_label")
        col_one_vlayout.addWidget(self.aimed_res_label)
        left_col_hlayout.addLayout(col_one_vlayout)

        col_two_vlayout = QVBoxLayout(None, 0, 6, "col_two_vlayout")

        self.space_group_ledit = QLineEdit(
            self.diffraction_plan_gb, "space_group_ledit"
        )
        self.space_group_ledit.setMinimumSize(QSize(50, 19))
        self.space_group_ledit.setMaximumSize(QSize(50, 32767))
        col_two_vlayout.addWidget(self.space_group_ledit)

        self.exp_time_ledit = QLineEdit(self.diffraction_plan_gb, "exp_time_ledit")
        self.exp_time_ledit.setMinimumSize(QSize(50, 19))
        self.exp_time_ledit.setMaximumSize(QSize(50, 32767))
        col_two_vlayout.addWidget(self.exp_time_ledit)

        self.max_exp_time_ledit = QLineEdit(
            self.diffraction_plan_gb, "max_exp_time_ledit"
        )
        self.max_exp_time_ledit.setMinimumSize(QSize(50, 19))
        self.max_exp_time_ledit.setMaximumSize(QSize(50, 32767))
        col_two_vlayout.addWidget(self.max_exp_time_ledit)

        self.osc_rage_ledit = QLineEdit(self.diffraction_plan_gb, "osc_rage_ledit")
        self.osc_rage_ledit.setMinimumSize(QSize(50, 19))
        self.osc_rage_ledit.setMaximumSize(QSize(50, 32767))
        col_two_vlayout.addWidget(self.osc_rage_ledit)

        self.aimed_res_ledit = QLineEdit(self.diffraction_plan_gb, "aimed_res_ledit")
        self.aimed_res_ledit.setMinimumSize(QSize(50, 19))
        self.aimed_res_ledit.setMaximumSize(QSize(50, 32767))
        col_two_vlayout.addWidget(self.aimed_res_ledit)
        left_col_hlayout.addLayout(col_two_vlayout)
        rone_hlayout.addLayout(left_col_hlayout)

        right_hlayout = QVBoxLayout(None, 0, 6, "right_hlayout")

        right_top_hlayout = QHBoxLayout(None, 0, 6, "right_top_hlayout")

        col_thee_vlayout = QVBoxLayout(None, 0, 6, "col_thee_vlayout")

        self.aimed_mult_label = QLabel(self.diffraction_plan_gb, "aimed_mult_label")
        col_thee_vlayout.addWidget(self.aimed_mult_label)

        self.aimed_ios_label = QLabel(self.diffraction_plan_gb, "aimed_ios_label")
        col_thee_vlayout.addWidget(self.aimed_ios_label)

        self.aimed_comp_label = QLabel(self.diffraction_plan_gb, "aimed_comp_label")
        col_thee_vlayout.addWidget(self.aimed_comp_label)

        self.complexity_label = QLabel(self.diffraction_plan_gb, "complexity_label")
        col_thee_vlayout.addWidget(self.complexity_label)
        right_top_hlayout.addLayout(col_thee_vlayout)

        col_four_vlayout = QVBoxLayout(None, 0, 6, "col_four_vlayout")

        self.aimed_mult_ledit = QLineEdit(self.diffraction_plan_gb, "aimed_mult_ledit")
        self.aimed_mult_ledit.setMinimumSize(QSize(50, 19))
        self.aimed_mult_ledit.setMaximumSize(QSize(50, 32767))
        col_four_vlayout.addWidget(self.aimed_mult_ledit)

        self.aimed_ios_ledit = QLineEdit(self.diffraction_plan_gb, "aimed_ios_ledit")
        self.aimed_ios_ledit.setMinimumSize(QSize(50, 0))
        self.aimed_ios_ledit.setMaximumSize(QSize(50, 32767))
        col_four_vlayout.addWidget(self.aimed_ios_ledit)

        self.aimed_com_ledit = QLineEdit(self.diffraction_plan_gb, "aimed_com_ledit")
        self.aimed_com_ledit.setMinimumSize(QSize(50, 19))
        self.aimed_com_ledit.setMaximumSize(QSize(50, 32767))
        col_four_vlayout.addWidget(self.aimed_com_ledit)

        self.complexity_ledit = QComboBox(
            0, self.diffraction_plan_gb, "complexity_ledit"
        )
        col_four_vlayout.addWidget(self.complexity_ledit)
        right_top_hlayout.addLayout(col_four_vlayout)
        right_hlayout.addLayout(right_top_hlayout)

        self.burn_strat_cbx = QCheckBox(self.diffraction_plan_gb, "burn_strat_cbx")
        right_hlayout.addWidget(self.burn_strat_cbx)
        rone_hlayout.addLayout(right_hlayout)
        diffraction_plan_gbLayout.addLayout(rone_hlayout)
        DiffractionPlanWidgetLayoutLayout.addWidget(self.diffraction_plan_gb)

        self.languageChange()

        self.resize(QSize(853, 196).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("Diffraction plan"))
        self.diffraction_plan_gb.setTitle(self.__tr("Diffraction plan"))
        self.space_group_label.setText(self.__tr("Force space group:"))
        self.exp_time_label.setText(self.__tr("Expousre time:"))
        self.max_exp_time_label.setText(self.__tr("Maximum exposure time:"))
        self.osc_range_label.setText(self.__tr("Oscillation range:"))
        self.aimed_res_label.setText(
            self.__tr("Aimed resolution (default - highest possible):")
        )
        self.aimed_mult_label.setText(
            self.__tr("Aimed multiplicity (default - optimized):")
        )
        self.aimed_ios_label.setText(
            self.__tr("Aimed I over Sigma at highest resolution:")
        )
        self.aimed_comp_label.setText(
            self.__tr("Aimed completeness (default >= 0.99):")
        )
        self.complexity_label.setText(self.__tr("Strategy complexity:"))
        self.complexity_ledit.clear()
        self.complexity_ledit.insertItem(self.__tr("Not used"))
        self.complexity_ledit.insertItem(self.__tr("Single subwedge"))
        self.complexity_ledit.insertItem(self.__tr("Few subwedges"))
        self.complexity_ledit.insertItem(self.__tr("Many subwedges"))
        self.burn_strat_cbx.setText(self.__tr("Induce burn strategy"))

    def __tr(self, s, c=None):
        return qApp.translate("DiffractionPlanWidgetLayout", s, c)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = DiffractionPlanWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
