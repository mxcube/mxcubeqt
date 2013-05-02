'''
Shutter brick

[Description]

The Shutter brick is a general purpose brick that allows to control any kind of shutters

[Properties]

mnemonic - string - name of a Shutter Hardware Object (or compatible)
iconFile - file - path to a synoptic icon file, to be displayed on top of the brick
showSynoptic - boolean - display synoptic icon or not
title - string - text to be displayed on top of the brick
showTitle - boolean - display title or not
alignment - (top, bottom, center) - vertical alignment of the brick
hint - string - tooltip message when user lets the mouse cursor over the brick for a while

[Signals]

synopticClicked - () - emitted when synoptic icon is clicked

[Comments]

The Shutter brick displays opened/closed state for the given Shutter
Hardware Object. User can also open or close the shutter.
'''

import logging

from qt import *

import SynopticBrick


__category__ = 'Synoptic'


# Tango test version

class ShutterBrick(SynopticBrick.SynopticBrick):


    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.im_func(self, *args)

        self.addProperty('mnemonic', 'string')
        self.shutter = None

        #
        # GUI elements
        #
        self.lblShutter = QLabel('shutter', self.containerBox)
        self.cmdOpenCloseShutter = QPushButton('', self.containerBox)
        self.lblShutter.setAlignment(Qt.AlignCenter)

        #
        # connect signals/slots
        #
        self.connect(self.cmdOpenCloseShutter, SIGNAL('clicked()'), self.cmdOpenCloseShutterClicked)

        #
        # configuration
        #
        self.cmdOpenCloseShutter.setEnabled(False)

        # TANGO by default.
        self.selectTacoTango("TANGO")

    def selectTacoTango(self, tt):
        if tt=="TACO":
            self.ds_type = "TACO"
            self.shutterState = {
                'unknown'   : 'gray',
                'closed'    : '#ff00ff',
                'opened'    : '#00ff00',
                'moving'    : '#663300',
                'automatic' : '#009900',
                'fault'     : '#990000',
                'disabled'  : '#ec3cdd',
                'error'     : '#990000'
            }
        elif tt=="TANGO":
            self.ds_type = "TANGO"
            self.shutterState = {
                'ON'       : 'WHITE',
                'OFF'      : '#012345',
                'CLOSED'   : '#FF00FF',
                'OPEN'     : '#00FF00',
                'INSERT'   : '#412345',
                'EXTRACT'  : '#512345',
                'MOVING'   : '#663300',
                'STANDBY'  : '#009900',
                'FAULT'    : '#990000',
                'INIT'     : '#990000',
                'RUNNING'  : '#990000',
                'ALARM'    : '#990000',
                'DISABLED' : '#EC3CDD',
                'UNKNOWN'  : 'GRAY',
                'FAULT'    : '#FF0000',
            }
        else:
            print "ShutterBrick.py : Error selecting taco or tango shutter ds type."

    def updateGUI(self):
        self.shutter = self.getHardwareObject(self['mnemonic'])

        if self.shutter is not None:
            if self.isRunning():
                self.setEnabled(True)

            # Get DS name and DS type (taco or tango)
            dsname = self.shutter.getProperty("taconame")
            if dsname is None:
                dsname = self.shutter.getProperty("tangoname")
                if dsname is not None:
                    self.selectTacoTango("TANGO")
                    logging.getLogger("ShutterBrick").info('ds tango name = %s', dsname)
            else:
                self.selectTacoTango("TACO")
                logging.getLogger("ShutterBrick").info('ds taco name = %s', dsname)

            self.shutterStateChanged(self.shutter.getShutterState())

            self.connect(self.shutter, PYSIGNAL('shutterStateChanged'), self.shutterStateChanged)
        else:
            self.cmdOpenCloseShutter.setEnabled(False)


    def shutterStateChanged(self, state):
        logging.getLogger("ShutterBrick").info("shutterStateChanged(%s) color : %s",state ,self.shutterState[state])

        # shutterState used only here:
        self.lblShutter.setPaletteBackgroundColor(QColor(self.shutterState[state]))
        self.lblShutter.setText('<b>%s</b>' % state)

        if self.ds_type == "TANGO":
            if state == 'OPEN':
                self.cmdOpenCloseShutter.setText('Open')
                self.cmdOpenCloseShutter.setEnabled(True)
            elif state == 'CLOSED':
                self.cmdOpenCloseShutter.setText('Closed')
                self.cmdOpenCloseShutter.setEnabled(True)
            else:
                self.cmdOpenCloseShutter.setEnabled(False)
        elif self.ds_type == "TACO":
            if state == 'opened' or state == 'automatic':
                self.cmdOpenCloseShutter.setText('Close')
                self.cmdOpenCloseShutter.setEnabled(True)
            elif state == 'closed':
                self.cmdOpenCloseShutter.setText('Open')
                self.cmdOpenCloseShutter.setEnabled(True)
            else:
                self.cmdOpenCloseShutter.setEnabled(False)
        else:
            logging.getLogger().error('%s : No such ds_type : %s', self.name(), self.ds_type)

    def cmdOpenCloseShutterClicked(self):
        if self.cmdOpenCloseShutter.text() == 'Open':
            self.shutter.openShutter()
        else:
            self.shutter.closeShutter()


    def setMnemonic(self, mne):
        self.getProperty('mnemonic').setValue(mne)
        self.updateGUI()


    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            self.updateGUI()
        else:
            SynopticBrick.SynopticBrick.propertyChanged.im_func(self, propertyName, oldValue, newValue)


