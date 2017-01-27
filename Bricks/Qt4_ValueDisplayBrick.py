"""
Qt4_ValueDisplayBrick
"""
import os
import logging
import types

from QtImport import *

#from BlissFramework import Qt4_Icons
#from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'SOLEIL'

class Qt4_ValueDisplayBrick(BlissWidget):    

    def __init__(self, *args):
        
        BlissWidget.__init__(self,*args)

        # Properties ---------------------------------------------------------- 
        self.addProperty('formatString', 'formatString', '+##.####')
        self.addProperty('mnemonic', 'string')
        self.addProperty('unit', 'string', '')
        self.addProperty('valueLabel', 'string', '')
        self.addProperty('displayType', 'combo', ('string', 'LCD (number)'), 'LCD (number)')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self.tacoHardwareObject = None
        # Internal values -----------------------------------------------------
        self.value = None
        
        # Graphic elements ----------------------------------------------------
        
        self._widget = loadUi(os.path.join(os.path.dirname(__file__),"widgets/ui_files/Qt4_value_display_widget.ui"))
        self._widget.lblValue.hide()
        
        # Layout --------------------------------------------------------------
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0) 
        
        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ----------------------------------------
    
    def setValue(self, value=None, *args):
        logging.getLogger().debug(" ValueDisplayBrick. Valuechanged. it is: %s" % value)
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
  
        self._widget.lcdValue.display(svalue)
        self._widget.lblValue.setText('<nobr><font face="courier">%s</font></nobr>' % svalue)
        # self.valueChanged.emit(svalue))
                 
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.tacoHardwareObject is not None:
                self.disconnect(self.tacoHardwareObject, 'valueChanged', self.setValue)
                self.disconnect(self.tacoHardwareObject, 'timeout', self.setValue)
                
            self.tacoHardwareObject = self.getHardwareObject(newValue)
            self.value = None

            if self.tacoHardwareObject is not None:
                self.connect(self.tacoHardwareObject, 'valueChanged', self.setValue)
                self.connect(self.tacoHardwareObject, 'timeout', self.setValue)
                self.setValue( self.tacoHardwareObject.getValue() )
            else:
                self.setValue(None)
        elif propertyName == 'displayType':
            if newValue == 'LCD (number)':
                self._widget.lblValue.hide()
                self._widget.lcdValue.show()
            else:
                self._widget.lblValue.show()
                self._widget.lcdValue.hide()
        elif propertyName == 'formatString':
            length = self.getProperty('formatString').getFormatLength()
            
            self._widget.lblValue.setFixedWidth(self.fontMetrics().width('#'*length))
            self._widget.lcdValue.setNumDigits(length)
            self.setValue()
        elif propertyName == 'unit':
            self._widget.lblUnit.setText(newValue)

            if len(newValue) == 0:
                self._widget.lblUnit.hide()
            else:
                self._widget.lblUnit.show()
        elif propertyName == 'valueLabel':
            self._widget.lblLabel.setText(newValue)
            
        else :
            BlissWidget.propertyChanged.im_func(self, propertyName, oldValue, newValue)

def test_brick(brick):
    pass
