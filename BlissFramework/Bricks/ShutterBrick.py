from qt import *

import SynopticBrick


__category__ = 'Synoptic'


class ShutterBrick(SynopticBrick.SynopticBrick):
    shutterState = {
        'unknown': 'gray',
        'closed': '#ffffef',
        'opened': '#00ff00',
        'moving': '#663300',
        'automatic': '#009900',
        'fault': '#990000',
        'disabled': '#ff00ff',
        'error': '#990000'
        }

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


    def updateGUI(self):
	self.shutter = self.getHardwareObject(self['mnemonic'])

        if self.shutter is not None:
	    if self.isRunning():
                self.setEnabled(True)

            self.shutterStateChanged(self.shutter.getShutterState())

            self.connect(self.shutter, PYSIGNAL('shutterStateChanged'), self.shutterStateChanged)
        else:
            self.cmdOpenCloseShutter.setEnabled(False)


    def shutterStateChanged(self, state):
        self.lblShutter.setPaletteBackgroundColor(QColor(ShutterBrick.shutterState[state]))
        self.lblShutter.setText('<b>%s</b>' % state)

        if state == 'opened' or state == 'automatic':
            self.cmdOpenCloseShutter.setText('Close')
            self.cmdOpenCloseShutter.setEnabled(True)
        elif state == 'closed':
            self.cmdOpenCloseShutter.setText('Open')
            self.cmdOpenCloseShutter.setEnabled(True)
        else:
            self.cmdOpenCloseShutter.setEnabled(False)

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
