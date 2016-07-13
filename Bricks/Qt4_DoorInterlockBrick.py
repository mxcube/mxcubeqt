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
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "General"


class Qt4_DoorInterlockBrick(BlissWidget):

    STATES = {'unknown': Qt4_widget_colors.LIGHT_GRAY,
              'disabled': Qt4_widget_colors.LIGHT_GRAY,
              'error': Qt4_widget_colors.LIGHT_RED,
              'unlocked': Qt4_widget_colors.LIGHT_GRAY, 
              'locked_active': Qt4_widget_colors.LIGHT_GREEN,
              'locked_inactive': Qt4_widget_colors.LIGHT_GRAY}

    def __init__(self, *args):
        BlissWidget.__init__(self,*args)

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic','string','')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self.door_interlock_hwobj=None

        # Internal values -----------------------------------------------------
        self.__expertMode = False
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtGui.QGroupBox("Door interlock", self)
        self.main_groupbox.setAlignment(QtCore.Qt.AlignCenter)
        self.state_label = QtGui.QLabel('<b>unknown</b>', self.main_groupbox)
        Qt4_widget_colors.set_widget_color(self.state_label,
                                           self.STATES['unknown']) 
        self.state_label.setAlignment(QtCore.Qt.AlignCenter)
        self.unlock_door_button = QtGui.QPushButton(\
             Qt4_Icons.load_icon("EnterHutch"),
             "Unlock", self.main_groupbox)

        # Layout -------------------------------------------------------------- 
        _main_gbox_vlayout = QtGui.QVBoxLayout(self.main_groupbox)
        _main_gbox_vlayout.addWidget(self.state_label)
        _main_gbox_vlayout.addWidget(self.unlock_door_button)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.unlock_door_button.clicked.connect(self.unlock_doors)

        # Other ---------------------------------------------------------------
        self.state_label.setToolTip("Shows the current door state")
        self.unlock_door_button.setToolTip("Unlocks the doors")

    def unlock_doors(self):
        self.door_interlock_hwobj.unlock_door_interlock()

    def updateLabel(self,label):
        self.main_groupbox.setTitle(label)

    def state_changed(self, state, state_label = None):
        try:
            color = self.STATES[state]
        except KeyError:
            state = 'unknown'
            color = self.STATES[state]
        Qt4_widget_colors.set_widget_color(self.state_label,
                                           color)
        if state_label is not None:
            self.state_label.setText('<b>%s</b>' % state_label)
        else:
            self.state_label.setText('<b>%s</b>' % state)

        self.unlock_door_button.setEnabled(state == 'locked_active')

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name=='mnemonic':
            if self.door_interlock_hwobj is not None:
                self.disconnect(self.door_interlock_hwobj,
                                'doorInterlockStateChanged',
                                self.state_changed)
            self.door_interlock_hwobj = self.getHardwareObject(new_value)
            if self.door_interlock_hwobj is not None:
                self.connect(self.door_interlock_hwobj,
                             'doorInterlockStateChanged',
                             self.state_changed)
                self.state_changed(self.door_interlock_hwobj.getState())
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)
