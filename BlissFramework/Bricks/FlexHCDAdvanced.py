import qt
import gevent
from BlissFramework import BaseComponents 
import functools

__category__ = 'Sample changer'

class FlexHCDAdvanced(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)
        self.addProperty("hwobj", "string", "")
        self.addProperty("hutch_mode", "boolean", False)
        self.addProperty("change_gripper", "boolean", True)
       
        self.btnHome = qt.QPushButton("Home", self)
        self.btnChangeGripper = qt.QPushButton("Change gripper", self)
        self.btnCleanGripper = qt.QPushButton("Clean gripper", self)
        self.btnResetLoaded = qt.QPushButton("Reset sample", self)
        self.lblCurrentGripper = qt.QLabel("Current gripper: ?", self)
        self.btnUserPort = qt.QPushButton("User port", self)
        self.btnUserPort.setToggleButton(True)
        self.btnScan = qt.QPushButton("Scan ProxiSense", self)
        self.btnScan.setEnabled(False)
        self.cellsbox = qt.QGrid(4, self)
        self.cellsbox.setMargin(60)
        self.cellsbox.setSpacing(20)
        self.cellsbox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self.btnChangeCell = []
        for i in range(8):
            self.btnChangeCell.append(qt.QPushButton(str(i+1), self.cellsbox))
            self.btnChangeCell[-1].setToggleButton(True)
            self.btnChangeCell[-1].moving = False
            qt.QObject.connect(self.btnChangeCell[-1], qt.SIGNAL("clicked()"), functools.partial(self.gotoCell, i))
        self.cellTimer = qt.QTimer(self)

        qt.QObject.connect(self.btnHome, qt.SIGNAL("clicked()"), self.homeClicked)
        qt.QObject.connect(self.btnChangeGripper, qt.SIGNAL("clicked()"), self.changeGripperClicked)
        qt.QObject.connect(self.btnCleanGripper, qt.SIGNAL("clicked()"), self.cleanGripperClicked)
        qt.QObject.connect(self.btnResetLoaded, qt.SIGNAL("clicked()"), self.resetLoadedClicked)
        qt.QObject.connect(self.btnUserPort, qt.SIGNAL("toggled(bool)"), self.userPortToggled)
        qt.QObject.connect(self.btnScan, qt.SIGNAL("clicked()"), self.scanProxiSense)
        qt.QObject.connect(self.cellTimer, qt.SIGNAL("timeout()"), self.readCell)

        qt.QGridLayout(self, 4, 3)
        self.layout().setSpacing(10)
        self.layout().setMargin(40)
        self.layout().addWidget(self.btnHome, 0, 1)
        self.layout().addWidget(self.btnCleanGripper, 0, 0)
        self.layout().addWidget(self.btnResetLoaded, 0, 2)
        self.layout().addMultiCellWidget(self.lblCurrentGripper, 1, 1, 0, 1)
        self.layout().addWidget(self.btnChangeGripper, 1, 2)
        self.layout().addWidget(self.btnUserPort, 2, 0)
        self.layout().addMultiCellWidget(self.btnScan, 2, 2, 1, 2)
        self.layout().addMultiCellWidget(self.cellsbox, 3, 3, 0, 2)
        
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Fixed)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'hwobj':
            self.hw_obj = self.getHardwareObject(new_value)

        elif property_name == 'hutch_mode':
            if new_value:
                for btn in (self.btnHome, self.btnCleanGripper, self.btnResetLoaded, self.lblCurrentGripper, self.btnChangeGripper):
                  btn.hide()
                for btn in (self.btnUserPort, self.btnScan):
                  btn.show() 
                self.cellsbox.show()
            else:
                for btn in (self.btnHome, self.btnCleanGripper, self.btnResetLoaded, self.lblCurrentGripper):
                  btn.show()
                if self["change_gripper"]:
                    self.btnChangeGripper.show()
                else:
                    self.btnChangeGripper.hide()
                for btn in (self.btnUserPort, self.btnScan):
                    btn.hide() 
                self.cellsbox.hide()
        elif property_name == 'change_gripper':
            if not new_value:
                self.btnChangeGripper.hide()

    def run(self):
        if self.hw_obj is not None:
            self.cellTimer.start(1000)
            self.connect(self.hw_obj, self.hw_obj.STATE_CHANGED_EVENT, self.stateUpdated)
            self.stateUpdated(self.hw_obj.getState(), None)

    def userPortToggled(self, open):
        self.hw_obj._execute_cmd("user_port", open)

    def scanProxiSense(self):
        pass

    def readCell(self):
        cell = self.hw_obj._execute_cmd('get_user_cell_position')
        for i in range(8):
          if not self.btnChangeCell[i].moving:
            self.btnChangeCell[i].setOn(False)
        if cell > 0:
          self.btnChangeCell[cell-1].setOn(True)
          if self.btnChangeCell[cell-1].moving:
            self.cellsbox.setEnabled(True)
            self.btnChangeCell[cell-1].moving = False
 
    def gotoCell(self, i):
        target = i+1
        self.btnChangeCell[i].moving = True
        self.hw_obj._execute_cmd("moveDewar", target, 1, True)
        self.cellsbox.setEnabled(False)

    def stateUpdated(self, state, former):
        if str(state) == '1':
	    gripper = self.hw_obj.get_gripper()
	    self.updateGripperType(gripper)

            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def updateGripperType(self, gripper_type):
        self.lblCurrentGripper.setText("Current gripper: %s" % gripper_type)

    def homeClicked(self):
        self.hw_obj.home(wait=False)

    def cleanGripperClicked(self):
        self.hw_obj.defreeze(wait=False)

    def enablePowerClicked(self):
        self.hw_obj.enable_power(wait=False)

    def changeGripperClicked(self):
        self.hw_obj.change_gripper(wait=False)

    def resetLoadedClicked(self):
        self.hw_obj.reset_loaded_sample()

