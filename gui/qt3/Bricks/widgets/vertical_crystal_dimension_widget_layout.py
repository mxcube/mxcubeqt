# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/vertical_crystal_dimension_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class VerticalCrystalDimensionWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("VerticalCrystalDimensionWidgetLayout")

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.MinimumExpanding,
                QSizePolicy.MinimumExpanding,
                0,
                0,
                self.sizePolicy().hasHeightForWidth(),
            )
        )

        VerticalCrystalDimensionWidgetLayoutLayout = QVBoxLayout(
            self, 0, 6, "VerticalCrystalDimensionWidgetLayoutLayout"
        )

        self.gbox = QGroupBox(self, "gbox")
        self.gbox.setSizePolicy(
            QSizePolicy(
                QSizePolicy.MinimumExpanding,
                QSizePolicy.MinimumExpanding,
                0,
                0,
                self.gbox.sizePolicy().hasHeightForWidth(),
            )
        )
        self.gbox.setChecked(0)
        self.gbox.setColumnLayout(0, Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QHBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        main_layout = QVBoxLayout(None, 0, 15, "main_layout")

        space_group_layout = QHBoxLayout(None, 0, 6, "space_group_layout")

        space_group_ledit_layout = QHBoxLayout(None, 0, 6, "space_group_ledit_layout")

        self.space_group_label = QLabel(self.gbox, "space_group_label")
        space_group_ledit_layout.addWidget(self.space_group_label)

        self.space_group_ledit = QComboBox(0, self.gbox, "space_group_ledit")
        self.space_group_ledit.setMinimumSize(QSize(100, 0))
        self.space_group_ledit.setMaximumSize(QSize(100, 32767))
        space_group_ledit_layout.addWidget(self.space_group_ledit)
        space_group_layout.addLayout(space_group_ledit_layout)
        space_group_hspacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        space_group_layout.addItem(space_group_hspacer)
        main_layout.addLayout(space_group_layout)

        vdim_layout = QVBoxLayout(None, 0, 2, "vdim_layout")

        vdim_heading_layout = QHBoxLayout(None, 0, 6, "vdim_heading_layout")

        self.dimension_label = QLabel(self.gbox, "dimension_label")
        vdim_heading_layout.addWidget(self.dimension_label)
        vdim_heading_spacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        vdim_heading_layout.addItem(vdim_heading_spacer)
        vdim_layout.addLayout(vdim_heading_layout)

        vdim_control_layout = QHBoxLayout(None, 0, 0, "vdim_control_layout")

        vdim_ledit_hlayout = QHBoxLayout(None, 0, 20, "vdim_ledit_hlayout")

        col_one_vdim_ledit_hlayout = QHBoxLayout(
            None, 0, 6, "col_one_vdim_ledit_hlayout"
        )

        vlayout_min_vdim_label = QVBoxLayout(None, 0, 6, "vlayout_min_vdim_label")

        self.min_vdim_label = QLabel(self.gbox, "min_vdim_label")
        vlayout_min_vdim_label.addWidget(self.min_vdim_label)

        self.vdim_min_phi_label = QLabel(self.gbox, "vdim_min_phi_label")
        vlayout_min_vdim_label.addWidget(self.vdim_min_phi_label)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_label)

        vlayout_min_vdim_ledit = QVBoxLayout(None, 0, 6, "vlayout_min_vdim_ledit")

        self.min_vdim_ledit = QLineEdit(self.gbox, "min_vdim_ledit")
        self.min_vdim_ledit.setMinimumSize(QSize(50, 0))
        self.min_vdim_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vdim_ledit)

        self.min_vphi_ledit = QLineEdit(self.gbox, "min_vphi_ledit")
        self.min_vphi_ledit.setMinimumSize(QSize(50, 0))
        self.min_vphi_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vphi_ledit)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_one_vdim_ledit_hlayout)

        col_two_vdim_ledit_hlayout = QHBoxLayout(
            None, 0, 6, "col_two_vdim_ledit_hlayout"
        )

        vlayout_two_vdim_hlayout = QVBoxLayout(None, 0, 6, "vlayout_two_vdim_hlayout")

        self.max_vdim_label = QLabel(self.gbox, "max_vdim_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vdim_label)

        self.max_vphi_label = QLabel(self.gbox, "max_vphi_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vphi_label)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_two_vdim_hlayout)

        vlayout_max_vdim_ledit = QVBoxLayout(None, 0, 6, "vlayout_max_vdim_ledit")

        self.max_vdim_ledit = QLineEdit(self.gbox, "max_vdim_ledit")
        self.max_vdim_ledit.setMinimumSize(QSize(50, 0))
        self.max_vdim_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vdim_ledit)

        self.max_vphi_ledit = QLineEdit(self.gbox, "max_vphi_ledit")
        self.max_vphi_ledit.setMinimumSize(QSize(50, 0))
        self.max_vphi_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vphi_ledit)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_max_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_two_vdim_ledit_hlayout)
        vdim_control_layout.addLayout(vdim_ledit_hlayout)
        vspacer = QSpacerItem(1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vdim_control_layout.addItem(vspacer)
        vdim_layout.addLayout(vdim_control_layout)
        main_layout.addLayout(vdim_layout)
        gboxLayout.addLayout(main_layout)
        VerticalCrystalDimensionWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(307, 163).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("VerticalCrystalDimensionWidget"))
        self.gbox.setTitle(self.__tr("Crystal"))
        self.space_group_label.setText(self.__tr("Space group:"))
        self.dimension_label.setText(self.__tr("Vertical crystal dimension (mm):"))
        self.min_vdim_label.setText(self.__tr("Min:"))
        self.vdim_min_phi_label.setText(
            self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x69\x6e\x3a")
        )
        self.max_vdim_label.setText(self.__tr("Max:"))
        self.max_vphi_label.setText(
            self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x61\x78\x3a")
        )

    def __tr(self, s, c=None):
        return qApp.translate("VerticalCrystalDimensionWidgetLayout", s, c)

    def __trUtf8(self, s, c=None):
        return qApp.translate(
            "VerticalCrystalDimensionWidgetLayout", s, c, QApplication.UnicodeUTF8
        )


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = VerticalCrystalDimensionWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
