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

import logging

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = "General"

class Qt4_ImageTrackingStatusBrick(BlissWidget):

    STATES = {'unknown': Qt4_widget_colors.LIGHT_GRAY,
              'busy'   : Qt4_widget_colors.LIGHT_GREEN,
              'tracking': Qt4_widget_colors.LIGHT_GREEN,
              'disabled': Qt4_widget_colors.LIGHT_GRAY,
              'error': Qt4_widget_colors.LIGHT_RED,
              'tracking': Qt4_widget_colors.LIGHT_GREEN,
              'ready': Qt4_widget_colors.LIGHT_GREEN}

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.image_tracking_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '/image-tracking')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = QtGui.QGroupBox("Image tracking", self)
        self.state_label = QtGui.QLabel('<b> </b>', _main_groupbox)
        self.image_tracking_cbox = QtGui.QCheckBox(\
             "Enable Adxv image tracking", _main_groupbox)
        
        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QtGui.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.state_label)
        _main_groupbox_vlayout.addWidget(self.image_tracking_cbox)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.image_tracking_cbox.toggled.connect(\
             self.image_tracking_cbox_changed)

        # Other ---------------------------------------------------------------
        self.state_label.setAlignment(QtGui.QLabel.AlignCenter)
        self.state_changed("unknown")
        
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.image_tracking_hwobj is not None:
                self.disconnect(self.image_tracking_hwobj, 
                                QtCore.SIGNAL('stateChanged'), 
                                self.state_changed)
            self.image_tracking_hwobj = self.getHardwareObject(newValue)
            if self.image_tracking_hwobj is not None:
                self.image_tracking_cbox.setChecked(\
                     self.image_tracking_hwobj.is_tracking_enabled() == True)
                self.connect(self.image_tracking_hwobj, 
                             QtCore.SIGNAL('stateChanged'), 
                             self.state_changed)
                self.image_tracking_hwobj.update_values()
                self.setEnabled(True)
            else:
                self.setEnabled(False)

        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    def image_tracking_cbox_changed(self, state):
        self.image_tracking_hwobj.set_image_tracking_state(state)

    def state_changed(self, state, state_label = None):
        color = None
        try:
            color=self.STATES[state]
        except KeyError:
            state='unknown'
            color=self.STATES[state]
        #if color is None:
        #    color = qt.QWidget.paletteBackgroundColor(self)

        if color:
            Qt4_widget_colors.set_widget_color(self.state_label, 
                                               color)
        if state_label is not None:
            self.state_label.setText('<b>%s</b>' % state_label)
        else:
            self.state_label.setText('<b>%s</b>' % state)
