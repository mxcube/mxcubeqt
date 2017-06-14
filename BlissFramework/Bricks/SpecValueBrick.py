"""
Spec Value Brick

[Description]

This brick displays values from Spec (integer, float, motors ...)

[Properties]

file - string - XML file where to find object to display

title - string - string describing value to display

type - combo - choice of type to display
               (string, integer, float, onoff, offon, motor)

id - string - HWObj variable name (Spec Variable) or device role (Motor)

orientation - combo - left-right or up-down representation
                      (horizontal, vertical)
                      
title size - int - fixed size of the title label in characters
                   0 = title size
                   
value size - int - fixed size of the vaue label in characters
                   0 = title size
                   
[Signals]

[Slots]

[Comments]

"""

import qt
import types

from BlissFramework.BaseComponents import BlissWidget

__category__ = "Spec"

class SpecValueBrick(BlissWidget):
    colorState = {
        'NOTINITIALIZED': 'gray', 
        'UNUSABLE': 'red',
        'READY': '#00ee00',
        'MOVESTARTED': 'lightgray',
        'MOVING': 'yellow',
        'ONLIMIT': 'orange',
        'On': '#00ee00', 
        'Off': '#ff5555',
        }
    nameState = [
        'NOTINITIALIZED', 
        'UNUSABLE',
        'READY',
        'MOVESTARTED',
        'MOVING',
        'ONLIMIT',
        ]
          
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        """
        variables
        """
        self.firstTime = True
        self.layout1 = None
        self.layout2 = None
        self.displayWidget = None
        self.valueSize = 0
        self.titleSize = 0
        
        """
        properties
        """
        self.addProperty('file', 'string')
        self.hwFile = None
        self.addProperty('title', 'string')
        self.title = None
        self.addProperty('type', 'combo',
                    ("string", "integer", "float", "onoff", "offon", "motor"),
                    "string")
        self.varType = None
        self.addProperty('id', 'string')
        self.hwId = None
        self.nameId = None
        self.addProperty('orientation', 'combo', ("horizontal", "vertical"),
                         "horizontal")
        self.orientation = "horizontal"
        self.addProperty('title size', 'integer', 0)
        self.titleSize = 0
        self.addProperty('value size', 'integer', 0)
        self.valueSize = 0
        
    def buildInterface(self):
        if self.displayWidget is not None:
            self.displayWidget.close(true)

        if self.orientation is not None:
            if self.orientation == "horizontal":
                self.layout1 = qt.QVBoxLayout(self)
                #self.layout1.setMargin(5)
                self.layout2 = qt.QHBoxLayout(self.layout1)
                orient = QubValue.Horizontal
            else:
                self.layout1 = qt.QHBoxLayout(self)
                #self.layout1.setMargin(5)
                self.layout2 = qt.QVBoxLayout(self.layout1)
                orient = QubValue.Vertical

        self.displayWidget = QubValue(self, titleType=QubValue.Label,
                                      valueType=QubValue.Label,
                                      orientation=orient)
                                      
        if self.valueSize > 0:
            strval = "l"
            strval = strval+"p"*(self.valueSize-1)
            self.displayWidget.setValue(strval)
            width = self.displayWidget.valueSizeHint().width()
            self.displayWidget.setValueMaximumWidth(width)
            self.displayWidget.setValueMinimumWidth(width)
            self.displayWidget.setValue("")
                                      
        if self.titleSize > 0:
            strval = "l"
            strval = strval+"p"*(self.titleSize-1)
            self.displayWidget.setTitle(strval)
            width = self.displayWidget.titleSizeHint().width()
            self.displayWidget.setTitleMaximumWidth(width)
            self.displayWidget.setTitleMinimumWidth(width)
            self.displayWidget.setTitle("")
            
        self.layout2.addWidget(self.displayWidget)
        self.layout2.addStretch(1)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'file':
            self.hwFile = self.getHardwareObject(newValue)
        
        if propertyName == "type":
            if self.varType is not None:
                if self.varType == "motor":
                    if self.hwId is not None:
                        self.disconnect(self.hwId,
                                        qt.PYSIGNAL('positionChanged'),
                                        self.valueChanged)
                        self.disconnect(self.hwId, qt.PYSIGNAL('stateChanged'),
                                        self.stateChanged)
                else:
                    if self.hwId is not None:
                        self.disconnect(self.hwId, qt.PYSIGNAL('update'),
                                        self.valueChanged)
                    
            self.varType = newValue
            
            if self.nameId is not None and self.hwFile is not None:
                if self.varType == "motor":
                    self.hwId = self.hwFile.getObjectByRole(self.nameId)
                else:
                    self.hwId = self.hwFile.getChannelObject(self.nameId)
                    
        if propertyName == "id":
            if self.hwId is not None:
                if self.varType is not None:
                    if self.varType == "motor":
                        self.disconnect(self.hwId,
                                        qt.PYSIGNAL('positionChanged'),
                                        self.valueChanged)
                        self.disconnect(self.hwId, qt.PYSIGNAL('stateChanged'),
                                        self.stateChanged)
                    else:
                        self.disconnect(self.hwId, qt.PYSIGNAL('update'),
                                        self.valueChanged)
                
            self.nameId = newValue
                
            if self.varType is not None and self.hwFile is not None:                        
                if self.varType == "motor":
                    self.hwId = self.hwFile.getObjectByRole(self.nameId)
                else:
                    self.hwId = self.hwFile.getChannelObject(self.nameId)
                   
        if propertyName == "title":
            self.title = newValue

        if propertyName == "orientation":
            self.orientation = newValue

        if propertyName == "value size":
            self.valueSize = newValue

        if propertyName == "title size":
            self.titleSize = newValue
            
        if not self.firstTime:
            self.configValue()
            
    def run(self):
        if self.firstTime:
            self.configValue()
            
        self.firstTime = False                                

    def configValue(self):
        """
        build interface
        """
        if self.orientation is not None:
            self.buildInterface()
            
        """
        title
        """
        if self.title is not None and self.displayWidget is not None:
            title = self.title.replace(" ", "&nbsp;")
            title = "<B>%s<B>"%title
            self.displayWidget.setTitle(title)
        
        """
        connect
        """
        if self.hwId is not None and self.varType is not None:
            if self.varType == "motor":
                self.connect(self.hwId, qt.PYSIGNAL('positionChanged'),
                             self.valueChanged)
                self.connect(self.hwId, qt.PYSIGNAL('stateChanged'),
                             self.stateChanged)
            else:
                self.connect(self.hwId, qt.PYSIGNAL('update'),
                             self.valueChanged)
                             
    def valueChanged(self, value):
        # Here a workaround in case of SPEC associative array use
        # in that case, a dictionnary is returned with a unique key
        #L.claustre 01-08-2007
        val = value
        # mo longer needed, Matias has change the framework to
        # to manage associative array, from the xml file use the
        # syntax MYARRAY/avalue to access the SPEC variable MYARRAY["avalue"].
        #if type(value) is  types.DictionaryType:
	#    val = value[value.keys()[0]]
        #    if type(val) is  types.DictionaryType:
        #        val = val[val.keys()[0]]
        if self.varType in ["motor", "float"]:
            strval = "%.4f"%float(val)
        if self.varType == "integer":
            strval = "%d"%int(val)
        if self.varType == "string":
            strval = val
        if self.varType == "onoff":
            if val == '1':
                strval = "Off"
            else:
                strval = "On"
        if self.varType == "offon":
            if val == '1':
                strval = "On"
            else:
                strval = "Off"
        
        if self.displayWidget is not None:
            self.displayWidget.setValue(strval)
            
        if self.varType in ["onoff", "offon"]:
            qcolor = qt.QColor(SpecValueBrick.colorState[strval])
            if self.displayWidget is not None:
                self.displayWidget.setValueBackgroundColor(qcolor)
            
    
    def stateChanged(self, index):
        state = SpecValueBrick.nameState[index]      
        qcolor = qt.QColor(SpecValueBrick.colorState[state])
        if self.displayWidget is not None:
            self.displayWidget.setValueBackgroundColor(qcolor)

