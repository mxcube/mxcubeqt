from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
from DuoStateBrick import DuoStateBrick
import TwoAxisAlignmentBrick
import logging

class beamstopLabel(QWidget):
    def __init__(self,label,parent):
        QWidget.__init__(self,parent)
        QHBoxLayout(self)
        self.buttonStop=QPushButton("*",self)
        self.buttonStop.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        QToolTip.add(self.buttonStop,"Stops the beamstop")
        QObject.connect(self.buttonStop,SIGNAL('clicked()'),self.buttonStopClicked)
        self.label=QLabel(self)
        self.button=QPushButton("+",self)
        self.button.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        QToolTip.add(self.button,"Aligns the beamstop")
        QObject.connect(self.button,SIGNAL('clicked()'),self.buttonClicked)
        self.layout().addWidget(self.buttonStop)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.button)
    def setText(self,txt):
        self.label.setText(txt)
    def setAlignment(self,align):
        self.label.setAlignment(align)
    def setButtonPixmap(self,px):
        self.button.setPixmap(px)
    def setButtonText(self,txt):
        self.button.setText(txt)
    def buttonClicked(self):
        self.emit(PYSIGNAL('setupClicked'), ())
    def setButtonEnabled(self,state):
        self.button.setEnabled(state)
    def showButton(self,state):
        if state:
            self.button.show()
        else:
            self.button.hide()
    def setButtonStopPixmap(self,px):
        self.buttonStop.setPixmap(px)
    def setButtonStopText(self,txt):
        self.buttonStop.setText(txt)
    def buttonStopClicked(self):
        self.emit(PYSIGNAL('stopClicked'), ())
    def setButtonStopEnabled(self,state):
        self.buttonStop.setEnabled(state)

class BeamStopAlignmentDialog(QWidget):
    def __init__(self, parent, caption):
        QWidget.__init__(self, None)
        self.setCaption(caption) 
        QVBoxLayout(self, 5, 5)
        self.alignmentWidget = TwoAxisAlignmentBrick.TwoAxisAlignmentBrick(self)
        cmdBox = QVBox(self)
        self.cmdOK = QPushButton('Save Positions', cmdBox)
        self.cmdDismiss = QPushButton('Dismiss', cmdBox)

        self.alignmentWidget['formatString'] = "###.###"
        self.alignmentWidget['title'] = "Move the beamstop using the arrows and\nclick 'Save Positions' when setup is done"
        self.setCaption(caption)
        self.cmdDismiss.setAutoDefault(False)
        self.cmdOK.setAutoDefault(False)
        cmdBox.setSpacing(10)
        self.connect(self.cmdDismiss, SIGNAL('clicked()'), self.dismissClicked)
        self.connect(self.cmdOK, SIGNAL('clicked()'), self.okClicked)
        
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(self.alignmentWidget)
        self.layout().addWidget(cmdBox, 0, Qt.AlignRight | Qt.AlignBottom)

    def setMnemonic(self, mne):
        self.alignmentWidget["mnemonic"] = mne

    def dismissClicked(self):
        self.close() # = False #done(0)

    def okClicked(self):
        self.emit(PYSIGNAL("aligned"), (True,))
        self.close()

