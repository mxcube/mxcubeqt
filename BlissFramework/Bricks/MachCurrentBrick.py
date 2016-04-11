"""
MachCurrentBrick

[Description]

The MachCurrent brick displays machine current (in mA), fill mode and operator's messages.

[Properties]

------------------------------------------------------------
|   Name           |  Type | Description    
------------------------------------------------------------
| mnemonic         | string | mnemonic to the MachCurrent Hardware Object
| formatString     | string | format string for numbers (defaults to ###.#)
| currentThreshold | float | low limit for current before error status is reported (defaults to 1.0)
------------------------------------------------------------

[Signals]

------------------------------------------------------------
|   Name   |   Arguments   |   Description 
------------------------------------------------------------
|  operatorMessage | opmsg | emitted everytime operator sends a new message 
------------------------------------------------------------

[Slots]

[HardwareObjects]

Example of valid Hardware Object :
==================================

<device class = "MachCurrent">
  <username>Mach</username>
  <taconame>//aries/fe/id/23</taconame>
  <interval>5000</interval>
</device>
"""
from BlissFramework import BaseComponents
from qt import *
import logging
import time

from BlissFramework.Utils import widget_colors

__category__ = 'Synoptic'

class MachCurrentBrick(BaseComponents.BlissWidget):
    STATES = {
        'unknown':  widget_colors.DARK_GRAY,
        'ready': widget_colors.LIGHT_BLUE,
        'error':  widget_colors.LIGHT_RED
        }

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.machCurrent=None
        self.lastValue=None

        self.addProperty('mnemonic','string','')
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('currentThreshold', 'float', 1.0)
        self.defineSignal('operatorMessage',())

        self.containerBox=QVGroupBox("Machine current",self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.containerBox.setAlignment(QLabel.AlignLeft)
        #self.containerBox.setFixedWidth(350)

        self.current=QLabel(self.containerBox)
        self.current.setAlignment(QLabel.AlignCenter)
        self.current.setPaletteForegroundColor(widget_colors.WHITE)
        font=self.current.font()
        font.setStyleHint(QFont.OldEnglish)
        self.current.setFont(font)
        self.mode=QLabel(self.containerBox)
        self.mode.setAlignment(QLabel.AlignCenter)
        self.mode.setPaletteBackgroundColor(widget_colors.LIGHT_BLUE)

        self.refillCountdown=QLCDNumber(self.containerBox)
        self.refillCountdown.setSegmentStyle(QLCDNumber.Flat)

        self.containerBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)

        QToolTip.add(self.current,"Current machine current")
        QToolTip.add(self.mode,"Fill mode")
        QToolTip.add(self.refillCountdown,"Refill countdown")

    def setValue(self,value=None,opmsg=None,fillmode=None,refill=None):
        if value is None:
            value=self.lastValue
        else:
            self.lastValue=value

        self.current.setText("")
        if value is None:
            self.setStateColor('unknown')
            self.current.setText("???.? mA")
        else:
            if value<self['currentThreshold']:
                self.setStateColor('error')
            else:
                self.setStateColor('ready')
            svalue = '<b>%s</b> mA' % str(self['formatString'] % value)
            self.current.setText(svalue)

        if fillmode is not None and fillmode!="":
            self.mode.setText("<i>%s</i>" % fillmode)

        try:
            refill_secs=int(refill)
            if refill_secs>=0:
                ts=time.gmtime(refill_secs)
                txt=time.strftime("%H:%M",ts)
            else:
                txt="00:00"
            self.refillCountdown.display(txt)
            self.refillCountdown.show()
        except TypeError,ValueError:
            self.refillCountdown.hide()

        if opmsg is not None and opmsg!="" and opmsg!="unknown":
            QToolTip.add(self.current,opmsg)
            self.emit(PYSIGNAL("operatorMessage"),(opmsg,))

    def setStateColor(self,state):
        color=MachCurrentBrick.STATES[state]
        self.current.setPaletteBackgroundColor(QColor(color))

        #if state == 'error':
            #QMessageBox.warning(self, 'mxCuBE', 'Warning: Check machine current') 
        

    def fontChange(self,oldFont):
        font=self.font()
        size=font.pointSize()
        font.setPointSize(5+size)
        self.current.setFont(font)
    
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.machCurrent is not None:
                self.disconnect(self.machCurrent,PYSIGNAL('valueChanged'),self.setValue)
                self.disconnect(self.machCurrent,PYSIGNAL('timeout'),self.setValue)

            self.setValue()

            self.machCurrent=self.getHardwareObject(newValue)
            if self.machCurrent is not None:
                self.containerBox.setEnabled(True)
                self.connect(self.machCurrent,PYSIGNAL('valueChanged'),self.setValue)
                self.connect(self.machCurrent,PYSIGNAL('timeout'),self.setValue)
            else:
                self.containerBox.setEnabled(False)
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
