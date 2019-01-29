# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/routine_dc_char_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class RoutineDCWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("RoutineDCWidgetLayout")

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred,
                0,
                0,
                self.sizePolicy().hasHeightForWidth(),
            )
        )

        RoutineDCWidgetLayoutLayout = QHBoxLayout(
            self, 10, 0, "RoutineDCWidgetLayoutLayout"
        )

        main_vlayout = QVBoxLayout(None, 0, 6, "main_vlayout")

        col_one_vlayout = QVBoxLayout(None, 0, 6, "col_one_vlayout")

        row_one_hlayout = QHBoxLayout(None, 0, 20, "row_one_hlayout")

        self.dose_time_bgroup = QButtonGroup(self, "dose_time_bgroup")
        self.dose_time_bgroup.setFrameShape(QButtonGroup.NoFrame)
        self.dose_time_bgroup.setMargin(0)
        self.dose_time_bgroup.setMidLineWidth(0)
        self.dose_time_bgroup.setAlignment(QButtonGroup.AlignTop)
        self.dose_time_bgroup.setFlat(0)
        self.dose_time_bgroup.setColumnLayout(0, Qt.Vertical)
        self.dose_time_bgroup.layout().setSpacing(0)
        self.dose_time_bgroup.layout().setMargin(0)
        dose_time_bgroupLayout = QVBoxLayout(self.dose_time_bgroup.layout())
        dose_time_bgroupLayout.setAlignment(Qt.AlignTop)

        bgroup_vlayout = QVBoxLayout(None, 0, 6, "bgroup_vlayout")

        self.min_dose_radio = QRadioButton(self.dose_time_bgroup, "min_dose_radio")
        bgroup_vlayout.addWidget(self.min_dose_radio)

        self.min_time_radio = QRadioButton(self.dose_time_bgroup, "min_time_radio")
        bgroup_vlayout.addWidget(self.min_time_radio)
        dose_time_bgroupLayout.addLayout(bgroup_vlayout)
        row_one_hlayout.addWidget(self.dose_time_bgroup)

        use_limit_hlayout = QHBoxLayout(None, 0, 10, "use_limit_hlayout")

        limit_label_layout = QVBoxLayout(None, 0, 6, "limit_label_layout")

        self.dose_limit_cbx = QCheckBox(self, "dose_limit_cbx")
        limit_label_layout.addWidget(self.dose_limit_cbx)

        self.time_limit_cbx = QCheckBox(self, "time_limit_cbx")
        limit_label_layout.addWidget(self.time_limit_cbx)
        use_limit_hlayout.addLayout(limit_label_layout)

        vlayout_line_edit = QVBoxLayout(None, 0, 6, "vlayout_line_edit")

        self.dose_ledit = QLineEdit(self, "dose_ledit")
        self.dose_ledit.setMinimumSize(QSize(50, 0))
        self.dose_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_line_edit.addWidget(self.dose_ledit)

        self.time_ledit = QLineEdit(self, "time_ledit")
        self.time_ledit.setMinimumSize(QSize(50, 0))
        self.time_ledit.setMaximumSize(QSize(50, 32767))
        vlayout_line_edit.addWidget(self.time_ledit)
        use_limit_hlayout.addLayout(vlayout_line_edit)
        row_one_hlayout.addLayout(use_limit_hlayout)
        col_one_vlayout.addLayout(row_one_hlayout)

        self.radiation_damage_cbx = QCheckBox(self, "radiation_damage_cbx")
        col_one_vlayout.addWidget(self.radiation_damage_cbx)
        main_vlayout.addLayout(col_one_vlayout)
        vpsacer = QSpacerItem(16, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_vlayout.addItem(vpsacer)
        RoutineDCWidgetLayoutLayout.addLayout(main_vlayout)
        hspacer = QSpacerItem(1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        RoutineDCWidgetLayoutLayout.addItem(hspacer)

        self.languageChange()

        self.resize(QSize(380, 114).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("RoutineDCWidget"))
        self.dose_time_bgroup.setTitle(QString.null)
        self.min_dose_radio.setText(self.__tr("Use min dose"))
        self.min_time_radio.setText(self.__tr("Use min time"))
        self.dose_limit_cbx.setText(self.__tr("Dose limit MGy:"))
        self.time_limit_cbx.setText(self.__tr("Total time limit (s):"))
        self.radiation_damage_cbx.setText(self.__tr("Account for radiation damage"))

    def __tr(self, s, c=None):
        return qApp.translate("RoutineDCWidgetLayout", s, c)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = RoutineDCWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
