import string
import logging
import time
import traceback
import sys
import os

from PyQt4 import QtGui
from PyQt4 import uic

from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors

__category__ = 'Sample Changer'

class Qt4_CatsMaintBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty("mnemonic", "string", "")
        self.defineSlot('setExpertMode',())

        self.expert_mode = False
      
        self.widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'widgets/ui_files/Qt4_catsmaint_widget.ui'))

        QtGui.QHBoxLayout(self)
        self.layout().addWidget(self.widget)
        
        self.widget.btPowerOn.clicked.connect(self._powerOn)        
        self.widget.btPowerOff.clicked.connect(self._powerOff)       
        self.widget.btLid1Open.clicked.connect(self._lid1Open)
        self.widget.btLid1Close.clicked.connect(self._lid1Close)
        self.widget.btLid2Open.clicked.connect(self._lid2Open)
        self.widget.btLid2Close.clicked.connect(self._lid2Close)
        self.widget.btLid3Open.clicked.connect(self._lid3Open)
        self.widget.btLid3Close.clicked.connect(self._lid3Close)
        self.widget.btRegulationOn.clicked.connect(self._regulationSetOn)                     
        self.widget.btRegulationOff.clicked.connect(self._regulationSetOff)                     

        self.widget.btOpenTool.clicked.connect(self._toolOpen)                     
        self.widget.btCloseTool.clicked.connect(self._toolClose)                     
        self.widget.btToolCalib.clicked.connect(self._toolCalibrate)                     
        self.widget.btMagnetOn.clicked.connect(self._magnetOn)                     
        self.widget.btMagnetOff.clicked.connect(self._magnetOff)                     
                
        # self.widget.btSoak.clicked.connect(self._soak)                     
        self.widget.btBack.clicked.connect(self._backTraj)                     
        self.widget.btSafe.clicked.connect(self._safeTraj)                     
        self.widget.btDry.clicked.connect(self._dry)                     
        self.widget.btHome.clicked.connect(self._home)                     

        #self.widget.btRestart.clicked.connect(self._restart)                     
        self.widget.btResetPutGet.clicked.connect(self._resetPutGet)                     
        self.widget.btResetMotion.clicked.connect(self._resetMotion)                     
        self.widget.btMemClear.clicked.connect(self._clearMemory)                     
        self.widget.btClear.clicked.connect(self._clearMemory)                     
        self.widget.btMore.clicked.connect(self._commandPrompt)

        self.widget.btAbort.clicked.connect(self._abort)                     
        # self.widget.btPanic.clicked.connect(self._panic)                     

        self.device=None
        self._pathRunning = None
        self._poweredOn = None
        self._regulationOn = None

        self._lid1State = False
        self._lid2State = False
        self._lid3State = False

        self._toolState = False

        self.widget.lblMessage.setStyleSheet("background-color: white;")

        self._updateButtons()

    def propertyChanged(self, property, oldValue, newValue):
        logging.getLogger("user_level_log").info("Property Changed: " + str(property) + " = " + str(newValue))
        if property == 'mnemonic':
            if self.device is not None:
                self.disconnect(self.device, 'lid1StateChanged', self._updateLid1State)
                self.disconnect(self.device, 'lid2StateChanged', self._updateLid2State)
                self.disconnect(self.device, 'lid3StateChanged', self._updateLid3State)
                self.disconnect(self.device, 'runningStateChanged', self._updatePathRunningFlag)
                self.disconnect(self.device, 'powerStateChanged', self._updatePowerState)
                self.disconnect(self.device, 'messageChanged', self._updateMessage)
                self.disconnect(self.device, 'regulationStateChanged', self._updateRegulationState)
                self.disconnect(self.device, 'toolStateChanged', self._updateToolState)
            # load the new hardware object
            self.device = self.getHardwareObject(newValue)                                    
            if self.device is not None:
                self.connect(self.device, 'regulationStateChanged', self._updateRegulationState)
                self.connect(self.device, 'messageChanged', self._updateMessage)
                self.connect(self.device, 'powerStateChanged', self._updatePowerState)
                self.connect(self.device, 'runningStateChanged', self._updatePathRunningFlag)
                self.connect(self.device, 'lid1StateChanged', self._updateLid1State)
                self.connect(self.device, 'lid2StateChanged', self._updateLid2State)
                self.connect(self.device, 'lid3StateChanged', self._updateLid3State)
                self.connect(self.device, 'toolStateChanged', self._updateToolState)

    def setExpertMode(self, mode):
        if mode:
             self.expert_mode = True
        else:
             self.expert_mode = False

        self._updateButtons()

    def _updateRegulationState(self, value):
        self._regulationOn = value
        if value:
            light_green = str(Qt4_widget_colors.LIGHT_GREEN.name())
            self.widget.lblRegulationState.setStyleSheet("background-color: %s;" % light_green)
        else:
            light_red = str(Qt4_widget_colors.LIGHT_RED.name())
            self.widget.lblRegulationState.setStyleSheet("background-color: %s;" % light_red)
        self._updateButtons()

    def _updatePowerState(self, value):
        self._poweredOn = value
        if value:
            light_green = str(Qt4_widget_colors.LIGHT_GREEN.name())
            self.widget.lblPowerState.setStyleSheet("background-color: %s;" % light_green)
        else:
            light_red = str(Qt4_widget_colors.LIGHT_RED.name())
            self.widget.lblPowerState.setStyleSheet("background-color: %s;" % light_red)
        self._updateButtons()

    def _updateMessage(self, value):
        self.widget.lblMessage.setText(str(value))

    def _updatePathRunningFlag(self, value):
        self._pathRunning = value
        self._updateButtons()

    def _updateLid1State(self, value):
        self._lid1State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid1Open.setEnabled(not value)
            self.widget.btLid1Close.setEnabled(value)
        else:
            self.widget.btLid1Open.setEnabled(False)
            self.widget.btLid1Close.setEnabled(False)

    def _updateLid2State(self, value):
        self._lid2State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid2Open.setEnabled(not value)
            self.widget.btLid2Close.setEnabled(value)
        else:
            self.widget.btLid2Open.setEnabled(False)
            self.widget.btLid2Close.setEnabled(False)

    def _updateLid3State(self, value):
        self._lid3State = value
        if self.device is not None and not self._pathRunning:
            self.widget.btLid3Open.setEnabled(not value)
            self.widget.btLid3Close.setEnabled(value)
        else:
            self.widget.btLid3Open.setEnabled(False)
            self.widget.btLid3Close.setEnabled(False)

    def _updateToolState(self, value):
        self._toolState = value
        if self.device is not None and not self._pathRunning:
            self.widget.btOpenTool.setEnabled(not value)
            self.widget.btCloseTool.setEnabled(value)
        else:
            self.widget.btOpenTool.setEnabled(False)
            self.widget.btCloseTool.setEnabled(False)

    def _updateButtons(self):

        if self.device is None:
            # disable all buttons
            self.widget.boxPower.setEnabled(False)
            self.widget.boxRegulation.setEnabled(False)
            self.widget.boxLid1.setEnabled(False)
            self.widget.boxLid2.setEnabled(False)
            self.widget.boxLid3.setEnabled(False)
            self.widget.lblMessage.setText('')
            self.widget.btAbort.setEnabled(False)
        else:
            self.widget.boxPower.setEnabled(True)
            self.widget.boxRegulation.setEnabled(True)

            ready = not self._pathRunning
            poweredOn = self._poweredOn and True or False # handles init state None as False

            if not self.expert_mode:
                self.widget.boxTools.hide()
                self.widget.btMore.hide()
                self.widget.btBarcodeRead.hide()
                self.widget.btBack.hide()
                self.widget.btSafe.hide()
                self.widget.btSafe.hide()
                self.widget.btClear.hide()
            else:
                self.widget.boxTools.show()
                self.widget.btMore.show()
                self.widget.btBarcodeRead.show()
                self.widget.btBack.show()
                self.widget.btSafe.show()
                self.widget.btClear.show()
                self.widget.btMemClear.show()

            # Open for users
            self.widget.btPowerOn.setEnabled(ready and not poweredOn)
            self.widget.btPowerOff.setEnabled(ready and poweredOn)

            if ready: 
                color = str(Qt4_widget_colors.LIGHT_GRAY.name())
                self.widget.btAbort.setEnabled(False)
            else:
                color = str(Qt4_widget_colors.LIGHT_RED.name())
                self.widget.btAbort.setEnabled(True)
            self.widget.btAbort.setStyleSheet("background-color: %s;" % color)

            self.widget.boxLid1.setEnabled(True)
            self.widget.boxLid2.setEnabled(True)
            self.widget.boxLid3.setEnabled(True)

            self.widget.btClear.setEnabled(ready)
            self.widget.btBack.setEnabled(ready and poweredOn)
            self.widget.btSafe.setEnabled(ready and poweredOn)

            regulOn = self._regulationOn and True or False
            self.widget.btRegulationOn.setEnabled(ready and not regulOn)
            self.widget.btRegulationOff.setEnabled(ready and regulOn)

            self._updateLid1State(self._lid1State)
            self._updateLid2State(self._lid2State)
            self._updateLid3State(self._lid3State)
            self._updateToolState(self._toolState)

    def _regulationSetOn(self):
        logging.getLogger("user_level_log").info("CATS: Regulation On")
        try:
            if self.device is not None:
                self.device._doEnableRegulation()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _regulationSetOff(self):
        logging.getLogger("user_level_log").info("CATS: Regulation Off")
        try:
            if self.device is not None:
                self.device._doDisableRegulation()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOn(self):
        logging.getLogger("user_level_log").info("CATS: Power On")
        try:
            if self.device is not None:
                self.device._doPowerState(True)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _powerOff(self):
        logging.getLogger("user_level_log").info("CATS: Power Off")
        try:
            if self.device is not None:
                self.device._doPowerState(False)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 1")
        try:
            if self.device is not None:
                self.device._doLid1State(True)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid1Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 1")
        try:
            if self.device is not None:
                self.device._doLid1State(False)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid2Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 2")
        try:
            if self.device is not None:
                self.device._doLid2State(True)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid2Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 2")
        try:
            if self.device is not None:
                self.device._doLid2State(False)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Open(self):
        logging.getLogger("user_level_log").info("CATS: Open Lid 3")
        try:
            if self.device is not None:
                self.device._doLid3State(True)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _lid3Close(self):
        logging.getLogger("user_level_log").info("CATS: Close  Lid 3")
        try:
            if self.device is not None:
                self.device._doLid3State(False)
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _toolOpen(self):
        try:
            if self.device is not None:
                self.device._doToolOpen()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _toolClose(self):
        try:
            if self.device is not None:
                self.device._doToolClose()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _toolCalibrate(self):
        try:
            if self.device is not None:
                self.device._doCalibration()   # adds a parameter 2 (for tool) in device
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _magnetOn(self):
        try:
            if self.device is not None:
                self.device._doMagnetOn()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _magnetOff(self):
        try:
            if self.device is not None:
                self.device._doMagnetOff()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _home(self):
        try:
            if self.device is not None:
                self.device._doHome()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _resetError(self):
        logging.getLogger("user_level_log").info("CATS: Reset")
        try:
            if self.device is not None:
                self.device._doReset()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _home(self):
        try:
            if self.device is not None:
                self.device._doHome()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _dry(self):
        try:
            if self.device is not None:
                self.device._doDryGripper()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _soak(self):
        try:
            if self.device is not None:
                self.device._doSoak()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _backTraj(self):
        logging.getLogger("user_level_log").info("CATS: Transfer sample back to dewar.")
        try:
            if self.device is not None:
                #self.device._doBack()
                self.device.backTraj()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _safeTraj(self):
        logging.getLogger("user_level_log").info("CATS: Safely move robot arm to home position.")
        try:
            if self.device is not None:
                #self.device._doSafe()
                self.device.safeTraj()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _abort(self):
        try:
            if self.device is not None:
                self.device._doAbort()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _panic(self):
        try:
            if self.device is not None:
                self.device._doPanic()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _restart(self):
        try:
            if self.device is not None:
                self.device._doRestart()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _resetMotion(self):
        try:
            if self.device is not None:
                self.device._doResetMotion()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _resetPutGet(self):
        try:
            if self.device is not None:
                self.device._doResetPutGet()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _clear(self):
        try:
            if self.device is not None:
                self.device._doClear()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _clearMemory(self):
        try:
            if self.device is not None:
                self.device._doResetMemory()
        except:
            QtGui.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _commandPrompt(self, index):
        self.command_dialog = CatsCommandDialog(self)
        self.command_dialog.set_cats_device(self.device)
        self.command_dialog.show()

