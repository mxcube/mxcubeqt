import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Bricks import MotorSpinBoxBrick
from BlissFramework.Bricks import CommandMenuBrick
import math

__category__ = 'mxCuBE'

class MinikappaBrick(BlissWidget):
    MINIKAPPA_ONOFF_COMMANDS = ("KappaOff","KappaOn")

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSlot("updateCollectParameters", ())

        self.minikappa=None
        self.motors={}
        self.__refs={}
        self.motorSteps={}
        self.currentMotorName=None

        self.kappaOnOngoing=None
        self.kappaOffOngoing=None

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('commandIcons', 'string', '')
        self.addProperty('motorIcons', 'string', '')
        self.addProperty('formatString','formatString','###.###')
        self.addProperty('decimalPlaces', 'string', '')
        self.addProperty('maxMotorsPerLine', 'integer', 3)

        self.topBox = QHGroupBox("Minikappa",self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)
        self.topBox.setCheckable(True)
        QObject.connect(self.topBox, SIGNAL('toggled(bool)'), self.enableChanged)

        self.motorBox = QVGroupBox("Motors",self.topBox)
        box1=QHBox(self.motorBox)
        self.motorBox.setInsideMargin(4)
        self.motorBox.setInsideSpacing(2)
        self.motorsList=QComboBox(box1)
        QObject.connect(self.motorsList, SIGNAL('activated(const QString &)'), self.motorChanged)
        self.currentMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(box1)
        self.currentMotor['showMoveButtons']=False
        self.currentMotor['showBox']=False
        self.currentMotor['showLabel']=False
        self.currentMotor['showStep']=False
        self.currentMotor['showStepList']=True

        self.motorsGrid=QWidget(self.motorBox)
        QGridLayout(self.motorsGrid, 0, 0, 2, 2)

        self.commands=CommandMenuBrick.CommandMenuBrick(self.topBox)
        self.commands.hideCommands(self.MINIKAPPA_ONOFF_COMMANDS)
        self.kappaOnCmd=None
        self.kappaOffCmd=None
        self.kappaInUseChan=None

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

    def enableChanged(self,enable):
        #print "MinikappaBrick.enableChanged",enable,self.kappaOnOngoing,self.kappaOffOngoing

        if self.kappaOnOngoing or self.kappaOffOngoing:
            return

        if enable:
            if self.kappaOnCmd is not None:
                try:
                    self.kappaOnCmd()
                except:
                    logging.getLogger().exception("MinikappaBrick: problem enabling the minikappa for the sample changer")

            self.currentMotor.setEnabled(True)
            self.commands.setEnabled(True)
        else:
            if self.kappaOffCmd is not None:
                try:
                    self.kappaOffCmd()
                except:
                    logging.getLogger().exception("MinikappaBrick: problem disabling the minikappa from the sample changer")

    def motorChanged(self,name):
        if self.currentMotorName is not None:
            self.motorSteps[self.currentMotorName]=self.currentMotor.getLineStep()
            
        try:
            self.currentMotor['mnemonic']=self.motors[str(name)][0]
        except KeyError:
            pass
        else:
            self.currentMotorName=str(name)

            icons_list=self['motorIcons'].split('/')
            icons_dict={}
            for icon in icons_list:
                icon_list=icon.split('=')
                try:
                    icons_dict[icon_list[0]]=icon_list[1]
                except IndexError:
                    pass

            try:
                icons=icons_dict[str(name)]
            except KeyError:
                pass
            else:
                self.currentMotor['icons']=icons

            try:
                laststep=self.motorSteps[str(name)]
            except KeyError:
                pass
            else:
                self.currentMotor.setLineStep(laststep)

    def addMotor(self,mnemonic,username,ho):
        i=len(self.motors.keys())
        col=i % self['maxMotorsPerLine']
        line=i / self['maxMotorsPerLine']

        motor_label=QLabel("%s:" % username,self.motorsGrid)
        motor_label.setAlignment(Qt.AlignRight)
        motor_pos=QLabel("0.0",self.motorsGrid)
        motor_pos.setAlignment(Qt.AlignRight)

        self.motorsGrid.layout().addWidget(motor_label, line, col*2)
        self.motorsGrid.layout().addWidget(motor_pos, line, (col*2)+1)

        self.motors[username]=(mnemonic,ho,motor_pos)
        self.motorsList.insertItem(username)

        position_changed=lambda position:MinikappaBrick.positionChanged(self,username,position)
        state_changed=lambda state:MinikappaBrick.stateChanged(self,username,state)
        self.__refs[ho]=(state_changed,position_changed)
        self.connect(ho,PYSIGNAL('stateChanged'),state_changed,instanceFilter=True)
        self.connect(ho,PYSIGNAL('positionChanged'),position_changed,instanceFilter=True)

        self.stateChanged(username,ho.getState())
        if ho.isReady():
            self.positionChanged(username,ho.getPosition())

    def setMotors(self,minikappa=None,disconnect=False):
        if disconnect:
            for ho in self.__refs:
                callbacks=self.__refs[ho]
                self.disconnect(ho,PYSIGNAL('stateChanged'),callbacks[0])
                self.disconnect(ho,PYSIGNAL('positionChanged'),callbacks[1])

            self.motors={}
            self.__refs={}
            self.motorsList.clear()
        elif minikappa is not None:
            self.topBox.setTitle(minikappa.userName())
            for role in ('omega', 'kappa', 'phi', '-X', 'Y', 'Z'):
              m=minikappa.getDeviceByRole(role)
              if m is not None:
                self.addMotor(m.name(), role, m)
            self.motorChanged(self.motorsList.currentText())

    def setCommands(self,minikappa=None,disconnect=False):
        if disconnect:
            if self.kappaOnCmd is not None:
                self.kappaOnCmd.disconnectSignal("commandStarted", self.kappaOnStarted)
                self.kappaOnCmd.disconnectSignal("commandReplyArrived", self.kappaOnFinished)
                self.kappaOnCmd.disconnectSignal("commandFailed", self.kappaOnFinished)

            if self.kappaOffCmd is not None:
                self.kappaOffCmd.disconnectSignal("commandStarted", self.kappaOffStarted)
                self.kappaOffCmd.disconnectSignal("commandReplyArrived", self.kappaOffFinished)
                self.kappaOffCmd.disconnectSignal("commandFailed", self.kappaOffFinished)

            self.kappaOnCmd=None
            self.kappaOffCmd=None
        else:
            if minikappa is not None:
                self.kappaOnCmd=minikappa.getCommandObject("KappaOn")
                self.kappaOffCmd=minikappa.getCommandObject("KappaOff")

                if self.kappaOnCmd is not None:
                    self.kappaOnCmd.connectSignal("commandStarted", self.kappaOnStarted)
                    self.kappaOnCmd.connectSignal("commandReplyArrived", self.kappaOnFinished)
                    self.kappaOnCmd.connectSignal("commandFailed", self.kappaOnFinished)

                if self.kappaOffCmd is not None:
                    self.kappaOffCmd.connectSignal("commandStarted", self.kappaOffStarted)
                    self.kappaOffCmd.connectSignal("commandReplyArrived", self.kappaOffFinished)
                    self.kappaOffCmd.connectSignal("commandFailed", self.kappaOffFinished)
            else:
                self.kappaOnCmd=None
                self.kappaOffCmd=None

    def kappaOnStarted(self):
        self.kappaOnOngoing=True

    def kappaOnFinished(self):
        self.kappaOnOngoing=False

    def kappaOffStarted(self):
        self.kappaOffOngoing=True

    def kappaOffFinished(self):
        self.kappaOffOngoing=False

    def stateChanged(self,username,state):
        motor_pos=self.motors[username][2]
        color=MotorSpinBoxBrick.MotorSpinBoxBrick.STATE_COLORS[state]
        motor_pos.setPaletteBackgroundColor(color)        

    def positionChanged(self,username,pos):
        motor_pos=self.motors[username][2]
        pos_str=self['formatString'] % pos
        motor_pos.setText(pos_str)

    def run(self):
        if self.minikappa is None:
            self.hide()
        else:
            if self.kappaInUseChan is not None:
                self.kappaInUseChanged(self.kappaInUseChan.getValue())
            else:
                self.topBox.setCheckable(False)

    def setChannels(self,minikappa=None,disconnect=False):
        if disconnect:
            if self.kappaInUseChan is not None:
                self.kappaInUseChan.disconnectSignal("update", self.kappaInUseChanged)
            self.kappaInUseChan=None
        else:
            if minikappa is not None:
                try:
                    self.kappaInUseChan=minikappa.getChannelObject("KappaInUse")
                except KeyError:
                    logging.getLogger().warning("MinikappaBrick: unable to know if minikappa is beging used!")
                    self.kappaInUseChan=None
                else:
                    if self.kappaInUseChan is not None:
                        self.kappaInUseChan.connectSignal('update',self.kappaInUseChanged)
                        self.kappaInUseChanged(self.kappaInUseChan.getValue())
            else:
                self.kappaInUseChan=None

    def setExpertMode(self, expert):
        # find checkbox and enable or disable it
        for w in self.topBox.children():
            if w.isWidgetType() and str(w.name())=="qt_groupbox_checkbox":
                w.setEnabled(expert)
                break        

    def kappaInUseChanged(self,state):
        state=bool(state)
        self.topBox.setChecked(state)
        self.motorBox.setEnabled(state)
        self.commands.setEnabled(state)

    def updateCollectParameters(self, params_dict):
        # this slot is called from bricks looking for data collection params
        # params_dict need to be updated
        try:
            kappa_in_use = self.kappaInUseChan.getValue()
        except:
            logging.warning("Invalid kappa in use channel")
            kappa_in_use = False
            
        if kappa_in_use:
            kappaStart = self.minikappa.getDeviceByRole("kappa").getPosition()
            phiStart = self.minikappa.getDeviceByRole("phi").getPosition()
            if math.fabs(kappaStart) < 1E-3:
                kappaStart = 0
        else:
          kappaStart = -9999
          phiStart = -9999
        params_dict.update({ "kappaStart": kappaStart, "phiStart": phiStart })

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            self.setMotors(self.minikappa,disconnect=True)
            self.setCommands(self.minikappa,disconnect=True)
            self.setChannels(self.minikappa,disconnect=True)

            self.commands['mnemonic']=newValue
            self.commands['label']='Commands'

            self.minikappa = self.getHardwareObject(newValue)
            if self.minikappa is not None:
                self.setMotors(self.minikappa)
                self.setCommands(self.minikappa)
                self.setChannels(self.minikappa)

        elif property == 'commandIcons':
            self.commands['icons']=newValue
        elif property == 'motorIcons':
            self.motorChanged(self.motorsList.currentText())
        elif property == 'formatString':
            self.currentMotor['formatString']=newValue
        elif property == 'decimalPlaces':
            self.currentMotor['decimalPlaces']=newValue
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)
