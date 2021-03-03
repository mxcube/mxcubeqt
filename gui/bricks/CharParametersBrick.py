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

from gui.utils import QtImport
from gui.BaseComponents import BaseWidget
from gui.widgets.char_parameters_widget import CharParametersWidget
from gui.widgets.webview_widget import WebViewWidget

from mxcubecore import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class CharParametersBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("tunable-energy", "boolean", "True")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_char_parameter_widget", {})

        # Graphic elements ----------------------------------------------------
        self.stacked_widget = QtImport.QStackedWidget(self)
        self.parameters_widget = CharParametersWidget(self)
        self.toggle_page_button = QtImport.QPushButton("View Results", self)
        self.toggle_page_button.setFixedWidth(100)

        self.results_view = WebViewWidget(self)
        self.stacked_widget.addWidget(self.parameters_widget)
        self.stacked_widget.addWidget(self.results_view)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.stacked_widget)
        # _main_vlayout.addStretch(0)
        _main_vlayout.addWidget(self.toggle_page_button)

        # SizePolicies -------------------------------------------------------
        self.results_view.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding
        )

        # Qt signal/slot connections ------------------------------------------
        self.toggle_page_button.clicked.connect(self.toggle_page)

        # Other ---------------------------------------------------------------
        self.stacked_widget.setCurrentWidget(self.parameters_widget)
        self.parameters_widget.collection_type = None
        self.toggle_page_button.setDisabled(True)

    def populate_char_parameter_widget(self, item):
        self.parameters_widget.path_widget.set_base_image_directory(
            HWR.beamline.session.get_base_image_directory()
        )
        self.parameters_widget.path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )

        char = item.get_model()

        if char.is_executed():
            self.stacked_widget.setCurrentWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
            self.parameters_widget.set_enabled(False)

            if char.html_report is not None:
                self.results_view.set_url(char.html_report)
            else:
                self.results_view.set_static_page(
                    "<center><h1>Characterisation failed</h1></center>"
                )
        else:
            self.parameters_widget.set_enabled(True)
            self.stacked_widget.setCurrentWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.populate_parameter_widget(item)
        self.toggle_page_button.setEnabled(char.is_executed())

    def toggle_page(self):
        if self.stacked_widget.currentWidget() is self.parameters_widget:
            self.stacked_widget.setCurrentWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stacked_widget.setCurrentWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "tunable-energy":
            self.parameters_widget.acq_widget.set_tunable_energy(new_value)
