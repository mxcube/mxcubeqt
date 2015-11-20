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
import copy

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import Qt4_queue_item
import Qt4_GraphicsManager
import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables

from widgets.Qt4_widget_utils import DataModelInputBinder
from Qt4_create_task_base import CreateTaskBase
from Qt4_data_path_widget import DataPathWidget
from Qt4_acquisition_widget_simple import AcquisitionWidgetSimple
from queue_model_enumerables_v1 import XTAL_SPACEGROUPS


class CreateCharWidget(CreateTaskBase):
    """
    Descript. :
    """

    def __init__(self,parent = None,name = None, fl = 0):
        """
        Descript. :
        """

        CreateTaskBase.__init__(self, parent, name, fl, 'Characterisation')
        self.setObjectName("create_char_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._current_selected_item = None
        self.init_models()
        self._char_params_mib = DataModelInputBinder(self._char_params)
   
        # Graphic elements ----------------------------------------------------
        self._acq_widget = \
            AcquisitionWidgetSimple(self, acq_params = self._acquisition_parameters,
                                    path_template = self._path_template)

        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_widget = DataPathWidget(
                               self._data_path_gbox,
                               data_model = self._path_template,
                               layout = 'vertical')

        self._vertical_dimension_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'ui_files/Qt4_vertical_crystal_dimension_widget_layout.ui'))
        
        self._char_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'ui_files/Qt4_characterise_simple_widget_vertical_layout.ui')) 

        # Layout --------------------------------------------------------------
        _data_path_gbox_layout = QtGui.QVBoxLayout(self._data_path_gbox)
        _data_path_gbox_layout.addWidget(self._data_path_widget)
        _data_path_gbox_layout.setSpacing(0)
        _data_path_gbox_layout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self) 
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_gbox)
        _main_vlayout.addWidget(self._char_widget)
        _main_vlayout.addWidget(self._vertical_dimension_widget)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.pathTemplateChangedSignal.connect(\
             self.handle_path_conflict)
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.\
             connect(self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)

        self._vertical_dimension_widget.space_group_ledit.activated.\
             connect(self._space_group_change)
        #self.connect(induced_burn_cbx, QtCore.SIGNAL("toggled(bool)"),
        #             self.use_induced_burn)

        self._char_widget.characterisation_gbox.toggled.connect(\
             self.characterisation_gbox_toggled)
        # Other ---------------------------------------------------------------
        self._char_params_mib.bind_value_update(
             'opt_sad', self._char_widget.optimised_sad_cbx,
             bool, None)

        self._char_params_mib.bind_value_update(
             'account_rad_damage', self._char_widget.account_rad_dmg_cbx,
             bool, None)

        #self._char_params_mib.bind_value_update('determine_rad_params', 
        #                                        induced_burn_cbx,
        #                                        bool, None)

        self._char_params_mib.bind_value_update(
             'strategy_complexity', self._char_widget.start_comp_cbox,
             int, None)

        self._char_params_mib.\
            bind_value_update('max_crystal_vdim',
                              self._vertical_dimension_widget.max_vdim_ledit, float,
                              QtGui.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('min_crystal_vdim',
                              self._vertical_dimension_widget.min_vdim_ledit, float,
                              QtGui.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('min_crystal_vphi',
                              self._vertical_dimension_widget.min_vphi_ledit, float,
                              QtGui.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('max_crystal_vphi',
                              self._vertical_dimension_widget.max_vphi_ledit, float,
                              QtGui.QDoubleValidator(0.0, 1000, 2, self))
        
        self._vertical_dimension_widget.space_group_ledit.addItems(XTAL_SPACEGROUPS)

    def use_induced_burn(self, state):
        """
        Descript. :
        """
        self._acquisition_parameters.induce_burn = state

    def _space_group_change(self, index):
        """
        Descript. :
        """
        self._char_params.space_group = queue_model_enumerables.\
                                        XTAL_SPACEGROUPS[index]
    def _set_space_group(self, space_group):
        """
        Descript. :
        """
        index  = 0
        
        if space_group in XTAL_SPACEGROUPS:
            index = XTAL_SPACEGROUPS.index(space_group)

        self._space_group_change(index)
        self._vertical_dimension_widget.space_group_ledit.setCurrentIndex(index)

    def init_models(self):
        """
        Descript. :
        """
        CreateTaskBase.init_models(self)
        self._init_models()

    def _init_models(self):
        """
        Descript. :
        """
        self._char = queue_model_objects.Characterisation()
        self._char_params = self._char.characterisation_parameters
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:            
            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_char_acq_parameters()

            self._char_params = self._beamline_setup_hwobj.\
                                get_default_characterisation_parameters()
            try:
                transmission = self._beamline_setup_hwobj.transmission_hwobj.getAttFactor()
                transmission = round(float(transmission), 1)
            except AttributeError:
                transmission = 0

            try:
                resolution = self._beamline_setup_hwobj.resolution_hwobj.getPosition()
                resolution = round(float(resolution), 3)
            except AttributeError:
                resolution = 0

            try:
                energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
                energy = round(float(energy), 4)
            except AttributeError:
                energy = 0

            self._acquisition_parameters.resolution = resolution
            self._acquisition_parameters.energy = energy
            self._acquisition_parameters.transmission = transmission
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
        
        self._path_template.reference_image_prefix = 'ref'
        # The num images drop down default value is 1
        # we would like it to be 2
        self._acquisition_parameters.num_images = 2
        self._char.characterisation_software =\
            queue_model_enumerables.COLLECTION_ORIGIN.EDNA
        self._path_template.num_files = 2
        self._acquisition_parameters.shutterless = False

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)
        
        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            self._init_models()
            self._set_space_group(self._char_params.space_group)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                                self._path_template)
            self._char_params_mib.set_model(self._char_params)
            #self._char_params = copy.deepcopy(self._char_params)
            #self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)
        elif isinstance(tree_item, Qt4_queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif isinstance(tree_item, Qt4_queue_item.CharacterisationQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            self._char = tree_item.get_model()

            if self._char.get_path_template():
                self._path_template = self._char.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
            
            data_collection = self._char.reference_image_collection

            self._char_params = self._char.characterisation_parameters
            self._char_params_mib.set_model(self._char_params)

            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters

            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
            self.get_acquisition_widget().use_osc_start(True)

            if len(data_collection.acquisitions) == 1:
                self.select_shape_with_cpos(self._acquisition_parameters.\
                                            centred_position)

            self._processing_parameters = data_collection.processing_parameters
        else:
            self.setDisabled(True)

    def update_processing_parameters(self, crystal):
        """
        Descript. :
        """
        self._processing_parameters.space_group = crystal.space_group
        self._char_params.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)
        selected_shapes = self._graphics_manager_hwobj.get_selected_shapes()

        for shape in selected_shapes:
            if isinstance(shape, Qt4_GraphicsManager.GraphicsItemPoint):
                result = True
        return result
        
    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. when a data collection group is selected.
    def _create_task(self, sample, shape):
        """
        Descript. :
        """
        tasks = []

        if not shape or not isinstance(shape, Qt4_GraphicsManager.GraphicsItemPoint):
            cpos = queue_model_objects.CentredPosition()
            cpos.snapshot_image = self._graphics_manager_hwobj.get_snapshot()
        else:
            # Shapes selected and sample is mounted, get the
            # centred positions for the shapes
            snapshot = self._graphics_manager_hwobj.\
                        get_snapshot(shape)
            cpos = copy.deepcopy(shape.get_centred_position())
            cpos.snapshot_image = snapshot 

        char_params = copy.deepcopy(self._char_params)
        acq = self._create_acq(sample)
        dc = queue_model_objects.\
                DataCollection([acq], sample.crystals[0],
                               self._processing_parameters)

        # Reference images for characterisations should be taken 90 deg apart
        # this is achived by setting overap to -89
        acq.acquisition_parameters.overlap = -89
        acq.acquisition_parameters.centred_position = cpos        
        
        dc.acquisitions[0] = acq
        dc.experiment_type = queue_model_enumerables.EXPERIMENT_TYPE.EDNA_REF

        char = queue_model_objects.Characterisation(dc, 
                                                    char_params)
        char.set_name(dc.acquisitions[0].\
                      path_template.get_prefix())
        char.set_number(dc.acquisitions[0].\
                        path_template.run_number)
        char.run_characterisation = self._char_widget.characterisation_gbox.isChecked()

        tasks.append(char)
        self._path_template.run_number += 1

        return tasks

    def characterisation_gbox_toggled(self, state):
        if self._char:
            self._char.run_characterisation = state
