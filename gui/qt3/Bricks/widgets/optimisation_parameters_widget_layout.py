# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/optimisation_parameters_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class OptimisationParametersWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("OptimisationParametersWidgetLayout")

        OptimisationParametersWidgetLayoutLayout = QVBoxLayout(
            self, 0, 0, "OptimisationParametersWidgetLayoutLayout"
        )

        self.gbox = QGroupBox(self, "gbox")
        self.gbox.setColumnLayout(0, Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QVBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        main_hlayout = QHBoxLayout(None, 0, 20, "main_hlayout")

        col_one_hlayout = QHBoxLayout(None, 0, 6, "col_one_hlayout")

        col_one_label_layout = QVBoxLayout(None, 0, 6, "col_one_label_layout")

        self.aimed_i_over_sigma_label = QLabel(self.gbox, "aimed_i_over_sigma_label")
        self.aimed_i_over_sigma_label.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Fixed,
                QSizePolicy.Preferred,
                0,
                0,
                self.aimed_i_over_sigma_label.sizePolicy().hasHeightForWidth(),
            )
        )
        self.aimed_i_over_sigma_label.setMinimumSize(QSize(0, 25))
        col_one_label_layout.addWidget(self.aimed_i_over_sigma_label)

        self.aimed_completeness_label = QLabel(self.gbox, "aimed_completeness_label")
        self.aimed_completeness_label.setMinimumSize(QSize(0, 25))
        col_one_label_layout.addWidget(self.aimed_completeness_label)

        self.maximum_res_cbx = QCheckBox(self.gbox, "maximum_res_cbx")
        self.maximum_res_cbx.setMinimumSize(QSize(0, 25))
        col_one_label_layout.addWidget(self.maximum_res_cbx)

        self.aimed_mult_cbx = QCheckBox(self.gbox, "aimed_mult_cbx")
        self.aimed_mult_cbx.setMinimumSize(QSize(0, 25))
        col_one_label_layout.addWidget(self.aimed_mult_cbx)
        col_one_hlayout.addLayout(col_one_label_layout)

        col_one_ledit_layout = QVBoxLayout(None, 0, 6, "col_one_ledit_layout")

        self.i_over_sigma_ledit = QLineEdit(self.gbox, "i_over_sigma_ledit")
        self.i_over_sigma_ledit.setMinimumSize(QSize(50, 25))
        self.i_over_sigma_ledit.setMaximumSize(QSize(50, 0))
        col_one_ledit_layout.addWidget(self.i_over_sigma_ledit)

        self.aimed_comp_ledit = QLineEdit(self.gbox, "aimed_comp_ledit")
        self.aimed_comp_ledit.setMinimumSize(QSize(50, 25))
        self.aimed_comp_ledit.setMaximumSize(QSize(50, 0))
        col_one_ledit_layout.addWidget(self.aimed_comp_ledit)

        self.maximum_res_ledit = QLineEdit(self.gbox, "maximum_res_ledit")
        self.maximum_res_ledit.setMinimumSize(QSize(50, 25))
        self.maximum_res_ledit.setMaximumSize(QSize(50, 0))
        col_one_ledit_layout.addWidget(self.maximum_res_ledit)

        self.aimed_mult_ledit = QLineEdit(self.gbox, "aimed_mult_ledit")
        self.aimed_mult_ledit.setMinimumSize(QSize(50, 25))
        self.aimed_mult_ledit.setMaximumSize(QSize(50, 0))
        col_one_ledit_layout.addWidget(self.aimed_mult_ledit)
        col_one_hlayout.addLayout(col_one_ledit_layout)
        main_hlayout.addLayout(col_one_hlayout)

        ctwo_hlayout = QVBoxLayout(None, 0, 6, "ctwo_hlayout")

        ctwo_rone_hlayout = QHBoxLayout(None, 0, 6, "ctwo_rone_hlayout")

        self.strat_comp_label = QLabel(self.gbox, "strat_comp_label")
        ctwo_rone_hlayout.addWidget(self.strat_comp_label)

        self.start_comp_cbox = QComboBox(0, self.gbox, "start_comp_cbox")
        ctwo_rone_hlayout.addWidget(self.start_comp_cbox)
        ctwo_hlayout.addLayout(ctwo_rone_hlayout)

        ctwo_rtwo_hlayout = QHBoxLayout(None, 0, 6, "ctwo_rtwo_hlayout")

        rotation_range_vlayout = QVBoxLayout(None, 0, 6, "rotation_range_vlayout")

        self.permitted_range_cbx = QCheckBox(self.gbox, "permitted_range_cbx")
        rotation_range_vlayout.addWidget(self.permitted_range_cbx)

        phi_main_hlayout = QHBoxLayout(None, 0, 6, "phi_main_hlayout")

        phi_hlayout = QHBoxLayout(None, 0, 6, "phi_hlayout")

        phi_label_vlayout = QVBoxLayout(None, 0, 6, "phi_label_vlayout")

        self.phi_start_label = QLabel(self.gbox, "phi_start_label")
        phi_label_vlayout.addWidget(self.phi_start_label)

        self.phi_end_label = QLabel(self.gbox, "phi_end_label")
        phi_label_vlayout.addWidget(self.phi_end_label)
        phi_hlayout.addLayout(phi_label_vlayout)

        phi_ledit_vlayout = QVBoxLayout(None, 0, 6, "phi_ledit_vlayout")

        self.phi_start_ledit = QLineEdit(self.gbox, "phi_start_ledit")
        self.phi_start_ledit.setMinimumSize(QSize(50, 25))
        self.phi_start_ledit.setMaximumSize(QSize(50, 0))
        phi_ledit_vlayout.addWidget(self.phi_start_ledit)

        self.phi_end_ledit = QLineEdit(self.gbox, "phi_end_ledit")
        self.phi_end_ledit.setMinimumSize(QSize(50, 25))
        self.phi_end_ledit.setMaximumSize(QSize(50, 0))
        phi_ledit_vlayout.addWidget(self.phi_end_ledit)
        phi_hlayout.addLayout(phi_ledit_vlayout)
        phi_main_hlayout.addLayout(phi_hlayout)
        phi_hspacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        phi_main_hlayout.addItem(phi_hspacer)
        rotation_range_vlayout.addLayout(phi_main_hlayout)
        ctwo_rtwo_hlayout.addLayout(rotation_range_vlayout)
        ctwo_hspacer = QSpacerItem(70, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        ctwo_rtwo_hlayout.addItem(ctwo_hspacer)
        ctwo_hlayout.addLayout(ctwo_rtwo_hlayout)
        main_hlayout.addLayout(ctwo_hlayout)
        gboxLayout.addLayout(main_hlayout)

        self.low_res_pass_cbx = QCheckBox(self.gbox, "low_res_pass_cbx")
        gboxLayout.addWidget(self.low_res_pass_cbx)
        OptimisationParametersWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(603, 190).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("OptimisationParametersWidget"))
        self.gbox.setTitle(self.__tr("Optimization parameters"))
        self.aimed_i_over_sigma_label.setText(
            self.__trUtf8(
                "\x41\x69\x6d\x65\x64\x20\x49\x2f\xcf\x83\x20\x61\x74\x20\x68\x69\x67\x68\x65\x73\x74\x20\x72\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x3a"
            )
        )
        self.aimed_completeness_label.setText(self.__tr("Aimed completeness:"))
        self.maximum_res_cbx.setText(self.__tr("Maximum resolution:"))
        self.aimed_mult_cbx.setText(self.__tr("Aimed multiplicity:"))
        self.strat_comp_label.setText(self.__tr("Strategy complexity:"))
        self.start_comp_cbox.clear()
        self.start_comp_cbox.insertItem(self.__tr("Single subwedge"))
        self.start_comp_cbox.insertItem(self.__tr("Few subwedges"))
        self.start_comp_cbox.insertItem(self.__tr("Many subwedges"))
        self.permitted_range_cbx.setText(self.__tr("Use permitted rotation range:"))
        self.phi_start_label.setText(
            self.__trUtf8("\xcf\x89\x2d\x73\x74\x61\x72\x74\x3a")
        )
        self.phi_end_label.setText(self.__trUtf8("\xcf\x89\x2d\x65\x6e\x64\x3a"))
        self.low_res_pass_cbx.setText(
            self.__tr("Calculate low resolution pass strategy")
        )

    def __tr(self, s, c=None):
        return qApp.translate("OptimisationParametersWidgetLayout", s, c)

    def __trUtf8(self, s, c=None):
        return qApp.translate(
            "OptimisationParametersWidgetLayout", s, c, QApplication.UnicodeUTF8
        )


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = OptimisationParametersWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
