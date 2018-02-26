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

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


class Qt4_ImageTrackingStatusBrick(BlissWidget):

    STATES = {'unknown': Qt4_widget_colors.LIGHT_GRAY,
              'busy'   : Qt4_widget_colors.LIGHT_GREEN,
              'tracking': Qt4_widget_colors.LIGHT_GREEN,
              'disabled': Qt4_widget_colors.LIGHT_GRAY,
              'error': Qt4_widget_colors.LIGHT_RED,
              'tracking': Qt4_widget_colors.LIGHT_GREEN,
              'ready': Qt4_widget_colors.LIGHT_BLUE}

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
        _main_groupbox = QGroupBox("Image tracking", self)
        self.state_label = QLabel('<b> </b>', _main_groupbox)
        self.image_tracking_cbox = QCheckBox(\
             "Enable Adxv image tracking", _main_groupbox)
        
        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.state_label)
        _main_groupbox_vlayout.addWidget(self.image_tracking_cbox)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.image_tracking_cbox.toggled.connect(\
             self.image_tracking_cbox_changed)

        # Other ---------------------------------------------------------------
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_changed("unknown")
        self.state_label.setFixedHeight(20)
        
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'mnemonic':
            if self.image_tracking_hwobj is not None:
                self.disconnect(self.image_tracking_hwobj,
                                'imageTrackingEnabledChanged',
                                self.image_tracking_enabled_changed)
                self.disconnect(self.image_tracking_hwobj, 
                                'stateChanged', 
                                self.state_changed)
            self.image_tracking_hwobj = self.getHardwareObject(new_value)
            if self.image_tracking_hwobj is not None:
                self.image_tracking_cbox.blockSignals(True)
                self.image_tracking_cbox.setChecked(\
                     self.image_tracking_hwobj.is_tracking_enabled() == True)
                self.image_tracking_cbox.blockSignals(False)
                self.connect(self.image_tracking_hwobj,
                                'imageTrackingEnabledChanged',
                                self.image_tracking_enabled_changed)
                self.connect(self.image_tracking_hwobj, 
                             'stateChanged', 
                             self.state_changed)
                self.image_tracking_hwobj.update_values()
                self.setEnabled(True)
            else:
                self.setEnabled(False)

        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)

    def image_tracking_cbox_changed(self, state):
        self.image_tracking_hwobj.set_image_tracking_state(state)

    def image_tracking_enabled_changed(self, state):
        self.image_tracking_cbox.setChecked(state) 

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
