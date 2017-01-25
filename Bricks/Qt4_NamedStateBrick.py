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

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

import logging

__category__ = 'SOLEIL'
__author__ = 'Laurent GADEA'
__version__ = '1.0'

# version Qt4 of () implemented by Bixente Rey Bakaikoa at SOLEIL

UNKNOWN_STYLE = """
QComboBox::drop-down:!editable {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                      stop: 0 #e1e1e1, stop: 0.4 #dddddd,
                      stop: 0.5 #d8d8d8, stop: 1.0 #d3d3d3);
}
"""

MOVING_STYLE = """
QComboBox::drop-down:!editable {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                      stop: 0 #f1f181, stop: 0.4 #fdfd7d,
                      stop: 0.5 #f8f878, stop: 1.0 #f3f373);
}
"""

STANDBY_STYLE = """
QComboBox::drop-down:!editable {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                      stop: 0 #c1f1c1, stop: 0.4 #cdfdcd,
                      stop: 0.5 #c8f8c8, stop: 1.0 #c3f3c3);
}
"""

class Qt4_NamedStateBrick(BlissWidget):
    """
    Descript. :
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self._hwobj = None
        self.hdwstate = "READY"

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Graphic elements ----------------------------------------------------
        self.lblUsername = QtGui.QLabel('')
        self.lstStates = QtGui.QComboBox()
        self.lstStates.activated.connect(self.change_state)
        self.lstStates.setToolTip("Trigger a change to new state")

        # Layout --------------------------------------------------------------
        main_vlayout = QtGui.QVBoxLayout(self)
        main_vlayout.addWidget(self.lblUsername)
        main_vlayout.addWidget(self.lstStates)
        main_vlayout.setContentsMargins(2, 2, 2, 2)
    
    # version Qt4
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == "mnemonic":
            if self._hwobj is not None:
                self.disconnect(self._hwobj, 'stateChanged', self.stateChanged)
                self.disconnect(self._hwobj, 'hardwareStateChanged', self.hdwStateChanged)
                self.disconnect(self._hwobj, 'newStateList', self.init_state_list)
                
            self._hwobj = self.getHardwareObject(new_value)
            
            if self._hwobj is not None:
                username = self._hwobj.getUserName()
                if username.strip() != "":
                    username += " :" 
                self.lblUsername.setText("<b>"+username+'</b>')
                
                self.init_state_list() 
                
                self.connect(self._hwobj, 'stateChanged', self.stateChanged)
                self.connect(self._hwobj, 'hardwareStateChanged', self.hdwStateChanged)
                self.connect(self._hwobj, 'newStateList', self.init_state_list)
                self._hwobj.update_values()
                
            if self._hwobj is None:
                self.setStyleSheet(UNKNOWN_STYLE)
            else:
                self.setStyleSheet(STANDBY_STYLE)
        else:
            self.lblUsername.setText('')
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)
            
    def init_state_list(self):
        """
        Descript. :
        """
        self.lstStates.clear()
        state_list = self._hwobj.getStateList()
        if len(state_list) > 0:
           for state in state_list:
               self.lstStates.addItem(state)           
           self.setEnabled(True)
        else:
           self.setEnabled(False)
    
    def change_state(self):
        """
        Descript. :
        """
        if self._hwobj.isReady():
            new_state = str(self.lstStates.currentText())
            self._hwobj.setState(new_state)
    
    def stateChanged(self, state):
        """
        Descript. :
        """
        if (state.lower() != "unknown" and
            self.lstStates.count() > 0):
            self.lstStates.setCurrentIndex(self.lstStates.findText(state))
            self.lstStates.setEnabled(True)
        else:
            self.lstStates.setEnabled(False) 

    def fillStates(self, states = None): 
        self.cleanStates()

        if self.hwo is not None:
            if states is None:
                states = self.hwo.getStateList()

        if states is None:
            states=[]

        for state_name in states:
            self.lstStates.insertItem(str(state_name))

        self.states=states

        if self.hwo is not None:
            if self.hwo.isReady():
                self.stateChanged(self.hwo.getCurrentState())
          
        self.lstStates.show()
        
    def hdwStateChanged(self, hdwstate):
        self.hdwstate = str(hdwstate)

        logging.debug(" NamedStateBrick: hdw state changed it is %s" % hdwstate)

        if self.hdwstate in ['RUNNING','MOVING']:
            self.lstStates.setStyleSheet(MOVING_STYLE)
        elif self.hdwstate in  ['STANDBY','READY']:
            self.lstStates.setStyleSheet(STANDBY_STYLE)
        else:
            self.lstStates.setStyleSheet(UNKNOWN_STYLE)

    def cleanStates(self):
        self.lstStates.clear()
        self.lstStates.insertItem('')
