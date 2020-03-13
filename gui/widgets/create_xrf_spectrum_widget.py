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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

import copy
import logging

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.comments_widget import CommentsWidget

from HardwareRepository.HardwareObjects import queue_model_objects
from HardwareRepository.HardwareObjects.QtGraphicsLib import GraphicsItemPoint

from HardwareRepository import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateXRFSpectrumWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):

        CreateTaskBase.__init__(
            self, parent, name, QtImport.Qt.WindowFlags(fl), "XRF spectrum"
        )

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.count_time = None
        self.xrf_spectrum_model = None

        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._data_path_widget = DataPathWidget(
            self, data_model=self._path_template, layout="vertical"
        )

        _parameters_gbox = QtImport.QGroupBox("Parameters", self)
        _count_time_label = QtImport.QLabel("Count time (sec.):", _parameters_gbox)
        self.count_time_ledit = QtImport.QLineEdit("1", _parameters_gbox)
        # self.count_time_ledit.setMaximumWidth(75)
        self.adjust_transmission_cbox = QtImport.QCheckBox(
            "Adjust transmission", _parameters_gbox
        )
        self.adjust_transmission_cbox.setChecked(True)

        self._comments_widget = CommentsWidget(self)

        # Layout --------------------------------------------------------------
        _parameters_gbox_hlayout = QtImport.QHBoxLayout(_parameters_gbox)
        _parameters_gbox_hlayout.addWidget(_count_time_label)
        _parameters_gbox_hlayout.addWidget(self.count_time_ledit)
        _parameters_gbox_hlayout.addWidget(self.adjust_transmission_cbox)
        _parameters_gbox_hlayout.addStretch(0)
        _parameters_gbox_hlayout.setSpacing(2)
        _parameters_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(_parameters_gbox)
        _main_vlayout.addWidget(self._comments_widget)
        _main_vlayout.setSpacing(6)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------
        self._comments_widget.setFixedHeight(100)

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )
        self.adjust_transmission_cbox.stateChanged.connect(
            self.adjust_transmission_state_changed
        )

        # Other ---------------------------------------------------------------
        self._data_path_widget.data_path_layout.compression_cbox.setVisible(False)

    def set_expert_mode(self, state):
        self.adjust_transmission_cbox.setEnabled(state)

    def enable_compression(self, state):
        CreateTaskBase.enable_compression(self, False)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self.xrf_spectrum_model = queue_model_objects.XRFSpectrum()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = "raw"
        self._path_template.compression = False

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        self.xrf_spectrum_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.XRFSpectrumQueueItem):
            if self.xrf_spectrum_model.is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if self.xrf_spectrum_model.get_path_template():
                self._path_template = self.xrf_spectrum_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not (
            isinstance(tree_item, queue_item.SampleQueueItem)
            or isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)
        ):
            self.setDisabled(True)

    def approve_creation(self):
        # base_result = CreateTaskBase.approve_creation(self)
        base_result = True
        self.count_time = None

        try:
            self.count_time = float(str(self.count_time_ledit.text()))
        except BaseException:
            logging.getLogger("GUI").error("Incorrect count time value.")

        return base_result and self.count_time

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.

    def _create_task(self, sample, shape, comments=None):
        data_collections = []

        if self.count_time is not None:
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = HWR.beamline.sample_view.get_scene_snapshot()
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, GraphicsItemPoint):
                    snapshot = HWR.beamline.sample_view.get_scene_snapshot(shape)

                    cpos = copy.deepcopy(shape.get_centred_position())
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)

            xrf_spectrum = queue_model_objects.XRFSpectrum(sample, path_template, cpos)
            xrf_spectrum.set_name(path_template.get_prefix())
            xrf_spectrum.set_number(path_template.run_number)
            xrf_spectrum.count_time = self.count_time
            xrf_spectrum.adjust_transmission = self.adjust_transmission_cbox.isChecked()

            data_collections.append(xrf_spectrum)
        else:
            logging.getLogger("GUI").error("No count time specified.")

        return data_collections

    def adjust_transmission_state_changed(self, state):
        self.xrf_spectrum_model.adjust_transmission = state > 0
