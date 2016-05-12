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


class XRFSpectrumParametersWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "xrf_spectrum_parameters_widget"):
        QtGui.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self.xrf_spectrum_hwobj = None

        # Internal variables --------------------------------------------------
        self.xrf_spectrum_model = queue_model_objects.XRFSpectrum()
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
        self.adjust_transmission_cbox = QtGui.QCheckBox("Adjust transmission", \
             self.other_parameters_gbox)
        self.adjust_transmission_cbox.hide()
        _snapshot_widget = QtGui.QWidget(self)
        self.position_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                          'ui_files/Qt4_snapshot_widget_layout.ui'))
        self.mca_spectrum_widget = McaSpectrumWidget(self)
 
        # Layout -------------------------------------------------------------
        _other_parameters_gbox_hlayout = QtGui.QHBoxLayout(self.other_parameters_gbox)
        _other_parameters_gbox_hlayout.addWidget(self.count_time_label)  
        _other_parameters_gbox_hlayout.addWidget(self.count_time_ledit)
        _other_parameters_gbox_hlayout.addWidget(self.adjust_transmission_cbox)
        _other_parameters_gbox_hlayout.addStretch(0)
        _other_parameters_gbox_hlayout.setSpacing(2)
        _other_parameters_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _parameters_widget_layout = QtGui.QVBoxLayout(_parameters_widget)
        _parameters_widget_layout.addWidget(self.data_path_widget)
        _parameters_widget_layout.addWidget(self.other_parameters_gbox)
        _parameters_widget_layout.addStretch(0)
        _parameters_widget_layout.setSpacing(2)
        _parameters_widget_layout.setContentsMargins(0, 0, 0, 0)

        #_snapshots_vlayout = QtGui.QVBoxLayout(_snapshot_widget)
        #_snapshots_vlayout.addWidget(self.position_widget)
        #_snapshots_vlayout.setContentsMargins(0, 0, 0, 0)
        #_snapshots_vlayout.setSpacing(2)
        #_snapshots_vlayout.addStretch(0)

        _top_widget_layout = QtGui.QHBoxLayout(_top_widget)
        _top_widget_layout.addWidget(_parameters_widget)
        _top_widget_layout.addWidget(self.position_widget)
        _top_widget_layout.setSpacing(2)
        _top_widget_layout.addStretch(0)
        _top_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_top_widget)
        _main_vlayout.addWidget(self.mca_spectrum_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
       
        # SizePolicies -------------------------------------------------------
        self.position_widget.setFixedSize(457, 350)
        self.mca_spectrum_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                               QtGui.QSizePolicy.Expanding)
        _top_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------ 
        self.data_path_widget.data_path_layout.prefix_ledit.\
             textChanged.connect(self._prefix_ledit_change)

        self.data_path_widget.data_path_layout.run_number_ledit.\
             textChanged.connect(self._run_number_ledit_change)

        self.count_time_ledit.textChanged.connect(self._count_time_ledit_change)
        
        # Other ---------------------------------------------------------------


    def _prefix_ledit_change(self, new_value):
        self.xrf_spectrum_model.set_name(str(new_value))
        self._tree_view_item.setText(0, self.xrf_spectrum_model.get_display_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_spectrum_model.set_number(int(new_value))
            self._tree_view_item.setText(0, self.xrf_spectrum_model.get_display_name())

    def _count_time_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_spectrum_model.set_count_time(float(new_value))
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        self.xrf_spectrum_model = item.get_model()
        executed = self.xrf_spectrum_model.is_executed()

        self.data_path_widget.setEnabled(not executed)
        self.other_parameters_gbox.setEnabled(not executed)    
        #self.mca_spectrum_widget.setEnabled(executed)        
 
        if executed:
            result = self.xrf_spectrum_model.get_spectrum_result()
            self.mca_spectrum_widget.set_data(result.mca_data, result.mca_calib, result.mca_config) 
        else:
            self.mca_spectrum_widget.clear()
        
        self.data_path_widget.update_data_model(self.xrf_spectrum_model.path_template)  
        self.count_time_ledit.setText(str(self.xrf_spectrum_model.count_time)) 

        image = self.xrf_spectrum_model.centred_position.snapshot_image
        if image is not None:
            try:
               ration = image.height() / float(image.width())
               image = image.scaled(400, 400 * ration, QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)
               self.position_widget.svideo.setPixmap(QtGui.QPixmap(image))
            except:
               pass

    def set_xrf_spectrum_hwobj(self, xrf_spectrum_hwobj):
        self.xrf_spectrum_hwobj = xrf_spectrum_hwobj
        if self.xrf_spectrum_hwobj:
            self.xrf_spectrum_hwobj.connect("xrfSpectrumFinished", self.spectrum_finished)

    def spectrum_finished(self, mca_data, mca_calib, mca_config):
        self.mca_spectrum_widget.set_data(mca_data, mca_calib, mca_config)

