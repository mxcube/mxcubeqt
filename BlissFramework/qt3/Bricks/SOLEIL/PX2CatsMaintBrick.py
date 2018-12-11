import string
import logging
import time
import qt
import traceback
import sys

from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework import BaseComponents 
from widgets.catsmaintwidget import CatsMaintWidget


__category__ = 'SOLEIL'

    
class CatsMaintBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)
        
        self.addProperty("hwobj", "string", "")
        
        self.widget = CatsMaintWidget(self)
        qt.QHBoxLayout(self)
        self.layout().addWidget(self.widget)
        
        qt.QObject.connect(self.widget.btPowerOn, qt.SIGNAL('clicked()'), self._powerOn)        
        qt.QObject.connect(self.widget.btPowerOff, qt.SIGNAL('clicked()'), self._powerOff)       
        qt.QObject.connect(self.widget.btLid1Open, qt.SIGNAL('clicked()'), self._lid1Open)
        qt.QObject.connect(self.widget.btLid1Close, qt.SIGNAL('clicked()'), self._lid1Close)
        qt.QObject.connect(self.widget.btLid2Open, qt.SIGNAL('clicked()'), self._lid2Open)
        qt.QObject.connect(self.widget.btLid2Close, qt.SIGNAL('clicked()'), self._lid2Close)
        qt.QObject.connect(self.widget.btLid3Open, qt.SIGNAL('clicked()'), self._lid3Open)
        qt.QObject.connect(self.widget.btLid3Close, qt.SIGNAL('clicked()'), self._lid3Close)
        qt.QObject.connect(self.widget.btResetError, qt.SIGNAL('clicked()'), self._resetError)
        qt.QObject.connect(self.widget.btBack, qt.SIGNAL('clicked()'), self._backTraj)                     
        qt.QObject.connect(self.widget.btSafe, qt.SIGNAL('clicked()'), self._safeTraj)                     
        qt.QObject.connect(self.widget.btRegulationOn, qt.SIGNAL('clicked()'), self._regulationOn)                     
                
        self.device=None
        self._pathRunning = None
        self._poweredOn = None
        self._regulationOn = None

        self._lid1State = False
        self._lid2State = False
        self._lid3State = False

        self._updateButtons()

    def propertyChanged(self, property, oldValue, newValue):
        logging.getLogger("user_level_log").info("CatsMaint property Changed: " + str(property) + " = " + str(newValue))
        if property == 'hwobj':
            if self.device is not None:
                self.disconnect(self.device, PYSIGNAL('lid1StateChanged'), self._updateLid1State)
                self.disconnect(self.device, PYSIGNAL('lid2StateChanged'), self._updateLid2State)
                self.disconnect(self.device, PYSIGNAL('lid3StateChanged'), self._updateLid3State)
                self.disconnect(self.device, PYSIGNAL('runningStateChanged'), self._updatePathRunningFlag)
                self.disconnect(self.device, PYSIGNAL('powerStateChanged'), self._updatePowerState)
                self.disconnect(self.device, PYSIGNAL('messageChanged'), self._updateMessage)
                self.disconnect(self.device, PYSIGNAL('regulationStateChanged'), self._updateRegulationState)
            # load the new hardware object

            self.device = self.getHardwareObject(newValue)                                    
            logging.info('CatsMaintBrick self.device %s newvalue %s' % (self.device, newValue))
            if self.device is not None:
                self.connect(self.device, PYSIGNAL('regulationStateChanged'), self._updateRegulationState)
                self.connect(self.device, PYSIGNAL('messageChanged'), self._updateMessage)
                self.connect(self.device, PYSIGNAL('powerStateChanged'), self._updatePowerState)
                self.connect(self.device, PYSIGNAL('runningStateChanged'), self._updatePathRunningFlag)
                self.connect(self.device, PYSIGNAL('lid1StateChanged'), self._updateLid1State)
                self.connect(self.device, PYSIGNAL('lid2StateChanged'), self._updateLid2State)
                self.connect(self.device, PYSIGNAL('lid3StateChanged'), self._updateLid3State)
            self._updateButtons()

    def _updateRegulationState(self, value):
        logging.info('CatsMaintBrick: _updateRegulationState %s' % value)
        self._regulationOn = value
        if value:
            self.widget.lblRegulationState.setPaletteBackgroundColor(QWidget.green)
        else:
            self.widget.lblRegulationState.setPaletteBackgroundColor(QWidget.red)
        self._updateButtons()

    def _updatePowerState(self, value):
        logging.info('CatsMaintBrick: _updatePowerState %s' % value)
        self._poweredOn = value
        if value:
            self.widget.lblPowerState.setPaletteBackgroundColor(QWidget.green)
        else:
            self.widget.lblPowerState.setPaletteBackgroundColor(QWidget.red)
        self._updateButtons()

    def _updateMessage(self, value):
        logging.info('CatsMaintBrick: _updateMessage %s' % value)
        self.widget.lblMessage.setText(str(value))

    def _updatePathRunningFlag(self, value):
        logging.info('CatsMaintBrick: _updatePathRunningFlag %s' % value)
        self._pathRunning = value
        self._updateButtons()

    def _updateLid1State(self, value):
        logging.info('CatsMaintBrick: _updateLid1State %s' % value)
        self._lid1State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid1Open.setEnabled(not value)
            self.widget.btLid1Close.setEnabled(value)
        else:
            self.widget.btLid1Open.setEnabled(False)
            self.widget.btLid1Close.setEnabled(False)

    def _updateLid2State(self, value):
        logging.info('CatsMaintBrick: _updateLid2State %s' % value)
        self._lid2State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid2Open.setEnabled(not value)
            self.widget.btLid2Close.setEnabled(value)
        else:
            self.widget.btLid2Open.setEnabled(False)
            self.widget.btLid2Close.setEnabled(False)

    def _updateLid3State(self, value):
        logging.info('CatsMaintBrick: _updateLid3State %s' % value)
        self._lid3State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid3Open.setEnabled(not value)
            self.widget.btLid3Close.setEnabled(value)
        else:
            self.widget.btLid3Open.setEnabled(False)
            self.widget.btLid3Close.setEnabled(False)

    def _updateButtons(self):
        if self.device is None:
            # disable all buttons
            logging.info('CatsMaintBrick, disabling all the buttons because self.device is None')
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
            self.widget.btRegulationOn.setEnabled(False)
            self.widget.lblMessage.setText('')
        else:
            logging.info('CatsMaintBrick, going to enable some of the buttons as appropriate')
            logging.info('self.device is %s' % self.device)
            ready = not self._pathRunning
            logging.info('ready? %s' % ready)
            #ready = not self.device.isDeviceReady()
            logging.info('powered on? %s' % self._poweredOn)
            logging.info('type(self._poweredOn) %s' % type(self._poweredOn))
            if self._poweredOn is not None:
              logging.info('self._poweredOn is %s' % self._poweredOn)
              self.widget.btPowerOn.setEnabled(ready and not self._poweredOn)
              self.widget.btPowerOff.setEnabled(ready and self._poweredOn)
              self.widget.btResetError.setEnabled(ready)
              self.widget.btBack.setEnabled(ready and self._poweredOn)
              self.widget.btSafe.setEnabled(ready and self._poweredOn)
            
            else:
              logging.info('self._poweredOn is %s' % self._poweredOn)
              self.widget.btPowerOn.setEnabled(ready) # and not self._poweredOn)
              self.widget.btPowerOff.setEnabled(ready) # and self._poweredOn)
              self.widget.btResetError.setEnabled(ready)
              self.widget.btBack.setEnabled(ready) # and self._poweredOn)
              self.widget.btSafe.setEnabled(ready) #and self._poweredOn)

            self.widget.btRegulationOn.setEnabled(not self._regulationOn)

            self._updateLid1State(self._lid1State)
            self._updateLid2State(self._lid2State)
            self._updateLid3State(self._lid3State)

    def _regulationOn(self):
        logging.getLogger("user_level_log").info("CATS: Regulation On")
        try:
            if self.device is not None:
                self.device._doEnableRegulation()
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOn(self):
        logging.getLogger("user_level_log").info("CATS: Power On")
        try:
            if self.device is not None:
                self.device._doPowerState(True)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOff(self):
        logging.getLogger("user_level_log").info("CATS: Power Off")
        try:
            if self.device is not None:
                self.device._doPowerState(False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 1")
        try:
            if self.device is not None:
                self.device._doLid1State(True)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 1")
        try:
            if self.device is not None:
                self.device._doLid1State(False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid2Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 2")
        try:
            if self.device is not None:
                self.device._doLid2State(True)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid2Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 2")
        try:
            if self.device is not None:
                self.device._doLid2State(False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 3")
        try:
            if self.device is not None:
                self.device._doLid3State(True)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 3")
        try:
            if self.device is not None:
                self.device._doLid3State(False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _resetError(self):
        logging.getLogger("user_level_log").info("CATS: Reset")
        try:
            if self.device is not None:
                self.device._doReset()
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _backTraj(self):
        logging.getLogger("user_level_log").info("CATS: Transfer sample back to dewar.")
        try:
            if self.device is not None:
                #self.device._doBack()
                self.device.backTraj()
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _safeTraj(self):
        logging.getLogger("user_level_log").info("CATS: Safely move robot arm to home position.")
        try:
            if self.device is not None:
                #self.device._doSafe()
                self.device.safeTraj()
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

