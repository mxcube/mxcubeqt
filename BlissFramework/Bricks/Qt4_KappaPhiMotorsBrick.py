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
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('formatString','formatString','###.##')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements-----------------------------------------------------

        _main_groupbox = QtGui.QGroupBox(self)
        self.kappa_value_ledit = QtGui.QLineEdit(_main_groupbox)
        #self.kappa_value_ledit.setFixedSize(qt.QSize(55,25))
        #self.kappa_value_ledit.setValidator(qt.QDoubleValidator(-180, 180, 2, self))
        #self.kappa_value_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN) 
        self.kappaphi_value_ledit = QtGui.QLineEdit(_main_groupbox)
        #self.kappaphi_value_ledit.setFixedSize(qt.QSize(55,25))
        #self.kappaphi_value_ledit.setValidator(qt.QDoubleValidator(-360, 360, 2, self))
        #self.kappaphi_value_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.apply_button = QtGui.QPushButton("Apply", _main_groupbox)  
        self.stop_button = QtGui.QPushButton(_main_groupbox)

        # Layout --------------------------------------------------------------
        _main_groupbox_hlayout = QtGui.QHBoxLayout(_main_groupbox)
        _main_groupbox_hlayout.addWidget(QtGui.QLabel("Kappa:", _main_groupbox)) 
        _main_groupbox_hlayout.addWidget(self.kappa_value_ledit)
        _main_groupbox_hlayout.addWidget(QtGui.QLabel("Phi:", _main_groupbox))
        _main_groupbox_hlayout.addWidget(self.kappaphi_value_ledit)
        _main_groupbox_hlayout.addWidget(self.apply_button)
        _main_groupbox_hlayout.addWidget(self.stop_button)
        _main_groupbox_hlayout.setSpacing(2)
        _main_groupbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(_main_groupbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.kappa_value_ledit.textChanged.connect(self.kappa_value_changed)
        self.kappaphi_value_ledit.textChanged.connect(self.kappaphi_value_changed)
        self.apply_button.clicked.connect(self.apply_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)
       
        #self.stop_button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
        # Other ---------------------------------------------------------------
        self.kappa_value_ledit.setAlignment(QtCore.Qt.AlignRight)
        self.kappa_value_ledit.setFixedWidth(75)
        self.kappaphi_value_ledit.setAlignment(QtCore.Qt.AlignRight)
        self.kappaphi_value_ledit.setFixedWidth(75)
        self.stop_button.setIcon(Qt4_Icons.load_icon('stop_small'))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(25)
        
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaMotorMoved"), self.kappa_motor_moved) 
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaPhiMotorMoved"), self.kappaphi_motor_moved)
                self.disconnect(self.diffractometer_hwobj, Qtcore.SIGNAL('minidiffStatusChanged'),self.diffractometer_state_changed)
            self.diffractometer_hwobj = self.getHardwareObject(newValue)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaMotorMoved"), self.kappa_motor_moved)            
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL("kappaPhiMotorMoved"), self.kappaphi_motor_moved)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffStatusChanged'),self.diffractometer_state_changed)
                self.setDisabled(self.diffractometer_hwobj.in_plate_mode())
                self.diffractometer_state_changed("Ready")
            else:
                self.setEnabled(False)
        elif propertyName=='showStop':
            if newValue:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif propertyName=='decimalPlaces':
            try:
                self.decPlaces=int(newValue)
            except ValueError:
                self.decPlaces=2
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def stop_clicked(self):
        self.diffractometer_hwobj.stop_kappa_phi_move()

    def apply_clicked(self):
        try:
           kappa_value = float(self.kappa_value_ledit.text())
           phi_value = float(self.kappaphi_value_ledit.text())
           self.diffractometer_hwobj.move_kappa_and_phi(kappa_value, phi_value)
        except:
           pass
        self.kappa_value_ledit.clearFocus()
        self.kappaphi_value_ledit.clearFocus()

    def kappa_value_changed(self, new_text):
        Qt4_widget_colors.set_widget_color(self.kappa_value_ledit, 
                                           QtGui.QColor(255,165,0),
                                           QtGui.QPalette.Base)

    def kappaphi_value_changed(self, new_text):
        Qt4_widget_colors.set_widget_color(self.kappaphi_value_ledit, 
                                           QtGui.QColor(255,165,0),
                                           QtGui.QPalette.Base)

    def kappa_motor_moved(self, value):
        self.kappa_value_ledit.blockSignals(True)
        txt = '?' if value is None else '%s' %\
              str(self['formatString'] % value)
        self.kappa_value_ledit.setText(txt)
        self.kappa_value_ledit.blockSignals(False)
    
    def kappaphi_motor_moved(self, value):
        self.kappaphi_value_ledit.blockSignals(True)
        txt = '?' if value is None else '%s' %\
              str(self['formatString'] % value)
        self.kappaphi_value_ledit.setText(txt)   
        self.kappaphi_value_ledit.blockSignals(False)

    def diffractometer_state_changed(self, state):
        if state == "Ready":
            self.apply_button.setEnabled(True)
            self.kappa_value_ledit.setEnabled(True)
            self.kappaphi_value_ledit.setEnabled(True)
            Qt4_widget_colors.set_widget_color(self.kappa_value_ledit,
                                               Qt4_widget_colors.LIGHT_GREEN,
                                               QtGui.QPalette.Base)
            Qt4_widget_colors.set_widget_color(self.kappaphi_value_ledit,
                                               Qt4_widget_colors.LIGHT_GREEN,
                                               QtGui.QPalette.Base)
        else:
            self.apply_button.setEnabled(False)
            self.kappa_value_ledit.setEnabled(False)
            self.kappaphi_value_ledit.setEnabled(False) 
            Qt4_widget_colors.set_widget_color(self.kappa_value_ledit,
                                               Qt4_widget_colors.LIGHT_YELLOW,
                                               QtGui.QPalette.Base)
            Qt4_widget_colors.set_widget_color(self.kappaphi_value_ledit,
                                               Qt4_widget_colors.LIGHT_YELLOW,
                                               QtGui.QPalette.Base)

    def setLabel(self,label):
        if not self['showLabel']:
            label=None

        if label is None:
            self.labelBox.hide()
            self.containerBox.setTitle("")
            return

        if self['showBox']:
            self.labelBox.hide()
            self.containerBox.setTitle(label)
        else:
            if label!="":
                label+=": "
            self.containerBox.setTitle("")
            self.label.setText(label)
            self.labelBox.show()

