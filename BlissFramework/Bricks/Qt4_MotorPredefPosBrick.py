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

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors


__category__ = 'Motor'


class Qt4_MotorPredefPosBrick(BlissWidget):

    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED, 
                    Qt4_widget_colors.LIGHT_RED,
                    Qt4_widget_colors.LIGHT_GREEN,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LINE_EDIT_CHANGED)

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values -----------------------------------------------------

        self.positions = None
        # Properties ----------------------------------------------------------
        self.addProperty('label','string','')
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('showMoveButtons', 'boolean', True)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setEnabled',())

        # Graphic elements ----------------------------------------------------
        _group_box = QtGui.QGroupBox(self)
        self.label = QtGui.QLabel("motor:", _group_box)
        self.positions_combo = QtGui.QComboBox(_group_box)
        self.previous_position_button = QtGui.QPushButton(_group_box)
        self.next_position_button = QtGui.QPushButton(_group_box)

        # Layout -------------------------------------------------------------- 
        _group_box_hlayout = QtGui.QHBoxLayout(_group_box)
        _group_box_hlayout.addWidget(self.label)
        _group_box_hlayout.addWidget(self.positions_combo) 
        _group_box_hlayout.addWidget(self.previous_position_button)
        _group_box_hlayout.addWidget(self.next_position_button)
        _group_box_hlayout.setSpacing(2)
        _group_box_hlayout.setContentsMargins(2, 2, 2, 2)

        main_layout = QtGui.QHBoxLayout(self)
        main_layout.addWidget(_group_box)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Size Policy ---------------------------------------------------------
        #box1.setSizePolicy(QtGui.QSizePolicy.Fixed, 
        #                   QtGui.QSizePolicy.Fixed)
        self.label.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                 QtGui.QSizePolicy.Fixed)
        #self.setSizePolicy(QtGui.QSizePolicy.Minimum,
        #                   QtGui.QSizePolicy.Fixed)
        # Qt signal/slot connections ------------------------------------------
        self.positions_combo.activated.connect(self.position_selected)
        self.previous_position_button.clicked.connect(self.select_previous_position)
        self.next_position_button.clicked.connect(self.select_next_position)

        # Other ---------------------------------------------------------------
        self.positions_combo.setToolTip("Moves the motor to a predefined position")
        self.previous_position_button.setIcon(Qt4_Icons.load_icon('Minus2'))
        self.previous_position_button.setFixedWidth(27) 
        self.next_position_button.setIcon(Qt4_Icons.load_icon('Plus2'))
        self.next_position_button.setFixedWidth(27)
       
    def setToolTip(self, name=None, state=None):
        states = ("NOTREADY", "UNUSABLE", "READY", "MOVESTARTED", "MOVING", "ONLIMIT")
        if name is None:
            name = self['mnemonic']
        if self.motor_hwobj is None:
            tip = "Status: unknown motor " + name
        else:
            if state is None:
                state = self.motor_hwobj.getState()
            try:
                state_str = states[state]
            except IndexError:
                state_str = "UNKNOWN"
            tip = "State:" + state_str

        self.label.setToolTip(tip)

    def motor_state_changed(self, state):
        s = state in (self.motor_hwobj.READY, self.motor_hwobj.ONLIMIT)
        self.positions_combo.setEnabled(s)
        Qt4_widget_colors.set_widget_color(self.positions_combo, 
                                           Qt4_MotorPredefPosBrick.STATE_COLORS[state],
                                           QtGui.QPalette.Button)
        self.setToolTip(state=state)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'label':
            if new_value == "" and self.motor_hwobj is not None:
                self.label.setText("<i>" + self.motor_hwobj.username + ":</i>")
            else:
                self.label.setText(new_value)
        elif property_name == 'mnemonic':
            if self.motor_hwobj is not None:
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('stateChanged'), self.motor_state_changed)
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('newPredefinedPositions'), self.fill_positions)
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('predefinedPositionChanged'), self.predefined_position_changed)
            self.motor_hwobj = self.getHardwareObject(new_value)
            if self.motor_hwobj is not None:
                self.connect(self.motor_hwobj, QtCore.SIGNAL('newPredefinedPositions'), self.fill_positions)
                self.connect(self.motor_hwobj, QtCore.SIGNAL('stateChanged'), self.motor_state_changed)
                self.connect(self.motor_hwobj, QtCore.SIGNAL('predefinedPositionChanged'), self.predefined_position_changed)
                self.fill_positions()
                if self.motor_hwobj.isReady():
                    self.predefined_position_changed(self.motor_hwobj.getCurrentPositionName(), 0)
                if self['label'] == "":
                    lbl=self.motor_hwobj.username
                    self.label.setText("<i>" + lbl + ":</i>")
                Qt4_widget_colors.set_widget_color(self.positions_combo,
                                                   Qt4_MotorPredefPosBrick.STATE_COLORS[0],
                                                   QtGui.QPalette.Button)
                self.motor_state_changed(self.motor_hwobj.getState())
        elif property_name == 'showMoveButtons':
            if new_value:
                self.previous_position_button.show()
                self.next_position_button.show()
            else:
                self.previous_position_button.hide()
                self.next_position_button.hide()
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.previous_position_button.setIcon(\
                    Qt4_Icons.load_icon(icons_list[0]))
                self.next_position_button.setIcon(\
                    Qt4_Icons.load_icon(icons_list[1]))
            except:
                pass
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)

    def fill_positions(self, positions = None): 
        self.positions_combo.clear()
        if self.motor_hwobj is not None:
            if positions is None:
                positions = self.motor_hwobj.getPredefinedPositionsList()
        if positions is None:
            positions=[]
        for p in positions:
            pos_list=p.split()
            pos_name=pos_list[1]
            self.positions_combo.addItem(str(pos_name))
        self.positions=positions
        if self.motor_hwobj is not None:
            if self.motor_hwobj.isReady():
                self.predefined_position_changed(self.motor_hwobj.getCurrentPositionName(), 0)

    def position_selected(self, index):
        if index >= 0:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveToPosition(self.positions[index])
            else:
                self.positions_combo.setCurrentIndex(0)
        self.next_position_button.setEnabled(index < (len(self.positions) - 1))
        self.previous_position_button.setEnabled(index >= 0)

    def predefined_position_changed(self, position_name, offset):
        if self.positions:
            index = 0
            for index in range(len(self.positions)):
                if self.positions[index] == position_name:
                    break

            self.positions_combo.setCurrentIndex(index)
            self.next_position_button.setEnabled(index < (len(self.positions) - 1))
            self.previous_position_button.setEnabled(index > 0)

    def select_previous_position(self):
        self.position_selected(self.positions_combo.currentIndex() - 1) 

    def select_next_position(self):
        self.position_selected(self.positions_combo.currentIndex() + 1)

