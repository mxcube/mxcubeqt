"""
Frontend brick

[Description]

The Frontend brick allows to control a beamline frontend.

[Properties]

mnemonic - string - name of the Frontend Hardware Object
iconFile - file - path to a synoptic icon file, to be displayed on top of the brick
showSynoptic - boolean - display synoptic icon or not
title - string - text to be displayed on top of the brick
showTitle - boolean - display title or not
alignment - (top, bottom, center) - vertical alignment of the brick
hint - string - tooltip message when user lets the mouse cursor over the brick for a while

[Signals]

synopticClicked - () - emitted when synoptic icon is clicked

[Comments]

The Frontend brick can be used to just display the Frontend
status (opened/closed) but also to set Automatic Mode and
see remaining time.
"""
from qt import *

import SynopticBrick

__category__ = 'Synoptic'

class FrontendBrick(SynopticBrick.SynopticBrick):
    shutterState = {
        'unknown': 'gray',
        'closed':    '#ffffef',
        'opened':    '#00ff00',
        'moving':    '#663300',
        'automatic': '#009900',
        'fault':     '#990000',
        'disabled':  '#ff00ff',
        'error':     '#990000'
        }
    
    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.im_func(self, *args)
        
        self.addProperty('mnemonic', 'string')

        self.shutter = None

        #
        # GUI elements
        #
        self.lblShutter = QLabel('frontend', self.containerBox)
        self.cmdOpenShutter  = QPushButton('Open',  self.containerBox)
        self.cmdCloseShutter = QPushButton('Close', self.containerBox)
        self.lblShutter.setAlignment(Qt.AlignCenter)

        #
        # connect signals/slots
        #
        self.connect(self.cmdOpenShutter, SIGNAL('clicked()'), self.cmdOpenShutterClicked)
        self.connect(self.cmdCloseShutter, SIGNAL('clicked()'), self.cmdCloseShutterClicked)

        #
        # configuration
        #
        self.cmdOpenShutter.setEnabled(False)
        self.cmdCloseShutter.setEnabled(False)


    def updateGUI(self):
        self.shutter = self.getHardwareObject(self['mnemonic'])
        
        if self.shutter is not None:
            self.shutterStateChanged(self.shutter.getShutterState(), self.shutter.getAutomaticModeTimeLeft())
                
            self.connect(self.shutter, PYSIGNAL('shutterStateChanged'), self.shutterStateChanged)
        else:
            self.cmdOpenShutter.setEnabled(False)
            self.cmdCloseShutter.setEnabled(False)


    def shutterStateChanged(self, state, automaticModeTimeLeft):
        if state == 'running':
            state = 'automatic'
        self.lblShutter.setText('<b>%s</b>' % state)
        self.lblShutter.setPaletteBackgroundColor(QColor(FrontendBrick.shutterState[state]))

        if state == 'opened' or state == 'automatic':
            self.cmdCloseShutter.setEnabled(True)
            self.cmdOpenShutter.setText('Start Auto')
            self.cmdOpenShutter.setEnabled(True)
            if state == 'automatic':
                try:
                    self.lblShutter.setText(str(self.lblShutter.text()) + '<br><nobr>%dh%dm left</nobr>' % (int(automaticModeTimeLeft/3600), int(automaticModeTimeLeft % 3600 / 60)))
                    self.cmdOpenShutter.setText('Stop Auto')
                except:
                    pass
        elif state == 'closed':
            self.cmdOpenShutter.setText('Open')
            self.cmdCloseShutter.setEnabled(False)
            self.cmdOpenShutter.setEnabled(True)
        else:
            self.cmdCloseShutter.setEnabled(False)
            self.cmdOpenShutter.setEnabled(False)

            
    def cmdOpenShutterClicked(self):
        state = self.shutter.getShutterState()
        if state == "running" :
            self.shutter.manualShutter()
        else:
            self.shutter.openShutter()

        
    def cmdCloseShutterClicked(self):
        self.shutter.closeShutter()
        

    def setMnemonic(self, mne):
        self.getProperty('mnemonic').setValue(mne)
        self.updateGUI()


    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            self.updateGUI()
        else:
            SynopticBrick.SynopticBrick.propertyChanged.im_func(self, propertyName, oldValue, newValue)
