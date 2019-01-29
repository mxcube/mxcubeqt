# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/data_path_widget_vertical_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class DataPathWidgetVerticalLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("DataPathWidgetVerticalLayout")

        DataPathWidgetVerticalLayoutLayout = QHBoxLayout(
            self, 0, 0, "DataPathWidgetVerticalLayoutLayout"
        )

        main_layout = QVBoxLayout(None, 0, 6, "main_layout")

        rone_layout = QHBoxLayout(None, 0, 6, "rone_layout")

        rone_cone_vlayout = QVBoxLayout(None, 0, 30, "rone_cone_vlayout")

        self.folder_label = QLabel(self, "folder_label")
        self.folder_label.setMaximumSize(QSize(32767, 32767))
        rone_cone_vlayout.addWidget(self.folder_label)

        self.file_name_label = QLabel(self, "file_name_label")
        self.file_name_label.setMaximumSize(QSize(32767, 32767))
        rone_cone_vlayout.addWidget(self.file_name_label)
        rone_layout.addLayout(rone_cone_vlayout)

        rone_ctwo_layout = QVBoxLayout(None, 0, 6, "rone_ctwo_layout")

        self.base_path_label = QLineEdit(self, "base_path_label")
        self.base_path_label.setMinimumSize(QSize(350, 0))
        self.base_path_label.setMaximumSize(QSize(350, 32767))
        self.base_path_label.setReadOnly(1)
        rone_ctwo_layout.addWidget(self.base_path_label)

        self.folder_ledit = QLineEdit(self, "folder_ledit")
        self.folder_ledit.setMinimumSize(QSize(350, 0))
        self.folder_ledit.setMaximumSize(QSize(350, 32767))
        rone_ctwo_layout.addWidget(self.folder_ledit)

        file_name_hlayout = QHBoxLayout(None, 0, 6, "file_name_hlayout")

        self.file_name_value_label = QLabel(self, "file_name_value_label")
        self.file_name_value_label.setMinimumSize(QSize(250, 0))
        self.file_name_value_label.setMaximumSize(QSize(250, 32767))
        file_name_hlayout.addWidget(self.file_name_value_label)
        file_name_hspacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        file_name_hlayout.addItem(file_name_hspacer)

        self.browse_button = QPushButton(self, "browse_button")
        self.browse_button.setMaximumSize(QSize(75, 32767))
        file_name_hlayout.addWidget(self.browse_button)
        rone_ctwo_layout.addLayout(file_name_hlayout)
        rone_layout.addLayout(rone_ctwo_layout)
        main_layout.addLayout(rone_layout)

        rtwo_hlayout = QHBoxLayout(None, 0, 6, "rtwo_hlayout")

        rtwo_cone_vlayout = QVBoxLayout(None, 0, 6, "rtwo_cone_vlayout")

        self.prefix_label = QLabel(self, "prefix_label")
        rtwo_cone_vlayout.addWidget(self.prefix_label)

        self.run_number_label = QLabel(self, "run_number_label")
        rtwo_cone_vlayout.addWidget(self.run_number_label)
        rtwo_hlayout.addLayout(rtwo_cone_vlayout)

        rtwo_ctwo_vlayout = QVBoxLayout(None, 0, 6, "rtwo_ctwo_vlayout")

        self.prefix_ledit = QLineEdit(self, "prefix_ledit")
        self.prefix_ledit.setMaximumSize(QSize(225, 32767))
        rtwo_ctwo_vlayout.addWidget(self.prefix_ledit)

        run_number_layout = QHBoxLayout(None, 0, 6, "run_number_layout")

        self.run_number_ledit = QLineEdit(self, "run_number_ledit")
        self.run_number_ledit.setMinimumSize(QSize(50, 0))
        self.run_number_ledit.setMaximumSize(QSize(50, 32767))
        run_number_layout.addWidget(self.run_number_ledit)
        run_number_spacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        run_number_layout.addItem(run_number_spacer)
        rtwo_ctwo_vlayout.addLayout(run_number_layout)
        rtwo_hlayout.addLayout(rtwo_ctwo_vlayout)
        main_layout.addLayout(rtwo_hlayout)
        vspacer = QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(vspacer)
        DataPathWidgetVerticalLayoutLayout.addLayout(main_layout)
        hspacer = QSpacerItem(16, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        DataPathWidgetVerticalLayoutLayout.addItem(hspacer)

        self.languageChange()

        self.resize(QSize(491, 190).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("Data path"))
        self.folder_label.setText(self.__tr("Folder:"))
        self.file_name_label.setText(self.__tr("File name:"))
        self.base_path_label.setText(QString.null)
        self.folder_ledit.setText(QString.null)
        self.file_name_value_label.setText(QString.null)
        self.browse_button.setText(self.__tr("Browse"))
        self.prefix_label.setText(self.__tr("Prefix"))
        self.run_number_label.setText(self.__tr("Run number"))

    def __tr(self, s, c=None):
        return qApp.translate("DataPathWidgetVerticalLayout", s, c)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = DataPathWidgetVerticalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
