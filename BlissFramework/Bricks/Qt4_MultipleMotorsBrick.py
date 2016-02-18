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
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui
from PyQt4 import QtCore

from Qt4_MotorSpinBoxBrick import Qt4_MotorSpinBoxBrick

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors


__category__ = 'Motor'


class Qt4_MultipleMotorsBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.motor_hwobj_list = []
        self.motor_widget_list = []
        self.motor_widget_labels = []
        self.predefined_positions_list = []

        self.positions = None
        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('labels','string','')
        self.addProperty('predefinedPositions', 'string', '')

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_group_box = QtGui.QGroupBox(self)

        # Layout -------------------------------------------------------------- 
        self.main_groupbox_hlayout = QtGui.QHBoxLayout(self.main_group_box)
        self.main_groupbox_hlayout.setSpacing(2)
        self.main_groupbox_hlayout.setContentsMargins(0, 0, 0, 0)

        self.main_hlayout = QtGui.QHBoxLayout(self)
        self.main_hlayout.addWidget(self.main_group_box)
        self.main_hlayout.setSpacing(2)
        self.main_hlayout.setContentsMargins(2, 2, 2, 2)

        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
       
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'mnemonic':
            hwobj_names_list = new_value.split()
            for hwobj_name in hwobj_names_list:
                temp_motor_hwobj = self.getHardwareObject(hwobj_name)
                temp_motor_widget = Qt4_MotorSpinBoxBrick(self)
                temp_motor_widget.set_motor(temp_motor_hwobj, hwobj_name)
                temp_motor_widget.move_left_button.hide()
                temp_motor_widget.move_right_button.hide()
                temp_motor_widget.step_button.hide()
                temp_motor_widget.set_line_step(10.0)
                temp_motor_widget.step_changed(None)
                self.main_groupbox_hlayout.addWidget(temp_motor_widget)

                self.motor_hwobj_list.append(temp_motor_hwobj)
                self.motor_widget_list.append(temp_motor_widget) 
            if len(self.motor_widget_labels):      
                for index, label in enumerate(self.motor_widget_labels):
                    self.motor_widget_list[index].setLabel(label)
        elif property_name == 'icons':
            icons_list = new_value.split()
        elif property_name == 'labels':
            self.motor_widget_labels = new_value.split()
            if len(self.motor_widget_list):
                for index, label in enumerate(self.motor_widget_labels):
                    self.motor_widget_list[index].setLabel(label)            
        elif property_name == 'predefinedPositions':
            self.predefined_positions_list = new_value.split()
            for predefined_position in self.predefined_positions_list:
                temp_position_button = QtGui.QPushButton(predefined_position, self.main_group_box)
                self.main_groupbox_hlayout.addWidget(temp_position_button)
                temp_position_button.clicked.connect(lambda: \
                     self.predefined_position_clicked(predefined_position))
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)

    def predefined_position_clicked(self, predefined_position):
        for motor in self.motor_hwobj_list:
            motor.move_to_predefined_position(predefined_position.lower()) 