class CatsCommandDialog(QtGui.QDialog):

    cmds = ["put(mount)", "get(un-mount)", "getput",
            "get_brcd", "getput_brcd", "barcode", 
            "gotodif", "get HT", "put HT",
            "getput HT", ]

    args = { 
        "put(mount)": ["tool", "from_cassette", "from_puck"], 
        "get(un-mount)": ["tool", ], 
        "getput": ["tool", "from_cassette", "from_puck"],
        "get_brcd": ["tool", ],
        "getput_brcd": ["tool", "from_cassette", "from_puck"],
        "barcode": [], 
        "gotodif": [], 
        "get HT": [], 
        "put HT": [],
        "getput HT": [], }

    def __init__(self, *args):


        QtGui.QDialog.__init__(self,*args)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)
        self.widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'widgets/ui_files/Qt4_catscommand_dialog.ui'))

        layout.addWidget(self.widget)

        self.btSend = self.widget.buttonBox.addButton("Send", QtGui.QDialogButtonBox.ApplyRole)
        self.btSend.clicked.connect(self.send_command)

        self.widget.cbCommand.clear()
        self.widget.cbCommand.insertItems(0, self.cmds)
        self.widget.cbCommand.activated.connect(self.command_selected)
        self.widget.buttonBox.rejected.connect(self.rejected)

    def show(self):
        self.widget.cbCommand.setCurrentIndex(2)
        QtGui.QDialog.show(self)

    def set_cats_device(self,device):
        self.device = device 

    def command_selected(self, cb_idx):
        logging.getLogger("GUI").info("command selected %s" % cb_idx)
         
    def build_command(self):
        cmd_str = ""

    def send_command(self):
        cmd = self.widget.leCommand.text()
        logging.getLogger("GUI").info("sending command %s" % cmd)

    def rejected(self):
        logging.getLogger("GUI").info("button rejected")
        self.close()
  
    def accepted(self):
        logging.getLogger("GUI").info("button accepted")

    def close_me(self):
        pass 
    def run_cmd(self):
        pass 
