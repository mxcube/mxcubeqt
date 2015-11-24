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

from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors


__category__ = 'Qt4_Motor'


class Qt4_MotorPredefPosBrick(BlissWidget):

    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED, 
                    Qt4_widget_colors.LIGHT_RED,
                    Qt4_widget_colors.LIGHT_GREEN,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LINE_EDIT_CHANGED)

    #DISABLED_COLOR = None

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values -----------------------------------------------------

        self.positions = None
        # Properties ----------------------------------------------------------
        self.addProperty('label','string','')
        self.addProperty('mnemonic', 'string', '')

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setEnabled',())

        # Graphic elements ----------------------------------------------------
        _group_box = QtGui.QGroupBox(self)
        self.label = QtGui.QLabel("motor:", _group_box)
        self.positions_combo = QtGui.QComboBox(_group_box)

        # Layout -------------------------------------------------------------- 
        _group_box_hlayout = QtGui.QHBoxLayout(_group_box)
        _group_box_hlayout.addWidget(self.label)
        _group_box_hlayout.addWidget(self.positions_combo) 
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
        self.positions_combo.activated.connect(self.lstPositionsClicked)

        # Other ---------------------------------------------------------------
        self.positions_combo.setToolTip("Moves the motor to a predefined position")
        

    def setToolTip(self,name=None,state=None):
        states=("NOTREADY","UNUSABLE","READY","MOVESTARTED","MOVING","ONLIMIT")
        if name is None:
            name=self['mnemonic']

        if self.motor_hwobj is None:
            tip="Status: unknown motor "+name
        else:
            if state is None:
                state=self.motor_hwobj.getState()
            try:
                state_str=states[state]
            except IndexError:
                state_str="UNKNOWN"
            tip="State:"+state_str

        self.label.setToolTip(tip)

    def motorStateChanged(self, state):
        s = state == self.motor_hwobj.READY 
        self.positions_combo.setEnabled(s)
        Qt4_widget_colors.set_widget_color(self.positions_combo, 
                                           Qt4_MotorPredefPosBrick.STATE_COLORS[state],
                                           QtGui.QPalette.Button)
        self.setToolTip(state=state)

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='label':
            if newValue=="" and self.motor_hwobj is not None:
                self.label.setText("<i>"+self.motor_hwobj.username+":</i>")
                tip=self.motor_hwobj.username
            else:
                self.label.setText(newValue)
                tip=newValue
        elif propertyName=='mnemonic':
            if self.motor_hwobj is not None:
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('stateChanged'), self.motorStateChanged)
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('newPredefinedPositions'), self.fillPositions)
                self.disconnect(self.motor_hwobj, QtCore.SIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)
            self.motor_hwobj = self.getHardwareObject(newValue)
            if self.motor_hwobj is not None:
                self.connect(self.motor_hwobj, QtCore.SIGNAL('newPredefinedPositions'), self.fillPositions)
                self.connect(self.motor_hwobj, QtCore.SIGNAL('stateChanged'), self.motorStateChanged)
                self.connect(self.motor_hwobj, QtCore.SIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)

                self.fillPositions()

                if self.motor_hwobj.isReady():
                    self.predefinedPositionChanged(self.motor_hwobj.getCurrentPositionName(), 0)

                if self['label']=="":
                    lbl=self.motor_hwobj.username
                    self.label.setText("<i>"+lbl+":</i>")
                Qt4_widget_colors.set_widget_color(self.positions_combo,
                                                   Qt4_MotorPredefPosBrick.STATE_COLORS[0],
                                                   QtGui.QPalette.Button)
                self.motorStateChanged(self.motor_hwobj.getState())
        elif propertyName=='listIndex':
            self.fillPositions()
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def fillPositions(self, positions = None): 
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
                self.predefinedPositionChanged(self.motor_hwobj.getCurrentPositionName(), 0)

    def lstPositionsClicked(self, index):
        if index > 0:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveToPosition(self.positions[index-1])
            else:
                self.positions_combo.setCurrentIndex(0)

    def predefinedPositionChanged(self, positionName, offset):
        self.positions_combo.setCurrentIndex(0)

        if self.positions:
           for i in range(len(self.positions)):
               if self.positions[i] == positionName:
                   self.positions_combo.setCurrentIndex(i+1)
                   break
