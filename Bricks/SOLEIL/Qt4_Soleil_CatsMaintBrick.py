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

import os
import sys
import logging

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'SOLEIL'
__author__ = 'Laurent GADEA'
__version__ = '1.0'

class Qt4_Soleil_CatsMaintBrick(BlissWidget):
    """
    Descript. :
    """
    
    def __init__(self, *args):
        """
        Descript. :
        """
        logging.info("###############################     INIT Qt4_SoleilCatsMaintBrick     #####################")
        BlissWidget.__init__(self, *args)
        
        pathfile = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "."))
        self.widget = loadUi(os.path.join(os.path.dirname(__file__), \
                                 "widgets/ui_files/Qt4_soleil_catsmaint_widget.ui"))
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.widget)
        
        # Hardware objects ----------------------------------------------------
        self._hwobj = None
        self._regulationOn = None
        # Internal values -----------------------------------------------------
        self._pathRunning = None
        self._poweredOn = None
        self._lid1State = False
        self._lid2State = False
        self._lid3State = False
        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')
        # Signals -------------------------------------------------------------
    
        # Slots ---------------------------------------------------------------
    
        # Connect -------------------------------------------------------------
        self.widget.btPowerOn.clicked.connect(self._powerOn)
        self.widget.btPowerOff.clicked.connect(self._powerOff)
        
        self.widget.btLid1Open.clicked.connect(self._lid1Open)
        self.widget.btLid1Close.clicked.connect(self._lid1Close)
        self.widget.btLid2Open.clicked.connect(self._lid2Open)
        self.widget.btLid2Close.clicked.connect(self._lid2Close)
        self.widget.btLid3Open.clicked.connect(self._lid3Open)
        self.widget.btLid3Close.clicked.connect(self._lid3Close)
        self.widget.btResetError.clicked.connect(self._resetError)
        self.widget.btBack.clicked.connect(self._backTraj)                     
        self.widget.btSafe.clicked.connect(self._safeTraj)
        # MS 2014-11-18
        self.widget.btHome.clicked.connect(self._homeTraj)
        #self.widget.btDry.clicked.connect(self._drySoakTraj)
        self.widget.btDry.clicked.connect(self._dryTraj)
        self.widget.btDrySoak.clicked.connect(self._drySoakTraj)
        self.widget.btSoak.clicked.connect(self._soakTraj)
        self.widget.btMemoryClear.clicked.connect(self._clearMemory)
        #self.connect(self.widget.btMemoryClear, qt.SIGNAL('clicked()'), self._clearMemory)
        #self.widget.btMemoryClear.clicked.connect(self._ackSampleMemory)
        self.widget.btMissingSample.clicked.connect(self._ackSampleMemory)
        self.widget.btToolOpen.clicked.connect(self._openTool)
        self.widget.btToolCal.clicked.connect(self._toolcalTraj)
        ###
        self.widget.btRegulationOn.clicked.connect(self._regulation)
        
        self._updateButtons()
        logging.info("###############################     INIT Qt4_SoleilCatsMaintBrick  DONE   #####################")
        
    def setValue(self):
        pass
    

    def propertyChanged(self,propertyname,oldValue,newValue):
        #logging.getLogger("user_level_log").info("QT4_CatsMaint property Changed: " + str(property) + " = " + str(newValue))
        if propertyname == "mnemonic":
            if self._hwobj is not None:
                self.disconnect(self._hwobj, 'powerStateChanged', self._updatePowerState)
                self.disconnect(self._hwobj, 'lid1StateChanged', self._updateLid1State)
                self.disconnect(self._hwobj, 'lid2StateChanged', self._updateLid2State)
                self.disconnect(self._hwobj, 'lid3StateChanged', self._updateLid3State)
                self.disconnect(self._hwobj, 'runningStateChanged', self._updatePathRunningFlag)
                self.disconnect(self._hwobj, 'messageChanged', self._updateMessage)
                self.disconnect(self._hwobj, 'sampleIsDetected', self._updateSampleIsDetected)
                self.disconnect(self._hwobj, 'regulationStateChanged', self._updateRegulationState)
                
            self._hwobj = self.getHardwareObject(newValue)
            logging.info("###############################     INIT Qt4_SoleilCatsMaintBrick  self._hwobj is %s   #####################" % str(self._hwobj))
            if self._hwobj is not None:
               self.connect(self._hwobj, 'powerStateChanged', self._updatePowerState)
               self.connect(self._hwobj, 'lid1StateChanged', self._updateLid1State)
               self.connect(self._hwobj, 'lid2StateChanged', self._updateLid2State)
               self.connect(self._hwobj, 'lid3StateChanged', self._updateLid3State)
               self.connect(self._hwobj, 'runningStateChanged', self._updatePathRunningFlag)
               self.connect(self._hwobj, 'messageChanged', self._updateMessage)
               self.connect(self._hwobj, 'sampleIsDetected', self._updateSampleIsDetected)
               self.connect(self._hwobj, 'regulationStateChanged', self._updateRegulationState)
               #for development
               self._updatePowerState(self._hwobj._chnPowered.getValue())
               self._updateRegulationState(True)
            self._updateButtons()
            
        else:
            BlissWidget.propertyChanged(self,propertyname,oldValue,newValue)
    
    def _updatePowerState(self, value):
        self._poweredOn = value
        if value:
            Qt4_widget_colors.set_widget_color(self.widget.lblPowerState,
                                           Qt4_widget_colors.LIGHT_GREEN,
                                           QPalette.Background)
        else:
            Qt4_widget_colors.set_widget_color(self.widget.lblPowerState,
                                           Qt4_widget_colors.RED,
                                           QPalette.Background)
        self._updateButtons()
        
    def _updateRegulationState(self, value):
        logging.info('CatsMaintBrick: _updateRegulationState %s' % value)
        self._regulationOn = value
        if value:
            Qt4_widget_colors.set_widget_color(self.widget.lblRegulationState,
                                           Qt4_widget_colors.GREEN,
                                           QPalette.Background)
        else:
            Qt4_widget_colors.set_widget_color(self.widget.lblRegulationState,
                                           Qt4_widget_colors.RED,
                                           QPalette.Background)
        self._updateButtons()
        
    def _updateLid1State(self, value):
        logging.info('CatsMaintBrick: _updateLid1State %s' % value)
        self._lid1State = value

        if self._hwobj is not None and not self._pathRunning and self._poweredOn is not None:
            self.widget.btLid1Open.setEnabled(not value and self._poweredOn)
            self.widget.btLid1Close.setEnabled(value and self._poweredOn)
        else:
            self.widget.btLid1Open.setEnabled(False)
            self.widget.btLid1Close.setEnabled(False)
    
    def _updateLid2State(self, value):
        logging.info('CatsMaintBrick: _updateLid2State %s' % value)
        self._lid2State = value
        if self._hwobj is not None and not self._pathRunning:
            self.widget.btLid2Open.setEnabled(not value and self._poweredOn )
            self.widget.btLid2Close.setEnabled(value and self._poweredOn)
        else:
            self.widget.btLid2Open.setEnabled(False)
            self.widget.btLid2Close.setEnabled(False)
    
    def _updateLid3State(self, value):
        logging.info('CatsMaintBrick: _updateLid3State %s' % value)
        self._lid3State = value
        if self._hwobj is not None and not self._pathRunning:
            self.widget.btLid3Open.setEnabled(not value and self._poweredOn)
            self.widget.btLid3Close.setEnabled(value and self._poweredOn)
        else:
            self.widget.btLid3Open.setEnabled(False)
            self.widget.btLid3Close.setEnabled(False)
    
    def _updatePathRunningFlag(self, value):
        logging.info('CatsMaintBrick: _updatePathRunningFlag %s' % value)
        self._pathRunning = value
        self._updateButtons()
        
    def _updateSampleIsDetected(self, value):
        logging.info('CatsMaintBrick: _updateSampleIsDetected is %s' % value)
        pass
