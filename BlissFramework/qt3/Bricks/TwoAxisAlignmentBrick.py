'''

Doc please...

'''

__version__ = 1.0
__author__ = "Matias Guijarro"
__category__ = 'Motor'


import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons


class TwoAxisAlignmentBrick(BlissWidget):
    def __init__(self, *args):
        """
        Constructor
        """
        BlissWidget.__init__(self, *args)

        self.verticalMotor = None
        self.horizontalMotor = None
        self.motorStatesColors = [self.colorGroup().background(),
                                  self.colorGroup().background(),
                                  Qt.green,
                                  Qt.yellow,
                                  Qt.yellow,
                                  Qt.red]
        
        # addProperty adds a property for the brick :
        #   - 1st argument is the name of the property ;
        #   - 2d argument is the type (one of string, integer, float, file, combo) ;
        #   - 3rd argument is the default value.
        # In some cases (e.g combo), the third argument is a tuple of choices
        # and the fourth argument is the default value.
        # When a property is changed, the propertyChanged() method is called.
        self.addProperty("mnemonic", "string", "")
        self.addProperty("defaultStepSize", "float", 0.1)
        self.addProperty("moveUpStepFactor", "combo", ("1", "-1"), "1")
        self.addProperty("moveLeftStepFactor", "combo", ("1", "-1"), "-1")
        self.addProperty("title", "string", "")
        self.addProperty("formatString", "formatString", "###.##")

        # now we can "draw" the brick, i.e creating GUI widgets
        # and arranging them in a layout. It is the default appearance
        # for the brick (if no property is set for example)
        self.lblTitle = QLabel(self)
        upBox = QWidget(self)
        upBoxLayout = QVBoxLayout(upBox, 0, 0)
        upBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.lblUp = QLabel(upBox)
        self.cmdUp = QPushButton(upBox)
        self.lblUp.setFont(QFont("courier"))
        # Icons is a Python module that comes with the Bliss Framework ;
        # it can load an icon file from the Resource directory inside the
        # BlissFramework package given its name (without extension).
        self.cmdUp.setPixmap(Icons.load("up_small"))
        upBoxLayout.addWidget(self.lblUp, 0, Qt.AlignCenter)
        upBoxLayout.addWidget(self.cmdUp, 0)
        
        downBox = QWidget(self)
        downBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        downBoxLayout = QVBoxLayout(downBox, 0, 0)
        self.cmdDown = QPushButton(downBox)
        self.cmdDown.setPixmap(Icons.load("down_small"))
        self.lblDown = QLabel(downBox)
        self.lblDown.setFont(QFont("courier"))
        downBoxLayout.addWidget(self.cmdDown, 0)
        downBoxLayout.addWidget(self.lblDown, 0, Qt.AlignCenter)
         
        leftBox = QHBox(self)
        leftBox.setSpacing(5)
        leftBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.lblLeft = QLabel(leftBox)
        self.lblLeft.setAlignment(Qt.AlignCenter)
        self.lblLeft.setFont(QFont("courier"))
        self.cmdLeft = QPushButton(leftBox)
        self.cmdLeft.setPixmap(Icons.load("left_small"))
        self.cmdLeft.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        rightBox = QHBox(self)
        rightBox.setSpacing(5)
        rightBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.cmdRight = QPushButton(rightBox)
        self.cmdRight.setPixmap(Icons.load("right_small"))
        self.cmdRight.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.lblRight = QLabel(rightBox)
        self.lblRight.setAlignment(Qt.AlignCenter)
        self.lblRight.setFont(QFont("courier"))
    
        centralBox = QVBox(self)
        centralBox.setSpacing(10)
        centralBox.setMargin(10)
        centralBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        stepBox = QVBox(centralBox)
        self.lblCurrentStep = QLabel("Current step : ?", stepBox)
        self.cmdChangeStep = QToolButton(stepBox)
        self.cmdChangeStep.setTextLabel("Change step")
        self.cmdChangeStep.setUsesTextLabel(True)
        self.cmdChangeStep.setIconSet(QIconSet(Icons.load("steps_small")))
        self.cmdAbort = QToolButton(centralBox)
        self.cmdAbort.setIconSet(QIconSet(Icons.load("stop_small")))
        self.cmdAbort.setTextLabel("Abort")
        self.cmdAbort.setUsesTextLabel(True)

        QGridLayout(self, 4, 3, 5, 5)
        self.layout().addMultiCellWidget(self.lblTitle, 0, 0, 0, 2, Qt.AlignHCenter)
        self.layout().addWidget(upBox, 1, 1)
        self.layout().addWidget(leftBox, 2, 0)
        self.layout().addWidget(centralBox, 2, 1, Qt.AlignCenter)
        self.layout().addWidget(rightBox, 2, 2)
        self.layout().addWidget(downBox, 3, 1)

        # establish connections between signals and slots
        QObject.connect(self.cmdUp, SIGNAL("clicked()"), self.cmdUpClicked)
        QObject.connect(self.cmdLeft, SIGNAL("clicked()"), self.cmdLeftClicked)
        QObject.connect(self.cmdRight, SIGNAL("clicked()"), self.cmdRightClicked)
        QObject.connect(self.cmdDown, SIGNAL("clicked()"), self.cmdDownClicked)
        QObject.connect(self.cmdAbort, SIGNAL("clicked()"), self.cmdAbortClicked)
        QObject.connect(self.cmdChangeStep, SIGNAL("clicked()"), self.cmdChangeStepClicked)

        self.currentVerticalLabel = self.lblUp
        self.currentHorizontalLabel = self.lblRight
        self.cmdAbort.setEnabled(False)
        

    def updateHMotorPosition(self, position=None):
        if position is not None:
            mne = self.horizontalMotor.userName()
            pos = self["formatString"] % position
        else:
            mne = "h. motor"
            pos = "?"
            
            if self.horizontalMotor is not None:
                mne = self.horizontalMotor.userName()
            
                if self.horizontalMotor.isReady():
                    hpos = self.horizontalMotor.getPosition()
                    pos = self["formatString"] % hpos
        
        for label in (self.lblLeft, self.lblRight):
            length = max(len(mne), len(str(pos)))
            label.setFixedSize(label.fontMetrics().width(length*"#"), 2*label.fontMetrics().height())
            
            if label == self.currentHorizontalLabel:
                label.setText('%s\n%s' % (mne, pos))
            else:
                label.setText("")
                label.setPaletteBackgroundColor(self.colorGroup().background())
                

    def updateVMotorPosition(self, position=None):
        if position is not None:
            mne = self.verticalMotor.userName()
            pos = self["formatString"] % position
        else:
            mne = "v. motor"
            pos = "?"
        
            if self.verticalMotor is not None:
                mne = self.verticalMotor.userName()
            
                if self.verticalMotor.isReady():
                    vpos = self.verticalMotor.getPosition()
                    pos = self["formatString"] % vpos
          
        for label in (self.lblUp, self.lblDown):
            label.setFixedSize(label.fontMetrics().width(mne + " " + str(pos)), label.fontMetrics().height())
            
            if label == self.currentVerticalLabel:
                label.setText('%s %s' % (mne, pos))
            else:
                label.setText("")
                label.setPaletteBackgroundColor(self.colorGroup().background())


    def updateMotorPositions(self):
        self.updateHMotorPosition()
        self.updateVMotorPosition()

    
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.verticalMotor is not None and self.horizontalMotor is not None:
                # remove connections previously established
                self.disconnect(self.verticalMotor, PYSIGNAL("stateChanged"), self.updateVMotorState)
                self.disconnect(self.horizontalMotor, PYSIGNAL("stateChanged"), self.updateHMotorState)
                self.disconnect(self.verticalMotor, PYSIGNAL("positionChanged"), self.updateVMotorPosition)
                self.disconnect(self.horizontalMotor, PYSIGNAL("positionChanged"), self.updateHMotorPosition)

            equipment = self.getHardwareObject(newValue)
       
            if equipment is not None:
                try:
                    self.verticalMotor = equipment.getDeviceByRole("vertical")
                    self.horizontalMotor = equipment.getDeviceByRole("horizontal")
                except:
                    logging.getLogger().error("%s: could not find vertical and horizontal motors in Hardware Object %s", str(self.name()), equipment.name())
                else:
                    if self.verticalMotor is not None and self.horizontalMotor is not None:
                        self.connect(self.verticalMotor, PYSIGNAL("stateChanged"), self.updateVMotorState)
                        self.connect(self.horizontalMotor, PYSIGNAL("stateChanged"), self.updateHMotorState)
                        self.connect(self.verticalMotor, PYSIGNAL("positionChanged"), self.updateVMotorPosition)
                        self.connect(self.horizontalMotor, PYSIGNAL("positionChanged"), self.updateHMotorPosition)

                        self.currentVerticalLabel = self.lblUp
                        self.currentHorizontalLabel = self.lblRight

                        # refresh labels
                        self["formatString"] = self.getProperty("formatString").getUserValue()
                    else:
                        logging.getLogger().error("%s: invalid vertical/horizontal motors in Hardware Object %s", str(self.name()), equipment.name())
                        
            self.updateMotorPositions()
            self.updateMotorStates()
        elif property == 'defaultStepSize':
            self.lblCurrentStep.setText("Current step : %s" % (newValue or "?"))
        elif property == 'title':
            self.lblTitle.setText(newValue)
        elif property == 'formatString':
            self.updateMotorPositions()

             
    def setAbortState(self):
        for motor in (self.horizontalMotor, self.verticalMotor):
            if motor is not None and motor.isReady() and motor.getState() == motor.MOVING:
                self.cmdAbort.setEnabled(True)
                return

        self.cmdAbort.setEnabled(False)


    def updateMotorStates(self):
        self.updateVMotorState()
        self.updateHMotorState()


    def updateVMotorState(self, state=None):
        if state is None:
            state = 0
            enabled = False
            if self.verticalMotor is not None:
                if self.verticalMotor.isReady():
                    state = self.verticalMotor.getState()
                    enabled = state > self.verticalMotor.UNUSABLE
        else:
            enabled = state > self.verticalMotor.UNUSABLE
            
        color = self.motorStatesColors[state]
        
        self.cmdDown.setEnabled(enabled)
        self.cmdUp.setEnabled(enabled)
            
        for label in (self.lblDown, self.lblUp):
            label.setEnabled(enabled)

            if label == self.currentVerticalLabel:
                label.setPaletteBackgroundColor(color)
            else:
                label.setPaletteBackgroundColor(label.colorGroup().background())
                label.setText("")

        self.updateVMotorPosition()
        self.setAbortState()
        

    def updateHMotorState(self, state=None):
        if state is None:
            state = 0
            enabled = False
            if self.horizontalMotor is not None:
                if self.horizontalMotor.isReady():
                    state = self.horizontalMotor.getState()
                    enabled = state > self.horizontalMotor.UNUSABLE
        else:
            enabled = state > self.horizontalMotor.UNUSABLE
            
        color = self.motorStatesColors[state]
        
        self.cmdLeft.setEnabled(enabled)
        self.cmdRight.setEnabled(enabled)
            
        for label in (self.lblLeft, self.lblRight):
            label.setEnabled(enabled)

            if label == self.currentHorizontalLabel:
                label.setPaletteBackgroundColor(color)
            else:
                label.setPaletteBackgroundColor(label.colorGroup().background())
                label.setText("")

        self.updateHMotorPosition()
        self.setAbortState()
 
        
    def cmdUpClicked(self):
        self.currentVerticalLabel = self.lblUp
        stepFactor = int(self["moveUpStepFactor"])
        self.verticalMotor.moveRelative(self["defaultStepSize"]*stepFactor)
        

    def cmdDownClicked(self):
        self.currentVerticalLabel = self.lblDown
        stepFactor = int(self["moveUpStepFactor"])
        self.verticalMotor.moveRelative(-self["defaultStepSize"]*stepFactor)


    def cmdLeftClicked(self):
        self.currentHorizontalLabel = self.lblLeft
        stepFactor = int(self["moveLeftStepFactor"])
        self.horizontalMotor.moveRelative(self["defaultStepSize"]*stepFactor)


    def cmdRightClicked(self):
        self.currentHorizontalLabel = self.lblRight
        stepFactor = int(self["moveLeftStepFactor"])
        self.horizontalMotor.moveRelative(-self["defaultStepSize"]*stepFactor)


    def cmdChangeStepClicked(self):
        newStep, ok = QInputDialog.getDouble("New step :", "Change step", self["defaultStepSize"], 0.00001, 100000, 5)
        
        if ok:
            self["defaultStepSize"] = newStep

    
    def cmdAbortClicked(self):
        for motor in (self.verticalMotor, self.horizontalMotor):
            if motor.getState() == motor.MOVING:
                motor.stop()




