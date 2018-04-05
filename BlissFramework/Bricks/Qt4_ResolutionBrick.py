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

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"

class Qt4_ResolutionBrick(BlissWidget):
    """
    Descript. : 
    """
    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED,
                    Qt4_widget_colors.LIGHT_RED,
                    Qt4_widget_colors.LIGHT_GREEN,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    QColor(255,165,0),
                    Qt4_widget_colors.LIGHT_RED)   

    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.resolution_hwobj = None
        self.detector_distance_hwobj = None
        self.door_interlock_hwobj = None
        self.energy_hwobj = None

        # Internal values -----------------------------------------------------
        self.resolution_limits = None
        self.detector_distance_limits = None
        self.door_interlocked = True

        # Properties ---------------------------------------------------------- 
        self.addProperty('resolution', 'string', '')
        self.addProperty('detectorDistance', 'string', '')
        self.addProperty('energy', 'string', '')
        self.addProperty('doorInterlock', 'string', '') 
        self.addProperty('defaultMode', 'combo',('Ang','mm'),'Ang')
        self.addProperty('mmFormatString','formatString','###.##')
        self.addProperty('angFormatString','formatString','##.###')        

        self.group_box = QGroupBox("Resolution", self)
        current_label = QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)

        self.resolution_ledit = QLineEdit(self.group_box)
        self.resolution_ledit.setReadOnly(True)
        self.detector_distance_ledit = QLineEdit(self.group_box)
        self.detector_distance_ledit.setReadOnly(True) 

        _new_value_widget = QWidget(self)
        set_to_label = QLabel("Set to:",self.group_box)
        self.new_value_ledit = QLineEdit(self.group_box)
        self.units_combobox = QComboBox(_new_value_widget)
        self.stop_button = QPushButton(_new_value_widget)
        self.stop_button.setIcon(Qt4_Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(25)

        # Layout --------------------------------------------------------------
        _new_value_widget_hlayout = QHBoxLayout(_new_value_widget)
        _new_value_widget_hlayout.addWidget(self.new_value_ledit)
        _new_value_widget_hlayout.addWidget(self.units_combobox)
        _new_value_widget_hlayout.addWidget(self.stop_button)
        _new_value_widget_hlayout.setSpacing(0)
        _new_value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _group_box_gridlayout = QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0, 2, 1)
        _group_box_gridlayout.addWidget(self.resolution_ledit, 0, 1)
        _group_box_gridlayout.addWidget(self.detector_distance_ledit, 1, 1)
        _group_box_gridlayout.addWidget(set_to_label, 2, 0)
        _group_box_gridlayout.addWidget(_new_value_widget, 2, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.new_value_ledit.returnPressed.connect(self.current_value_changed)
        self.new_value_ledit.textChanged.connect(self.input_field_changed)
        self.units_combobox.activated.connect(self.unit_changed)
        self.stop_button.clicked.connect(self.stop_clicked)

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.new_value_ledit,
                                           Qt4_widget_colors.LINE_EDIT_ACTIVE,
                                           QPalette.Base)
        self.new_value_validator = QDoubleValidator(\
             0, 15, 4, self.new_value_ledit)

        self.units_combobox.addItem(chr(197))
        self.units_combobox.addItem("mm")
        self.instance_synchronize("group_box",
                                  "resolution_ledit",
                                  "detector_distance_ledit",
                                  "new_value_ledit",
                                  "units_combobox")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        if property_name == 'resolution':
            if self.resolution_hwobj is not None:
                self.disconnect(self.resolution_hwobj,
                                'deviceReady',
                                self.resolution_ready)
                self.disconnect(self.resolution_hwobj,
                                'deviceNotReady',
                                self.resolution_not_ready)
                self.disconnect(self.resolution_hwobj,
                                'stateChanged',
                                self.resolution_state_changed)
                self.disconnect(self.resolution_hwobj,
                                'positionChanged',
                                self.resolution_value_changed)
                self.disconnect(self.resolution_hwobj,
                                'limitsChanged',
                                self.resolution_limits_changed)

            self.resolution_hwobj = self.getHardwareObject(new_value)
            if self.resolution_hwobj is not None:
                self.connect(self.resolution_hwobj,
                             'deviceReady',
                             self.resolution_ready)
                self.connect(self.resolution_hwobj,
                             'deviceNotReady',
                             self.resolution_not_ready)
                self.connect(self.resolution_hwobj,
                             'stateChanged',
                             self.resolution_state_changed)
                self.connect(self.resolution_hwobj,
                             'positionChanged',
                             self.resolution_value_changed)
                self.connect(self.resolution_hwobj,
                             'limitsChanged',
                             self.resolution_limits_changed)

                if self.resolution_hwobj.isReady():
                    self.resolution_hwobj.update_values()
                    self.connected()
                else:
                    self.disconnected()
            self.update_gui()
        elif property_name == 'detectorDistance':
            if self.detector_distance_hwobj is not None:
                self.disconnect(self.detector_distance_hwobj,
                                'deviceReady',
                                self.detector_distance_ready)
                self.disconnect(self.detector_distance_hwobj,
                                'deviceNotReady',
                                self.detector_distance_not_ready)
                self.disconnect(self.detector_distance_hwobj,
                                'stateChanged',
                                self.detector_distance_state_changed)
                self.disconnect(self.detector_distance_hwobj,
                                'positionChanged',
                                self.detector_distance_changed)
                self.disconnect(self.detector_distance_hwobj,
                                'limitsChanged',
                                self.detector_distance_limits_changed)

            self.detector_distance_hwobj = self.getHardwareObject(new_value)
            if self.detector_distance_hwobj is not None:
                self.connect(self.detector_distance_hwobj, 
                             'deviceReady',
                             self.detector_distance_ready)
                self.connect(self.detector_distance_hwobj,
                             'deviceNotReady',
                             self.detector_distance_not_ready)
                self.connect(self.detector_distance_hwobj,
                             'stateChanged',
                             self.detector_distance_state_changed)
                self.connect(self.detector_distance_hwobj,
                             'positionChanged',
                             self.detector_distance_changed)
                self.connect(self.detector_distance_hwobj,
                             'limitsChanged',
                             self.detector_distance_limits_changed)

                if self.detector_distance_hwobj.is_ready():
                    self.detector_distance_hwobj.update_values()
                    self.connected()
                else:
                    self.disconnected()
            self.update_gui()
        elif property_name == 'energy':
            if self.energy_hwobj is not None:
                self.disconnect(self.energy_hwobj,
                                'moveEnergyFinished',
                                self.energy_changed)
            self.energy_hwobj = self.getHardwareObject(new_value)
            if self.energy_hwobj is not None:
                self.connect(self.energy_hwobj, 
                             'moveEnergyFinished', 
                             self.energy_changed)

        elif property_name == 'doorInterlock':
            if self.door_interlock_hwobj is not None:
                self.disconnect(self.door_interlock_hwobj,
                                'doorInterlockStateChanged',
                                self.door_interlock_state_changed)
            self.door_interlock_hwobj = self.getHardwareObject(new_value)
            if self.door_interlock_hwobj is not None:
                self.connect(self.door_interlock_hwobj,
                             'doorInterlockStateChanged',
                             self.door_interlock_state_changed)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def input_field_changed(self, input_field_text):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_CHANGED,
                QPalette.Base)
        else:
           Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_ERROR,
                QPalette.Base)

    def current_value_changed(self):
        """
        Descript. : 
        Args.     : 
        Return    : None
        """
        input_field_text = self.new_value_ledit.text()

        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            unit = self.units_combobox.currentText()
            value = float()
            self.new_value_ledit.setText("")
            if unit == chr(197):
                self.set_resolution(float(input_field_text))
            elif unit=="mm":
                self.set_detector_distance(float(input_field_text))
            Qt4_widget_colors.set_widget_color(\
                 self.new_value_ledit,
                 Qt4_widget_colors.LINE_EDIT_ACTIVE,
                 QPalette.Base)

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

    def detector_distance_limits_changed(self, limits):
        if limits:
            self.detector_distance_limits = limits
            self.update_gui()

    def resolution_limits_changed(self, limits):
        if limits:
            self.resolution_limits = limits
            self.update_gui()
    
    def create_tool_tip(self):
        tool_tip = ""
        if self.units_combobox.currentText() == "mm":
            if self.detector_distance_limits:
                tool_tip = "Detector distance limits %0.4f : %0.4f mm" \
                           %(self.detector_distance_limits[0],
                             self.detector_distance_limits[1])
        elif self.resolution_limits:
            tool_tip = "Resolution limits %0.4f : %0.4f %s"\
                       %(self.resolution_limits[0], 
                         self.resolution_limits[1],
                         chr(197))
        if not self.door_interlocked:
            tool_tip = "\n\nMove resolution command disabled."
            tool_tip += "\nLock the hutch doors to enable."
        self.new_value_ledit.setToolTip(tool_tip)

    def unit_changed(self, unit_index):
        self.update_gui()

        self.new_value_ledit.blockSignals(True)
        self.new_value_ledit.setText("")
        self.new_value_ledit.blockSignals(False)

    def update_gui(self, resolution_ready=None, detector_ready=None):
        """
        Door interlock is optional, because not all sites might have it
        """
        if self.detector_distance_hwobj is None:
            detector_ready = False
        elif detector_ready is None:
            try:
                if self.detector_distance_hwobj.connection.isSpecConnected():
                    detector_ready = self.detector_distance_hwobj.isReady()
            except AttributeError:
                detector_ready = self.detector_distance_hwobj.is_ready()

        if detector_ready:
            self.get_detector_distance_limits()
            curr_detector_distance = self.detector_distance_hwobj.get_position()
            self.detector_distance_changed(curr_detector_distance)
            self.detector_distance_state_changed(self.detector_distance_hwobj.get_state())
            if self.units_combobox.currentText() == "mm":
                self.group_box.setTitle('Detector distance')
                self.new_value_validator.setRange(self.detector_distance_limits[0],
                                                  self.detector_distance_limits[1],
                                                  2)
        else:
            self.detector_distance_state_changed(None)


        if self.resolution_hwobj is None:
            resolution_ready = False
        elif resolution_ready is None:
            try:
                if self.resolution_hwobj.connection.isSpecConnected():
                    resolution_ready = self.resolution_hwobj.isReady()
            except AttributeError:
                resolution_ready = self.resolution_hwobj.isReady()


        if resolution_ready:
            self.get_resolution_limits()
            curr_resolution = self.resolution_hwobj.getPosition()
            self.resolution_value_changed(curr_resolution)
            self.resolution_state_changed(self.resolution_hwobj.getState())
            if self.units_combobox.currentText() != "mm":
                self.group_box.setTitle('Resolution')
                self.new_value_validator.setRange(self.resolution_limits[0],
                                                  self.resolution_limits[1],
                                                  3)
        else:
            self.resolution_state_changed(None)

        self.new_value_ledit.setEnabled(self.door_interlocked)
        self.setEnabled(self.door_interlocked)
        self.create_tool_tip()

    def resolution_ready(self):
        self.update_gui(resolution_ready=True)

    def resolution_not_ready(self):
        self.update_gui(resolution_ready=False)

    def detector_distance_ready(self):
        self.update_gui(detector_ready=True)

    def detector_distance_not_ready(self):
        self.update_gui(detector_ready=False)

    def set_resolution(self, value):
        if self.resolution_limits is not None:
            if self.resolution_limits[0] < value < self.resolution_limits[1]:
                self.resolution_hwobj.move(value)

    def set_detector_distance(self, value):
        if self.detector_distance_limits is not None:
            if self.detector_distance_limits[0] < value < self.detector_distance_limits[1]:
                self.detector_distance_hwobj.move(value)

    def energy_changed(self):
        self.get_resolution_limits(True)

    def get_resolution_limits(self, force = False, resolution_ready = None):
        if self.resolution_limits is not None and force is False:
            return

        if resolution_ready is None:
            resolution_ready=False
            if self.resolution_hwobj is not None:
                try:
                    if self.resolution_hwobj.connection.isSpecConnected():
                        resolution_ready = self.resolution_hwobj.isReady()
                except AttributeError:
                    resolution_ready = self.resolution_hwobj.isReady()

        if resolution_ready:
            #TODO remove this check and use get_limits
            if hasattr(self.resolution_hwobj, "getLimits"):
                self.resolution_limits_changed(self.resolution_hwobj.getLimits())
            else:
                self.resolution_limits_changed(self.resolution_hwobj.get_limits())
        else:
            self.resolution_limits = None

    def get_detector_distance_limits(self, force = False):
        if self.detector_distance_limits is not None and force is False:
            return

        detector_ready = False
        if self.detector_distance_hwobj is not None:
            try:
                if self.detector_distance_hwobj.connection.isSpecConnected():
                    detector_ready = self.detector_distance_hwobj.is_ready()
            except AttributeError:
                detector_ready=self.detector_distance_hwobj.is_ready()

        if detector_ready:
            self.detector_distance_limits_changed(self.detector_distance_hwobj.get_limits())
        else:
            self.detector_distance_limits = None

    def resolution_value_changed(self, value):
        if value:
            resolution_str = self['angFormatString'] % float(value)
            self.resolution_ledit.setText("%s %s" % (resolution_str, u"\u212B"))

    def detector_distance_changed(self, value):
        if value:
            detector_str = self['mmFormatString'] % value
            self.detector_distance_ledit.setText("%s mm" % detector_str)

    def resolution_state_changed(self, state):
        if self.detector_distance_hwobj is not None:
            if state:
                color = Qt4_ResolutionBrick.STATE_COLORS[state]
            else:
                color = Qt4_widget_colors.LIGHT_RED

            unit = self.units_combobox.currentText()
            if unit is chr(197):
                if state == self.detector_distance_hwobj.motor_states.READY:
                    self.new_value_ledit.blockSignals(True)
                    self.new_value_ledit.setText("")
                    self.new_value_ledit.blockSignals(False)
                    self.new_value_ledit.setEnabled(True)
                else:
                    self.new_value_ledit.setEnabled(False)
                if state == self.detector_distance_hwobj.motor_states.MOVING: #or state == self.detector_distance_hwobj.motor_states.MOVESTARTED:
                    self.stop_button.setEnabled(True)
                else:
                    self.stop_button.setEnabled(False)

                Qt4_widget_colors.set_widget_color(self.new_value_ledit, color)

    def detector_distance_state_changed(self, state):
        if state is None:
            return

        color = Qt4_ResolutionBrick.STATE_COLORS[state]
        unit = self.units_combobox.currentText()
        if unit == "mm":
            if state == self.detector_distance_hwobj.motor_states.READY:
                self.new_value_ledit.blockSignals(True)
                self.new_value_ledit.setText("")
                self.new_value_ledit.blockSignals(False)
                self.new_value_ledit.setEnabled(True)
            else:
                self.new_value_ledit.setEnabled(False)
            if state == self.detector_distance_hwobj.motor_states.MOVING : #or \
                #state == self.detector_distance_hwobj.motor_states.MOVESTARTED:
                self.stop_button.setEnabled(True)
            else:
                self.stop_button.setEnabled(False)

            Qt4_widget_colors.set_widget_color(self.new_value_ledit, color)

    def stop_clicked(self):
        unit = self.units_combobox.currentText()
        if unit == chr(197):
            self.resolution_hwobj.stop()
        elif unit == "mm":
            self.detector_distance_hwobj.stop()

    def door_interlock_state_changed(self, state, state_message):
        self.door_interlocked = state in ['locked_active', 'locked_inactive']
        self.update_gui()
