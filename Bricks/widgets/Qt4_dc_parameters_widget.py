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
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from widgets.Qt4_widget_utils import DataModelInputBinder
from widgets.Qt4_processing_widget import ProcessingWidget

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework import Qt4_Icons


__category__ = 'Qt4_TaskToolbox_Tabs'


class DCParametersWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "parameter_widget"):

        QtGui.QWidget.__init__(self, parent)
        if name is not None:
            self.setObjectName(name) 

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None

        # Internal variables --------------------------------------------------
        self._data_collection = None
        self.add_dc_cb = None
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        _dc_parameters_widget = QtGui.QWidget(self)
        self._data_path_widget = DataPathWidget(_dc_parameters_widget)
        self._acq_widget = AcquisitionWidget(_dc_parameters_widget, 
                                            layout = 'horizontal')
        #self._acq_widget.setFixedHeight(170)
        self._processing_widget = ProcessingWidget(_dc_parameters_widget)
        _snapshot_widget = QtGui.QWidget(self)
        self.position_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                          'ui_files/Qt4_snapshot_widget_layout.ui'))
        
        # Layout --------------------------------------------------------------
        _dc_parameters_widget_layout = QtGui.QVBoxLayout(_dc_parameters_widget)
        _dc_parameters_widget_layout.addWidget(self._data_path_widget)
        _dc_parameters_widget_layout.addWidget(self._acq_widget)
        _dc_parameters_widget_layout.addWidget(self._processing_widget)
        _dc_parameters_widget_layout.setContentsMargins(0, 0, 0, 0)
        _dc_parameters_widget_layout.setSpacing(2)
        _dc_parameters_widget_layout.addStretch(0)

        _snapshots_vlayout = QtGui.QVBoxLayout(_snapshot_widget)
        _snapshots_vlayout.addWidget(self.position_widget)
        _snapshots_vlayout.setContentsMargins(0, 0, 0, 0)
        _snapshots_vlayout.setSpacing(2)
        _snapshots_vlayout.addStretch(10)

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(_dc_parameters_widget)
        _main_hlayout.addWidget(_snapshot_widget)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        _main_hlayout.setSpacing(2)
        _main_hlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------
        

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.connect(
                     self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.connect( 
                     self._run_number_ledit_change)
        self._acq_widget.madEnergySelectedSignal.connect(self.mad_energy_selected)
        self._acq_widget.acqParametersChangedSignal.connect(\
             self.acq_parameters_changed)

        # Other ---------------------------------------------------------------

    def set_beamline_setup(self, bl_setup):
        self._acq_widget.set_beamline_setup(bl_setup)
        self._beamline_setup_hwobj = bl_setup

    def _prefix_ledit_change(self, new_value):
        prefix = self._data_collection.acquisitions[0].\
                 path_template.get_prefix()
        self._data_collection.set_name(prefix)
        self._tree_view_item.setText(0, self._data_collection.get_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._data_collection.set_number(int(new_value))
            self._tree_view_item.setText(0, self._data_collection.get_name())

    def acq_parameters_changed(self):
        if self._tree_view_item is None:
            #TODO fix this
            return 
        dc_tree_widget = self._tree_view_item.listView().parent()
        dc_tree_widget.check_for_path_collisions()
        path_template = self._data_collection.acquisitions[0].path_template
        path_conflict = self.queue_model_hwobj.\
                        check_for_path_collisions(path_template)
        if new_value != '':
            if path_conflict:
                logging.getLogger("user_level_log").\
                    error('The current path settings will overwrite data' +\
                          ' from another task. Correct the problem before collecting')

                widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            else:
                widget.setPaletteBackgroundColor(widget_colors.WHITE)

    def __add_data_collection(self):
        return self.add_dc_cb(self._data_collection, self.collection_type)
    
    def mad_energy_selected(self, name, energy, state):
        path_template = self._data_collection.acquisitions[0].path_template

        if state:
            path_template.mad_prefix = name
        else:
            path_template.mad_prefix = ''

        run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
          get_next_run_number(path_template)

        self._data_path_widget.set_run_number(run_number)
        self._data_path_widget.set_prefix(path_template.base_prefix)
        model = self._tree_view_item.get_model()
        model.set_name(path_template.get_prefix())
        self._tree_view_item.setText(0, model.get_name())
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_parameter_widget(self._tree_view_item)

    def set_enabled(self, state):
        self._acq_widget.setEnabled(state)
        self._data_path_widget.setEnabled(state)
        self._processing_widget.setEnabled(state)

    def populate_widget(self, item):
        data_collection = item.get_model()
        self._tree_view_item = item
        self._data_collection = data_collection
        self._acquisition_mib = DataModelInputBinder(self._data_collection.\
                                                         acquisitions[0].acquisition_parameters)

        # The acq_widget sends a signal to the path_widget, and it relies
        # on that both models upto date, we need to refactor this part
        # so that both models are set before taking ceratin actions.
        # This workaround, works for the time beeing.
        self._data_path_widget._data_model = data_collection.acquisitions[0].path_template

        self._acq_widget.set_energies(data_collection.crystal.energy_scan_result)
        self._acq_widget.update_data_model(data_collection.acquisitions[0].\
                                          acquisition_parameters,
                                          data_collection.acquisitions[0].\
                                          path_template)
        self._data_path_widget.update_data_model(data_collection.\
                                           acquisitions[0].path_template)
        
        self._processing_widget.update_data_model(data_collection.\
                                                 processing_parameters)

        if data_collection.acquisitions[0].acquisition_parameters.\
                centred_position.snapshot_image:
            image = data_collection.acquisitions[0].\
                acquisition_parameters.centred_position.snapshot_image
            ration = image.height() / float(image.width())
            image = image.scaled(400, 400 * ration, QtCore.Qt.KeepAspectRatio)
            self.position_widget.svideo.setPixmap(QtGui.QPixmap(image))

        invalid = self._acquisition_mib.validate_all()

        if invalid:
            msg = "This data collection has one or more incorrect parameters,"+\
                " correct the fields marked in red to solve the problem."

            logging.getLogger("user_level_log").\
                warning(msg)
