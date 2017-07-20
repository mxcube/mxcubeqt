"""
Example of valid Hardware Object XML
====================================
<device class="Oxford700">
  <username>Cryo</username>
  <controller>/bliss</controller>
  <cryostat>cryostream</cryostat>
  <interval>120</interval>
</device>
"""
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *
from BlissFramework.Utils import widget_colors

__category__ = "Synoptic"
__author__ = "A.Beteva"
__version__ = 1.0

class CryostatBrick(BlissWidget):

    PHASE = ['RAMP', 'COOL']
    OXPHASE = ['PLAT', 'HOLD', 'END', 'PURGE']
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('warningTemp', 'integer', 360)
        self.addProperty('control_mode', 'boolean', False)

        self.cryodev = None #Cryo Hardware Object
        self.pause = False #Flag to know if we pause or not the hold phase
        self.cryo_type = None
        self.unit = None
        self.ramprate_unit = None

        self.containerBox=QVGroupBox('Cryostat', self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.containerBox.setAlignment(QLabel.AlignCenter)

        self.temperature=QLabel(self.containerBox)
        self.temperature.setAlignment(QLabel.AlignCenter)
        self.temperature.setPaletteForegroundColor(widget_colors.WHITE)
        font=self.temperature.font()
        font.setStyleHint(QFont.OldEnglish)
        self.temperature.setFont(font)

        self.paramsBox = QWidget(self.containerBox)
        QGridLayout(self.paramsBox, 2, 5, 4, 4)
        #self.paramsBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        self.lblPhase = QLabel("Phase:", self.paramsBox)
        self.paramsBox.layout().addWidget(self.lblPhase, 0, 0)
        self.lblPhase.setAlignment(QWidget.AlignRight)
        self.lstPhase = QComboBox(self.paramsBox)
        #self.lstPhase.setFixedWidth(100)
        self.paramsBox.layout().addWidget(self.lstPhase, 0, 1)
        for item_name in CryostatBrick.PHASE:
            self.lstPhase.insertItem(item_name)
        self.connect(self.lstPhase, SIGNAL('activated(int)'), self.setPhase)

        self.lblTarget = QLabel("Target temperature [K]:", self.paramsBox)
        self.paramsBox.layout().addWidget(self.lblTarget, 1, 0)
        self.lblTarget.setAlignment(QWidget.AlignRight)
        self.leditTarget = QLineEdit(self.paramsBox)
        self.leditTarget.setValidator(QDoubleValidator(self))
        #self.leditTarget.setFixedWidth(100)
        self.paramsBox.layout().addWidget(self.leditTarget, 1, 1)
        self.connect(self.leditTarget, SIGNAL('returnPressed()'), self.setTarget)
        self.connect(self.leditTarget, SIGNAL('textChanged(const QString &)'), self.leditTargetInputChanged)
        QToolTip.add(self.leditTarget, "Target temperature [%s]"% self.unit)

        self.lblRate = QLabel("Ramp rate [%s]:" % self.ramprate_unit, self.paramsBox)
        self.paramsBox.layout().addWidget(self.lblRate, 2, 0)
        self.lblRate.setAlignment(QWidget.AlignRight)
        self.leditRate = QLineEdit(self.paramsBox)
        #self.leditRate.setFixedWidth(100)
        self.leditRate.setValidator(QDoubleValidator(self))
        self.paramsBox.layout().addWidget(self.leditRate, 2, 1)
        self.connect(self.leditRate, SIGNAL('returnPressed()'), self.setRate)
        self.connect(self.leditRate, SIGNAL('textChanged(const QString &)'), self.leditRateInputChanged)
        QToolTip.add(self.leditRate, "Ramp rate [%s]"% self.ramprate_unit)

        self.startButton = QPushButton("Execute", self.paramsBox)
        self.paramsBox.layout().addWidget(self.startButton, 3, 0)
        #self.startButton = QPushButton("Execute", self.containerBox)
        self.connect(self.startButton,SIGNAL('clicked()'),self.startClicked)
        QToolTip.add(self.startButton,"Execute the required action")

        self.stopButton = QPushButton('Pause', self.paramsBox)
        self.paramsBox.layout().addWidget(self.stopButton, 3,1)
        self.stopButton.setEnabled(False)
        self.connect(self.stopButton,SIGNAL('clicked()'),self.stopClicked)
        QToolTip.add(self.stopButton,"Temporarily enter hold")

        self.containerBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)

    def fontChange(self,oldFont):
        font=self.font()
        size=font.pointSize()
        font.setPointSize(int(1.5*size))
        self.temperature.setFont(font)

    def setTemperature(self, temp, temp_error=None, old={"warning":False}):
        try:
            t = float(temp)
        except TypeError:
            self.temperature.setPaletteBackgroundColor(widget_colors.DARK_GRAY)
            self.temperature.setText("?")
        else:
            svalue = "%s %s" % (str(self['formatString'] % temp), self.unit)
            self.temperature.setText(svalue)

            if temp > self['warningTemp']:
              self.temperature.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
              if not old["warning"]:
                old["warning"]=True
                QMessageBox.critical(self, "Warning: risk for sample", "Cryo temperature is too high - sample is in danger!\nPlease fix the problem with cryo cooler") 
            else:
              old["warning"]=False 
              self.temperature.setPaletteBackgroundColor(widget_colors.LIGHT_BLUE)

    def setState(self, state):
        #self.startButton.setEnabled(False)
        #self.stopButton.setEnabled(False)
        #self.startButton.setPaletteForegroundColor(widget_colors.GRAY)
        #self.stopButton.setPaletteForegroundColor(widget_colors.GRAY)
        if state == 'RUN' or state == 'READY':
            self.startButton.setPaletteBackgroundColor(widget_colors.GREEN)
            self.startButton.setPaletteForegroundColor(QWidget.black)
            self.startButton.setEnabled(True)
        elif state == 'SHUTDOWNOK' or state == 'STARTUPOK':
            self.startButton.setPaletteBackgroundColor(widget_colors.LIGHT_YELLOW)
            self.startButton.setEnabled(True)
            self.startButton.setPaletteForegroundColor(QWidget.black)
        else:
            self.startButton.setPaletteBackgroundColor(widget_colors.DARK_GRAY)
            self.startButton.setPaletteForegroundColor(widget_colors.GRAY)
            self.stopButton.setPaletteBackgroundColor(widget_colors.DARK_GRAY)
            self.stopButton.setPaletteForegroundColor(widget_colors.GRAY)

    def propertyChanged(self, property, old_value, new_value):
        if property == 'mnemonic':
            if self.cryodev is not None:
                self.disconnect(self.cryodev, PYSIGNAL("temperatureChanged"), self.setTemperature)
                self.disconnect(self.cryodev, PYSIGNAL("stateChanged"), self.setState)
                
            self.cryodev = self.getHardwareObject(new_value)
            if self.cryodev is not None:
                self.containerBox.setEnabled(True)
                self.connect(self.cryodev, PYSIGNAL("temperatureChanged"), self.setTemperature)
                self.connect(self.cryodev, PYSIGNAL("stateChanged"), self.setState)
                try:
                    self.cryo_type, self.unit, rate = self.cryodev.get_static_parameters()

                    self.ramprate_unit = self.unit+"/"+rate
                    name = self.cryodev.getProperty('username')
                    if name:
                        self.containerBox.setTitle(name.title())
                    else:
                        self.containerBox.setTitle(self.cryo_type.title())
                    self.lblTarget.setText("Target temperature [%s]" % self.unit)
                    msg = "RAMP: Change temperature at a controlled rate\n"
                    msg += "COOL: Cool as quick as possible\n"
                    if self.cryo_type == 'oxford':
                        for item_name in CryostatBrick.OXPHASE:
                            self.lstPhase.insertItem(item_name)

                        msg += "PLAT: Maintain temperature fixed for a certain time\n"
                        msg += "HOLD: Maintain temperature fixed indefinitely\n"
                        msg += "PURGE: Warm up the Coldhead as quickly as possible\n"
                        msg += "END: System shutdown\n"
                    elif self.cryo_type == 'eurotherm':
                        self.stopButton.hide()
                    QToolTip.add(self.lstPhase,msg)
                except AttributeError:
                    pass
                try:
                    target, rate, phase, run_mode = self.cryodev.get_params()
                    self.leditTarget.setText(str(target))
                    self.leditRate.setText(str(rate))
                    phase_name = str(phase).upper()
                    if phase_name in CryostatBrick.PHASE:
                        self.setPhase(CryostatBrick.PHASE.index(phase_name))
                        self.lstPhase.setCurrentText(phase_name)
                except (TypeError, ValueError):
                    pass
                self.setTemperature(self.cryodev.temp)
            else:
                self.containerBox.setEnabled(False)
                self.setTemperature(None)
                #self.setLevel(None)
        elif property == 'control_mode':
            if new_value:
                self.paramsBox.show()
            else:
                self.paramsBox.hide()
        else:
            BlissWidget.propertyChanged(self,property,old_value,new_value)

    def run(self):
        if self.cryodev is None:
            self.hide()

    def setPhase(self, value):
        val = int(value)
        self.startButton.setText("Execute")
        self.stopButton.setText("Pause")
        self.stopButton.setEnabled(True)
        self.setState(self.cryodev.get_state())
        self.lblTarget.setEnabled(False)
        self.lblRate.setEnabled(False)
        self.lblRate.setText("Ramp rate [%s]:" % self.ramprate_unit)
        self.leditTarget.setEnabled(False)
        self.leditRate.setEnabled(False)
        if val == 0:
            self.lblTarget.setEnabled(True)
            self.lblRate.setEnabled(True)
            self.leditTarget.setEnabled(True)
            self.leditRate.setEnabled(True)
        elif val == 1:
            self.lblTarget.setEnabled(True)
            self.leditTarget.setEnabled(True)
        elif val == 2:
            self.lblRate.setText("Duration [minutes]:")
            self.lblRate.setEnabled(True)
            self.leditRate.setEnabled(True)
        elif val == 3:
            self.startButton.setText("Hold")
            self.stopButton.setEnabled(False)
        elif val == 4:
            self.lblRate.setEnabled(True)
            self.leditRate.setEnabled(True)

    def setTarget(self):
        #self.stopButton.setEnabled(False)
        state = self.cryodev.get_state()
        self.setState(state)
        try:
            val = float(self.leditTarget.text())
            self.leditTarget.setPaletteBackgroundColor(widget_colors.WHITE)
        except (TypeError, ValueError):
            self.leditTarget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            self.startButton.setEnabled(False)
            self.leditTarget.setText("?")

    def leditTargetInputChanged(self, text):
        self.leditFieldChanged(self.leditTarget, text)

    def setRate(self):
        state = self.cryodev.get_state()
        self.setState(state)
        try:
            val = float(self.leditRate.text())
            self.leditRate.setPaletteBackgroundColor(widget_colors.WHITE)
        except (TypeError, ValueError):
            self.leditRate.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            self.startButton.setEnabled(False)
            self.leditRate.setText("?")

    def leditRateInputChanged(self, text):
        self.leditFieldChanged(self.leditRate, text)


    def leditFieldChanged(self, field, text=""):
        field.setPaletteBackgroundColor(widget_colors.LIGHT_YELLOW)
        text=str(text)
        if text=="":
            field.setPaletteBackgroundColor(widget_colors.WHITE)
        else:
            try:
                val = float(text)
            except (TypeError, ValueError):
                field.setPaletteBackgroundColor(widget_colors.LIGHT_RED)

    def startClicked(self):
        phase = str(self.lstPhase.currentText())
        if phase == 'RAMP':
            #self.stopButton.setEnabled(False)
            try:
                target = float(self.leditTarget.text())
                rate = float(self.leditRate.text())
                self.leditTarget.setPaletteBackgroundColor(widget_colors.WHITE)
                self.leditRate.setPaletteBackgroundColor(widget_colors.WHITE)
                self.cryodev.start_action(phase, target, rate)
                self.stopButton.setEnabled(True)
                self.stopButton.setText('Pause')
                self.pause = False
            except (TypeError, ValueError):
                self.leditTarget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                self.leditRate.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                self.startButton.setEnabled(False)
                self.stopButton.setEnabled(False)
        elif phase == 'COOL':
            #self.stopButton.setEnabled(False)
            try:
                target = float(self.leditTarget.text())
                self.leditRate.setPaletteBackgroundColor(widget_colors.WHITE)
                self.cryodev.start_action(phase, target)
                self.stopButton.setEnabled(True)
                self.stopButton.setText('Pause')
                self.pause = False
            except (TypeError, ValueError):
                self.leditTarget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                self.startButton.setEnabled(False)
                self.stopButton.setEnabled(False)
        elif phase == 'END' or phase == 'PLAT':
            try:
                rate = float(self.leditRate.text())
                self.leditRate.setPaletteBackgroundColor(widget_colors.WHITE)
                self.cryodev.start_action(phase, rate)
            except (TypeError, ValueError):
                self.leditRate.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                self.startButton.setEnabled(False)
                self.stopButton.setEnabled(False)    
        else:
            self.stopButton.setEnabled(False)
            self.cryodev.start_action(phase, target=None, rate=None)

        self.setState(self.cryodev.get_state())


    def stopClicked(self):
        set_phase = str(self.lstPhase.currentText())
        if set_phase == 'RAMP' or set_phase == 'COOL':            
            _,_,phase,state = self.cryodev.get_params()
            if state == 'Run':
                if phase == 'RAMP' or phase == 'COOL':
                    self.stopButton.setText('Resume')
                    QToolTip.add(self.stopButton,"Exit temporary hold")
                    self.pause = False
                elif phase == 'HOLD':
                    self.stopButton.setText('Pause')
                    QToolTip.add(self.stopButton,"Temporarily enter hold")
                    self.pause = True
                self.cryodev.pause(self.pause)
        else:
            #we do not know how to stop other than ramp and cool actions
            pass

