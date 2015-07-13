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

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from widgets.Qt4_data_path_widget import DataPathWidget


class ReferenceImageWidget(QtGui.QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("ReferenceImageWidget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QtGui.QGroupBox("Reference images", self)
        self.tool_box = QtGui.QToolBox(self.group_box)
        self.page_widget = QtGui.QWidget(self.tool_box)
        self.path_widget = DataPathWidget(self.page_widget)
        self.acq_groupbox = QtGui.QGroupBox("Acquisition", self.page_widget)
        self.acq_widget = AcquisitionWidget(self.acq_groupbox, 'horizontal')
        self.acq_widget.acq_widget.inverse_beam_cbx.hide()
        self.acq_widget.acq_widget.shutterless_cbx.hide()
        self.acq_widget.acq_widget.subwedge_size_label.hide()
        self.acq_widget.acq_widget.subwedge_size_ledit.hide()
        #self.acq_widget.acq_widget.setFixedHeight(130)
        self.tool_box.addItem(self.page_widget, "Acquisition parameters")

        # Layout --------------------------------------------------------------
        _acq_groupbox_layout = QtGui.QVBoxLayout(self)
        _acq_groupbox_layout.addWidget(self.acq_widget)
        _acq_groupbox_layout.setSpacing(0)
        _acq_groupbox_layout.setContentsMargins(0, 0, 0, 0)
        self.acq_groupbox.setLayout(_acq_groupbox_layout)

        _page_widget_layout = QtGui.QVBoxLayout(self)
        _page_widget_layout.addWidget(self.path_widget)
        _page_widget_layout.addWidget(self.acq_groupbox)
        _page_widget_layout.addStretch(0)
        _page_widget_layout.setSpacing(0)
        _page_widget_layout.setContentsMargins(0, 0, 0, 0)  
        self.page_widget.setLayout(_page_widget_layout)
        
        _group_box_vlayout = QtGui.QVBoxLayout(self)
        _group_box_vlayout.addWidget(self.tool_box)
        _group_box_vlayout.setSpacing(0)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)
        self.group_box.setLayout(_group_box_vlayout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.GROUP_BOX_GRAY) 
