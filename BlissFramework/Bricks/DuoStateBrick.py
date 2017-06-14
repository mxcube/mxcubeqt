from BlissFramework import BaseComponents
from BlissFramework import Icons
from BlissFramework.Utils import widget_colors
from qt import *
import new
import re
import logging

###
### Brick to control a hardware object with two states
###
class DuoStateBrick(BaseComponents.BlissWidget):

    STATES = {
        'unknown': (None, True, True, False, False),
        'disabled': (widget_colors.LIGHT_RED, False, False, False, False),
        'error': (widget_colors.LIGHT_RED, True, True, False, False),
        'out': (widget_colors.DARK_GRAY, True, True, False, True),
        'moving': (widget_colors.LIGHT_YELLOW, False, False, None, None),
        'in': (widget_colors.LIGHT_GREEN, True, True, True, False),
        'automatic': (widget_colors.WHITE, True, True, False, False)
    }

    LABEL_CLASS=QLabel

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self,*args)

        self.wrapperHO=None
        self.__expertMode = False
        
        self.addProperty('mnemonic','string','')
        self.addProperty('forceNoControl','boolean',False)
        self.addProperty('expertModeControlOnly', 'boolean', False)
        self.addProperty('icons','string','')
        self.addProperty('in','string','in')
        self.addProperty('out','string','out')
        self.addProperty('setin','string','Set in')
        self.addProperty('setout','string','Set out')
        self.addProperty('username','string','')
        self.defineSlot('allowControl',())
        #self.defineSlot('stateChanged',())

        self.defineSignal('duoStateBrickIn',())
        self.defineSignal('duoStateBrickOut',())
        self.defineSignal('duoStateBrickMoving',())

        self.containerBox=QVGroupBox("none",self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)

        #self.stateLabel = myLabel('<b> </b>', self.containerBox)
        self.stateLabel = self.LABEL_CLASS('<b> </b>', self.containerBox)

        self.buttonsBox=QHBox(self.containerBox)
        self.setInButton=QPushButton("Set in",self.buttonsBox)
        self.setInButton.setToggleButton(True)
        self.connect(self.setInButton,SIGNAL('toggled(bool)'),self.setIn)

        self.setOutButton=QPushButton("Set out",self.buttonsBox)
        self.setOutButton.setToggleButton(True)
        self.connect(self.setOutButton,SIGNAL('toggled(bool)'),self.setOut)

        #self.stateLabel.setHintWidget(self.buttonsBox)

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)

        self.stateLabel.setAlignment(QLabel.AlignCenter)

        QToolTip.add(self.stateLabel,"Shows the current control state")
        QToolTip.add(self.setInButton,"Changes the control state")
        QToolTip.add(self.setOutButton,"Changes the control state")


    def setExpertMode(self, expert):
        self.__expertMode = expert

        self.buttonsBox.show()
        
        if not expert and self["expertModeControlOnly"]:
            self.buttonsBox.hide()

        
    def setIn(self,state):
        #print "DuoStateBrick.setIn",state
        if state:
            self.wrapperHO.setIn()
        else:
            self.setInButton.blockSignals(True)
            self.setInButton.setState(QPushButton.On)
            self.setInButton.blockSignals(False)

    def setOut(self,state):
        #print "DuoStateBrick.setOut",state
        if state:
            self.wrapperHO.setOut()
        else:
            self.setOutButton.blockSignals(True)
            self.setOutButton.setState(QPushButton.On)
            self.setOutButton.blockSignals(False)

    def updateLabel(self,label):
        self.containerBox.setTitle(label)

    def stateChanged(self,state,state_label=None):
        #logging.info("DuoStateBrick.stateChanged(%s)" % state)
        try:
            color=self.STATES[state][0]
        except KeyError:
            state='unknown'
            color=self.STATES[state][0]
        if color is None:
            color=QWidget.paletteBackgroundColor(self)

        self.stateLabel.setPaletteBackgroundColor(QColor(color))
        try:
            state_label=self[state]
        except KeyError:
            state_label=None
        if state_label is not None:
            self.stateLabel.setText('<b>%s</b>' % state_label)
        else:
            self.stateLabel.setText('<b>%s</b>' % state)

        try:
            in_enable=self.STATES[state][1]
            out_enable=self.STATES[state][2]
        except KeyError:
            in_enable=False
            out_enable=False
        self.setInButton.setEnabled(in_enable)
        self.setOutButton.setEnabled(out_enable)

        try:
            in_state=self.STATES[state][3]
            out_state=self.STATES[state][4]
        except KeyError:
            in_state=QPushButton.Off
            out_state=QPushButton.Off
        if in_state is not None:
            if in_state:
                self.setInButton.blockSignals(True)
                self.setInButton.setState(QPushButton.On)
                self.setInButton.blockSignals(False)
            else:
                self.setInButton.blockSignals(True)
                self.setInButton.setState(QPushButton.Off)
                self.setInButton.blockSignals(False)
        if out_state is not None:
            if out_state:
                self.setOutButton.blockSignals(True)
                self.setOutButton.setState(QPushButton.On)
                self.setOutButton.blockSignals(False)
            else:
                self.setOutButton.blockSignals(True)
                self.setOutButton.setState(QPushButton.Off)
                self.setOutButton.blockSignals(False)

        if state=='in':
            self.emit(PYSIGNAL("duoStateBrickMoving"), (False, ))
            self.emit(PYSIGNAL("duoStateBrickIn"), (True, ))
        elif state=='out':
            self.emit(PYSIGNAL("duoStateBrickMoving"), (False, ))
            self.emit(PYSIGNAL("duoStateBrickOut"), (True, ))
        elif state=='moving':
            self.emit(PYSIGNAL("duoStateBrickMoving"), (True, ))
        elif state=='error' or state=='unknown' or state=='disabled':
            self.emit(PYSIGNAL("duoStateBrickMoving"), (False, ))
            self.emit(PYSIGNAL("duoStateBrickIn"), (False, ))
            self.emit(PYSIGNAL("duoStateBrickOut"), (False, ))

    def allowControl(self,enable):
        if self['forceNoControl']:
            return
        if enable:
            self.buttonsBox.show()
        else:
            self.buttonsBox.hide()

    def run(self):
        if self.wrapperHO is None:
            self.containerBox.hide()

    def stop(self):
        self.containerBox.show()

    def propertyChanged(self,propertyName,oldValue,newValue):
        #print "DuoStateBrick.propertyChanged",propertyName,newValue
        if propertyName=='mnemonic':
            if self.wrapperHO is not None:
                self.disconnect(self.wrapperHO,PYSIGNAL('duoStateChanged'), self.stateChanged)

            h_obj=self.getHardwareObject(newValue)
            if h_obj is not None:
                self.wrapperHO=WrapperHO(h_obj)
                self.containerBox.show()
                
                if self['username']=='':
                    self['username']=self.wrapperHO.userName()

                help=self['setin']+" the "+self['username'].lower()
                QToolTip.add(self.setInButton,help)
                help=self['setout']+" the "+self['username'].lower()
                QToolTip.add(self.setOutButton,help)

                self.containerBox.setTitle(self['username'])
                self.connect(self.wrapperHO,PYSIGNAL('duoStateChanged'), self.stateChanged)
                self.stateChanged(self.wrapperHO.getState())
            else:
                self.wrapperHO=None
                #self.containerBox.hide()
        elif propertyName=='expertModeControlOnly':
            if newValue:
                if self.__expertMode:
                    self.buttonsBox.show()
                else:
                    self.buttonsBox.hide()
            else:
                self.buttonsBox.show()
        elif propertyName=='forceNoControl':
            if newValue:
                self.buttonsBox.hide()
            else:
                self.buttonsBox.show()
        elif propertyName=='icons':
            w=self.fontMetrics().width("Set out")
            icons_list=newValue.split()
            try:
                self.setInButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                self.setInButton.setText(self['setin'])
                self.setInButton.setMinimumWidth(w)
            try:
                self.setOutButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                self.setOutButton.setText(self['setout'])
                self.setOutButton.setMinimumWidth(w)

        elif propertyName=='in':
            if self.wrapperHO is not None:
                self.stateChanged(self.wrapperHO.getState())

        elif propertyName=='out':
            if self.wrapperHO is not None:
                self.stateChanged(self.wrapperHO.getState())

        elif propertyName=='setin':
            icons=self['icons']
            w=self.fontMetrics().width("Set out")
            icons_list=icons.split()
            try:
                i=icons_list[0]
            except IndexError:
                self.setInButton.setText(newValue)
                self.setInButton.setMinimumWidth(w)
            help=newValue+" the "+self['username'].lower()
            QToolTip.add(self.setInButton,help)

        elif propertyName=='setout':
            icons=self['icons']
            w=self.fontMetrics().width("Set out")
            icons_list=icons.split()
            try:
                i=icons_list[1]
            except IndexError:
                self.setOutButton.setText(newValue)
                self.setOutButton.setMinimumWidth(w)
            help=newValue+" the "+self['username'].lower()
            QToolTip.add(self.setOutButton,help)

        elif propertyName=='username':
            if newValue=='':
                if self.wrapperHO is not None:
                    name=self.wrapperHO.userName()
                    if name!='':
                        self['username']=name
                        return
            help=self['setin']+" the "+newValue.lower()
            QToolTip.add(self.setInButton,help)
            help=self['setout']+" the "+newValue.lower()
            QToolTip.add(self.setOutButton,help)            
            self.containerBox.setTitle(self['username'])

        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