###
### Brick to control and align the beamstop
###
class BeamstopBrick(DuoStateBrick):
    LABEL_CLASS=beamstopLabel
    
    def __init__(self, *args):
        DuoStateBrick.__init__.im_func(self, *args)
        self.alignmentDialog = BeamStopAlignmentDialog(self, "Beamstop alignment")
        self.alignmentDialog.hide()
        QObject.connect(self.alignmentDialog, PYSIGNAL("aligned"), self.beamstopAligned)
        self.beamstop = None
        self.positions = {}
        self.connect(self.stateLabel,PYSIGNAL('setupClicked'),self.setupClicked)
        self.connect(self.stateLabel,PYSIGNAL('stopClicked'),self.stopClicked)
        self.addProperty('setupIcon', 'string', '')
        self.addProperty('stopIcon', 'string', '')

    #def allowSetup(self,state):
    def setExpertMode(self,state):
        self.stateLabel.showButton(state)

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.beamstop is not None:
                self.disconnect(self.beamstop, PYSIGNAL('equipmentReady'), self.equipmentReady)
                self.disconnect(self.beamstop, PYSIGNAL('equipmentNotReady'), self.equipmentNotReady)
                self.disconnect(self.beamstop, PYSIGNAL("positionReached"), self.positionChanged)
                self.disconnect(self.beamstop, PYSIGNAL("noPosition"), self.positionChanged) 

            self.beamstop = self.getHardwareObject(newValue)

            if self.beamstop is not None:
                self.connect(self.beamstop, PYSIGNAL('equipmentReady'), self.equipmentReady)
                self.connect(self.beamstop, PYSIGNAL('equipmentNotReady'), self.equipmentNotReady)
                self.connect(self.beamstop, PYSIGNAL("positionReached"), self.positionChanged)
                self.connect(self.beamstop, PYSIGNAL("noPosition"), self.positionChanged)

                help=self['setin']+" the "+self.beamstop.userName().lower()
                QToolTip.add(self.setInButton,help)
                help=self['setout']+" the "+self.beamstop.userName().lower()
                QToolTip.add(self.setOutButton,help)
                 
                if not "in" in self.beamstop.positions or not "out" in self.beamstop.positions:
                    logging.getLogger().warning("%s: vertical beamstop motor does not define In and Out positions", str(self.name()))
                
                self.containerBox.setTitle(self.beamstop.userName())
                self.alignmentDialog.setMnemonic(newValue)

                # do some checkings...
                try:
                    bstopz = self.beamstop.getDeviceByRole("vertical").getMotorMnemonic()
                    bstopy = self.beamstop.getDeviceByRole("horizontal").getMotorMnemonic()
                except:
                    logging.getLogger().error("%s: could not find vertical and horizontal motors in Hardware Object %s", str(self.name()), self.beamstop.name())

                if self.beamstop.isReady():
                    self.beamstop.setNewPositions("out", {"vertical": self.beamstop.getDeviceByRole("vertical").getLimits()[0] })
                    self.equipmentReady()
                    self.beamstop.checkPosition()
                else:
                    self.equipmentNotReady()
            else:
                self.equipmentNotReady()

            self.wrapperHO=self.beamstop
        elif propertyName=='setupIcon':
            if newValue=="":
                self.stateLabel.setButtonText('+')
            else:
                self.stateLabel.setButtonPixmap(Icons.load(newValue))
        elif propertyName=='stopIcon':
            if newValue=="":
                self.stateLabel.setButtonStopText('*')
            else:
                self.stateLabel.setButtonStopPixmap(Icons.load(newValue))
        elif propertyName=='icons':
            DuoStateBrick.propertyChanged.im_func(self,propertyName,oldValue,newValue)
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def setIn(self,state):
        #print "BeamstopBrick.setIn",state
        if state:
            #print "GO IN"
            self.beamstop.moveToPosition("in")
        else:
            DuoStateBrick.setIn.im_func(self,False)

    def setOut(self,state):
        #print "BeamstopBrick.setOut",state
        self.beamstop.setNewPositions("out", {"vertical": self.beamstop.getDeviceByRole("vertical").getLimits()[0] })
        if state:
            self.beamstop.moveToPosition("out")
        else:
            DuoStateBrick.setOut.im_func(self,False)

    def equipmentReady(self):
        self.setEnabled(True)

    def equipmentNotReady(self):
        self.stateChanged('disabled')
        self.setEnabled(False)

    def setupClicked(self):
        self.alignmentDialog.show() #exec_loop()
        
    def beamstopAligned(self):
            try:
                bstopz = self.beamstop.getDeviceByRole("vertical")
                bstopy = self.beamstop.getDeviceByRole("horizontal")
                bstopzPos = bstopz.getPosition()
                bstopyPos = bstopy.getPosition()
            except:
                logging.getLogger().error("%s: could not find vertical and horizontal motors in hardware object %s", str(self.name()), self.beamstop.name())
            else:
                newInPos = { 'vertical': bstopzPos, 'horizontal': bstopyPos }
                self.beamstop.setNewPositions("in", newInPos)
                newOutPos = newInPos
                newOutPos['vertical'] = self.beamstop.getDeviceByRole("vertical").getLimits()[0]
                self.beamstop.setNewPositions("out", newOutPos)

                QMessageBox.information(self, "Beamstop alignment", "New beamstop positions saved successfully.", QMessageBox.Ok)
                return

            QMessageBox.warning(self, "Beamstop alignment", "An error occured while trying to save beamstop positions.", QMessageBox.Cancel)

    def positionChanged(self, positionName = ""):
        #print "BeamstopBrick.positionChanged",positionName
        if positionName in ("in", "unknown"):
            self.stateLabel.setButtonEnabled(True)
        else:
            self.stateLabel.setButtonEnabled(False)

        if positionName in ("in", "out"):
            self.stateChanged(positionName)
        else:
            if self.beamstop.getState()=="MOVING":
                self.stateChanged("moving")
            else:
                self.stateChanged("unknown")

    def stateChanged(self,state):
        self.stateLabel.setButtonStopEnabled(state=="moving")
        # weird Python bug : why do we need im_func sometimes?
        DuoStateBrick.stateChanged.im_func(self,state)

    def stopClicked(self):
        for motor in self.beamstop.motors:
            self.beamstop.motors[motor].stop()
	    return
