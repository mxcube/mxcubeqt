#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import copy

import  QtImport

from gui.utils import queue_item
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.acquisition_widget import AcquisitionWidget
from gui.widgets.xray_imaging_parameters_widget import XrayImagingParametersWidget

from HardwareRepository.HardwareObjects.Qt4_GraphicsLib import GraphicsItemPoint
from HardwareRepository.HardwareObjects import queue_model_objects, queue_model_enumerables


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


class CreateXrayImagingWidget(CreateTaskBase):
    """Widget used to create xray imaging method
    """

    def __init__(self, parent=None,name=None, fl=0):
        CreateTaskBase.__init__(self, parent, name, 
            QtImport.Qt.WindowFlags(fl), 'XrayImaging')

        if not name:
            self.setObjectName("create_xray_imaging_widget")

        # Hardware objects ----------------------------------------------------
 
        # Internal variables --------------------------------------------------
        self._xray_imaging_parameters = None
        self._processing_parameters = None
        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._xray_imaging_parameters_widget = XrayImagingParametersWidget(\
             self, 'xray_imaging_widget',
             xray_imaging_params=self._xray_imaging_parameters)

        self._acq_widget =  AcquisitionWidget(self, "acquisition_widget",
             layout='vertical', acq_params=self._acquisition_parameters,
             path_template=self._path_template)
        self._acq_widget.grid_mode = False

        self._data_path_widget = DataPathWidget(self, 'create_dc_path_widget', 
             data_model=self._path_template, layout='vertical')

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._xray_imaging_parameters_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(6)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._acq_widget.acqParametersChangedSignal.\
             connect(self.acq_parameters_changed)
        self._data_path_widget.pathTemplateChangedSignal.\
             connect(self.path_template_changed)

        # Other ---------------------------------------------------------------
        self._acq_widget.use_osc_start(False)
        self._acq_widget.use_kappa(False)
        self._acq_widget.acq_widget_layout.max_osc_range_cbx.setVisible(False)
        self._acq_widget.acq_widget_layout.first_image_label.setVisible(False)
        self._acq_widget.acq_widget_layout.first_image_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.detector_roi_mode_label.setVisible(False)
        self._acq_widget.acq_widget_layout.detector_roi_mode_combo.setVisible(False)
        self._acq_widget.acq_widget_layout.energies_combo.setVisible(False)
        self._acq_widget.acq_widget_layout.mad_cbox.setVisible(False)
        self._acq_widget.acq_widget_layout.energy_label.setVisible(False)
        self._acq_widget.acq_widget_layout.energy_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.transmission_label.setVisible(False)
        self._acq_widget.acq_widget_layout.transmission_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.resolution_label.setVisible(False)
        self._acq_widget.acq_widget_layout.resolution_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.kappa_label.setVisible(False)
        self._acq_widget.acq_widget_layout.kappa_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.kappa_phi_label.setVisible(False)
        self._acq_widget.acq_widget_layout.kappa_phi_ledit.setVisible(False)
        self._acq_widget.acq_widget_layout.shutterless_cbx.setVisible(False)

    def approve_creation(self):
        return True

    def enable_compression(self, state):
        CreateTaskBase.enable_compression(self, False)

    def init_models(self):
        """
        Descript. :
        """
        CreateTaskBase.init_models(self)

        self._xray_imaging_parameters = queue_model_objects.XrayImagingParameters()
        if self._beamline_setup_hwobj is not None:
            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters("default_imaging_values")
            self._path_template.suffix = 'tiff'

    def set_beamline_setup(self, bl_setup_hwobj):
        """
        In plate mode osciallation is start is in the middle of grid
        """
        CreateTaskBase.set_beamline_setup(self, bl_setup_hwobj)

        self._xray_imaging_parameters_widget.set_beamline_setup(bl_setup_hwobj)
        bl_setup_hwobj.detector_distance_hwobj.connect(
             'positionChanged',
             self._xray_imaging_parameters_widget.set_detector_distance)

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)
        self.setDisabled(True)

        if isinstance(tree_item, queue_item.SampleQueueItem):
            self._xray_imaging_parameters = copy.deepcopy(self._xray_imaging_parameters)
            self._xray_imaging_parameters_widget.update_data_model(\
                 self._xray_imaging_parameters)
            self._xray_imaging_parameters_widget.set_detector_distance(
                 self._beamline_setup_hwobj.detector_distance_hwobj.get_position()
            )
            self.setDisabled(False)
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif isinstance(tree_item, queue_item.XrayImagingQueueItem):
            data_model= tree_item.get_model()

            self._path_template = data_model.get_path_template()
            self._data_path_widget.update_data_model(self._path_template)

            self._acquisition_parameters = data_model.acquisition.acquisition_parameters
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)

            self._xray_imaging_parameters = data_model.xray_imaging_parameters
            self._xray_imaging_parameters_widget.update_data_model(self._xray_imaging_parameters)
    

            self.setDisabled(False)

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        """
        Descript. :
        """
        if isinstance(shape, GraphicsItemPoint):
            snapshot = self._graphics_manager_hwobj.get_scene_snapshot(shape)
            cpos = copy.deepcopy(shape.get_centred_position())
            cpos.snapshot_image = snapshot
        else:
            cpos = queue_model_objects.CentredPosition()
            cpos.snapshot_image = self._graphics_manager_hwobj.get_scene_snapshot()

        #self._path_template.run_number += 1
        xray_imaging_parameters = copy.deepcopy(self._xray_imaging_parameters) 
        acq = self._create_acq(sample)
        acq.acquisition_parameters.centred_position = cpos

        dc = queue_model_objects.XrayImaging(xray_imaging_parameters,
                                             acq,
                                             sample.crystals[0])
        dc.set_name(acq.path_template.get_prefix())
        dc.set_number(acq.path_template.run_number)

        return [dc]
