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

from QtImport import *

import queue_model_objects_v1 as queue_model_objects

import Qt4_queue_item
from widgets.Qt4_widget_utils import DataModelInputBinder
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget


class AdvancedParametersWidget(QWidget):
    def __init__(self, parent = None, name = "advanced_parameters_widget"):
        QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------
        self._queue_model_hwobj = None
        self._beamline_setup_hwobj = None

        # Internal values -----------------------------------------------------
        self._data_collection = None
        self._tree_view_item = None

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _dc_parameters_widget = QWidget(self)
        self._data_path_widget = DataPathWidget(_dc_parameters_widget)
        self._acq_widget = AcquisitionWidget(_dc_parameters_widget,
                                            layout = 'horizontal')

        # Layout --------------------------------------------------------------
        _dc_parameters_widget_layout = QVBoxLayout(_dc_parameters_widget)
        _dc_parameters_widget_layout.addWidget(self._data_path_widget)
        _dc_parameters_widget_layout.addWidget(self._acq_widget)
        _dc_parameters_widget_layout.setSpacing(2)
        _dc_parameters_widget_layout.addStretch(10)
        _dc_parameters_widget_layout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(_dc_parameters_widget)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)
        _main_hlayout.addStretch(0)

        # Qt signal/slot connections ------------------------------------------
        #self._acq_widget.acqParametersChangedSignal.\
        #     connect(self.acq_parameters_changed)
        #self._data_path_widget.pathTemplateChangedSignal.\
        #     connect(self.acq_parameters_changed)
        self._acq_widget.madEnergySelectedSignal.connect(\
             self.mad_energy_selected)

        # Ohter ---------------------------------------------------------------
        self._acq_widget.use_osc_start(False)
        self._acq_widget.acq_widget_layout.mad_cbox.hide()
        self._acq_widget.acq_widget_layout.energies_combo.hide()
        self._acq_widget.acq_widget_layout.shutterless_cbx.hide()

    def set_beamline_setup(self, bl_setup):
        self._beamline_setup_hwobj = bl_setup
        self._acq_widget.set_beamline_setup(bl_setup)

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
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, tree_view_item, data_collection):
        self._tree_view_item = tree_view_item
        self._data_collection = data_collection

        #if isinstance(tree_view_item, Qt4_queue_item.XrayCenteringQueueItem):
        #    self._data_collection = tree_view_item.get_model().reference_image_collection
        #else:
        #    self._data_collection = tree_view_item.get_model()
        executed = self._data_collection.is_executed()

        self._acq_widget.setEnabled(not executed)
        self._data_path_widget.setEnabled(not executed)

        self._acquisition_mib = DataModelInputBinder(self._data_collection.\
             acquisitions[0].acquisition_parameters)

        # The acq_widget sends a signal to the path_widget, and it relies
        # on that both models upto date, we need to refactor this part
        # so that both models are set before taking ceratin actions.
        # This workaround, works for the time beeing.
        self._data_path_widget._data_model = self._data_collection.\
             acquisitions[0].path_template
        self._data_path_widget.update_data_model(self._data_collection.\
              acquisitions[0].path_template)

        self._acq_widget.update_data_model(\
             self._data_collection.acquisitions[0].acquisition_parameters,
             self._data_collection.acquisitions[0].path_template)
        #self._acq_widget.use_osc_start(False)

        self._acq_widget.acq_widget_layout.num_images_ledit.setDisabled(data_collection.is_mesh())
        invalid = self._acquisition_mib.validate_all()
        if invalid:
            msg = "This data collection has one or more incorrect parameters,"+\
                  " correct the fields marked in red to solve the problem."
            logging.getLogger("GUI").warning(msg)
