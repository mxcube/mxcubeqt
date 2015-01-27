#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui


class VerticalCrystalDimensionWidgetLayout(QtGui.QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("VerticalCrystalDimensionWidgetLayout")

        return

        self.setSizePolicy(QtGui.QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.sizePolicy().hasHeightForWidth()))

        VerticalCrystalDimensionWidgetLayoutLayout = QtGui.QVBoxLayout(self,0,6,"VerticalCrystalDimensionWidgetLayoutLayout")

        self.gbox = QtGui.QGroupBox(self,"gbox")
        self.gbox.setSizePolicy(QtGui.QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.gbox.sizePolicy().hasHeightForWidth()))
        self.gbox.setChecked(0)
        self.gbox.setColumnLayout(0,QtGui.Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QtGui.QHBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(QtGui.Qt.AlignTop)

        main_layout = QtGui.QVBoxLayout(None,0,15,"main_layout")

        space_group_layout = QtGui.QHBoxLayout(None,0,6,"space_group_layout")

        space_group_ledit_layout = QtGui.QHBoxLayout(None,0,6,"space_group_ledit_layout")

        self.space_group_label = QtGui.QLabel(self.gbox,"space_group_label")
        space_group_ledit_layout.addWidget(self.space_group_label)

        self.space_group_ledit = QtGui.QComboBox(0,self.gbox,"space_group_ledit")
        self.space_group_ledit.setMinimumSize(QtGui.QSize(100,0))
        self.space_group_ledit.setMaximumSize(QtGui.QSize(100,32767))
        space_group_ledit_layout.addWidget(self.space_group_ledit)
        space_group_layout.addLayout(space_group_ledit_layout)
        space_group_hspacer = QtGui.QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        space_group_layout.addItem(space_group_hspacer)
        main_layout.addLayout(space_group_layout)

        vdim_layout = QtGui.QVBoxLayout(None,0,2,"vdim_layout")

        vdim_heading_layout = QtGui.QHBoxLayout(None,0,6,"vdim_heading_layout")

        self.dimension_label = QtGui.QLabel(self.gbox,"dimension_label")
        vdim_heading_layout.addWidget(self.dimension_label)
        vdim_heading_spacer = QtGui.QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        vdim_heading_layout.addItem(vdim_heading_spacer)
        vdim_layout.addLayout(vdim_heading_layout)

        vdim_control_layout = QtGui.QHBoxLayout(None,0,0,"vdim_control_layout")

        vdim_ledit_hlayout = QtGui.QHBoxLayout(None,0,20,"vdim_ledit_hlayout")

        col_one_vdim_ledit_hlayout = QtGui.QHBoxLayout(None,0,6,"col_one_vdim_ledit_hlayout")

        vlayout_min_vdim_label = QtGui.QVBoxLayout(None,0,6,"vlayout_min_vdim_label")

        self.min_vdim_label = QtGui.QLabel(self.gbox,"min_vdim_label")
        vlayout_min_vdim_label.addWidget(self.min_vdim_label)

        self.vdim_min_phi_label = QtGui.QLabel(self.gbox,"vdim_min_phi_label")
        vlayout_min_vdim_label.addWidget(self.vdim_min_phi_label)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_label)

        vlayout_min_vdim_ledit = QtGui.QVBoxLayout(None,0,6,"vlayout_min_vdim_ledit")

        self.min_vdim_ledit = QtGui.QLineEdit(self.gbox,"min_vdim_ledit")
        self.min_vdim_ledit.setMinimumSize(QtGui.QSize(50,0))
        self.min_vdim_ledit.setMaximumSize(QtGui.QSize(50,32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vdim_ledit)

        self.min_vphi_ledit = QtGui.QLineEdit(self.gbox,"min_vphi_ledit")
        self.min_vphi_ledit.setMinimumSize(QtGui.QSize(50,0))
        self.min_vphi_ledit.setMaximumSize(QtGui.QSize(50,32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vphi_ledit)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_one_vdim_ledit_hlayout)

        col_two_vdim_ledit_hlayout = QtGui.QHBoxLayout(None,0,6,"col_two_vdim_ledit_hlayout")

        vlayout_two_vdim_hlayout = QtGui.QVBoxLayout(None,0,6,"vlayout_two_vdim_hlayout")

        self.max_vdim_label = QtGui.QLabel(self.gbox,"max_vdim_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vdim_label)

        self.max_vphi_label = QtGui.QLabel(self.gbox,"max_vphi_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vphi_label)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_two_vdim_hlayout)

        vlayout_max_vdim_ledit = QtGui.QVBoxLayout(None,0,6,"vlayout_max_vdim_ledit")

        self.max_vdim_ledit = QtGui.QLineEdit(self.gbox,"max_vdim_ledit")
        self.max_vdim_ledit.setMinimumSize(QtGui.QSize(50,0))
        self.max_vdim_ledit.setMaximumSize(QtGui.QSize(50,32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vdim_ledit)

        self.max_vphi_ledit = QtGui.QLineEdit(self.gbox,"max_vphi_ledit")
        self.max_vphi_ledit.setMinimumSize(QtGui.QSize(50,0))
        self.max_vphi_ledit.setMaximumSize(QtGui.QSize(50,32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vphi_ledit)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_max_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_two_vdim_ledit_hlayout)
        vdim_control_layout.addLayout(vdim_ledit_hlayout)
        vspacer = QtGui.QSpacerItem(1,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        vdim_control_layout.addItem(vspacer)
        vdim_layout.addLayout(vdim_control_layout)
        main_layout.addLayout(vdim_layout)
        gboxLayout.addLayout(main_layout)
        VerticalCrystalDimensionWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QtGui.QSize(307,163).expandedTo(self.minimumSizeHint()))
        self.clearWState(QtGui.Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("VerticalCrystalDimensionWidget"))
        self.gbox.setTitle(self.__tr("Crystal"))
        self.space_group_label.setText(self.__tr("Space group:"))
        self.dimension_label.setText(self.__tr("Vertical crystal dimension (mm):"))
        self.min_vdim_label.setText(self.__tr("Min:"))
        self.vdim_min_phi_label.setText(self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x69\x6e\x3a"))
        self.max_vdim_label.setText(self.__tr("Max:"))
        self.max_vphi_label.setText(self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x61\x78\x3a"))


    def __tr(self,s,c = None):
        return QtGui.QApplication.translate("VerticalCrystalDimensionWidgetLayout",s,c)

    def __trUtf8(self,s,c = None):
        return QtGui.QApplication.translate("VerticalCrystalDimensionWidgetLayout",s,c,QtGui.QApplication.UnicodeUTF8)