class QubValue(qt.QWidget):

    (Horizontal, Vertical) = (0, 1)
    (Combo, Text, Label) = (0, 1, 2)
    
    def __init__(self, parent, \
                 titleType=Label, valueType=Label, orientation=Horizontal):
        qt.QWidget.__init__(self, parent)
        
        self.__valueList = []
        self.__titleList = []
        
        self.orientation = orientation
        self.titleType = titleType
        self.valueType = valueType
        
        if self.orientation == QubValue.Horizontal:
            self.layout = qt.QHBoxLayout(self)
        else:
            self.layout = qt.QVBoxLayout(self)
        
        if self.titleType == QubValue.Combo:
            self.titleWidget = qt.QComboBox(self)
            self.connect(self.titleWidget, qt.SIGNAL("activated(int)"),
                         self.__activatedType)
        else:   
            self.titleWidget = qt.QLabel(self)
        self.layout.addWidget(self.titleWidget)
        
        self.layout.addSpacing(5)
        
        if self.valueType == QubValue.Combo:
            self.valueWidget = qt.QComboBox(self)
            self.connect(self.valueWidget, qt.SIGNAL("activated(int)"),
                         self.__activatedValue)
        elif self.valueType == QubValue.Text:
            self.valueWidget = qt.QLineEdit(self)
            self.connect(self.valueWidget, qt.SIGNAL("returnPressed()"),
                         self.__returnPressed)
        else:
            self.valueWidget = qt.QLabel(self)            
            self.valueWidget.setFrameShape(qt.QFrame.Box)
            self.valueWidget.setFrameShadow(qt.QFrame.Plain)
        self.layout.addWidget(self.valueWidget)
            
    def __returnPressed(self):
        self.emit(qt.PYSIGNAL("NewValue"),(self.valueWidget.text(), 0))
            
    def __activatedValue(self):
        ind = self.valueWidget.currentItem()
        text = self.valueWidget.currentText()
        self.emit(qt.PYSIGNAL("NewValue"),(text, ind))
            
    def __activatedTitle(self):
        ind = self.titleWidget.currentItem()
        text = self.titleWidget.currentText()
        self.emit(qt.PYSIGNAL("NewTitle"),(text, ind))
    
    def setComboValue(self, values):
        self.__valueList = values
        if self.valueType == QubValue.Combo:
            for value in values:
                self.valueWidget.insertItem(value)
    
    def setComboTitle(self, titles):
        self.__titleList = titles
        if self.titleType == QubValue.Combo:
            for title in titles:
                self.valueWidget.insertItem(titles)

    def setValueIndex(self, ind):
        if self.valueType == QubValue.Combo:
            self.valueWidget.setCurrentItem(ind)
                          
    def setValue(self, text):
        if self.valueType == QubValue.Combo:
            self.valueWidget.setCurrentItem(self.__valueList.index(text))
        else:
            self.valueWidget.setText(text)
        
    def setTitleIndex(self, ind):
        if self.titleType == QubValue.Combo:
            self.titleWidget.setCurrentItem(ind)
            
    def setTitle(self, text):
        if self.titleType == QubValue.Combo:
            self.titleWidget.setCurrentItem(self.__titleList.index(text))
        else:
            self.titleWidget.setText(text)
    
    def setValueMinimumWidth(self, width):
        self.valueWidget.setMinimumWidth(width)
    
    def setTitleMinimumWidth(self, width):
        self.titleWidget.setMinimumWidth(width)
    
    def setValueMaximumWidth(self, width):
        self.valueWidget.setMaximumWidth(width)
    
    def setTitleMaximumWidth(self, width):
        self.titleWidget.setMaximumWidth(width)
           
    def setValueMaximumSize(self, size):
        self.valueWidget.setMaximumSize(size)
        
    def setTitleMaximumSize(self, size):
        self.titleWidget.setMaximumSize(size)
        
    def setValueMinimumSize(self, size):
        self.valueWidget.setMinimumSize(size)
        
    def setTitleMinimumSize(self, size):
        self.titleWidget.setMinimumSize(size)
        
    def value(self):
        if self.valueType == QubValue.Combo:
            return self.valueWidget.currentText()
        else:
            return self.valueWidget.text()

    def valueIndex(self):
        if self.valueType == QubValue.Combo:
            return self.valueWidget.currentItem()
        else:
            return 0
        
    def title(self):
        if self.titleType == QubValue.Combo:
            return self.titleWidget.currentText()
        else:
            return self.titleWidget.text()

    def titleIndex(self):
        if self.titleType == QubValue.Combo:
            return self.titleWidget.currentItem()
        else:
            return 0
                    
    def valueSizeHint(self):
        return self.valueWidget.sizeHint()
        
    def titleSizeHint(self):
        return self.titleWidget.sizeHint()

    def valueBackgroundColor(self):
        return self.valueWidget.paletteBackgroungColor()
    
    def setValueBackgroundColor(self, color):
        self.valueWidget.setPaletteBackgroundColor(color)
