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

from mxcubeqt.utils import queue_item, qt_import
from mxcubeqt.base_components import BaseWidget
from mxcubeqt.widgets.advanced_parameters_widget import AdvancedParametersWidget
from mxcubeqt.widgets.snapshot_widget import SnapshotWidget

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class AdvancedBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self._data_collection = None

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_advanced_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.tool_box = qt_import.QToolBox(self)
        self.mesh_parameters_widget = AdvancedParametersWidget(self)

        self.line_parameters_widget = AdvancedParametersWidget(self)
        self.snapshot_widget = SnapshotWidget(self)

        self.tool_box.addItem(self.mesh_parameters_widget, "2D Heat map: Parameters")
        self.tool_box.addItem(self.line_parameters_widget, "Line scan: Parameters")

        # Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QHBoxLayout(self)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.snapshot_widget)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.connect(HWR.beamline.sample_view,
                     "gridClicked",
                     self.grid_clicked
        )

    def populate_advanced_widget(self, item):
        self.mesh_parameters_widget._data_path_widget.set_base_image_directory(
            HWR.beamline.session.get_base_image_directory()
        )
        self.mesh_parameters_widget._data_path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )

        self.line_parameters_widget._data_path_widget.set_base_image_directory(
            HWR.beamline.session.get_base_image_directory()
        )
        self.line_parameters_widget._data_path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )

        if isinstance(item, queue_item.XrayCenteringQueueItem):
            self._data_collection = item.get_model().mesh_dc
            self.mesh_parameters_widget.populate_widget(item, self._data_collection)

            #self.line_parameters_widget.populate_widget(
            #    item, item.get_model().
            #)
        else:
            self._data_collection = item.get_model()
            self.mesh_parameters_widget.populate_widget(item, self._data_collection)

        self.line_parameters_widget.setEnabled(
            isinstance(item, queue_item.XrayCenteringQueueItem)
        )

        try:
            self.snapshot_widget.display_snapshot(self._data_collection.grid.get_snapshot())
        except BaseException:
            pass

    def grid_clicked(self, grid, image, line, image_num):
        if self._data_collection is not None:
            image_path = self._data_collection.acquisitions[0].path_template.get_image_path() % image_num
            # try:
            #     HWR.beamline.image_tracking.load_image(image_path)
            # except AttributeError:
            #     pass
            if hasattr(HWR.beamline, "image_tracking"):
                HWR.beamline.image_tracking.load_image(image_path)
