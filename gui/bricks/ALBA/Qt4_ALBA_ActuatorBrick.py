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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = "ALBA"

#
# These state list is as in ALBAEpsActuator.py
#
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)

STATES = {
    STATE_IN: Qt4_widget_colors.LIGHT_GREEN,
    STATE_OUT: Qt4_widget_colors.LIGHT_GRAY,
    STATE_MOVING: Qt4_widget_colors.LIGHT_YELLOW,
    STATE_FAULT: Qt4_widget_colors.LIGHT_RED,
    STATE_ALARM: Qt4_widget_colors.LIGHT_RED,
    STATE_UNKNOWN: Qt4_widget_colors.LIGHT_GRAY,
}


class Qt4_ALBA_ActuatorBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
        self.logger = logging.getLogger("GUI Alba Actuator")
        self.logger.info("__init__()")

        # Hardware objects ----------------------------------------------------
        self.actuator_hwo = None
        self.state = None

        # Properties ----------------------------------------------------------
        self.addProperty("mnemonic", "string", "")
        self.addProperty("in_cmd_name", "string", "")
        self.addProperty("out_cmd_name", "string", "")

        # Graphic elements ----------------------------------------------------
        self.widget = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "widgets/ui_files/alba_actuator.ui")
        )

        QtGui.QHBoxLayout(self)

        self.layout().addWidget(self.widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setContentsMargins(0, 0, 0, 0)

        self.widget.cmdInButton.clicked.connect(self.do_cmd_in)
        self.widget.cmdOutButton.clicked.connect(self.do_cmd_out)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding
        )

        # Other ---------------------------------------------------------------
        self.setToolTip(
            "Main information about machine current, "
            + "machine status and top-up remaining time."
        )

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   :
        """
        if property_name == "mnemonic":
            if self.actuator_hwo is not None:
                self.disconnect(
                    self.actuator_hwo, QtCore.SIGNAL("stateChanged"), self.state_changed
                )

            self.actuator_hwo = self.getHardwareObject(new_value)
            if self.actuator_hwo is not None:
                self.setEnabled(True)
                self.connect(
                    self.actuator_hwo, QtCore.SIGNAL("stateChanged"), self.state_changed
                )
                self.actuator_hwo.update_values()
                logging.getLogger("HWR").info(
                    "User Name is: %s" % self.actuator_hwo.getUserName()
                )
                self.widget.actuatorBox.setTitle(self.actuator_hwo.getUserName())
            else:
                self.setEnabled(False)
        elif property_name == "in_cmd_name":
            self.widget.cmdInButton.setText(new_value)
        elif property_name == "out_cmd_name":
            self.widget.cmdOutButton.setText(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def update(self, state=None):
        """
        Descript. :
        Args.     :
        Return.   :
        """
        if self.actuator_hwo is not None:
            if state is None:
                state = self.actuator_hwo.getState()
                status = self.actuator_hwo.getStatus()
                self.widget.stateLabel.setText(status)
                Qt4_widget_colors.set_widget_color(
                    self.widget.stateLabel, STATES[state]
                )

                self.widget.cmdInButton.setEnabled(False)
                self.widget.cmdOutButton.setEnabled(False)
                self.widget.cmdInButton.setChecked(False)
                self.widget.cmdOutButton.setChecked(False)

                if state == STATE_IN:
                    self.widget.cmdOutButton.setEnabled(True)
                    self.widget.cmdInButton.setChecked(True)
                elif state == STATE_OUT:
                    self.widget.cmdInButton.setEnabled(True)
                    self.widget.cmdOutButton.setChecked(True)

                self.state = state

    def state_changed(self, state):
        if state != self.state:
            self.update()

    def do_cmd_in(self):
        if self.actuator_hwo is not None:
            self.actuator_hwo.cmdIn()

    def do_cmd_out(self):
        if self.actuator_hwo is not None:
            self.actuator_hwo.cmdOut()
