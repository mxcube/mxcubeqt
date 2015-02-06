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

import logging

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "Qt4_General"


class Qt4_ResolutionBrick(BlissWidget):
    """
    Descript. : 
    """
    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.resolution_hwobj = None

        # Internal values -----------------------------------------------------
        self.resolution_limits = None

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('formatString','formatString','###.##')

        self.main_frame = QtGui.QFrame(self)
        self.main_frame.setFrameStyle(QtGui.QFrame.StyledPanel)
        self.group_box = QtGui.QGroupBox("Resolution", self.main_frame)
        current_label = QtGui.QLabel("Current:",self.group_box)
        current_label.setFixedWidth(75)
        self.resolution_ledit = QtGui.QLineEdit(self.group_box)
        self.resolution_ledit.setReadOnly(True)
        set_to_label = QtGui.QLabel("Set to:",self.group_box)
        self.new_value_ledit = QtGui.QLineEdit(self.group_box)

        # Layout --------------------------------------------------------------
        self.group_box_layout = QtGui.QGridLayout()
        self.group_box_layout.addWidget(current_label, 0, 0)
        self.group_box_layout.addWidget(self.resolution_ledit, 0, 1)
        self.group_box_layout.addWidget(set_to_label, 1, 0)
        self.group_box_layout.addWidget(self.new_value_ledit, 1, 1)
        self.group_box_layout.setSpacing(0)
        self.group_box_layout.setContentsMargins(1,1,1,1)
        self.group_box.setLayout(self.group_box_layout)

        self.main_frame_layout = QtGui.QVBoxLayout()
        self.main_frame_layout.setSpacing(0)
        self.main_frame_layout.setContentsMargins(0,0,0,0)
        self.main_frame_layout.addWidget(self.group_box)
        self.main_frame.setLayout(self.main_frame_layout)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,2,2)
        self.main_layout.addWidget(self.main_frame)
        self.setLayout(self.main_layout)

        # SizePolicies --------------------------------------------------------
        self.setMaximumWidth(250)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------
        self.connect(self.new_value_ledit, QtCore.SIGNAL('returnPressed()'), self.current_value_changed)
        self.connect(self.new_value_ledit, QtCore.SIGNAL('textChanged(const QString &)'), self.input_field_changed)

        # Other --------------------------------------------------------------- 
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)
        Qt4_widget_colors.set_widget_color(self.new_value_ledit,
                                       Qt4_widget_colors.LINE_EDIT_ACTIVE,
                                       QtGui.QPalette.Base)
        self.new_value_validator = QtGui.QDoubleValidator(self.new_value_ledit)
        
    def propertyChanged(self, property_value, old_value, new_value):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        if property_value == 'mnemonic':
            if self.resolution_hwobj is not None:
                self.disconnect(self.resolution_hwobj, QtCore.SIGNAL('deviceReady'), self.connected)
                self.disconnect(self.resolution_hwobj, QtCore.SIGNAL('deviceNotReady'), self.disconnected)
                self.disconnect(self.resolution_hwobj, QtCore.SIGNAL('stateChanged'), self.resolution_state_changed)
                self.disconnect(self.resolution_hwobj, QtCore.SIGNAL('positionChanged'), self.resolution_value_changed)

            self.resolution_hwobj = self.getHardwareObject(new_value)
            if self.resolution_hwobj is not None:

                self.connect(self.resolution_hwobj, QtCore.SIGNAL('deviceReady'), self.connected)
                self.connect(self.resolution_hwobj, QtCore.SIGNAL('deviceNotReady'), self.disconnected)
                self.connect(self.resolution_hwobj, QtCore.SIGNAL('stateChanged'), self.resolution_state_changed)
                self.connect(self.resolution_hwobj, QtCore.SIGNAL('positionChanged'), self.resolution_value_changed)
                self.resolution_hwobj.update_values()

                if self.resolution_hwobj.isReady():
                    self.connected()
                else:
                    self.disconnected()
            else:
                self.disconnected()
        else:
            BlissWidget.propertyChanged(self, property_value, old_value, new_value)

    def input_field_changed(self,text):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        if input_field_text == "":
            Qt4_widget_colors.set_widget_color(self.new_value_ledit,
                                               Qt4_widget_colors.LINE_EDIT_ACTIVE,
                                               QtGui.QPalette.Base)
        else:
            Qt4_widget_colors.set_widget_color(self.new_value_ledit,
                                               Qt4_widget_colors.LINE_EDIT_CHANGED,
                                               QtGui.QPalette.Base)

    def current_value_changed(self):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        self.resolution_hwobj.newResolution(float(self.new_value_ledit.text()))
        self.new_value_ledit.setText("")

    def connected(self):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        self.setEnabled(True)

    def disconnected(self):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        self.setEnabled(False)

    def resolution_state_changed(self, state):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        return

    def resolution_value_changed(self, value):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        self.resolution_ledit.setText(str(value))
