# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/processing_widget_vertical_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class ProcessingWidgetVerticalLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("ProcessingWidgetVerticalLayout")


        ProcessingWidgetVerticalLayoutLayout = QHBoxLayout(self,0,0,"ProcessingWidgetVerticalLayoutLayout")

        main_layout = QVBoxLayout(None,0,6,"main_layout")

        rone_layout = QHBoxLayout(None,0,20,"rone_layout")

        cbx_layout = QVBoxLayout(None,0,6,"cbx_layout")

        self.use_processing = QCheckBox(self,"use_processing")
        cbx_layout.addWidget(self.use_processing)

        self.use_anomalous = QCheckBox(self,"use_anomalous")
        cbx_layout.addWidget(self.use_anomalous)
        rone_layout.addLayout(cbx_layout)

        space_group_layout = QHBoxLayout(None,0,6,"space_group_layout")

        space_group_label_layout = QVBoxLayout(None,0,6,"space_group_label_layout")

        self.num_residues_label = QLabel(self,"num_residues_label")
        space_group_label_layout.addWidget(self.num_residues_label)

        self.space_geoup_label = QLabel(self,"space_geoup_label")
        space_group_label_layout.addWidget(self.space_geoup_label)
        space_group_layout.addLayout(space_group_label_layout)

        space_group_layout_ledit = QVBoxLayout(None,0,6,"space_group_layout_ledit")

        self.num_residues_ledit = QLineEdit(self,"num_residues_ledit")
        self.num_residues_ledit.setMinimumSize(QSize(75,0))
        self.num_residues_ledit.setMaximumSize(QSize(75,32767))
        space_group_layout_ledit.addWidget(self.num_residues_ledit)

        self.space_group_ledit = QComboBox(0,self,"space_group_ledit")
        self.space_group_ledit.setMinimumSize(QSize(75,0))
        self.space_group_ledit.setMaximumSize(QSize(75,32767))
        space_group_layout_ledit.addWidget(self.space_group_ledit)
        space_group_layout.addLayout(space_group_layout_ledit)
        rone_layout.addLayout(space_group_layout)
        main_layout.addLayout(rone_layout)

        rtwo_layout = QHBoxLayout(None,0,6,"rtwo_layout")

        unitcell_layout = QVBoxLayout(None,0,0,"unitcell_layout")

        unit_cell_heading_layout = QHBoxLayout(None,0,6,"unit_cell_heading_layout")

        self.unit_cell_heading = QLabel(self,"unit_cell_heading")
        unit_cell_heading_layout.addWidget(self.unit_cell_heading)
        unit_cell_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        unit_cell_heading_layout.addItem(unit_cell_spacer)
        unitcell_layout.addLayout(unit_cell_heading_layout)

        unit_cell_ledit_layout = QHBoxLayout(None,0,8,"unit_cell_ledit_layout")

        a_layout = QHBoxLayout(None,0,6,"a_layout")

        self.a_label = QLabel(self,"a_label")
        a_layout.addWidget(self.a_label)

        self.a_ledit = QLineEdit(self,"a_ledit")
        self.a_ledit.setMinimumSize(QSize(35,0))
        self.a_ledit.setMaximumSize(QSize(35,32767))
        a_layout.addWidget(self.a_ledit)
        unit_cell_ledit_layout.addLayout(a_layout)

        b_layout = QHBoxLayout(None,0,6,"b_layout")

        self.b_label = QLabel(self,"b_label")
        b_layout.addWidget(self.b_label)

        self.b_ledit = QLineEdit(self,"b_ledit")
        self.b_ledit.setMinimumSize(QSize(35,0))
        self.b_ledit.setMaximumSize(QSize(35,32767))
        b_layout.addWidget(self.b_ledit)
        unit_cell_ledit_layout.addLayout(b_layout)

        c_layout = QHBoxLayout(None,0,6,"c_layout")

        self.c_label = QLabel(self,"c_label")
        c_layout.addWidget(self.c_label)

        self.c_ledit = QLineEdit(self,"c_ledit")
        self.c_ledit.setMinimumSize(QSize(35,0))
        self.c_ledit.setMaximumSize(QSize(35,32767))
        c_layout.addWidget(self.c_ledit)
        unit_cell_ledit_layout.addLayout(c_layout)

        alpha_layout = QHBoxLayout(None,0,6,"alpha_layout")

        self.alpha_label = QLabel(self,"alpha_label")
        alpha_layout.addWidget(self.alpha_label)

        self.alpha_ledit = QLineEdit(self,"alpha_ledit")
        self.alpha_ledit.setMinimumSize(QSize(35,0))
        self.alpha_ledit.setMaximumSize(QSize(35,32767))
        alpha_layout.addWidget(self.alpha_ledit)
        unit_cell_ledit_layout.addLayout(alpha_layout)

        beta_layout = QHBoxLayout(None,0,6,"beta_layout")

        self.beta_label = QLabel(self,"beta_label")
        beta_layout.addWidget(self.beta_label)

        self.beta_ledit = QLineEdit(self,"beta_ledit")
        self.beta_ledit.setMinimumSize(QSize(35,0))
        self.beta_ledit.setMaximumSize(QSize(35,32767))
        beta_layout.addWidget(self.beta_ledit)
        unit_cell_ledit_layout.addLayout(beta_layout)

        gamma_layout = QHBoxLayout(None,0,6,"gamma_layout")

        self.gamma_label = QLabel(self,"gamma_label")
        gamma_layout.addWidget(self.gamma_label)

        self.gamma_ledit = QLineEdit(self,"gamma_ledit")
        self.gamma_ledit.setMinimumSize(QSize(35,0))
        self.gamma_ledit.setMaximumSize(QSize(35,32767))
        gamma_layout.addWidget(self.gamma_ledit)
        unit_cell_ledit_layout.addLayout(gamma_layout)
        unitcell_layout.addLayout(unit_cell_ledit_layout)
        rtwo_layout.addLayout(unitcell_layout)
        unit_cell_layout = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rtwo_layout.addItem(unit_cell_layout)
        main_layout.addLayout(rtwo_layout)

        rthree_layout = QHBoxLayout(None,0,6,"rthree_layout")

        pdb_layout = QVBoxLayout(None,0,0,"pdb_layout")

        pdb_heading_layout = QHBoxLayout(None,0,20,"pdb_heading_layout")

        self.pdb_label = QLabel(self,"pdb_label")
        pdb_heading_layout.addWidget(self.pdb_label)

        self.upload_button_gbox = QButtonGroup(self,"upload_button_gbox")
        self.upload_button_gbox.setFrameShape(QButtonGroup.NoFrame)
        self.upload_button_gbox.setMargin(0)
        self.upload_button_gbox.setMidLineWidth(0)
        self.upload_button_gbox.setAlignment(QButtonGroup.AlignTop)
        self.upload_button_gbox.setFlat(0)
        self.upload_button_gbox.setColumnLayout(0,Qt.Vertical)
        self.upload_button_gbox.layout().setSpacing(0)
        self.upload_button_gbox.layout().setMargin(0)
        upload_button_gboxLayout = QHBoxLayout(self.upload_button_gbox.layout())
        upload_button_gboxLayout.setAlignment(Qt.AlignTop)

        button_gbox_layout = QHBoxLayout(None,0,10,"button_gbox_layout")

        self.upload_radio = QRadioButton(self.upload_button_gbox,"upload_radio")
        button_gbox_layout.addWidget(self.upload_radio)

        self.use_code_radio = QRadioButton(self.upload_button_gbox,"use_code_radio")
        button_gbox_layout.addWidget(self.use_code_radio)
        upload_button_gboxLayout.addLayout(button_gbox_layout)
        pdb_heading_layout.addWidget(self.upload_button_gbox)
        pdb_heading_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        pdb_heading_layout.addItem(pdb_heading_spacer)
        pdb_layout.addLayout(pdb_heading_layout)

        path_layout = QHBoxLayout(None,0,6,"path_layout")

        self.path_ledit = QLineEdit(self,"path_ledit")
        path_layout.addWidget(self.path_ledit)

        self.browse_button = QPushButton(self,"browse_button")
        path_layout.addWidget(self.browse_button)
        pdb_layout.addLayout(path_layout)
        rthree_layout.addLayout(pdb_layout)
        rthree_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rthree_layout.addItem(rthree_spacer)
        main_layout.addLayout(rthree_layout)
        vpsacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        main_layout.addItem(vpsacer)
        ProcessingWidgetVerticalLayoutLayout.addLayout(main_layout)
        hpsacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        ProcessingWidgetVerticalLayoutLayout.addItem(hpsacer)

        self.languageChange()

        self.resize(QSize(400,189).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Processing"))
        self.use_processing.setText(self.__tr("Process and analyse data"))
        self.use_anomalous.setText(self.__tr("Anomalous"))
        self.num_residues_label.setText(self.__tr("N.o. residues:"))
        self.space_geoup_label.setText(self.__tr("Space group:"))
        self.unit_cell_heading.setText(self.__tr("Unit cell:"))
        self.a_label.setText(self.__tr("a:"))
        self.b_label.setText(self.__tr("b:"))
        self.c_label.setText(self.__tr("c:"))
        self.alpha_label.setText(self.__trUtf8("\xce\xb1\x3a"))
        self.beta_label.setText(self.__trUtf8("\xce\xb2\x3a"))
        self.gamma_label.setText(self.__trUtf8("\xce\xb3\x3a"))
        self.pdb_label.setText(self.__tr("PDB:"))
        self.upload_button_gbox.setTitle(QString.null)
        self.upload_radio.setText(self.__tr("Upload"))
        self.use_code_radio.setText(self.__tr("Use code"))
        self.browse_button.setText(self.__tr("Browse"))


    def __tr(self,s,c = None):
        return qApp.translate("ProcessingWidgetVerticalLayout",s,c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("ProcessingWidgetVerticalLayout",s,c,QApplication.UnicodeUTF8)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = ProcessingWidgetVerticalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
