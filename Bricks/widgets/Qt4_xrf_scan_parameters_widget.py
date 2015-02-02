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

import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import queue_model_objects_v1 as queue_model_objects

from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_mca_spectrum_widget import McaSpectrumWidget


__category__ = 'Qt4_TaskToolbox_Tabs'


class XRFScanParametersWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "xrf_scan_tab_widget"):
        QtGui.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self.xrf_scan_hwobj = None

        # Internal variables --------------------------------------------------
        self.xrf_scan = queue_model_objects.XRFScan()
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        _top_widget = QtGui.QWidget(self)
        _parameters_widget = QtGui.QWidget(_top_widget)
        self.data_path_widget = DataPathWidget(_parameters_widget)
        self.other_parameters_gbox = QtGui.QGroupBox("Other parameters", _parameters_widget) 
        self.count_time_label = QtGui.QLabel("Count time:", 
                                             self.other_parameters_gbox)
	self.count_time_ledit = QtGui.QLineEdit(self.other_parameters_gbox)
	self.count_time_ledit.setFixedWidth(50)
        self.position_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                          'ui_files/Qt4_snapshot_widget_layout.ui'))
        self.mca_spectrum_widget = McaSpectrumWidget(self)
 
        # Layout -------------------------------------------------------------
        self.other_parameters_gbox_layout = QtGui.QHBoxLayout(self)
        self.other_parameters_gbox_layout.addWidget(self.count_time_label)  
        self.other_parameters_gbox_layout.addWidget(self.count_time_ledit)
        self.other_parameters_gbox_layout.addStretch(0)
        self.other_parameters_gbox_layout.setSpacing(2)
        self.other_parameters_gbox_layout.setContentsMargins(3, 3, 3, 3)
        self.other_parameters_gbox.setLayout(self.other_parameters_gbox_layout)

        _parameters_widget_layout = QtGui.QVBoxLayout()
        _parameters_widget_layout.addWidget(self.data_path_widget)
        _parameters_widget_layout.addWidget(self.other_parameters_gbox)
        _parameters_widget_layout.addStretch(0)
        _parameters_widget_layout.setSpacing(2)
        _parameters_widget_layout.setContentsMargins(0, 0, 0, 0)
        _parameters_widget.setLayout(_parameters_widget_layout)

        _top_widget_layout = QtGui.QHBoxLayout(_top_widget)
        _top_widget_layout.addWidget(_parameters_widget)
        _top_widget_layout.addWidget(self.position_widget)
        _top_widget_layout.setSpacing(2)
        _top_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        _top_widget.setLayout(_top_widget_layout) 

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_top_widget)
        _main_vlayout.addWidget(self.mca_spectrum_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)
       
        # SizePolicies -------------------------------------------------------
        self.position_widget.setFixedSize(457, 350)
        self.mca_spectrum_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                               QtGui.QSizePolicy.Expanding)
        _top_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Fixed)
        #self.mca_spectrum_widget.setMinimumHeight(800)
        #self.setSizePolicy(QtGui.QSizePolicy.Expanding,
        #                   QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------ 
        QtCore.QObject.connect(self.data_path_widget.data_path_layout.\
                               findChild(QtGui.QLineEdit, 'prefix_ledit'), 
                               QtCore.SIGNAL("textChanged(const QString &)"), 
                               self._prefix_ledit_change)

        QtCore.QObject.connect(self.data_path_widget.data_path_layout.\
                               findChild(QtGui.QLineEdit, 'run_number_ledit'), 
                               QtCore.SIGNAL("textChanged(const QString &)"), 
                               self._run_number_ledit_change)

        QtCore.QObject.connect(self.count_time_ledit,
                               QtCore.SIGNAL("textChanged(const QString &)"),
                               self._count_time_ledit_change)
        
        #QtCore.QObject.connect(.qApp, qt.PYSIGNAL('tab_changed'),
        #                   self.tab_changed)

        # Other ---------------------------------------------------------------
        Qt4_widget_colors.set_widget_color(self.other_parameters_gbox,
                                           Qt4_widget_colors.GROUP_BOX_GRAY)
        Qt4_widget_colors.set_widget_color(self.data_path_widget,
                                           Qt4_widget_colors.GROUP_BOX_GRAY) 
        Qt4_widget_colors.set_widget_color(self.position_widget, 
                                           Qt4_widget_colors.GROUP_BOX_GRAY)

    def _prefix_ledit_change(self, new_value):
        self.xrf_scan.set_name(str(new_value))
        self._tree_view_item.setText(0, self.xrf_scan.get_display_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_scan.set_number(int(new_value))
            self._tree_view_item.setText(0, self.xrf_scan.get_display_name())

    def _count_time_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_scan.set_count_time(float(new_value))
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        self.xrf_scan = item.get_model()
        executed = self.xrf_scan.is_executed()

        self.data_path_widget.setEnabled(not executed)
        self.other_parameters_gbox.setEnabled(not executed)    
        self.mca_spectrum_widget.setEnabled(executed)        
 
        if executed:
            result = self.xrf_scan.get_scan_result()
            self.mca_spectrum_widget.setData(result.mca_data, result.mca_calib, result.mca_config) 
        else:
            self.mca_spectrum_widget.clear()
        
        self.data_path_widget.update_data_model(self.xrf_scan.path_template)  
        self.count_time_ledit.setText(str(self.xrf_scan.count_time)) 

        image = self.xrf_scan.centred_position.snapshot_image
        if image:
            try:
               image = image.scale(427, 320)
               self.position_widget.child("svideo").setPixmap(qt.QPixmap(image))
            except:
               pass 

    def set_xrf_scan_hwobj(self, xrf_scan_hwobj):
        self.xrf_scan_hwobj = xrf_scan_hwobj
        if self.xrf_scan_hwobj:
            self.xrf_scan_hwobj.connect("xrfScanFinished", self.scan_finished)

    def scan_finished(self, mcaData, mcaCalib, mcaConfig):
        self.mca_spectrum_widget.setData(mcaData, mcaCalib, mcaConfig)
 
