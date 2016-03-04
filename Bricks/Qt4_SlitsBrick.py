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

"""
[Name] Qt4_SlitsBrick

[Description]
SlitsBrick displays horizontal and vertical gap size. 
Size is estimated by related slit pairs
Depending of the beam focusing mode user can enter gap sizes by using spinboxes.

[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| slitBox      | string | name of the BeamSlitBox Hardware Object
| formatString | string | format string for size display (defaults to #.###)
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]	
-----------------------------------------------------------------------
| name         | signals             | functions
-----------------------------------------------------------------------
| BeamSlitBox  | gapSizeChanged      | setGap() 
|  	       | statusChanged       | stopGapChange()
|  	       | focusModeChanged    | getStepSizes()
|  	       | gapLimitsVhanged    | gapLimits()
-----------------------------------------------------------------------
"""

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'General'


class Qt4_SlitsBrick(BlissWidget):
    CONNECTED_COLOR = Qt4_widget_colors.LIGHT_GREEN
    CHANGED_COLOR = Qt4_widget_colors.LIGHT_YELLOW
    OUTLIMITS_COLOR = Qt4_widget_colors.LIGHT_RED

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------	
	self.slitbox_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString','formatString','###')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = QtGui.QGroupBox('Slits', self) #h
        hor_label = QtGui.QLabel("Horizontal:", self.main_gbox)
        self.current_hor_pos_ledit = QtGui.QLineEdit(self.main_gbox)
	self.current_hor_pos_ledit.setAlignment(QtCore.Qt.AlignRight)
        boldFont = self.current_hor_pos_ledit.font()
        boldFont.setBold(True)
        self.current_hor_pos_ledit.setFont(boldFont)
	self.current_hor_pos_ledit.setMaximumWidth(70)
        self.current_hor_pos_ledit.setEnabled(False)
        self.hor_pos_dspinbox = QtGui.QDoubleSpinBox(self.main_gbox)
	self.hor_pos_dspinbox.setMaximumWidth(70)
	self.hor_pos_dspinbox.setEnabled(False)	
	self.set_hor_gap_button = QtGui.QPushButton(\
             Qt4_Icons.load_icon("Draw"), "", self.main_gbox)
	self.set_hor_gap_button.setEnabled(False)
        self.set_hor_gap_button.setFixedWidth(27)
	self.stop_hor_button = QtGui.QPushButton(\
             Qt4_Icons.load_icon("Stop2"), "", self.main_gbox)
	self.stop_hor_button.setEnabled(False)
        self.stop_hor_button.setFixedWidth(27)

	#Vertical gap
        ver_label = QtGui.QLabel("Vertical:", self.main_gbox)
        self.current_ver_pos_ledit = QtGui.QLineEdit(self.main_gbox)
	self.current_ver_pos_ledit.setAlignment(QtCore.Qt.AlignRight)
        self.current_ver_pos_ledit.setFont(boldFont)
	self.current_ver_pos_ledit.setMaximumWidth(70)
        self.current_ver_pos_ledit.setEnabled(False)
        self.ver_pos_dspinbox = QtGui.QDoubleSpinBox(self.main_gbox)
	self.ver_pos_dspinbox.setMaximumWidth(70)
	self.ver_pos_dspinbox.setEnabled(False)
	self.set_ver_gap_button = QtGui.QPushButton(\
             Qt4_Icons.load_icon("Draw"), "", self.main_gbox)
	self.set_ver_gap_button.setEnabled(False)
        self.set_ver_gap_button.setFixedWidth(27)
	self.stop_ver_button = QtGui.QPushButton(\
             Qt4_Icons.load_icon("Stop2"), "", self.main_gbox)
	self.stop_ver_button.setEnabled(False)
        self.stop_ver_button.setFixedWidth(27)

        # Layout --------------------------------------------------------------
        _main_gbox_gridlayout = QtGui.QGridLayout(self.main_gbox)
        _main_gbox_gridlayout.addWidget(hor_label, 0, 0)
        _main_gbox_gridlayout.addWidget(self.current_hor_pos_ledit, 0, 1)
        _main_gbox_gridlayout.addWidget(self.hor_pos_dspinbox, 0, 2)
        _main_gbox_gridlayout.addWidget(self.set_hor_gap_button, 0, 3)
        _main_gbox_gridlayout.addWidget(self.stop_hor_button, 0, 4)
        _main_gbox_gridlayout.addWidget(ver_label, 1, 0)
        _main_gbox_gridlayout.addWidget(self.current_ver_pos_ledit, 1, 1)
        _main_gbox_gridlayout.addWidget(self.ver_pos_dspinbox, 1, 2)
        _main_gbox_gridlayout.addWidget(self.set_ver_gap_button, 1, 3)
        _main_gbox_gridlayout.addWidget(self.stop_ver_button, 1, 4)
        _main_gbox_gridlayout.setSpacing(2)
        _main_gbox_gridlayout.setContentsMargins(2, 2, 2, 2)        

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.hor_pos_dspinbox.lineEdit().textChanged.\
             connect(self.hor_gap_edited)
        self.hor_pos_dspinbox.lineEdit().returnPressed.\
             connect(self.change_hor_gap)
        self.set_hor_gap_button.clicked.connect(self.change_hor_gap)
        self.stop_hor_button.clicked.connect(self.stop_hor_clicked)

	self.ver_pos_dspinbox.lineEdit().textChanged.\
             connect(self.ver_gap_edited)
        self.ver_pos_dspinbox.lineEdit().returnPressed.\
             connect(self.change_ver_gap)
	self.set_ver_gap_button.clicked.connect(self.change_ver_gap)
	self.stop_ver_button.clicked.connect(self.stop_ver_clicked)

        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        self.current_hor_pos_ledit.setToolTip("Current horizontal gap size")
        self.set_hor_gap_button.setToolTip("Set new horizontal gap size")
        self.stop_hor_button.setToolTip("Stop horizontal slits movements")
        self.current_ver_pos_ledit.setToolTip("Current vertical gap size")
        self.set_ver_gap_button.setToolTip("Set new vertical gap size")
        self.stop_ver_button.setToolTip("Stop vertical slits movements")

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'mnemonic':
	    if self.slitbox_hwobj is not None:
		self.disconnect(self.slitbox_hwobj, QtCore.SIGNAL('gapSizeChanged'), self.gap_value_changed)
		self.disconnect(self.slitbox_hwobj, QtCore.SIGNAL('statusChanged'), self.gap_status_changed)
	        self.disconnect(self.slitbox_hwobj, QtCore.SIGNAL('focusModeChanged'), self.focus_mode_changed)
	        self.disconnect(self.slitbox_hwobj, QtCore.SIGNAL('gapLimitsChanged'), self.gap_limits_changed)
	    self.slitbox_hwobj = self.getHardwareObject(new_value)
	    if self.slitbox_hwobj is not None:
		self.connect(self.slitbox_hwobj, QtCore.SIGNAL('gapSizeChanged'), self.gap_value_changed)
		self.connect(self.slitbox_hwobj, QtCore.SIGNAL('statusChanged'), self.gap_status_changed)
                self.connect(self.slitbox_hwobj, QtCore.SIGNAL('focusModeChanged'), self.focus_mode_changed)
	        self.connect(self.slitbox_hwobj, QtCore.SIGNAL('gapLimitsChanged'), self.gap_limits_changed)

                self.slitbox_hwobj.update_values()
            	self.slitBoxReady()
	    else:
                self.slitBoxNotReady()
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)
    
    def initiate_spinboxes(self):
        stepSizes = self.slitbox_hwobj.get_step_sizes()
	gapLimits = self.slitbox_hwobj.get_gap_limits('Hor')
	value = int(self.slitbox_hwobj.get_gap_hor() * 1000)
        self.hor_pos_dspinbox.setRange(int(gapLimits[0] * 1000), 
                                       int(gapLimits[1] * 1000))
        self.hor_pos_dspinbox.setSingleStep(1)
        self.hor_pos_dspinbox.setValue(value)
	gapLimits = self.slitbox_hwobj.get_gap_limits('Ver')
        value = int(self.slitbox_hwobj.get_gap_ver() * 1000)
        self.ver_pos_dspinbox.setRange(int(gapLimits[0] * 1000), 
                                       int(gapLimits[1] * 1000))
        self.ver_pos_dspinbox.setSingleStep(1)
        self.ver_pos_dspinbox.setValue(value)

        Qt4_widget_colors.set_widget_color(self.hor_pos_dspinbox,
                                           Qt4_SlitsBrick.CONNECTED_COLOR,
                                           QtGui.QPalette.Button)
        Qt4_widget_colors.set_widget_color(self.ver_pos_dspinbox,
                                           Qt4_SlitsBrick.CONNECTED_COLOR,
                                           QtGui.QPalette.Button)

    def stop_hor_clicked(self):
	self.slitbox_hwobj.stop_gap_move('Hor')

    def stop_ver_clicked(self):
	self.slitbox_hwobj.stop_gap_move('Ver')  

    def hor_gap_edited(self, text):
        Qt4_widget_colors.set_widget_color(self.hor_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LINE_EDIT_CHANGED,
                                              QtGui.QPalette.Base)

    def ver_gap_edited(self, text):
        Qt4_widget_colors.set_widget_color(self.ver_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LINE_EDIT_CHANGED,
                                              QtGui.QPalette.Base)

    def change_hor_gap(self):
        val = self.hor_pos_dspinbox.value() / 1000.0
        self.slitbox_hwobj.set_gap('Hor', val)
        self.hor_pos_dspinbox.clearFocus()
    
    def change_ver_gap(self):
        val = self.ver_pos_dspinbox.value() / 1000.0
        self.slitbox_hwobj.set_gap('Ver', val)
        self.ver_pos_dspinbox.clearFocus()

    def slitBoxReady(self):
	self.main_gbox.setEnabled(True)
	self.initiate_spinboxes()

    def slitBoxNotReady(self):
        self.main_gbox.setEnabled(False)
    
    def gap_value_changed(self, newGap):
        if newGap[0] is None:
	     self.current_hor_pos_ledit.setText("-")
	#elif newGap[0] < 0:
	#     self.current_hor_pos_ledit.setText("-")
        else:
             self.current_hor_pos_ledit.setText('%d %sm' % (newGap[0] * 1000, unichr(956)))
	if newGap[1] is None:
	     self.current_ver_pos_ledit.setText("-")
        #elif newGap[1] < 0:
	#     self.current_ver_pos_ledit.setText("-")
        else:
             gap_str= str(newGap[1] * 1000)
             self.current_ver_pos_ledit.setText('%d %sm' % (newGap[1] * 1000, unichr(956)))

    def gap_status_changed(self, gapHorStatus, gapVerStatus):
	if gapHorStatus == 'Move':  #Moving
           self.stop_hor_button.setEnabled(True)
           Qt4_widget_colors.set_widget_color(self.hor_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LIGHT_YELLOW,
                                              QtGui.QPalette.Base)
        else:
           self.stop_hor_button.setEnabled(False)
           Qt4_widget_colors.set_widget_color(self.hor_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LIGHT_GREEN,
                                              QtGui.QPalette.Base)

	if gapVerStatus == 'Move':  #Moving
           self.stop_ver_button.setEnabled(True)
           Qt4_widget_colors.set_widget_color(self.ver_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LIGHT_YELLOW,
                                              QtGui.QPalette.Base)
        else:
           self.stop_ver_button.setEnabled(False)
           Qt4_widget_colors.set_widget_color(self.ver_pos_dspinbox.lineEdit(),
                                              Qt4_widget_colors.LIGHT_GREEN,
                                              QtGui.QPalette.Base)

    def focus_mode_changed(self, horFocMode, verFocMode):
	self.hor_pos_dspinbox.setEnabled(horFocMode)
	self.set_hor_gap_button.setEnabled(horFocMode)
        self.ver_pos_dspinbox.setEnabled(verFocMode)
        self.set_ver_gap_button.setEnabled(verFocMode)

    def gap_limits_changed(self, newMaxLimits):
	if newMaxLimits is not None:
	   if newMaxLimits[0] > 0:
	      self.hor_pos_dspinbox.setMaxValue(int(newMaxLimits[0] * 1000)) 
           if newMaxLimits[1] > 0:
              self.ver_pos_dspinbox.setMaxValue(int(newMaxLimits[1] * 1000))
