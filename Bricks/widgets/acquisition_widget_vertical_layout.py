# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/acquisition_widget_vertical_layout.ui'
#
# Created: Fri Jun 21 15:28:22 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class AcquisitionWidgetVerticalLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("AcquisitionWidgetVerticalLayout")


        AcquisitionWidgetVerticalLayoutLayout = QHBoxLayout(self,0,0,"AcquisitionWidgetVerticalLayoutLayout")

        main_layout = QVBoxLayout(None,0,15,"main_layout")

        rone_hlayout = QHBoxLayout(None,0,20,"rone_hlayout")

        rone_cone_hlayout = QHBoxLayout(None,0,6,"rone_cone_hlayout")

        row_one_labels_vlayout = QVBoxLayout(None,0,12,"row_one_labels_vlayout")

        self.osc_range_label = QLabel(self,"osc_range_label")
        row_one_labels_vlayout.addWidget(self.osc_range_label)

        self.overlap_label = QLabel(self,"overlap_label")
        row_one_labels_vlayout.addWidget(self.overlap_label)

        self.osc_start_label = QLabel(self,"osc_start_label")
        row_one_labels_vlayout.addWidget(self.osc_start_label)
        rone_cone_hlayout.addLayout(row_one_labels_vlayout)

        row_one_ledit_vlayout = QVBoxLayout(None,0,6,"row_one_ledit_vlayout")

        self.osc_range_ledit = QLineEdit(self,"osc_range_ledit")
        self.osc_range_ledit.setMinimumSize(QSize(50,0))
        self.osc_range_ledit.setMaximumSize(QSize(50,32767))
        row_one_ledit_vlayout.addWidget(self.osc_range_ledit)

        self.overlap_ledit = QLineEdit(self,"overlap_ledit")
        self.overlap_ledit.setMinimumSize(QSize(50,0))
        self.overlap_ledit.setMaximumSize(QSize(50,32767))
        row_one_ledit_vlayout.addWidget(self.overlap_ledit)

        self.osc_start_ledit = QLineEdit(self,"osc_start_ledit")
        self.osc_start_ledit.setMinimumSize(QSize(50,0))
        self.osc_start_ledit.setMaximumSize(QSize(50,32767))
        row_one_ledit_vlayout.addWidget(self.osc_start_ledit)
        rone_cone_hlayout.addLayout(row_one_ledit_vlayout)
        rone_hlayout.addLayout(rone_cone_hlayout)

        rone_ctwo_hlayout = QHBoxLayout(None,0,6,"rone_ctwo_hlayout")

        row_two_labels_vlayout = QVBoxLayout(None,0,6,"row_two_labels_vlayout")

        self.first_iamge_label = QLabel(self,"first_iamge_label")
        row_two_labels_vlayout.addWidget(self.first_iamge_label)

        self.num_images_label = QLabel(self,"num_images_label")
        self.num_images_label.setAcceptDrops(1)
        row_two_labels_vlayout.addWidget(self.num_images_label)

        self.num_passes_label = QLabel(self,"num_passes_label")
        row_two_labels_vlayout.addWidget(self.num_passes_label)
        rone_ctwo_hlayout.addLayout(row_two_labels_vlayout)

        row_two_ledit_vlayout = QVBoxLayout(None,0,6,"row_two_ledit_vlayout")

        self.first_image_ledit = QLineEdit(self,"first_image_ledit")
        self.first_image_ledit.setMinimumSize(QSize(50,0))
        self.first_image_ledit.setMaximumSize(QSize(50,32767))
        row_two_ledit_vlayout.addWidget(self.first_image_ledit)

        self.num_images_ledit = QLineEdit(self,"num_images_ledit")
        self.num_images_ledit.setMinimumSize(QSize(50,0))
        self.num_images_ledit.setMaximumSize(QSize(50,32767))
        row_two_ledit_vlayout.addWidget(self.num_images_ledit)

        self.num_passes_ledit = QLineEdit(self,"num_passes_ledit")
        self.num_passes_ledit.setMinimumSize(QSize(50,0))
        self.num_passes_ledit.setMaximumSize(QSize(50,32767))
        row_two_ledit_vlayout.addWidget(self.num_passes_ledit)
        rone_ctwo_hlayout.addLayout(row_two_ledit_vlayout)
        rone_hlayout.addLayout(rone_ctwo_hlayout)
        main_layout.addLayout(rone_hlayout)

        rtwo_hlayout = QHBoxLayout(None,0,16,"rtwo_hlayout")

        row_three_labels_layout = QVBoxLayout(None,0,6,"row_three_labels_layout")

        self.exp_time_label = QLabel(self,"exp_time_label")
        row_three_labels_layout.addWidget(self.exp_time_label)

        self.energy_label = QLabel(self,"energy_label")
        row_three_labels_layout.addWidget(self.energy_label)

        self.resolution_label = QLabel(self,"resolution_label")
        row_three_labels_layout.addWidget(self.resolution_label)

        self.transmission_label = QLabel(self,"transmission_label")
        row_three_labels_layout.addWidget(self.transmission_label)
        rtwo_hlayout.addLayout(row_three_labels_layout)

        rtwo_ledit_layout = QVBoxLayout(None,0,6,"rtwo_ledit_layout")

        self.exp_time_ledit = QLineEdit(self,"exp_time_ledit")
        self.exp_time_ledit.setMinimumSize(QSize(50,0))
        self.exp_time_ledit.setMaximumSize(QSize(50,32767))
        rtwo_ledit_layout.addWidget(self.exp_time_ledit)

        energy_layout = QHBoxLayout(None,0,10,"energy_layout")

        self.energy_ledit = QLineEdit(self,"energy_ledit")
        self.energy_ledit.setMinimumSize(QSize(50,0))
        self.energy_ledit.setMaximumSize(QSize(50,32767))
        energy_layout.addWidget(self.energy_ledit)

        mad_layout = QHBoxLayout(None,0,10,"mad_layout")

        self.mad_cbox = QCheckBox(self,"mad_cbox")
        mad_layout.addWidget(self.mad_cbox)

        self.energies_combo = QComboBox(0,self,"energies_combo")
        mad_layout.addWidget(self.energies_combo)
        energy_layout.addLayout(mad_layout)
        rtwo_ledit_layout.addLayout(energy_layout)

        self.resolution_ledit = QLineEdit(self,"resolution_ledit")
        self.resolution_ledit.setMinimumSize(QSize(50,0))
        self.resolution_ledit.setMaximumSize(QSize(50,32767))
        rtwo_ledit_layout.addWidget(self.resolution_ledit)

        self.transmission_ledit = QLineEdit(self,"transmission_ledit")
        self.transmission_ledit.setMinimumSize(QSize(50,0))
        self.transmission_ledit.setMaximumSize(QSize(50,32767))
        rtwo_ledit_layout.addWidget(self.transmission_ledit)
        rtwo_hlayout.addLayout(rtwo_ledit_layout)
        rtwo_hspacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rtwo_hlayout.addItem(rtwo_hspacer)
        main_layout.addLayout(rtwo_hlayout)

        rfour_hlayout = QHBoxLayout(None,0,6,"rfour_hlayout")

        cbx_vlayout = QVBoxLayout(None,0,6,"cbx_vlayout")

        self.inverse_beam_cbx = QCheckBox(self,"inverse_beam_cbx")
        cbx_vlayout.addWidget(self.inverse_beam_cbx)

        self.shutterless_cbx = QCheckBox(self,"shutterless_cbx")
        cbx_vlayout.addWidget(self.shutterless_cbx)
        rfour_hlayout.addLayout(cbx_vlayout)
        cbx_spacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        rfour_hlayout.addItem(cbx_spacer)
        main_layout.addLayout(rfour_hlayout)
        AcquisitionWidgetVerticalLayoutLayout.addLayout(main_layout)
        hpsacer = QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        AcquisitionWidgetVerticalLayoutLayout.addItem(hpsacer)

        self.languageChange()

        self.resize(QSize(477,294).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Acquisition widget"))
        self.osc_range_label.setText(self.__tr("Oscillation range:"))
        self.overlap_label.setText(self.__tr("Oscillation overlap:"))
        self.osc_start_label.setText(self.__tr("Oscillation start:"))
        self.first_iamge_label.setText(self.__tr("First image:"))
        self.num_images_label.setText(self.__tr("Number of images:"))
        self.num_passes_label.setText(self.__tr("Number of passes:"))
        self.exp_time_label.setText(self.__tr("Exposure time:"))
        self.energy_label.setText(self.__tr("Energy (KeV):"))
        self.resolution_label.setText(self.__trUtf8("\x52\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x20\x28\xc3\x85\x29\x3a"))
        self.transmission_label.setText(self.__tr("Transmission (%):"))
        self.mad_cbox.setText(self.__tr("MAD"))
        self.inverse_beam_cbx.setText(self.__tr("Inverse beam"))
        self.shutterless_cbx.setText(self.__tr("Shutterless"))


    def __tr(self,s,c = None):
        return qApp.translate("AcquisitionWidgetVerticalLayout",s,c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("AcquisitionWidgetVerticalLayout",s,c,QApplication.UnicodeUTF8)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = AcquisitionWidgetVerticalLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
