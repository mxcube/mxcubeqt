# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/collect_progress_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class CollectProgressWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("CollectProgressWidgetLayout")

        CollectProgressWidgetLayoutLayout = QHBoxLayout(
            self, 0, 6, "CollectProgressWidgetLayoutLayout"
        )

        vlayout = QVBoxLayout(None, 0, 6, "vlayout")

        self.progress_bar = QProgressBar(self, "progress_bar")
        self.progress_bar.setProgress(0)
        self.progress_bar.setIndicatorFollowsStyle(0)
        self.progress_bar.setPercentageVisible(1)
        vlayout.addWidget(self.progress_bar)

        row_one_halyout = QHBoxLayout(None, 0, 6, "row_one_halyout")

        col_one_hlayout = QHBoxLayout(None, 0, 5, "col_one_hlayout")

        self.elapsed_time_label = QLabel(self, "elapsed_time_label")
        col_one_hlayout.addWidget(self.elapsed_time_label)

        self.elapsed_time_value = QLabel(self, "elapsed_time_value")
        col_one_hlayout.addWidget(self.elapsed_time_value)
        row_one_halyout.addLayout(col_one_hlayout)
        hspacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        row_one_halyout.addItem(hspacer)

        col_two_hlayout = QHBoxLayout(None, 0, 5, "col_two_hlayout")

        self.est_time_label = QLabel(self, "est_time_label")
        self.est_time_label.setEnabled(1)
        col_two_hlayout.addWidget(self.est_time_label)

        self.est_time_value = QLabel(self, "est_time_value")
        col_two_hlayout.addWidget(self.est_time_value)
        row_one_halyout.addLayout(col_two_hlayout)
        vlayout.addLayout(row_one_halyout)
        CollectProgressWidgetLayoutLayout.addLayout(vlayout)

        self.languageChange()

        self.resize(QSize(338, 57).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("Progress bar"))
        self.elapsed_time_label.setText(self.__tr("Elapsed time:"))
        self.elapsed_time_value.setText(self.__tr("<time>"))
        self.est_time_label.setText(self.__tr("Estimated time:"))
        self.est_time_value.setText(self.__tr("<time>"))

    def __tr(self, s, c=None):
        return qApp.translate("CollectProgressWidgetLayout", s, c)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = CollectProgressWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
