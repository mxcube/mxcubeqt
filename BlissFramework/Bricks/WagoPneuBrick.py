from qt import *

import SynopticBrick


__category__ = 'Synoptic'


class WagoPneuBrick(SynopticBrick.SynopticBrick):
    wagoStates = {
        'out': '#ff00ff',
        'in': '#00ff00',
        'unknown': '#ff0000',
        }
    
    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.__func__(self, *args)
        
        self.addProperty('mnemonic', 'string')
        self.addProperty('allow_control', 'boolean')
        self.wagopneu      = None
        self.allow_control = False

        self.defineSlot('allowControl',())

        #
        # GUI elements
        #
        self.lblWago      = QLabel('?', self.containerBox)
        self.cmdOpenClose = QPushButton('', self.containerBox)
        self.lblWago.setAlignment(Qt.AlignCenter)

        self.lblWago.setMinimumWidth( self.fontMetrics().width("1234567890"))
        #
        # connect signals/slots
        #
        self.connect(self.cmdOpenClose, SIGNAL('clicked()'), self.cmdOpenCloseClicked)

        #
        # configuration
        #
        self.setEnabled(False)
            

    def updateGUI(self):
        self.wagopneu = self.getHardwareObject(self['mnemonic'])
        
        if self.wagopneu is not None:
            if self.isRunning():
                self.setEnabled(True)
                
            self.stateChanged(self.wagopneu.getWagoState())
                
            self.connect(self.wagopneu, PYSIGNAL('wagoStateChanged'), self.stateChanged)
        else:
            self.setEnabled(False)

        if self.allow_control:
            self.cmdOpenClose.show()
        else:
            self.cmdOpenClose.hide()


    def allowControl(self,state):
        self['allow_control']=state


    def stateChanged(self, state):
        self.lblWago.setText('<b>%s</b>' % state)
        self.lblWago.setPaletteBackgroundColor(QColor(WagoPneuBrick.wagoStates[state]))

        if state == 'in':
            self.cmdOpenClose.setText('Set Out')
        elif state == 'out':
            self.cmdOpenClose.setText('Set In')
           
            
    def cmdOpenCloseClicked(self):
        if self.cmdOpenClose.text() == 'Set In':
            self.wagopneu.wagoIn()
        else:
            self.wagopneu.wagoOut()
        
        
    def run(self):
        self.updateGUI()

        
    def stop(self):
        self.setEnabled(False)
        

    def setMnemonic(self, mne):
        self.getProperty('mnemonic').setValue(mne)
        self.updateGUI()

                
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            self.updateGUI()
        elif propertyName == 'allow_control':
            self.allow_control = newValue
            self.updateGUI()
        else:
            SynopticBrick.SynopticBrick.propertyChanged.__func__(self, propertyName, oldValue, newValue)









