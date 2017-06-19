from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
from DuoStateBrick import DuoStateBrick
import logging

__category__ = 'mxCuBE'

class hutchTriggerLabel(QWidget):
    def __init__(self,label,parent):
        QWidget.__init__(self,parent)
        QHBoxLayout(self)
        self.buttonStop=QPushButton("*",self)
        self.buttonStop.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        QToolTip.add(self.buttonStop,"Stops the hutch trigger")
        QObject.connect(self.buttonStop,SIGNAL('clicked()'),self.buttonStopClicked)
        self.buttonStop.setEnabled(False)
        self.label=QLabel(self)
        self.layout().addWidget(self.buttonStop)
        self.layout().addWidget(self.label)
    def setText(self,txt):
        self.label.setText(txt)
    def setAlignment(self,align):
        self.label.setAlignment(align)
    def setButtonStopPixmap(self,px):
        self.buttonStop.setPixmap(px)
    def setButtonStopText(self,txt):
        self.buttonStop.setText(txt)
    def buttonStopClicked(self):
        self.emit(PYSIGNAL('stopClicked'), ())
    def setButtonStopEnabled(self,state):
        self.buttonStop.setEnabled(state)

###
### Brick to control the hutch trigger operations
###
class HutchTriggerBrick2(DuoStateBrick):
    LABEL_CLASS=hutchTriggerLabel

    STATES = {
        'disabled': (None, False, False, False, False),
        'error': (QWidget.red, True, True, False, False),
        'entering': (QWidget.yellow, False, False, None, None),
        'leaving': (QWidget.yellow, False, False, None, None),
        'automatic': (QWidget.white, True, True, False, False),
        'ready': (QWidget.green, True, True, False, False)
    }

    def __init__(self, *args):
        DuoStateBrick.__init__.im_func(self, *args)
        self.hutchTrigger = None
        self.connect(self.stateLabel,PYSIGNAL('stopClicked'),self.stopClicked)
        self.addProperty('stopIcon', 'string', '')
        self.addProperty('mode', 'combo', ('automatic', 'manual'), 'automatic')

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.hutchTrigger is not None:
                self.disconnect(self.hutchTrigger, PYSIGNAL('connected'), self.connected)
                self.disconnect(self.hutchTrigger, PYSIGNAL('disconnected'), self.connected)
                self.disconnect(self.hutchTrigger, PYSIGNAL('statusChanged'), self.statusChanged)
                self.disconnect(self.hutchTrigger, PYSIGNAL('msgChanged'), self.msgChanged)
                self.disconnect(self.hutchTrigger, PYSIGNAL('macroStarted'), self.hutchTriggerStarted)
                self.disconnect(self.hutchTrigger, PYSIGNAL('macroDone'), self.hutchTriggerDone)
                self.disconnect(self.hutchTrigger, PYSIGNAL('macroFailed'), self.hutchTriggerFailed)
                self.disconnect(self.hutchTrigger, PYSIGNAL('hutchTrigger'), self.hutchTriggerChanged)

            self.hutchTrigger = self.getHardwareObject(newValue)

            if self.hutchTrigger is not None:
                self.connect(self.hutchTrigger, PYSIGNAL('connected'), self.connected)
                self.connect(self.hutchTrigger, PYSIGNAL('disconnected'), self.connected)
                self.connect(self.hutchTrigger, PYSIGNAL('statusChanged'), self.statusChanged)
                self.connect(self.hutchTrigger, PYSIGNAL('msgChanged'), self.msgChanged)
                self.connect(self.hutchTrigger, PYSIGNAL('macroStarted'), self.hutchTriggerStarted)
                self.connect(self.hutchTrigger, PYSIGNAL('macroDone'), self.hutchTriggerDone)
                self.connect(self.hutchTrigger, PYSIGNAL('macroFailed'), self.hutchTriggerFailed)
                self.connect(self.hutchTrigger, PYSIGNAL('hutchTrigger'), self.hutchTriggerChanged)

                QToolTip.add(self.setInButton,"Executes the enter hutch operations")
                QToolTip.add(self.setOutButton,"Executes the leave hutch operations")

                if self['username']=="":
                    self.containerBox.setTitle(self.hutchTrigger.userName())

                if self.hutchTrigger.isConnected():
                    self.connected()
                else:
                    self.disconnected()
            else:
                self.disconnected()

            self.wrapperHO=self.hutchTrigger
        elif propertyName=='stopIcon':
            if newValue=="":
                self.stateLabel.setButtonStopText('*')
            else:
                self.stateLabel.setButtonStopPixmap(Icons.load(newValue))
        elif propertyName=='icons':
            DuoStateBrick.propertyChanged.im_func(self,propertyName,oldValue,newValue)
        elif propertyName=='username':
            if newValue!="":
                self.containerBox.setTitle(newValue)
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def setIn(self,state):
        if state:
            self.stateChanged('entering')
            self.hutchTrigger.macro(1)
        else:
            DuoStateBrick.setIn.im_func(self,False)

    def setOut(self,state):
        if state:
            self.stateChanged('leaving')
            self.hutchTrigger.macro(0)
        else:
            DuoStateBrick.setOut.im_func(self,False)

    def connected(self):
        if self['mode']=='automatic':
            self.stateChanged('automatic')
        else:
            self.stateChanged('ready')

    def disconnected(self):
        self.stateChanged('disabled')

    def statusChanged(self,status):
        #print "HutchTrigger2.statusChanged",status
        pass

    def msgChanged(self,msg):
        logging.getLogger().info(msg)

    def hutchTriggerStarted(self):
        self.stateLabel.setButtonStopEnabled(True)

    def hutchTriggerDone(self):
        self.stateLabel.setButtonStopEnabled(False)
        if self['mode']=='automatic':
            self.stateChanged('automatic')
        else:
            self.stateChanged('ready')

    def hutchTriggerFailed(self):
        self.stateLabel.setButtonStopEnabled(False)
        self.stateChanged('error')

    def hutchTriggerChanged(self,state):
        if self['mode']=='automatic':
            if state:
                self.setIn(True)
            else:
                self.setOut(True)

    def stopClicked(self):
        self.hutchTrigger.abort()
