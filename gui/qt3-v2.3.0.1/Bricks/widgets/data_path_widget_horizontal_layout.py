# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/data_path_widget_horizontal_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class DataPathWidgetHorizontalLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("DataPathWidgetHorizontalLayout")

        DataPathWidgetHorizontalLayoutLayout = QHBoxLayout(
            self, 0, 0, "DataPathWidgetHorizontalLayoutLayout"
        )

        self.data_path_gb = QGroupBox(self, "data_path_gb")
        self.data_path_gb.setColumnLayout(0, Qt.Vertical)
        self.data_path_gb.layout().setSpacing(6)
        self.data_path_gb.layout().setMargin(11)
        data_path_gbLayout = QHBoxLayout(self.data_path_gb.layout())
        data_path_gbLayout.setAlignment(Qt.AlignTop)

        main_layout = QVBoxLayout(None, 0, 10, "main_layout")

        rone_layout = QHBoxLayout(None, 0, 6, "rone_layout")

        rone_cone_vlayout = QVBoxLayout(None, 0, 6, "rone_cone_vlayout")

        self.folder_label = QLabel(self.data_path_gb, "folder_label")
        rone_cone_vlayout.addWidget(self.folder_label)

        self.file_name_label = QLabel(self.data_path_gb, "file_name_label")
        rone_cone_vlayout.addWidget(self.file_name_label)
        rone_layout.addLayout(rone_cone_vlayout)

        rone_ctwo_layout = QVBoxLayout(None, 0, 6, "rone_ctwo_layout")

        path_ledit_layout = QHBoxLayout(None, 0, 6, "path_ledit_layout")

        self.base_path_label = QLabel(self.data_path_gb, "base_path_label")
        self.base_path_label.setMinimumSize(QSize(200, 0))
        self.base_path_label.setMaximumSize(QSize(400, 32767))
        path_ledit_layout.addWidget(self.base_path_label)

        self.folder_ledit = QLineEdit(self.data_path_gb, "folder_ledit")
        self.folder_ledit.setMinimumSize(QSize(200, 0))
        self.folder_ledit.setMaximumSize(QSize(32767, 32767))
        path_ledit_layout.addWidget(self.folder_ledit)
        rone_ctwo_layout.addLayout(path_ledit_layout)

        file_name_hlayout = QHBoxLayout(None, 0, 6, "file_name_hlayout")

        self.file_name_value_label = QLabel(self.data_path_gb, "file_name_value_label")
        file_name_hlayout.addWidget(self.file_name_value_label)
        file_name_hspacer = QSpacerItem(
            61, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        file_name_hlayout.addItem(file_name_hspacer)

        self.browse_button = QPushButton(self.data_path_gb, "browse_button")
        self.browse_button.setMaximumSize(QSize(75, 32765))
        file_name_hlayout.addWidget(self.browse_button)
        rone_ctwo_layout.addLayout(file_name_hlayout)
        rone_layout.addLayout(rone_ctwo_layout)
        main_layout.addLayout(rone_layout)

        rtwo_hlayout = QHBoxLayout(None, 0, 6, "rtwo_hlayout")

        self.prefix_label = QLabel(self.data_path_gb, "prefix_label")
        self.prefix_label.setMinimumSize(QSize(73, 0))
        self.prefix_label.setMaximumSize(QSize(73, 32767))
        rtwo_hlayout.addWidget(self.prefix_label)

        self.prefix_ledit = QLineEdit(self.data_path_gb, "prefix_ledit")
        self.prefix_ledit.setMinimumSize(QSize(150, 0))
        self.prefix_ledit.setMaximumSize(QSize(300, 32767))
        rtwo_hlayout.addWidget(self.prefix_ledit)
        prefix_hspacer = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        rtwo_hlayout.addItem(prefix_hspacer)

        self.run_num_label = QLabel(self.data_path_gb, "run_num_label")
        rtwo_hlayout.addWidget(self.run_num_label)

        self.run_number_ledit = QLineEdit(self.data_path_gb, "run_number_ledit")
        self.run_number_ledit.setMinimumSize(QSize(50, 0))
        self.run_number_ledit.setMaximumSize(QSize(50, 32767))
        rtwo_hlayout.addWidget(self.run_number_ledit)
        run_number_spacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        rtwo_hlayout.addItem(run_number_spacer)
        main_layout.addLayout(rtwo_hlayout)
        data_path_gbLayout.addLayout(main_layout)
        DataPathWidgetHorizontalLayoutLayout.addWidget(self.data_path_gb)

        self.languageChange()

        self.resize(QSize(712, 125).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("Data path"))
        self.data_path_gb.setTitle(self.__tr("Data location"))
        self.folder_label.setText(self.__tr("Folder:"))
        self.file_name_label.setText(self.__tr("File name:"))
        self.base_path_label.setText(QString.null)
        self.folder_ledit.setText(self.__tr("<folder>"))
        self.file_name_value_label.setText(self.__tr("<file name>"))
        self.browse_button.setText(self.__tr("Browse"))
        self.prefix_label.setText(self.__tr("Prefix:"))
        self.run_num_label.setText(self.__tr("Run number:"))

    def __tr(self, s, c=None):
        return qApp.translate("DataPathWidgetHorizontalLayout", s, c)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = DataPathWidgetHorizontalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