###
### Wrapper around different hardware objects, to make them have the
### same behavior to the brick
###
class WrapperHO(QObject):
    wagoStateDict={'in':'in', 'out':'out', 'unknown':'unknown'}
    actuatorStateDict={'in':'in', 'out':'out', 'unknown':'unknown'}

    shutterStateDict={'fault':'error', 'opened':'in', 'closed':'out',\
        'unknown':'unknown', 'moving':'moving', 'automatic':'automatic',\
        'disabled':'disabled', 'error':'error'}

    motorWPosDict=('out', 'in')
    motorWStateDict=('disabled', 'error', None, 'moving',\
        'moving', 'moving')

    STATES = ('unknown','disabled','error','out','moving','in','automatic')

    def __init__(self,hardware_obj):
        QObject.__init__(self)

        self.setIn = new.instancemethod(lambda self: None, self)
        self.setOut = self.setIn 
        self.getState = new.instancemethod(lambda self: "unknown", self)

        self.dev=hardware_obj
        try:
            sClass = str(self.dev.__class__)
            i, j = re.search("'.*'", sClass).span()
        except:
            dev_class = sClass
        else:
            dev_class = sClass[i+1:j-1]
        self.devClass = dev_class.split('.')[-1]

        #print "Type is",self.devClass
        if self.devClass=="Device":
            self.devClass="Procedure"

        if self.devClass=="TangoShutter":
            self.devClass="Shutter"

        if self.devClass=="MicrodiffInOut":
            self.devClass="Actuator"

        #2011-08-30-bessy-mh: let the wrapper also feel responsible for my new ShutterEpics hardware object
        #                     identical to the original Shutter hardware object
        if self.devClass == "ShutterEpics":
            self.devClass = "Shutter"
        #2011-08-30-bessy-mh: end

        #2013-10-31-bessy-mh: ... and for the MD2 shutter hardware object too!
        if self.devClass == "MD2v4_FastShutter":
            self.devClass = "Shutter"
        #2013-10-31-bessy-mh: end
            
        if not self.devClass in ("WagoPneu", "Shutter", "SpecMotorWSpecPositions", "Procedure", "Actuator"):
          self.devClass = "WagoPneu"

        initFunc = getattr(self, "init%s" % self.devClass)
        initFunc()
        self.setIn = getattr(self, "setIn%s" % self.devClass)
        self.setOut = getattr(self, "setOut%s" % self.devClass)
        self.getState = getattr(self, "getState%s" % self.devClass)

    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict["setIn"]
        del dict["setOut"]
        del dict["getState"]
        return dict

    def __setstate__(self, dict):
        self.__dict__ = dict.copy()
        self.setIn = new.instancemethod(lambda self: None, self)
        self.setOut = self.setIn
        self.getState = new.instancemethod(lambda self: "unknown", self)

    def userName(self):
        return self.dev.userName()

    # WagoPneu HO methods
    def initWagoPneu(self):
        #print "initWagoPneu"
        self.dev.connect(self.dev,'wagoStateChanged', self.stateChangedWagoPneu)
    def setInWagoPneu(self):
        #print "setInWagoPneu"
        self.emit(PYSIGNAL('duoStateChanged'), ('moving', ))
        self.dev.wagoIn()
    def setOutWagoPneu(self):
        #print "setOutWagoPneu"
        self.emit(PYSIGNAL('duoStateChanged'), ('moving', ))
        self.dev.wagoOut()
    def stateChangedWagoPneu(self,state):
        #print "stateChangedWagoPneu",state
        try:
            state=WrapperHO.wagoStateDict[state]
        except KeyError:
            state='error'
        self.emit(PYSIGNAL('duoStateChanged'), (state, ))
    def getStateWagoPneu(self):
        #print "getStateWagoPneu"
        state=self.dev.getWagoState()
        try:
            state=WrapperHO.wagoStateDict[state]
        except KeyError:
            state='error'
        return state

    # Actuator HO methods
    def initActuator(self):
        #print "initActuator"
        self.dev.connect(self.dev,'actuatorStateChanged', self.stateChangedActuator)
    def setInActuator(self):
        #print "setInActuator"
        self.emit(PYSIGNAL('duoStateChanged'), ('moving', ))
        self.dev.actuatorIn()
    def setOutActuator(self):
        #print "setOutActuator"
        self.emit(PYSIGNAL('duoStateChanged'), ('moving', ))
        self.dev.actuatorOut()
    def stateChangedActuator(self,state):
        #print "stateChangedActuator",state
        try:
            state=WrapperHO.actuatorStateDict[state]
        except KeyError:
            state='error'
        self.emit(PYSIGNAL('duoStateChanged'), (state, ))
    def getStateActuator(self):
        #print "getStateActuator"
        state=self.dev.getActuatorState()
        try:
            state=WrapperHO.actuatorStateDict[state]
        except KeyError:
            state='error'
        return state

    # Shutter HO methods
    def initShutter(self):
        #print "initShutter"
        self.dev.connect(self.dev, 'shutterStateChanged', self.stateChangedShutter)
    def setInShutter(self):
        #print "setInShutter"
        self.dev.openShutter()
    def setOutShutter(self):
        #print "setOutShutter"
        self.dev.closeShutter()
    def stateChangedShutter(self,state):
        #print "stateChangedShutter"
        #logging.info("stateChangedShutter %s" % state) 
        try:
            state=WrapperHO.shutterStateDict[state]
        except KeyError:
            state='error'
        self.emit(PYSIGNAL('duoStateChanged'), (state, ))
    def getStateShutter(self):
        #print "getStateShutter"
        state=self.dev.getShutterState()
        try:
            state=WrapperHO.shutterStateDict[state]
        except KeyError:
            state='error'
        return state

    # SpecMotorWSpecPositions HO methods
    def initSpecMotorWSpecPositions(self):
        #print "initSpecMotorWSpecPositions"
        self.positions=None
        self.dev.connect(self.dev, 'predefinedPositionChanged', self.positionChangedSpecMotorWSpecPositions)
        self.dev.connect(self.dev, 'stateChanged', self.stateChangedSpecMotorWSpecPositions)
        self.dev.connect(self.dev, 'newPredefinedPositions', self.newPredefinedSpecMotorWSpecPositions)
    def setInSpecMotorWSpecPositions(self):
        #print "setInSpecMotorWSpecPositions"
        if self.positions is not None:
            self.dev.moveToPosition(self.positions[1])
    def setOutSpecMotorWSpecPositions(self):
        #print "setOutSpecMotorWSpecPositions"
        if self.positions is not None:
            self.dev.moveToPosition(self.positions[0])
    def stateChangedSpecMotorWSpecPositions(self,state):
        #logging.info("stateChangedSpecMotorWSpecPositions %s" % state)
        try:
            state = WrapperHO.motorWStateDict[state]
        except IndexError:
            state = 'error'
        if state is not None:
            #print "emiting duoStateChanged",state
            self.emit(PYSIGNAL('duoStateChanged'), (state, ))
    def positionChangedSpecMotorWSpecPositions(self,pos_name,pos):
        #print "positionChangedSpecMotorWSpecPositions",pos_name,pos

        if self.dev.getState()!=self.dev.READY:
            return
        
        state="error"
        if self.positions is not None:
            for i in range(len(self.positions)):
                if pos_name==self.positions[i]:
                    state=WrapperHO.motorWPosDict[i]
        #print "emiting duoStateChanged",state
        self.emit(PYSIGNAL('duoStateChanged'), (state, ))
    def getStateSpecMotorWSpecPositions(self):
        #print "getStateSpecMotorWSpecPositions"
        if self.positions is None:
            return "error"
        curr_pos=self.dev.getCurrentPositionName()
        if curr_pos is None:
            state=self.dev.getState()
            try:
                state=WrapperHO.motorWStateDict[state]
            except IndexError:
                state='error'
            return state
        else:
            for i in range(len(self.positions)):
                if curr_pos==self.positions[i]:
                    return WrapperHO.motorWPosDict[i]                    
        return 'error'
    def newPredefinedSpecMotorWSpecPositions(self): 
        #print "newPredefinedSpecMotorWSpecPositions"
        self.positions=self.dev.getPredefinedPositionsList()
        self.positionChangedSpecMotorWSpecPositions(self.dev.getCurrentPositionName(),self.dev.getPosition())

    # Procedure HO methods
    def initProcedure(self):
        #print "initProcedure"
        cmds=self.dev.getCommands()

        self.setInCmd=None
        self.setOutCmd=None

        try:
            channel=self.dev.getChannelObject("dev_state")
        except KeyError:
            channel=None
        self.stateChannel=channel
        if self.stateChannel is not None:
            self.state_dict={'OPEN':'in', 'CLOSED':'out', 'ERROR':'error', '1':'in', '0':'out'}
            self.stateChannel.connectSignal('update', self.channelUpdate)
        else:
            self.state_dict={}

        for c in cmds:
            if c.name()=="set in":
                self.setInCmd=c
                if self.stateChannel is not None:
                    self.setInCmd.connectSignal('commandReplyArrived', self.procedureSetInEnded)
                    self.setInCmd.connectSignal('commandBeginWaitReply', self.procedureStarted)
                    self.setInCmd.connectSignal('commandFailed', self.procedureAborted)
                    self.setInCmd.connectSignal('commandAborted', self.procedureAborted)
            elif c.name()=="set out":
                self.setOutCmd=c
                if self.stateChannel is not None:
                    self.setOutCmd.connectSignal('commandReplyArrived', self.procedureSetOutEnded)
                    self.setOutCmd.connectSignal('commandBeginWaitReply', self.procedureStarted)
                    self.setOutCmd.connectSignal('commandFailed', self.procedureAborted)
                    self.setOutCmd.connectSignal('commandAborted', self.procedureAborted)

    def channelUpdate(self,value):
        try:
            key=self.dev.statekey
        except AttributeError:
            pass
        else:
            try:
                value=value[key]
            except TypeError:
                value='error'
        try:
            value=self.state_dict[value]
        except KeyError:
            pass
        self.emit(PYSIGNAL('duoStateChanged'), (value, ))
    def setInProcedure(self):
        if self.setInCmd is not None:
            self.setInCmd()
    def setOutProcedure(self):
        if self.setOutCmd is not None:
            self.setOutCmd()
    """
    def stateChangedProcedure(self,state):
        #print "stateChangedProcedure",state
        pass
    """
    def getStateProcedure(self):
        #print "getStateProcedure"
        if self.stateChannel is not None:
            try:
                state=self.stateChannel.getValue()
            except:
                state='error'
            else:
                try:
                    key=self.dev.statekey
                except AttributeError:
                    pass
                else:
                    try:
                        state=state[key]
                    except TypeError:
                        state='error'
            try:
                state=self.state_dict[state]
            except KeyError:
                pass
            return state
        return "unknown"
    def procedureSetInEnded(self, *args):
        self.emit(PYSIGNAL('duoStateChanged'), ('in', ))
        
    def procedureSetOutEnded(self, *args):
        self.emit(PYSIGNAL('duoStateChanged'), ('out', ))
        
    def procedureStarted(self, *args):
        self.emit(PYSIGNAL('duoStateChanged'), ('moving', ))
        
    def procedureAborted(self, *args):
        self.emit(PYSIGNAL('duoStateChanged'), ('error', ))
