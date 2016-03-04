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

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'Motor'

class Qt4_KappaPhiMotorsBrick(BlissWidget):

    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED, 
                    Qt4_widget_colors.DARK_GRAY,
                    Qt4_widget_colors.LIGHT_GREEN,
                    Qt4_widget_colors.LIGHT_YELLOW,  
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW)

    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None

        # Internal values ----------------------------------------------------- 
        

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic','string','')
        self.addProperty('label','string','')
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('defaultStep', 'string', '10.0')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements-----------------------------------------------------

        _main_groupbox = QtGui.QGroupBox(self)
        self.kappa_dspinbox = QtGui.QDoubleSpinBox(_main_groupbox)
        self.kappa_dspinbox.setRange(-360, 360)
        self.kappaphi_dspinbox = QtGui.QDoubleSpinBox(_main_groupbox)
        self.kappaphi_dspinbox.setRange(-360, 360)
        self.step_cbox = QtGui.QComboBox(_main_groupbox)
        self.step_button_icon = Qt4_Icons.load_icon('TileCascade2')
        self.close_button = QtGui.QPushButton("Close", _main_groupbox)
        self.stop_button = QtGui.QPushButton(_main_groupbox)

        # Layout --------------------------------------------------------------
        _main_groupbox_hlayout = QtGui.QHBoxLayout(_main_groupbox)
        _main_groupbox_hlayout.addWidget(QtGui.QLabel("Kappa:", _main_groupbox)) 
        _main_groupbox_hlayout.addWidget(self.kappa_dspinbox)
        _main_groupbox_hlayout.addWidget(QtGui.QLabel("Phi:", _main_groupbox))
        _main_groupbox_hlayout.addWidget(self.kappaphi_dspinbox)
        _main_groupbox_hlayout.addWidget(self.step_cbox)
        _main_groupbox_hlayout.addWidget(self.close_button)
        _main_groupbox_hlayout.addWidget(self.stop_button)
        _main_groupbox_hlayout.setSpacing(2)
        _main_groupbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(_main_groupbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        kappa_dspinbox_event = SpinBoxEvent(self.kappa_dspinbox)
        kappaphi_dspinbox_event = SpinBoxEvent(self.kappaphi_dspinbox)
        self.kappa_dspinbox.installEventFilter(kappa_dspinbox_event)
        self.kappaphi_dspinbox.installEventFilter(kappaphi_dspinbox_event)
        kappa_dspinbox_event.returnPressedSignal.connect(self.change_position)
        kappaphi_dspinbox_event.returnPressedSignal.connect(self.change_position)
        self.kappa_dspinbox.lineEdit().textEdited.connect(self.kappa_value_edited)
        self.kappaphi_dspinbox.lineEdit().textEdited.connect(self.kappaphi_value_edited)

        self.step_cbox.activated.connect(self.go_to_step)
        self.step_cbox.activated.connect(self.step_changed)
        self.step_cbox.textChanged.connect(self.step_edited)
 
        self.close_button.clicked.connect(self.close_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)
       
        #self.stop_button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
        # Other ---------------------------------------------------------------
        self.kappa_dspinbox.setAlignment(QtCore.Qt.AlignRight)
        self.kappa_dspinbox.setFixedWidth(75)
        self.kappaphi_dspinbox.setAlignment(QtCore.Qt.AlignRight)
        self.kappaphi_dspinbox.setFixedWidth(75)

        self.step_cbox.setEditable(True)
        self.step_cbox.setValidator(QtGui.QDoubleValidator(0, 360, 5, self.step_cbox))
        self.step_cbox.setDuplicatesEnabled(False)

        self.stop_button.setIcon(Qt4_Icons.load_icon('Stop2'))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(25)
        
    def propertyChanged(self,property_name, old_value, new_value):
        if property_name == 'mnemonic':
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaMotorMoved"), self.kappa_motor_moved) 
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaPhiMotorMoved"), self.kappaphi_motor_moved)
                self.disconnect(self.diffractometer_hwobj, Qtcore.SIGNAL('minidiffStatusChanged'),self.diffractometer_state_changed)
            self.diffractometer_hwobj = self.getHardwareObject(new_value)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaMotorMoved"), self.kappa_motor_moved)            
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaPhiMotorMoved"), self.kappaphi_motor_moved)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffStatusChanged'),self.diffractometer_state_changed)
                self.setDisabled(self.diffractometer_hwobj.in_plate_mode())
                self.diffractometer_state_changed("Ready")
            else:
                self.setEnabled(False)
        elif property_name == 'showStop':
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == 'defaultStep':
            if new_value != "":
                self.set_line_step(float(new_value))
                self.step_changed(None)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def stop_clicked(self):
        self.diffractometer_hwobj.stop_kappa_phi_move()

    def close_clicked(self):
        self.diffractometer_hwobj.move_kappa_and_phi(0, 0)

    def change_position(self):
        self.diffractometer_hwobj.move_kappa_and_phi(\
             self.kappa_dspinbox.value(),
             self.kappaphi_dspinbox.value())                 

    def kappa_value_edited(self, text):
        Qt4_widget_colors.set_widget_color(self.kappa_dspinbox.lineEdit(),
                                           Qt4_widget_colors.LINE_EDIT_CHANGED,
                                           QtGui.QPalette.Base)

    def kappaphi_value_edited(self, text):
        Qt4_widget_colors.set_widget_color(self.kappaphi_dspinbox.lineEdit(),
                                           Qt4_widget_colors.LINE_EDIT_CHANGED,
                                           QtGui.QPalette.Base)

    def kappa_value_accepted(self):
        self.diffractometer_hwobj.move_kappa_and_phi(\
             self.kappa_dspinbox.value(),
             self.kappaphi_dspinbox.value())
        
    def kappa_motor_moved(self, value):
        self.kappa_dspinbox.blockSignals(True)
        #txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappa_dspinbox.setValue(value)
        self.kappa_dspinbox.blockSignals(False)

    def kappaphi_motor_moved(self, value):
        self.kappaphi_dspinbox.blockSignals(True)
        #txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappaphi_dspinbox.setValue(value)   
        self.kappaphi_dspinbox.blockSignals(False)

    def diffractometer_state_changed(self, state):
        if state == "Ready":
            self.kappa_dspinbox.setEnabled(True)
            self.kappaphi_dspinbox.setEnabled(True)
            self.close_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            Qt4_widget_colors.set_widget_color(\
                self.kappa_dspinbox.lineEdit(),
                Qt4_widget_colors.LIGHT_GREEN,
                QtGui.QPalette.Base)
            Qt4_widget_colors.set_widget_color(\
                self.kappaphi_dspinbox.lineEdit(),
                Qt4_widget_colors.LIGHT_GREEN,
                QtGui.QPalette.Base)
        else:
            self.kappa_dspinbox.setEnabled(False)
            self.kappaphi_dspinbox.setEnabled(False) 
            self.close_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            Qt4_widget_colors.set_widget_color(\
                self.kappa_dspinbox.lineEdit(),
                Qt4_widget_colors.LIGHT_YELLOW, 
                QtGui.QPalette.Base)
            Qt4_widget_colors.set_widget_color(\
                self.kappaphi_dspinbox.lineEdit(),
                Qt4_widget_colors.LIGHT_YELLOW,
                QtGui.QPalette.Base)

    def go_to_step(self, step_index):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        step = str(self.step_cbox.currentText())
        if step != "":
            self.set_line_step(step)

    def set_line_step(self, val):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.kappa_dspinbox.setSingleStep(float(val))
        self.kappaphi_dspinbox.setSingleStep(float(val))
        found = False
        for i in range(self.step_cbox.count()):
            if float(str(self.step_cbox.itemText(i))) == float(val):
                found = True
                self.step_cbox.setItemIcon(i, self.step_button_icon)
        if not found:
            self.step_cbox.addItem(self.step_button_icon, str(val))
            self.step_cbox.setCurrentIndex(self.step_cbox.count() - 1)

    def step_changed(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.step_cbox.lineEdit(),
             QtCore.Qt.white, QtGui.QPalette.Base)

    def step_edited(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.step_cbox,
                                           Qt4_widget_colors.LINE_EDIT_CHANGED,
                                           QtGui.QPalette.Button)

class SpinBoxEvent(QtCore.QObject):
    returnPressedSignal = QtCore.pyqtSignal()
    contextMenuSignal = QtCore.pyqtSignal()

    def eventFilter(self,  obj,  event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in [QtCore.Qt.Key_Enter,
                               QtCore.Qt.Key_Return]:
                self.returnPressedSignal.emit()

        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            self.returnPressedSignal.emit()
        elif event.type() == QtCore.QEvent.ContextMenu:
            self.contextMenuSignal.emit()
        return False
