# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/acquisition_widget_horizontal_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class AcquisitionWidgetHorizontalLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("AcquisitionWidgetHorizontalLayout")


        AcquisitionWidgetHorizontalLayoutLayout = QHBoxLayout(self,11,20,"AcquisitionWidgetHorizontalLayoutLayout")

        col_one_vlayout = QVBoxLayout(None,0,6,"col_one_vlayout")

        col_one_hlayout = QHBoxLayout(None,0,6,"col_one_hlayout")

        col_one_label_layout = QVBoxLayout(None,0,6,"col_one_label_layout")

        self.osc_start_label = QLabel(self,"osc_start_label")
        col_one_label_layout.addWidget(self.osc_start_label)

        self.first_iamge_label = QLabel(self,"first_iamge_label")
        col_one_label_layout.addWidget(self.first_iamge_label)

        self.transmission_label = QLabel(self,"transmission_label")
        col_one_label_layout.addWidget(self.transmission_label)

        self.exp_time_label = QLabel(self,"exp_time_label")
        col_one_label_layout.addWidget(self.exp_time_label)
        col_one_hlayout.addLayout(col_one_label_layout)

        col_one_ledit_layout = QVBoxLayout(None,0,6,"col_one_ledit_layout")

        self.osc_start_ledit = QLineEdit(self,"osc_start_ledit")
        self.osc_start_ledit.setMinimumSize(QSize(50,0))
        self.osc_start_ledit.setMaximumSize(QSize(50,32767))
        col_one_ledit_layout.addWidget(self.osc_start_ledit)

        self.first_image_ledit = QLineEdit(self,"first_image_ledit")
        self.first_image_ledit.setMinimumSize(QSize(50,0))
        self.first_image_ledit.setMaximumSize(QSize(50,32767))
        col_one_ledit_layout.addWidget(self.first_image_ledit)

        self.transmission_ledit = QLineEdit(self,"transmission_ledit")
        self.transmission_ledit.setMinimumSize(QSize(50,0))
        self.transmission_ledit.setMaximumSize(QSize(50,32767))
        col_one_ledit_layout.addWidget(self.transmission_ledit)

        self.exp_time_ledit = QLineEdit(self,"exp_time_ledit")
        self.exp_time_ledit.setMinimumSize(QSize(50,0))
        self.exp_time_ledit.setMaximumSize(QSize(50,32767))
        col_one_ledit_layout.addWidget(self.exp_time_ledit)
        col_one_hlayout.addLayout(col_one_ledit_layout)
        col_one_vlayout.addLayout(col_one_hlayout)
        col_one_spacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        col_one_vlayout.addItem(col_one_spacer)
        AcquisitionWidgetHorizontalLayoutLayout.addLayout(col_one_vlayout)

        col_two_vlayout = QVBoxLayout(None,0,6,"col_two_vlayout")

        col_two_hlayout = QHBoxLayout(None,0,6,"col_two_hlayout")

        col_two_label_layout = QVBoxLayout(None,0,6,"col_two_label_layout")

        self.osc_range_label = QLabel(self,"osc_range_label")
        col_two_label_layout.addWidget(self.osc_range_label)

        self.num_images_label = QLabel(self,"num_images_label")
        self.num_images_label.setAcceptDrops(1)
        col_two_label_layout.addWidget(self.num_images_label)

        self.resolution_label = QLabel(self,"resolution_label")
        col_two_label_layout.addWidget(self.resolution_label)

        self.inverse_beam_cbx = QCheckBox(self,"inverse_beam_cbx")
        col_two_label_layout.addWidget(self.inverse_beam_cbx)
        col_two_hlayout.addLayout(col_two_label_layout)

        col_two_ledit_layout = QVBoxLayout(None,0,6,"col_two_ledit_layout")

        self.osc_range_ledit = QLineEdit(self,"osc_range_ledit")
        self.osc_range_ledit.setMinimumSize(QSize(50,0))
        self.osc_range_ledit.setMaximumSize(QSize(50,32767))
        col_two_ledit_layout.addWidget(self.osc_range_ledit)

        self.num_images_ledit = QLineEdit(self,"num_images_ledit")
        self.num_images_ledit.setMinimumSize(QSize(50,0))
        self.num_images_ledit.setMaximumSize(QSize(50,32767))
        col_two_ledit_layout.addWidget(self.num_images_ledit)

        self.resolution_ledit = QLineEdit(self,"resolution_ledit")
        self.resolution_ledit.setMinimumSize(QSize(50,0))
        self.resolution_ledit.setMaximumSize(QSize(50,32767))
        col_two_ledit_layout.addWidget(self.resolution_ledit)

        self.shutterless_cbx = QCheckBox(self,"shutterless_cbx")
        col_two_ledit_layout.addWidget(self.shutterless_cbx)
        col_two_hlayout.addLayout(col_two_ledit_layout)
        col_two_vlayout.addLayout(col_two_hlayout)
        col_two_spacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        col_two_vlayout.addItem(col_two_spacer)
        AcquisitionWidgetHorizontalLayoutLayout.addLayout(col_two_vlayout)

        col_three_vlayout = QVBoxLayout(None,0,6,"col_three_vlayout")

        col_three_hlayout = QHBoxLayout(None,0,6,"col_three_hlayout")

        col_three_label_layout = QVBoxLayout(None,0,6,"col_three_label_layout")

        self.overlap_label = QLabel(self,"overlap_label")
        col_three_label_layout.addWidget(self.overlap_label)

        self.num_passes_label = QLabel(self,"num_passes_label")
        col_three_label_layout.addWidget(self.num_passes_label)

        self.energy_label = QLabel(self,"energy_label")
        col_three_label_layout.addWidget(self.energy_label)
        col_thee_spacer = QSpacerItem(20,30,QSizePolicy.Minimum,QSizePolicy.Fixed)
        col_three_label_layout.addItem(col_thee_spacer)
        col_three_hlayout.addLayout(col_three_label_layout)

        col_three_ledit_layout = QVBoxLayout(None,0,6,"col_three_ledit_layout")

        self.overlap_ledit = QLineEdit(self,"overlap_ledit")
        self.overlap_ledit.setMinimumSize(QSize(50,0))
        self.overlap_ledit.setMaximumSize(QSize(50,32767))
        col_three_ledit_layout.addWidget(self.overlap_ledit)

        self.num_passes_ledit = QLineEdit(self,"num_passes_ledit")
        self.num_passes_ledit.setMinimumSize(QSize(50,0))
        self.num_passes_ledit.setMaximumSize(QSize(50,32767))
        col_three_ledit_layout.addWidget(self.num_passes_ledit)

        self.energy_ledit = QLineEdit(self,"energy_ledit")
        self.energy_ledit.setMinimumSize(QSize(50,0))
        self.energy_ledit.setMaximumSize(QSize(50,32767))
        col_three_ledit_layout.addWidget(self.energy_ledit)

        mad_layout = QHBoxLayout(None,0,10,"mad_layout")

        self.mad_cbox = QCheckBox(self,"mad_cbox")
        mad_layout.addWidget(self.mad_cbox)

        self.energies_combo = QComboBox(0,self,"energies_combo")
        mad_layout.addWidget(self.energies_combo)
        col_three_ledit_layout.addLayout(mad_layout)
        col_three_hlayout.addLayout(col_three_ledit_layout)
        col_three_vlayout.addLayout(col_three_hlayout)
        col_three_vspacer = QSpacerItem(20,1,QSizePolicy.Minimum,QSizePolicy.Expanding)
        col_three_vlayout.addItem(col_three_vspacer)
        AcquisitionWidgetHorizontalLayoutLayout.addLayout(col_three_vlayout)
        hspacer = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        AcquisitionWidgetHorizontalLayoutLayout.addItem(hspacer)

        self.languageChange()

        self.resize(QSize(809,143).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Acquisition widget"))
        self.osc_start_label.setText(self.__tr("Oscillation start:"))
        self.first_iamge_label.setText(self.__tr("First image:"))
        self.transmission_label.setText(self.__tr("Transmission (%):"))
        self.exp_time_label.setText(self.__tr("Exposure time:"))
        self.osc_range_label.setText(self.__tr("Oscillation range:"))
        self.num_images_label.setText(self.__tr("Number of images:"))
        self.resolution_label.setText(self.__trUtf8("\x52\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x20\x28\xc3\x85\x29\x3a"))
        self.inverse_beam_cbx.setText(self.__tr("Inverse beam"))
        self.shutterless_cbx.setText(self.__tr("Shutterless"))
        self.overlap_label.setText(self.__tr("Oscillation overlap:"))
        self.num_passes_label.setText(self.__tr("Number of passes:"))
        self.energy_label.setText(self.__tr("Energy (KeV):"))
        self.mad_cbox.setText(self.__tr("MAD"))


    def __tr(self,s,c = None):
        return qApp.translate("AcquisitionWidgetHorizontalLayout",s,c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("AcquisitionWidgetHorizontalLayout",s,c,QApplication.UnicodeUTF8)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = AcquisitionWidgetHorizontalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
