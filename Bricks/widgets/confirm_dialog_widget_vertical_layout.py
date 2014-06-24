# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/confirm_dialog_widget_vertical_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class ConfirmDialogWidgetVerticalLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        self.snapshots_list = [4,1,2,0]

        if not name:
            self.setName("ConfirmDialogWidgetVerticalLayout")


        ConfirmDialogWidgetVerticalLayoutLayout = QHBoxLayout(self,11,6,"ConfirmDialogWidgetVerticalLayoutLayout")

        main_layout = QVBoxLayout(None,0,15,"main_layout")

        self.summary_gbox = QGroupBox(self,"summary_gbox")
        self.summary_gbox.setColumnLayout(0,Qt.Vertical)
        self.summary_gbox.layout().setSpacing(15)
        self.summary_gbox.layout().setMargin(11)
        summary_gboxLayout = QVBoxLayout(self.summary_gbox.layout())
        summary_gboxLayout.setAlignment(Qt.AlignTop)

        self.summary_label = QLabel(self.summary_gbox,"summary_label")
        summary_gboxLayout.addWidget(self.summary_label)

        cbx_layout = QVBoxLayout(None,0,6,"cbx_layout")

        self.force_dark_cbx = QCheckBox(self.summary_gbox,"force_dark_cbx")
        cbx_layout.addWidget(self.force_dark_cbx)

        self.skip_existing_images_cbx = QCheckBox(self.summary_gbox,"skip_existing_images_cbx")
        cbx_layout.addWidget(self.skip_existing_images_cbx)


	take_snapshots_layout = QHBoxLayout(None,0,3,"snapshots_layout")

	self.take_snapshots_label = QLabel(self.summary_gbox, "take_snaphots_label")
	take_snapshots_layout.addWidget(self.take_snapshots_label)

        self.take_snapshots_cbox = QComboBox(self.summary_gbox, "take_snapshosts_cbox")
	take_snapshots_layout.addWidget(self.take_snapshots_cbox)

	take_snapshots_hspacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        take_snapshots_layout.addItem(take_snapshots_hspacer)

	cbx_layout.addLayout(take_snapshots_layout)

        self.missing_one_cbx = QCheckBox(self.summary_gbox,"missing_one_cbx")
        cbx_layout.addWidget(self.missing_one_cbx)

        self.missing_two_cbx = QCheckBox(self.summary_gbox,"missing_two_cbx")
        cbx_layout.addWidget(self.missing_two_cbx)
        summary_gboxLayout.addLayout(cbx_layout)
        main_layout.addWidget(self.summary_gbox)

        self.file_list_view = QListView(self,"file_list_view")
        self.file_list_view.addColumn(self.__tr("Sample"))
        self.file_list_view.header().setClickEnabled(0,self.file_list_view.header().count() - 1)
        self.file_list_view.addColumn(self.__tr("Directory"))
        self.file_list_view.addColumn(self.__tr("File name"))
        self.file_list_view.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.file_list_view.sizePolicy().hasHeightForWidth()))
        main_layout.addWidget(self.file_list_view)

        button_layout = QHBoxLayout(None,0,6,"button_layout")
        hspacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        button_layout.addItem(hspacer)

        self.continue_button = QPushButton(self,"continue_button")
        button_layout.addWidget(self.continue_button)

        self.cancel_button = QPushButton(self,"cancel_button")
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        ConfirmDialogWidgetVerticalLayoutLayout.addLayout(main_layout)

        self.languageChange()

        self.resize(QSize(1018,472).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Confirm collect"))
        self.summary_gbox.setTitle(self.__tr("Summary"))
        self.summary_label.setText(self.__tr("<summary label>"))
        self.force_dark_cbx.setText(self.__tr("Force dark current"))
        self.skip_existing_images_cbx.setText(self.__tr("Skip already collected images"))
	self.take_snapshots_label.setText(self.__tr("Number of crystal snapshots:"))

	self.take_snapshots_cbox.clear()
        for i in self.snapshots_list:
          self.take_snapshots_cbox.insertItem(self.__tr(str(i)))
		
        self.missing_one_cbx.setText(self.__tr("Missing box one"))
        self.missing_two_cbx.setText(self.__tr("Missing box two"))
        self.file_list_view.header().setLabel(0,self.__tr("Sample"))
        self.file_list_view.header().setLabel(1,self.__tr("Directory"))
        self.file_list_view.header().setLabel(2,self.__tr("File name"))
        self.continue_button.setText(self.__tr("Continue"))
        self.cancel_button.setText(self.__tr("Cancel"))


    def __tr(self,s,c = None):
        return qApp.translate("ConfirmDialogWidgetVerticalLayout",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = ConfirmDialogWidgetVerticalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
