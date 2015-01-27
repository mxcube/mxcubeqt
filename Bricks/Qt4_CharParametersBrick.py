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

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_char_parameters_widget import CharParametersWidget


__category__ = 'Qt4_Task'


class Qt4_CharParametersBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.session_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty("tunable-energy", "boolean", "True")
        self.addProperty("session", "string", "/session")
        self.addProperty("beamline_setup", "string", "/Qt4_beamline-setup")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_char_parameter_widget", {})

        # Graphic elements ---------------------------------------------------- 
        self.stacked_widget = QtGui.QStackedWidget(self)
        self.parameters_widget = CharParametersWidget(self)
        self.toggle_page_button = QtGui.QPushButton('View Results', self)
        self.toggle_page_button.setFixedWidth(100)

        self.results_view = QtGui.QTextBrowser(self)
        self.stacked_widget.addWidget(self.parameters_widget)
        self.stacked_widget.addWidget(self.results_view)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.stacked_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.addWidget(self.toggle_page_button)
        self.setLayout(_main_vlayout)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.toggle_page_button.clicked.connect(self.toggle_page)

        # Other --------------------------------------------------------------- 
        self.stacked_widget.setCurrentWidget(self.parameters_widget)
        self.parameters_widget.collection_type = None
        self.toggle_page_button.setDisabled(True)

    def populate_char_parameter_widget(self, item):
        self.parameters_widget.path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.parameters_widget.path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        char = item.get_model()

        if char.is_executed():
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
            self.parameters_widget.set_enabled(False)

            if char.html_report:
                if self.results_view.mimeSourceFactory().\
                       data(char.html_report) == None:
                    self.results_view.setText("<center><h1>Characterisation failed</h1></center>") 
                else:
                    self.results_view.setSource(char.html_report)
            else:
                self.results_view.setText("<center><h1>Characterisation failed</h1></center>") 
        else:
            self.parameters_widget.set_enabled(True)
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.populate_parameter_widget(item)
        self.toggle_page_button.setEnabled(char.is_executed())

    def toggle_page(self):
        if self.stack.visibleWidget() is self.parameters_widget:
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

    # Framework-2 callback
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'tunable-energy':
            self.parameters_widget.acq_widget.set_tunable_energy(new_value)            
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'beamline_setup':            
            beamline_setup = self.getHardwareObject(new_value)
            self.parameters_widget.set_beamline_setup(beamline_setup)
