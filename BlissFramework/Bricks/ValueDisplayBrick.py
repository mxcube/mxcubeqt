import logging
import types

from qt import *

import SynopticBrick

__category__ = 'Synoptic'

class ValueDisplayBrick(SynopticBrick.SynopticBrick):    
    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.im_func(self, *args)

        self.addProperty('formatString', 'formatString', '+##.####')
        self.addProperty('mnemonic', 'string')
        self.addProperty('unit', 'string', '')
        self.addProperty('valueLabel', 'string', '')
        self.addProperty('displayType', 'combo', ('string', 'LCD (number)'), 'LCD (number)')
        self.tacoHardwareObject = None
        self.value = None

        self.box = QHBox(self.containerBox)
        self.lblLabel = QLabel(self.box)
        self.lblValue = QLabel(self.box)
        self.lblValue.hide()
        self.lcdValue = QLCDNumber(self.box)
        self.lcdValue.setSegmentStyle( QLCDNumber.Flat )
        self.lblUnit = QLabel(self.box)

        self.box.setSpacing(5)
        self.lblValue.setAlignment(Qt.AlignRight)
        self.lblUnit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                 

    def setValue(self, value=None):
        if value is None:
            value = self.value
        else:
            self.value = value
            
        if value is None:
            svalue = '-'
        else:
            if type(value) == types.IntType or type(value) == types.FloatType:
                svalue = '%s' % str(self['formatString'] % value)
            elif type(value) == types.StringType:
                svalue = str(value)
            else:
				svalue = '-'
				logging.getLogger().error('%s: cannot display value, unknown type %s', str(self.name()), type(value))
  
        self.lcdValue.display(svalue)
        self.lblValue.setText('<nobr><font face="courier">%s</font></nobr>' % svalue)
        self.emit(PYSIGNAL("valueChanged"),(svalue,))

       

    def setMnemonic(self, mne):
        self['mnemonic'] = mne


    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.tacoHardwareObject is not None:
                self.disconnect(self.tacoHardwareObject, PYSIGNAL('valueChanged'), self.setValue)
                self.disconnect(self.tacoHardwareObject, PYSIGNAL('timeout'), self.setValue)
                
            self.tacoHardwareObject = self.getHardwareObject(newValue)
            self.value = None

            if self.tacoHardwareObject is not None:
                self.connect(self.tacoHardwareObject, PYSIGNAL('valueChanged'), self.setValue)
                self.connect(self.tacoHardwareObject, PYSIGNAL('timeout'), self.setValue)
            else:
                self.setValue(None)
        elif propertyName == 'displayType':
            if newValue == 'LCD (number)':
                self.lblValue.hide()
                self.lcdValue.show()
            else:
                self.lblValue.show()
                self.lcdValue.hide()
        elif propertyName == 'formatString':
            length = self.getProperty('formatString').getFormatLength()
            
            self.lblValue.setFixedWidth(self.fontMetrics().width('#'*length))
            self.lcdValue.setNumDigits(length)
            self.setValue()
        elif propertyName == 'unit':
            self.lblUnit.setText(newValue)

            if len(newValue) == 0:
                self.lblUnit.hide()
            else:
                self.lblUnit.show()
        elif propertyName == 'valueLabel':
            self.lblLabel.setText(newValue)
        else:
            SynopticBrick.SynopticBrick.propertyChanged.im_func(self, propertyName, oldValue, newValue)
