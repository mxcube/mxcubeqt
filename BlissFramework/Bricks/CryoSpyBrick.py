"""
CryoSpyBrick

[Description]
The CryoSpy brick shows temperature and other information from
a cryo cooling device.

[Properties]
------------------------------------------------------------------
| name       | type   | description
------------------------------------------------------------------
| mnemonic   | string |  name of corresponding Hardware Object
| formatString | string |  format string for numbers (defaults to ###.#)
------------------------------------------------------------------

[Signals]

[Slots]

[HardwareObjects]
The corresponding Hardware Object should emit these signals :
- temperatureChanged
- cryoStatusChanged
- dryStatusChanged
- sdryStatusChanged

Example of valid Hardware Object XML :
======================================
<device class="Cryo">
  <username>Cryo</username>
  <taconame>id23/cryospy/2</taconame>
  <interval>1000</interval>
</device>
"""
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *
from BlissFramework.Utils import widget_colors

__category__ = "Synoptic"
__author__ = "Vicente Rey, Matias Guijarro, Jose Gabadinho"
__version__ = 1.0

CRYO_COLORS = { "OFF": widget_colors.GRAY,
                "SATURATED": widget_colors.LIGHT_RED,
                "READY": widget_colors.LIGHT_GREEN,
                "WARNING": widget_colors.LIGHT_YELLOW,
                "FROZEN": widget_colors.LIGHT_BLUE,
                "UNKNOWN": None }

class CryoSpyBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty("mnemonic", "string", "")
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('warningTemp', 'integer', 110)

        self.cryodev = None #Cryo Hardware Object

        self.containerBox=QVGroupBox("Cryo",self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.containerBox.setAlignment(QLabel.AlignCenter)

        self.temperature=QLabel(self.containerBox)
        self.temperature.setAlignment(QLabel.AlignCenter)
        self.temperature.setPaletteForegroundColor(widget_colors.WHITE)
        #self.temperature.setPaletteBackgroundColor(widget_colors.LIGHT_BLUE)
        font=self.temperature.font()
        font.setStyleHint(QFont.OldEnglish)
        self.temperature.setFont(font)

        #self.level=QProgressBar(self.containerBox)

        # grid1=QWidget(self.containerBox)
        # QGridLayout(grid1, 3, 2, 2, 1)

        # label1=QLabel("Dry:",grid1)
        # grid1.layout().addWidget(label1, 0, 0)
        # self.dryState=QLabel(grid1)
        # self.dryState.setAlignment(QLabel.AlignCenter)
        # self.dryState.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        # grid1.layout().addWidget(self.dryState, 0, 1)

        # label2=QLabel("Superdry:",grid1)
        # grid1.layout().addWidget(label2, 1, 0)
        # self.superdryState=QLabel(grid1)
        # self.superdryState.setAlignment(QLabel.AlignCenter)
        # self.superdryState.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        # grid1.layout().addWidget(self.superdryState, 1, 1)

        # label3=QLabel("Icing:",grid1)
        # grid1.layout().addWidget(label3, 2, 0)
        # self.icingState=QLabel(grid1)
        # self.icingState.setAlignment(QLabel.AlignCenter)
        # self.icingState.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        # grid1.layout().addWidget(self.icingState, 2, 1)

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
            #self.temperature.setText("?%s" % chr(176))
            self.temperature.setText("? K")
        else:
            svalue = "%s K" % str(self['formatString'] % temp)
            self.temperature.setText(svalue)

            if temp > self["warningTemp"]:
              self.temperature.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
              if not old["warning"]:
                old["warning"]=True
                QMessageBox.critical(self, "Warning: risk for sample", "Cryo temperature is too high - sample is in danger!\nPlease fix the problem with cryo cooler") 
            else:
              old["warning"]=False 
              self.temperature.setPaletteBackgroundColor(widget_colors.LIGHT_BLUE)
              

    def setDrier(self, status):
        if status is None or status=='':
            status="UNKNOWN"
        try:
            color = CRYO_COLORS[status]
        except KeyError:
            color = CRYO_COLORS["UNKNOWN"]
        if color is None:
            color=QWidget.paletteBackgroundColor(self)
        self.dryState.setPaletteBackgroundColor(QColor(color))
        try:
            status=status.lower()
        except:
            status="unknown"
        self.dryState.setText(status)
        
    def setIcing(self, status):
        if status is None or status=='':
            status="UNKNOWN"
        try:
            color = CRYO_COLORS[status]
        except KeyError:
            color = CRYO_COLORS["UNKNOWN"]
        if color is None:
            color=QWidget.paletteBackgroundColor(self)
        self.icingState.setPaletteBackgroundColor(QColor(color))
        try:
            status=status.lower()
        except:
            status="unknown"
        self.icingState.setText(status)

    def setSDrier(self, status):
        if status is None or status=='':
            status="UNKNOWN"
        try:
            color = CRYO_COLORS[status]
        except KeyError:
            color = CRYO_COLORS["UNKNOWN"]
        if color is None:
            color=QWidget.paletteBackgroundColor(self)
        self.superdryState.setPaletteBackgroundColor(QColor(color))
        try:
            status=status.lower()
        except:
            status="unknown"
        self.superdryState.setText(status)

    def setLevel(self,level):
        pass
##         if level is None:
##             self.level.reset()
##         else:
##             try:
##                 level=int(level)
##             except:
##                 pass
##             else:
##                 self.level.setProgress(level)

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.cryodev is not None:
                self.disconnect(self.cryodev, PYSIGNAL("levelChanged"), self.setLevel)
                self.disconnect(self.cryodev, PYSIGNAL("temperatureChanged"), self.setTemperature)
                #self.disconnect(self.cryodev, PYSIGNAL("cryoStatusChanged"), self.setIcing)
                #self.disconnect(self.cryodev, PYSIGNAL("dryStatusChanged"), self.setDrier)
                #self.disconnect(self.cryodev, PYSIGNAL("sdryStatusChanged"), self.setSDrier)
                
            self.cryodev = self.getHardwareObject(newValue)
            if self.cryodev is not None:
                self.containerBox.setEnabled(True)
                self.connect(self.cryodev, PYSIGNAL("levelChanged"), self.setLevel)
                self.connect(self.cryodev, PYSIGNAL("temperatureChanged"), self.setTemperature)
                #self.connect(self.cryodev, PYSIGNAL("cryoStatusChanged"), self.setIcing)
                #self.connect(self.cryodev, PYSIGNAL("dryStatusChanged"), self.setDrier)
                #self.connect(self.cryodev, PYSIGNAL("sdryStatusChanged"), self.setSDrier)

                self.setLevel(self.cryodev.n2level)
                self.setTemperature(self.cryodev.temp)
                #self.setIcing(self.cryodev.cryo_status)
                #self.setDrier(self.cryodev.dry_status)
                #self.setSDrier(self.cryodev.sdry_status)
            else:
                self.containerBox.setEnabled(False)
                self.setTemperature(None)
                #self.setDrier("UNKNOWN")
                #self.setSDrier("UNKNOWN")
                #self.setIcing("UNKNOWN")
                self.setLevel(None)
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    def run(self):
        if self.cryodev is None:
            self.hide()