#==============================================================================
#         self.widget.btLid1Open.setEnabled(not value)
#         self.widget.btLid1Close.setEnabled(not value)
#         self.widget.btLid2Open.setEnabled(not value)
#         self.widget.btLid2Close.setEnabled(not value)
#         self.widget.btLid3Open.setEnabled(not value)
#         self.widget.btLid3Close.setEnabled(not value)
#==============================================================================
        
    def _updateMessage(self, value):
        logging.info('Qt4_SOLEIL_CatsMaintBrick: _updateMessage %s' % value)
        self.widget.lblMessage.setText(str(value))
    
    def _updateButtons(self):
        if self._hwobj is None:
            # disable all buttons
            logging.info('Qt4_Soleil_catsMaintBrick, disabling all the buttons because self._hwobj is None')
            self.widget.btPowerOn.setEnabled(False)
            self.widget.btPowerOff.setEnabled(False)
            self.widget.btLid1Open.setEnabled(False)
            self.widget.btLid1Close.setEnabled(False)
            self.widget.btLid2Open.setEnabled(False)
            self.widget.btLid2Close.setEnabled(False)
            self.widget.btLid3Open.setEnabled(False)
            self.widget.btLid3Close.setEnabled(False)
            self.widget.btResetError.setEnabled(False)
            self.widget.btBack.setEnabled(False)
            self.widget.btSafe.setEnabled(False)
            self.widget.btHome.setEnabled(False)
            self.widget.btDry.setEnabled(False)
            self.widget.btDrySoak.setEnabled(False)
            self.widget.btSoak.setEnabled(False)
            self.widget.btMemoryClear.setEnabled(False)
            self.widget.btMissingSample.setEnabled(False)
            self.widget.btToolOpen.setEnabled(False)
            self.widget.btToolCal.setEnabled(False)
            
            self.widget.btRegulationOn.setEnabled(False)
            self.widget.lblMessage.setText('')
        else:
            ready = not self._pathRunning
            logging.info('ready? %s' % ready)
            #ready = not self._hwobj._isDeviceReady()
            if self._poweredOn is not None:
              self.widget.btPowerOn.setEnabled(ready and not self._poweredOn)
              self.widget.btPowerOff.setEnabled(ready and self._poweredOn)
              self.widget.btResetError.setEnabled(ready and self._poweredOn)
              self.widget.btBack.setEnabled(ready and self._poweredOn)
              self.widget.btSafe.setEnabled(ready and self._poweredOn)
              self.widget.btHome.setEnabled(ready and self._poweredOn)
              self.widget.btDry.setEnabled(ready and self._poweredOn)
              self.widget.btDrySoak.setEnabled(ready and self._poweredOn)
              self.widget.btSoak.setEnabled(ready and self._poweredOn)
              self.widget.btMemoryClear.setEnabled(ready and self._poweredOn)
              self.widget.btMissingSample.setEnabled(ready and self._poweredOn)
              self.widget.btToolOpen.setEnabled(ready and self._poweredOn)
              self.widget.btToolCal.setEnabled(ready and self._poweredOn)
            else:
              self.widget.btPowerOn.setEnabled(ready) # and not self._poweredOn)
              self.widget.btPowerOff.setEnabled(ready) # and self._poweredOn)
              self.widget.btResetError.setEnabled(ready)
              self.widget.btBack.setEnabled(ready) # and self._poweredOn)
              self.widget.btSafe.setEnabled(ready) #and self._poweredOn)

            self.widget.btRegulationOn.setEnabled(not self._regulationOn)

            self._updateLid1State(self._lid1State)
            self._updateLid2State(self._lid2State)
            self._updateLid3State(self._lid3State)

    #connect to Hwobj

    def _regulation(self):
        logging.getLogger("user_level_log").info("CATS: Regulation On")
        try:
            if self._hwobj is not None:
                self._hwobj._doEnableRegulation()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOn(self):
        logging.getLogger("user_level_log").info("CATS: Power On")
        try:
            if self._hwobj is not None:
                logging.info(">>>>>>>>>>>>>>>>>........................_powerOn hwobj is not NONE ")
                self._hwobj._doPowerState(True)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOff(self):
        logging.getLogger("user_level_log").info("CATS: Power Off")
        try:
            if self._hwobj is not None:
                self._hwobj._doPowerState(False)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 1")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid1State(True)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 1")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid1State(False)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid2Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 2")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid2State(True)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    def _lid2Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 2")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid2State(False)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 3")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid3State(True)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 3")
        try:
            if self._hwobj is not None:
                self._hwobj._doLid3State(False)
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _resetError(self):
        logging.getLogger("user_level_log").info("CATS: Reset")
        try:
            if self._hwobj is not None:
                self._hwobj._doReset()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _backTraj(self):
        logging.getLogger("user_level_log").info("CATS: Transfer sample back to dewar.")
        try:
            if self._hwobj is not None:
                #self._hwobj._doBack()
                self._hwobj.backTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    def recover(self):
        import os
        return os.system('gnome-terminal --title "recover cats"  --geometry 80x24+1980+0 --execute /bin/bash -c "dry_tremp_toolcal_calibrate.py; bash" &')
    
    def _safeTraj(self):
        logging.getLogger("user_level_log").info("CATS: Safely move robot arm to home position.")
        try:
            if self._hwobj is not None:
                #self.device._doSafe()
                #self.device.safeTraj()
                self.recover()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    #old
    def _safeTraj_old(self):
        logging.getLogger("user_level_log").info("CATS: Safely move robot arm to home position.")
        try:
            if self._hwobj is not None:
                #self._hwobj._doSafe()
                self._hwobj.safeTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
    
    # MS 2014-11-18
    def _homeTraj(self):
        logging.getLogger("user_level_log").info("CATS: Move robot arm to home position.")
        try:
            if self._hwobj is not None:
                self._hwobj.homeTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    def _dryTraj(self):
        logging.getLogger("user_level_log").info("CATS: Dry the gripper.")
        try:
            if self._hwobj is not None:
                self._hwobj.dryTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
    
    def _drySoakTraj(self):
        logging.getLogger("user_level_log").info("CATS: Dry and soak the gripper.")
        try:
            if self._hwobj is not None:
                self._hwobj.drySoakTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
        
    def _soakTraj(self):
        logging.getLogger("user_level_log").info("CATS: Soak the gripper.")
        try:
            if self._hwobj is not None:
                self._hwobj.soakTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    def _clearMemory(self):
        logging.getLogger("user_level_log").info("CATS: clear the memory.")
        try:
            if self._hwobj is not None:
                self._hwobj.clearMemory()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
   
    def _ackSampleMemory(self):
        logging.getLogger("user_level_log").info("CATS: acknowlege missing sample.")
        try:
            if self._hwobj is not None:
                self._hwobj.ackSampleMemory()
                self._hwobj.clearMemory()
                self._hwobj._doReset()
                #self._hwobj.ackSampleMemory()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
         
    def _openTool(self):
        logging.getLogger("user_level_log").info("CATS: Open the tool.")
        try:
            if self._hwobj is not None:
                self._hwobj.openTool()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
            
    def _toolcalTraj(self):
        logging.getLogger("user_level_log").info("CATS: Calibrate the tool.")
        try:
            if self._hwobj is not None:
                self._hwobj.toolcalTraj()
        except:
            QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
