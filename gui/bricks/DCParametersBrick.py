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

from gui.BaseComponents import BaseWidget
from gui.utils import html_template, QtImport
from gui.widgets.dc_parameters_widget import DCParametersWidget
from gui.widgets.image_tracking_widget import ImageTrackingWidget
from gui.widgets.advanced_results_widget import AdvancedResultsWidget
from gui.widgets.snapshot_widget import SnapshotWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class DCParametersBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("useImageTracking", "boolean", True)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_dc_parameter_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.tool_box = QtImport.QToolBox(self)
        self.parameters_widget = DCParametersWidget(self, "parameters_widget")
        self.results_static_view = QtImport.QTextBrowser(self.tool_box)
        self.image_tracking_widget = ImageTrackingWidget(self.tool_box)
        self.advance_results_widget = AdvancedResultsWidget(self.tool_box)
        self.snapshot_widget = SnapshotWidget(self)

        self.tool_box.addItem(self.parameters_widget, "Parameters")
        self.tool_box.addItem(self.image_tracking_widget, "Results - ADXV control")
        self.tool_box.addItem(self.results_static_view, "Results - Summary")
        self.tool_box.addItem(
            self.advance_results_widget, "Results - Parallel processing"
        )

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.snapshot_widget)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def populate_dc_parameter_widget(self, item):
        self.parameters_widget._data_path_widget.set_base_image_directory(
            HWR.beamline.session.get_base_image_directory()
        )
        self.parameters_widget._data_path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )

        data_collection = item.get_model()

        # if data_collection.is_helical():
        #    self.advance_results_widget.show()
        # else:
        #    self.advance_results_widget.hide()

        self.snapshot_widget.display_snapshot(
            data_collection.acquisitions[
                0
            ].acquisition_parameters.centred_position.snapshot_image,
            width=800,
        )

        if data_collection.is_collected():
            self.parameters_widget.setEnabled(False)
            self.results_static_view.reload()
            self.image_tracking_widget.set_data_collection(data_collection)
            self.image_tracking_widget.refresh()
        else:
            self.parameters_widget.setEnabled(True)

        self.parameters_widget.populate_widget(item)
        self.advance_results_widget.populate_widget(item)

    def populate_results(self, data_collection):
        if data_collection.html_report[-4:] == "html":
            if (
                self.results_static_view.mimeSourceFactory().data(
                    data_collection.html_report
                )
                is None
            ):
                self.results_static_view.setText(
                    html_template.html_report(data_collection)
                )
            else:
                self.results_static_view.setSource(data_collection.html_report)
        else:
            self.results_static_view.setText(html_template.html_report(data_collection))

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "useImageTracking":
            if new_value:
                self.tool_box.removeItem(
                    self.tool_box.indexOf(self.results_static_view)
                )
                self.results_static_view.hide()
            else:
                self.tool_box.removeItem(
                    self.tool_box.indexOf(self.image_tracking_widget)
                )
                self.image_tracking_widget.hide()
