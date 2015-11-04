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

from PyQt4 import QtGui

import os

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_advanced_parameters_widget import AdvancedParametersWidget
from widgets.Qt4_advanced_results_widget import AdvancedResultsWidget

__category__ = 'Task'


class Qt4_AdvancedBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.session_hwobj = None
        self.beamline_setup = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty("session", "string", "/session")
        self.addProperty("beamline_setup", "string", "/Qt4_beamline-setup")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_advanced_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.stacked_widget = QtGui.QStackedWidget(self)
        self.parameters_widget = AdvancedParametersWidget(self) 
        self.results_widget = AdvancedResultsWidget(self)
        self.toggle_page_button = QtGui.QPushButton('View Results', self)
        self.toggle_page_button.setFixedWidth(120)
        self.stacked_widget.addWidget(self.parameters_widget)
        self.stacked_widget.addWidget(self.results_widget)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.stacked_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.addWidget(self.toggle_page_button)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.toggle_page_button.clicked.connect(self.toggle_page)

        # Other ---------------------------------------------------------------
        self.stacked_widget.setCurrentWidget(self.parameters_widget)

        self.toggle_page_button.setEnabled(True)

    def populate_advanced_widget(self, item):
        self.parameters_widget._data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.parameters_widget._data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        self.parameters_widget.populate_widget(item)
        self.results_widget.populate_widget(item)

        data_collection = item.get_model()
        executed = data_collection.is_executed()

        if executed:
            self.stacked_widget.setCurrentWidget(self.results_widget)
            self.toggle_page_button.setText("View parameters")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'beamline_setup':
            self.beamline_setup = self.getHardwareObject(new_value)
            self.parameters_widget.set_beamline_setup(self.beamline_setup)
            self.results_widget.set_beamline_setup(self.beamline_setup)

    def toggle_page(self):
        if self.stacked_widget.currentWidget() is self.parameters_widget:
            self.stacked_widget.setCurrentWidget(self.results_widget)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stacked_widget.setCurrentWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")   
