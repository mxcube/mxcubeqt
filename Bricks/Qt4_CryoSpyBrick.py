"""

Name:   Qt4_CryoSpyBrick.py

Description:
----------------------------------------
The CryoSpy brick shows temperature and N2 filling level from 
a cryo cooling device.

Properties
----------------------------------------

The following properties can be setup for this brick::

  ------------------------------------------------------------------
  | name         | type   | description
  ------------------------------------------------------------------
  | mnemonic     | string |  name of corresponding Hardware Object
  | formatString | string |  format string for numbers (defaults to ###.#)
  ------------------------------------------------------------------

Signals
----------------------------------------
No signal is emitted by this Brick

Slots
----------------------------------------
No public slots are implemented in this Brick

HardwareObject
----------------------------------------
A Hardware Object connected to this brick should emit the following
signals:

   - levelChanged [level_value] (in %)
   - temperatureChanged [temp_value] (in deg. Kelvin)
   - stateChanged (a valid state)
       * If state is "RUNNING" (ok)
       * Any other state (Not ok)
      

Supported
---------------------------------
The SOLEIL/TangoCryo.py  HardwareObject implementation is supported by
this Brick 

"""

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

import os
import math
import logging

__category__ = "General"
__author__ = "Laurent Gadea"
__version__ = 1.0

CRYO_COLORS = { "OFF": Qt4_widget_colors.GRAY,
                "SATURATED": Qt4_widget_colors.LIGHT_RED,
                "READY": Qt4_widget_colors.LIGHT_GREEN,
                "RUNNING": Qt4_widget_colors.LIGHT_GREEN,
                "WARNING": Qt4_widget_colors.LIGHT_YELLOW,
                "TEMP_WARNING": Qt4_widget_colors.RED,
                "FROZEN": Qt4_widget_colors.LIGHT_BLUE,
                "UNKNOWN": Qt4_widget_colors.LIGHT_RED }

DEFAULT_STYLE = """
QProgressBar {
   color: white;
   font-weight: bold;
   background-color: lightblue;
   border-radius: 8px;
   border: 1px solid grey;
}

QProgressBar::chunk {
   background-color: #3333ff;
   border-radius: 8px;
}
"""

WARNING_STYLE = """
QProgressBar {
   color: white;
   font-weight: bold;
   background-color: #ffcccc;
   border-radius: 8px;
   border: 1px solid grey;
}

QProgressBar::chunk {
   background-color: #993333;
   border-radius: 8px;
}
"""

class Qt4_CryoSpyBrick(BlissWidget):

    def __init__(self, *args):

        BlissWidget.__init__(self, *args)
        
        self.addProperty("mnemonic", "string", "")
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('warningTemp', 'integer', 110)

        self.cryodev = None #Cryo Hardware Object
        
        self.cryo_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                               "widgets/ui_files/Qt4_cryospy.ui"))
       
        self.cryo_widget.ln2level.setTextVisible(True)
        self.cryo_widget.ln2level.setStyleSheet(DEFAULT_STYLE)
           
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.cryo_widget)

        self.warning_temp = 200  # overwritten by Brick properties
        self.temp_warning = False

        self.state = "UNKNOWN"
        self.updateState()

    def ofontChange(self,oldFont):
        #font=self.font()
        font=oldFont
        size=font.pointSize()
        font.setPointSize(int(1.5*size))
        self.cryo_widget.temperature.setFont(font)
    
    def temperatureChanged(self, temp):

        if not isinstance(temp,float):
            self.cryo_widget.temperature.setText("? &deg;K")
        elif math.isnan(temp):
            self.cryo_widget.temperature.setText("? &deg;K")
        else:
            svalue = "%s <sup>o</sup>K" % str(self['formatString'] % temp)
            self.cryo_widget.temperature.setText(svalue)

    def levelChanged(self,level):
        if level is None:
            self.cryo_widget.ln2level.reset()
        else:
            try:
                level=int(level)
            except:
                pass
            else:
                self.cryo_widget.ln2level.setValue(level)

    def stateChanged(self,state):
        if self.state != state:
            self.state = state
            self.updateState()

    def updateState(self):

        if self.state in CRYO_COLORS:
            color = CRYO_COLORS[self.state]
        else:
            color = CRYO_COLORS["UNKNOWN"]

        if self.state == "TEMP_WARNING":
            QtGui.QMessageBox.critical(self, "Warning: risk for sample", "Cryo temperature is too high - sample is in danger!\nPlease fix the problem with cryo cooler")
            self.cryo_widget.temperature.setStyleSheet("color: white;font-weight: bold;")
            self.cryo_widget.ln2level.setStyleSheet(WARNING_STYLE)
        else:
            self.cryo_widget.temperature.setStyleSheet("color: black;font-weight: bold;")
            self.cryo_widget.ln2level.setStyleSheet(DEFAULT_STYLE)

        Qt4_widget_colors.set_widget_color(self.cryo_widget.temperature, color)
 
    def propertyChanged(self, property, oldValue, newValue):

        if property == 'mnemonic':

            if self.cryodev is not None:
                self.disconnect(self.cryodev, "levelChanged", self.levelChanged)
                self.disconnect(self.cryodev, "temperatureChanged", self.temperatureChanged)
                self.disconnect(self.cryodev, "stateChanged", self.stateChanged)

            self.cryodev = self.getHardwareObject(newValue)

            if self.cryodev is not None:
                self.connect(self.cryodev, "levelChanged", self.levelChanged)
                self.connect(self.cryodev, "temperatureChanged", self.temperatureChanged)
                self.connect(self.cryodev, "stateChanged", self.stateChanged)
            else:
                self.temperatureChanged(None)
                self.levelChanged(None)
                self.updateState()

        elif property == 'warningTemp':
            self.warning_temp = newValue
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    #def run(self):
        #if self.cryodev is None:
            #self.hide()
