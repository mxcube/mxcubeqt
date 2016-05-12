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
from widgets.Qt4_heat_map_widget import HeatMapWidget


class AdvancedResultsWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName('advanced_results_widget')  

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._tree_view_item = None
        self._half_widget_size = 900

        # Graphic elements ----------------------------------------------------
        _snapshot_widget = QtGui.QWidget(self)
        self.position_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'ui_files/Qt4_snapshot_widget_layout.ui'))
        self.heat_map_widget = HeatMapWidget(self)

        # Layout --------------------------------------------------------------
        _snapshots_vlayout = QtGui.QVBoxLayout(_snapshot_widget)
        _snapshots_vlayout.addWidget(self.position_widget)
        _snapshots_vlayout.setContentsMargins(0, 0, 0, 0)
        _snapshots_vlayout.setSpacing(0)
        _snapshots_vlayout.addStretch(0)

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(self.heat_map_widget)
        _main_hlayout.addWidget(_snapshot_widget)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        _main_hlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def set_beamline_setup(self, bl_setup):
        if hasattr(bl_setup, 'parallel_processing_hwobj'):
            if bl_setup.parallel_processing_hwobj:
                bl_setup.parallel_processing_hwobj.connect(
                         'paralleProcessingResults', 
                         self.set_processing_results)
        self.heat_map_widget.set_beamline_setup(bl_setup)

    def populate_widget(self, item):
        advanced = item.get_model()
        data_collection = advanced.reference_image_collection

        executed = advanced.is_executed()
        associated_grid = advanced.get_associated_grid()

        self.heat_map_widget.clean_result()
        self.heat_map_widget.set_associated_data_collection(data_collection)
        self.heat_map_widget.set_associated_grid(associated_grid)
     
        if executed: 
            processing_results = advanced.get_first_processing_results()
            if processing_results is not None: 
                self.heat_map_widget.set_results(processing_results, True)    

        if associated_grid:
            try:
               image = associated_grid.get_snapshot()
               ratio = image.height() / float(image.width())
               image = image.scaled(600, 600 * ratio, QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)
               self.position_widget.svideo.setPixmap(QtGui.QPixmap(image))    
            except:
               pass
 
    def set_processing_results(self, processing_results, param, last_results):
        self.heat_map_widget.set_results(processing_results, last_results)
