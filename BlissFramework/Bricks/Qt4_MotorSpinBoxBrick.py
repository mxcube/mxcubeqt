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

import math
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_Motor'


class Qt4_MotorSpinBoxBrick(BlissWidget):
    """
    Descript. :
    """
    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED, 
                    Qt4_widget_colors.DARK_GRAY,
                    Qt4_widget_colors.LIGHT_GREEN,
                    Qt4_widget_colors.LIGHT_YELLOW,  
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW)

    MAX_HISTORY = 20

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values ----------------------------------------------------- 
        self.step_editor = None
        self.demand_move = 0
        self.in_expert_mode = None

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '+##.##')
        self.addProperty('label', 'string', '')
        self.addProperty('showLabel', 'boolean', True)
        self.addProperty('showMoveButtons', 'boolean', True)
        self.addProperty('showBox', 'boolean', True)
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('showStep', 'boolean', True)
        self.addProperty('showStepList', 'boolean', False)
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('invertButtons', 'boolean', False)
        self.addProperty('delta', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('helpDecrease', 'string', '')
        self.addProperty('helpIncrease', 'string', '')
        self.addProperty('decimalPlaces', 'string', '')
        self.addProperty('hideInUser', 'boolean', False)
        self.addProperty('defaultStep', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setEnabled',())
        self.defineSlot('setDisabled',())
        self.defineSlot('toggle_enabled',())

        # Graphic elements-----------------------------------------------------
        self.main_gbox = QtGui.QGroupBox(self)
        self.motor_label = QtGui.QLabel(self.main_gbox)

        #Main controls
        self.control_box = QtGui.QWidget(self.main_gbox)
        self.move_left_button = QtGui.QPushButton(self.control_box)
        self.move_left_button.setIcon(QtGui.QIcon(Qt4_Icons.load('far_left')))
        self.move_left_button.setToolTip("Moves the motor down (while pressed)")
        self.move_right_button = QtGui.QPushButton(self.control_box)
        self.move_right_button.setIcon(QtGui.QIcon(Qt4_Icons.load('far_right')))
        self.move_right_button.setToolTip("Moves the motor up (while pressed)")  
        
        self.spin_box = CustomSpinBox(self.control_box)
        self.spin_box.set_decimal_places(4)
        self.spin_box.setMinValue(-10000)
        self.spin_box.setMaxValue(10000)
        self.spin_box.setMinimumSize(QtCore.QSize(75, 25))
        self.spin_box.setMaximumSize(QtCore.QSize(75, 25))
        self.spin_box.setToolTip("Moves the motor to a specific position or step by step; right-click for motor history")

        #Extra controls
        self.extra_button_box = QtGui.QWidget(self.main_gbox)
        self.stop_button = QtGui.QPushButton(self.extra_button_box)
        self.stop_button.setIcon(QtGui.QIcon(Qt4_Icons.load('stop_small')))
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stops the motor")
        self.step_button = QtGui.QPushButton(self.extra_button_box)
        self.step_button_icon = QtGui.QIcon(Qt4_Icons.load('steps_small'))
        self.step_button.setIcon(self.step_button_icon)
        self.step_button.setToolTip("Changes the motor step")

        self.step_list = CustomComboBox(self.extra_button_box)
        #self.step_list.setValidator(QDoubleValidator(self))
        self.step_list.setDuplicatesEnabled(False)

        # Layout --------------------------------------------------------------
        self.control_box_layout = QtGui.QHBoxLayout()
        self.control_box_layout.addWidget(self.move_left_button)
        self.control_box_layout.addWidget(self.move_right_button)
        self.control_box_layout.addWidget(self.spin_box)
        self.control_box_layout.setSpacing(0)
        self.control_box_layout.setContentsMargins(0, 0, 0, 0)
        self.control_box.setLayout(self.control_box_layout)  

        self.main_gbox_layout = QtGui.QHBoxLayout()
        self.main_gbox_layout.addWidget(self.motor_label) 
        self.main_gbox_layout.addWidget(self.control_box)
        self.main_gbox_layout.setSpacing(0)
        self.main_gbox_layout.setContentsMargins(0, 0, 0, 0)
        self.main_gbox.setLayout(self.main_gbox_layout) 
      
        self.extra_button_box_layout = QtGui.QHBoxLayout()
        self.extra_button_box_layout.addWidget(self.stop_button)
        self.extra_button_box_layout.addWidget(self.step_button)
        self.extra_button_box_layout.addWidget(self.step_list)
        self.extra_button_box_layout.setSpacing(0)
        self.extra_button_box_layout.setContentsMargins(0, 0, 0, 0)
        self.extra_button_box.setLayout(self.extra_button_box_layout)

        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.addWidget(self.main_gbox)
        self.main_layout.addWidget(self.extra_button_box)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout) 

        # SizePolicy (horizontal, vertical) -----------------------------------
        self.move_left_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                            QtGui.QSizePolicy.Minimum)
        self.move_right_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                             QtGui.QSizePolicy.Minimum)
        self.stop_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                       QtGui.QSizePolicy.Minimum)
        self.step_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                       QtGui.QSizePolicy.Minimum)
        self.extra_button_box.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                            QtGui.QSizePolicy.Fixed)

        # Object events ---------------------
        self.connect(self.step_list, QtCore.SIGNAL('activated(int)'), self.go_to_step)
        self.connect(self.spin_box, QtCore.SIGNAL('stepUp'), self.step_up)
        self.connect(self.spin_box, QtCore.SIGNAL('stepDown'), self.step_down)
        self.connect(self.stop_button, QtCore.SIGNAL('clicked()'), self.stop_motor)
        self.connect(self.step_button, QtCore.SIGNAL('clicked()'), self.open_step_editor)
        self.connect(self.spin_box, QtCore.SIGNAL('contextMenu'), self.open_history_menu)
        self.connect(self.spin_box, QtCore.SIGNAL('valueChanged()'), self.value_changed_str)
        self.connect(self.move_left_button, QtCore.SIGNAL('pressed()'), self.move_down)
        self.connect(self.move_left_button, QtCore.SIGNAL('released()'), self.stop_moving)
        self.connect(self.move_right_button, QtCore.SIGNAL('pressed()'), self.move_up)
        self.connect(self.move_right_button, QtCore.SIGNAL('released()'), self.stop_moving)

        # Other ---------------------------------------------------------------
        #self.instanceSynchronize("spin_box","step_list")

    def setExpertMode(self, mode):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.in_expert_mode = mode
        if self['hideInUser']:
            if mode:
                self.main_gbox.show()
            else:
                self.main_gbox.hide()

    def toggle_enabled(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(not self.isEnabled())

    def run(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.in_expert_mode is not None:
            self.setExpertMode(self.in_expert_mode)

    def stop(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.main_gbox.show()

    def get_line_step(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.spin_box.lineStep()

    def set_line_step(self, val):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.spin_box.setLineStep(float(val))
        found = False
        for i in range(self.step_list.count()):
            if float(str(self.step_list.text(i))) == float(val):
                found = True
        if not found:
            self.step_list.addItem(self.step_button_icon, str(val))
            self.step_list.setCurrentIndex(self.step_list.count() - 1)

    def go_to_step(self, step_index):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        step = str(self.step_list.currentText())
        if step != "":
            self.step_list.changeItem(self.step_button_icon, step, step_index)
            self.step_list.setCurrentIndex(step_index)
            self.setLineStep(step)

    def set_step_button_icon(self, icon_name):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.step_button_icon = QtGui.QIcon(Qt4_Icons.load(icon_name))
        self.step_button.setIcon(self.stepButtonIcon)
        for i in range(self.step_kist.count()):
            txt = self.step_list.text(i)
            self.step_list.changeItem(self.step_button_icon, txt, i)

    def stop_motor(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.motor.stop()

    def stop_moving(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.demand_move = 0

    def move_up(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.demand_move = 1
        self.update_gui()
        state = self.motor_hwobj.getState()
        if state == self.motor_jwobj.READY:
            if self['invertButtons']:
                self.really_move_down()
            else:
                self.really_move_up()

    def move_down(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.demand_move = -1
        self.update_gui()
        state = self.motor_hwobj.getState()
        if state == self.motor_hwobj.READY:
            if self['invertButtons']:
                self.really_move_up()
            else:
                self.really_move_down()

    def really_move_up(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self['delta'] != "":
            s = float(self['delta'])
        else:        
            try:
                s = self.motor_hwobj.GUIstep
            except:
                s = 1.0
        if self.motor_hwobj is not None:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveRelative(s)

    def really_move_down(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self['delta'] != "":
            s = float(self['delta'])
        else:
            try:
                s = self.motor_hwobj.GUIstep
            except:
                s = 1.0
        if self.motor_hwobj is not None:
            if self.motor_hwobj.isReady():
                self.set_spin_box_color(self.motor_hwobj.READY)
                self.motor_hwobj.moveRelative(-s)

    def update_gui(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None: 
            self.main_gbox.setEnabled(True)
            try:
                if self.motor_hwobj.isReady():
                    self.limits_changed(self.motor_hwobj.getLimits())
                    self.position_changed(self.motor_hwobj.getPosition())
                self.state_changed(self.motor_hwobj.getState())
            except:
                if self.motor_hwobj is not None:
                    self.state_changed(self.motor_hwobj.UNUSABLE)
                else:
                    pass
        else:
            self.main_gbox.setEnabled(False)

    def limits_changed(self, limits):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.spin_box.blockSignals(True)
        self.spin_box.setMinimum(limits[0])
        self.spin_box.setMaximum(limits[1])
        self.spin_box.blockSignals(False)
        self.setToolTip(limits = limits)

    def open_history_menu(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        menu = QtGui.QMenu(self)
        menu.insertItem(QtGui.QLabel('<nobr><b>%s history</b></nobr>' % self.motor_hwobj.userName(), menu))
        menu.insertSeparator()
        for i in range(len(self.posHistory)):
            menu.insertItem(self.posHistory[i], i)
        menu.popup(QtCore.QCursor.pos())
        QtCore.QObject.connect(menu, QtCore.SIGNAL('activated(int)'), self.goToHistoryPos)

    def go_to_history_pos(self, index):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pos = self.pos_history[index]
        self.motor_hwobj.move(float(pos))

    def update_history(self, pos):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pos = str(pos)
        if pos not in self.pos_history:
            if len(self.pos_history) == Qt4_MotorSpinBoxBrick.MAX_HISTORY:
                del self.pos_history[-1]
            self.pos_history.insert(0, pos)

    def open_step_editor(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.isRunning():
            if self.step_editor is None:
                self.step_editor = StepEditorDialog(self)
                icons_list = self['icons'].split()
                try:
                    self.step_editor.setQt4_Icons(icons_list[4], icons_list[5])
                except IndexError:
                    pass

            self.step_editor.set_motor(self.motor_hwobj, self, self['label'], self['defaultStep'])
            s = self.font().pointSize()
            f = self.step_editor.font()
            f.setPointSize(s)
            self.step_editor.setFont(f)
            self.step_editor.updateGeometry()

            self.step_editor.show()
            #self.step_editor.setActiveWindow()
            #self.step_editor.raiseW()

    def position_changed(self, new_position):  
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.spin_box.setValue(float(new_position))

    def set_spin_box_color(self, state):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        color = Qt4_MotorSpinBoxBrick.STATE_COLORS[state]
        Qt4_widget_colors.set_widget_color(self.spin_box.lineEdit(), color)

    def state_changed(self, state):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.set_spin_box_color(state)
        if state == self.motor_hwobj.MOVESTARTED:
            self.update_history(self.motor_hwobj.getPosition())
        if state == self.motor_hwobj.READY:
            if self.demand_move == 1:
                if self['invertButtons']:
                    self.really_move_down()
                else:
                    self.really_move_up()
                return
            elif self.demand_move == -1:
                if self['invertButtons']:
                    self.really_move_up()
                else:
                    self.really_move_down()
                return

            self.spin_box.setMoving(False)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        elif state in (self.motor_hwobj.NOTINITIALIZED, self.motor_hwobj.UNUSABLE):
            self.spin_box.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        elif state in (self.motor_hwobj.MOVING, self.motor_hwobj.MOVESTARTED):
            self.stop_button.setEnabled(True)
            self.spin_box.setMoving(True)
        elif state == self.motor_hwobj.ONLIMIT:
            self.spin_box.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        self.setToolTip(state = state)

    def step_up(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveRelative(self.spin_box.lineStep())

    def step_down(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor is not None:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveRelative(-self.spin_box.lineStep())

    def value_changed_int(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.update_gui()
        if self.motor_hwobj is not None:
            self.motor_hwobj.move(value)

    def value_changed_str(self): #,value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            self.motor_hwobj.move(float(str(self.spin_box.lineEdit().text())))

    def setToolTip(self, name = None, state = None, limits = None):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        states = ("NOTINITIALIZED", "UNUSABLE", "READY", 
                  "MOVESTARTED", "MOVING", "ONLIMIT")
        if name is None:
            name = self['mnemonic']

        if self.motor_hwobj is None:
            tip = "Status: unknown motor "+name
        else:
            try:
                if state is None:
                    state = self.motor_hwobj.getState()
            except:
                logging.exception("%s: could not get motor state", self.objectName())
                state = self.motor_hwobj.UNUSABLE
                
            try:
                if limits is None and self.motor_hwobj.isReady():
                    limits = self.motor_hwobj.getLimits()
            except:
                logging.exception("%s: could not get motor limits", self.objectName())
                limits = None

            try:
                state_str = states[state]
            except IndexError:
                state_str = "UNKNOWN"
                
            limits_str = ""
            if limits is not None:
                l_bot = self['formatString'] % float(limits[0])
                l_top = self['formatString'] % float(limits[1])
                limits_str = " Limits:%s,%s" % (l_bot, l_top)
            tip = "State:" + state_str + limits_str

        self.motor_label.setToolTip(tip)
        if not self['showBox']:
            tip = ""
        self.main_gbox.setToolTip(tip)

    def setLabel(self, label):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if not self['showLabel']:
            label = None

        if label is None:
            self.motor_label.hide()
            self.containerBox.setTitle("")
            return
    
        if label == "":
            if self.motor_hwobj is not None:
                label = self.motor_hwobj.username

        if self['showBox']:
            self.motor_label.hide()
            self.main_gbox.setTitle(label)
        else:
            if label != "":
                label += ": "
            self.main_gbox.setTitle("")
            self.motor_label.setText(label)
            self.motor_label.show()

    def set_motor(self, motor, motor_ho_name = None):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            self.disconnect(self.motor_hwobj, QtCore.SIGNAL('limitsChanged'), self.limits_changed)
            self.disconnect(self.motor_hwobj, QtCore.PYSIGNAL('positionChanged'), self.position_changed)
            self.disconnect(self.motor_hwobj, QtCore.PYSIGNAL('stateChanged'), self.state_changed)

        if motor_ho_name is not None:
            self.motor_hwobj = self.getHardwareObject(motor_ho_name)
        
        if self.motor_hwobj is None:
          # first time motor is set
            try:
                s = float(self['defaultStep'])
            except:
                try:
                    s = motor_hwobj.GUIstep
                except:
                    s = 1.0
            self.set_line_step(s)

        if self.motor_hwobj is not None:
            self.connect(self.motor_hwobj, QtCore.SIGNAL('limitsChanged'), self.limits_changed)
            self.connect(self.motor_hwobj, QtCore.SIGNAL('positionChanged'), self.position_changed, instanceFilter = True)
            self.connect(self.motor_hwobj, QtCore.SIGNAL('stateChanged'), self.state_changed, instanceFilter=True)

        self.pos_history = []
        self.update_gui()
        #self['label'] = self['label']
        #self['defaultStep']=self['defaultStep']

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == 'mnemonic':
            self.set_motor(self.motor_hwobj, new_value)
        elif property_name == 'formatString':
            if self.motor_hwobj is not None:
                self.update_GUI()
        elif property_name == 'label':
            self.setLabel(new_value)
        elif property_name == 'showLabel':
            if new_value:
                self.setLabel(self['label'])
            else:
                self.setLabel(None)
        elif property_name == 'showMoveButtons':
            if new_value:
                self.move_left_button.show()
                self.move_right_button.show()
            else:            
                self.move_left_button.hide()
                self.move_right_button.hide()
        elif property_name == 'showStop':
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == 'showStep':
            if new_value:
                self.step_button.show()
            else:
                self.step_button.hide()
        elif property_name == 'showStepList':
            if new_value:
                self.step_list.show()
            else:
                self.step_list.hide()
        elif property_name == 'showPosition':
            if new_value:
                self.spin_box.show()
            else:
                self.spin_box.hide()
        elif property_name == 'showBox':
            if new_value:
                self.main_button_gbox.setFrameShape(self.self.main_button_gbox)
                #self.main_gbox.setContentsMargins(2, 2, 0, 0)
                #elf.containerBox.setInsideSpacing(0)
            else:
                self.main_gbox.setContentsMargins(2, 0, 0, 0)
                #self.containerBox.setFrameShape(self.containerBox.NoFrame)
                #elf.containerBox.setInsideSpacing(0)            
            self.setLabel(self['label'])
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.move_left_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[0])))
                self.move_right_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[1])))
                self.stop_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[2])))
                self.set_step_button_icon(icons_list[3])
            except IndexError:
                pass                
        elif property_name == 'helpDecrease':
            if new_value == "":
                self.move_left_button.setToolTip("Moves the motor down (while pressed)")
            else:
                self.move_left_button.setToolTip(newValue)
        elif property_name == 'helpIncrease':
            if new_value == "" :
                self.move_right_button.setToolTip("Moves the motor up (while pressed)")
            else:
                self.move_right_button.setToolTip(newValue)
        elif property_name == 'decimalPlaces':
            try:
                dec_places = int(new_value)
            except ValueError:
                dec_places = 2
            self.spin_box.set_decimal_places(dec_places)
        elif property_name == 'defaultStep':
            if new_value != "":
                self.setLineStep(float(new_value))
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

class CustomSpinBox(QtGui.QSpinBox):
    """
    Descript. :
    Args.     :
    Return.   : 
    """

    CHANGED_COLOR = QtGui.QColor(255, 165, 0)

    def __init__(self, parent):    
        """
        Descript. :
        """
        QtGui.QSpinBox.__init__(self, parent)
        self.decimalPlaces = 1
        self.__moving = False
        self.colorGroupDict = {}
        #self.setValidator(QtCore.QDoubleValidator(self))
        self.lineEdit().setAlignment(QtCore.Qt.AlignRight)
        QtCore.QObject.connect(self.lineEdit(), QtCore.SIGNAL("textChanged(const QString &)"), self.textChanged)
        self.range_change()
        self.update()

    def setMoving(self, moving):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(not moving)
        self.__moving = moving

    def textChanged(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.__moving:
            return
        else:
            Qt4_widget_colors.set_widget_color(self.lineEdit(), 
                                           CustomSpinBox.CHANGED_COLOR,
                                           QtGui.QPalette.Base)

    def i2d(self, v):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return v / math.pow(10, self.decimalPlaces)

    def d2i(self, v):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        d = 1 if v >= 0 else -1
        return int(d * 0.5 + math.pow(10, self.decimalPlaces) * v)

    def range_change(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return 

    def setValue(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if type(value) == type(0.0):
            return QtGui.QSpinBox.setValue(self, self.d2i(value))
        else:
            return self.setValue(self.i2d(value)) 

    def value(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.i2d(QtGui.QSpinBox.value(self))

    def stepUp(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.emit(QtCore.SIGNAL("stepUp"), ())

    def stepDown(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.emit(QtCore.SIGNAL("stepDown"), ())

    def set_decimal_places(self, places):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        minval = self.minValue()
        maxval = self.maxValue()
        val = self.value()
        ls = self.lineStep()
        self.decimalPlaces = places
        self.setMaxValue(maxval)
        self.setMinValue(minval)
        self.setValue(val)
        self.setLineStep(ls)
        self.update()

    def setMinValue(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        value = self.d2i(value) 
        if math.fabs(value) > 1E8:
            value = int(math.copysign(1E8, value))
        return QtGui.QSpinBox.setMinimum(self, value)

    def setMaxValue(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        value = self.d2i(value) 
        if math.fabs(value) > 1E8:
            value = int(math.copysign(1E8, value))
        return QtGui.QSpinBox.setMaximum(self, value)

    def minValue(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.i2d(QtGui.QSpinBox.minimum(self))

    def maxValue(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.i2d(QtGui.QSpinBox.maximum(self))

    def decimalPlaces(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.decimalPlaces

    def mapValueToText(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        frmt =  "%." + "%df" % self.decimalPlaces
        return QtCore.QString(frmt % self.i2d(value))

    def mapTextToValue(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        t = str(self.text())
        try:
            return (self.d2i(float(t)), True)
        except:
            return (0, False)

    def lineStep(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.i2d(QtGui.QSpinBox.singleStep(self))

    def setLineStep(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return QtGui.QSpinBox.setSingleStep(self, self.d2i(step))

    def eventFilter(self, obj, ev):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if isinstance(ev, QtCore.QContextMenuEvent):
            self.emit(QtCore.SIGNAL("contextMenu"), ())
            return True
        else:
            return QtGui.QSpinBox.eventFilter(self, obj, ev)

class StepEditorDialog(QtGui. QDialog):
    """
    Descript. :
    """

    def __init__(self, parent):
        """
        Descript. :
        """
        QtGui.QDialog.__init__(self, parent)
        # Graphic elements-----------------------------------------------------
        #self.main_gbox = QtGui.QGroupBox('Motor step', self)
        #box2 = QtGui.QWidget(self)
        self.grid = QtGui.QWidget(self)
        label1 = QtGui.QLabel("Current:", self)
        self.current_step = QtGui.QLineEdit(self)
        self.current_step.setEnabled(False)
        label2 = QtGui.QLabel("Set to:", self)
        self.new_step = QtGui.QLineEdit(self)
        self.new_step.setAlignment(QtCore.Qt.AlignRight)
        self.new_step.setValidator(QtGui.QDoubleValidator(self))

        self.button_box = QtGui.QWidget(self)
        self.apply_button = QtGui.QPushButton("Apply", self.button_box)
        self.close_button = QtGui.QPushButton("Dismiss", self.button_box)

        # Layout --------------------------------------------------------------
        self.button_box_layout = QtGui.QHBoxLayout()
        self.button_box_layout.addWidget(self.apply_button)
        self.button_box_layout.addWidget(self.close_button)
        self.button_box.setLayout(self.button_box_layout)

        self.grid_layout = QtGui.QGridLayout()
        self.grid_layout.addWidget(label1, 0, 0)
        self.grid_layout.addWidget(self.current_step, 0, 1)
        self.grid_layout.addWidget(label2, 1, 0)
        self.grid_layout.addWidget(self.new_step, 1, 1)
        self.grid.setLayout(self.grid_layout)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addWidget(self.grid)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Qt signal/slot connections -----------------------------------------
        self.connect(self.new_step, QtCore.SIGNAL('returnPressed()'), self.apply_clicked)
        self.connect(self.apply_button, QtCore.SIGNAL('clicked()'), self.apply_clicked)
        self.connect(self.close_button, QtCore.SIGNAL("clicked()"), self.accept)

        # SizePolicies --------------------------------------------------------
        self.close_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
 
        # Other ---------------------------------------------------------------
        self.setWindowTitle("Motor step editor")

    def set_motor(self, motor, brick, name, default_step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.motor_hwobj = motor
        self.brick = brick

        if name is None or name == "":
            name = motor.userName()
        self.setWindowTitle(name)
        self.setWindowTitle('%s step editor' % name)
        self.current_step.setText(str(brick.get_line_step()))

    def apply_clicked(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        try:
            val = float(str(self.new_step.text()))
        except ValueError:
            return
        self.brick.set_line_step(val)
        self.new_step.setText('')
        self.current_step.setText(str(val))

    def setQt4_Icons(self, apply_icon, dismiss_icon):
        self.apply_button.setIcon(QtGui.QIcon(Qt4_Icons.load(apply_icon)))
        self.close_button.setIcon(QtGui.QIcon(Qt4_Icons.load(dismiss_icon)))

class CustomComboBox(QtGui.QComboBox):
    """
    Descript. :
    """
    CHANGED_COLOR = QtGui.QColor(255, 165, 0)
    
    def __init__(self, *args):
        """
        Descript. :
        """
        QtGui.QComboBox.__init__(self, *args)    
        self.setEditable(True)
        QtCore.QObject.connect(self, QtCore.SIGNAL('activated(int)'), self.stepChanged)
        QtCore.QObject.connect(self, QtCore.SIGNAL('textChanged(const QString &)'), self.stepEdited)

    def sizeHint(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        hint = QtGui.QComboBox.sizeHint(self)
        hint.setWidth(1.10 * hint.width())
        return hint

    def stepEdited(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.lineEdit(),
                                       CustomComboBox.CHANGED_COLOR,
                                       QtGui.QPalette.Base)

    def stepChanged(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.lineEdit(),
                                       QtGui.QWidget.white,
                                       QtGui.QPalette.Base)
