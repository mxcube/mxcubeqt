from qt import *
from qttable import QTable
from qttable import QTableItem
from qttable import QCheckTableItem
from qttable import QComboTableItem

import types
import weakref
import logging

import PropertyBag
from BlissFramework import Icons


class ConfigurationTable(QTable):
    def __init__(self, parent):
        QTable.__init__(self, parent, 'configurationTable')

        self.setFrameShape(QTable.ToolBarPanel)
        self.setFrameShadow(QTable.Sunken)
        self.setResizePolicy(QTable.Default)
        self.setLeftMargin(0)
        self.setNumCols(3)
        self.setSelectionMode(QTable.NoSelection)
        self.horizontalHeader().setLabel(0, self.trUtf8('Properties'))
        self.horizontalHeader().setLabel(1, self.trUtf8('Values'))
        self.horizontalHeader().setLabel(2, self.trUtf8(''))
        self.horizontalHeader().setResizeEnabled(False)
        self.horizontalHeader().setClickEnabled(False)
        self.horizontalHeader().setMovingEnabled(False)
 
        self.setColumnReadOnly(0, 1) # column 0 is read-only
        self.setColumnReadOnly(0, 2)
        self.setColumnStretchable(0, 0)
        self.setColumnStretchable(1, 1)
        self.setColumnStretchable(2, 0)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.propertyBag = None

        QObject.connect(self, SIGNAL('valueChanged(int, int)'), self.OnValueChanged)

        
    def clear(self):
        for i in range(self.numRows()):
            self.removeRow(i)
        self.setNumRows(0)
        self.propertyBag = None

        
    def setPropertyBag(self, propertyBag, showHidden=False):
        self.clear()           

        if self.propertyBag is not None:
            for property in self.propertyBag:
                property._editor = None

        self.propertyBag = propertyBag

        if self.propertyBag is not None:
            self.setNumRows(len(self.propertyBag))
           
            #
            # add properties
            #
            i = 0
            for property in self.propertyBag:
                property._editor = weakref.ref(self)
                
                if not showHidden and property.hidden:
                    continue
                
                self.setText(i, 0, property.getName())
                
                self.blockSignals(True) # block signals to prevent valueChanged events
                self.setWidgetFromProperty(i, property)
                self.blockSignals(False)
                
                validationPanel = ValidationTableItem(self)
                self.setItem(i, 2, validationPanel)
                self.connect(validationPanel.OK, SIGNAL('clicked()'), self.OnValidateClick)
                self.connect(validationPanel.Cancel, SIGNAL('clicked()'), self.OnInvalidateClick)
                self.connect(validationPanel.Reset, SIGNAL('clicked()'), self.OnResetClick)
                                
                i += 1

            self.setNumRows(i)
            
        #
        # finish layout
        #
        self.adjustColumn(0)
        self.adjustColumn(1)
        self.adjustColumn(2)
        
        
    def setWidgetFromProperty(self, row, property):
        if property.getType() == 'boolean':
            newPropertyItem = QCheckTableItem(self, '')
            self.setItem(row, 1, newPropertyItem)

            if property.getUserValue():
                self.item(row, 1).setChecked(1)
            else:
                self.item(row, 1).setChecked(0)
        elif property.getType() == 'combo':
            choicesList = QStringList()
            choices = property.getChoices()
            for choice in choices:
                choicesList.append(choice)
            newPropertyItem = QComboTableItem(self, choicesList, 0)
            self.setItem(row, 1, newPropertyItem)

            self.item(row, 1).setCurrentItem(str(property.getUserValue()))
        elif property.getType() == 'file':
            newPropertyItem = FileTableItem(self, property.getUserValue(), property.getFilter())
            self.setItem(row, 1, newPropertyItem)
        elif property.getType() == 'color':
            newPropertyItem = ColorTableItem(self, property.getUserValue())
            self.setItem(row, 1, newPropertyItem)
        else:                                           
            if property.getUserValue() is None:
                self.setText(row, 1, '')
            else:
                self.setText(row, 1, str(property.getUserValue()))
                

    def OnValueChanged(self, row, col):
        property = self.propertyBag.getProperty(str(self.text(row, 0)))
        
        oldValue = property.getUserValue()
        
        if property.getType() == 'boolean':
            property.setValue(self.item(row, 1).isChecked())
        elif property.getType() == 'combo':
            property.setValue(self.item(row, 1).currentText())
        elif property.getType() == 'file':
            property.setValue(self.item(row, 1).filename)
        elif property.getType() == 'color':
            property.setValue(self.item(row,1).color)
        else: 
            try:
                property.setValue(str(self.text(row, 1)))
            except:
                logging.getLogger().error('Cannot assign value to property')

            if property.getUserValue() is None:
                self.setText(row, 1, '')
            else:
                self.setText(row, 1, str(property.getUserValue()))
            
        if not oldValue == property.getUserValue():
            self.emit(PYSIGNAL('propertyChanged'), (property.getName(), oldValue, property.getUserValue(), ))

   
    def OnValidateClick(self):
        self.endEdit(self.currentRow(), 1, 1, 0) #current row, col 1, accept = 1, replace = 0
        self.activateNextCell()
        

    def OnInvalidateClick(self):
        self.endEdit(self.currentRow(), 1, 0, 0) #current row, col 1, accept = 0, replace = 0


    def OnResetClick(self):
        self.endEdit(self.currentRow(), 1, 0, 0)

        property = self.propertyBag.getProperty(str(self.text(self.currentRow(), 0)))

        defaultValue = property.getDefaultValue()
        if not defaultValue == None:
            property.setValue(defaultValue)
        
        self.setWidgetFromProperty(self.currentRow(), property)
            

    def beginEdit(self, row, col, replace):
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(1)
            
        return QTable.beginEdit(self, row, col, replace)

        
    def endEdit(self, row, col, accept, replace):
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(0)

            if accept:
                property = self.propertyBag.getProperty(str(self.text(row, 0)))

                oldValue = property.getUserValue()
            
                if property.getType() == 'boolean':
                    property.setValue(self.item(row, 1).isChecked())
                elif property.getType() == 'combo':
                    property.setValue(self.item(row, 1).currentText())
                else: 
                    try:
                        property.setValue(str(self.text(row, 1)))
                    except:
                        logging.getLogger().error('Cannot assign value to property')

                    if property.getUserValue() is None:
                        self.setText(row, 1, '')
                    else:
                        self.setText(row, 1, str(property.getUserValue()))

                if not oldValue == property.getUserValue():
                    self.emit(PYSIGNAL('propertyChanged'), (property.getName(), oldValue, property.getUserValue(), ))

        return QTable.endEdit(self, row, col, accept, replace)



class ValidationTableItem(QTableItem):
    def __init__(self, parent):
        QTableItem.__init__(self, parent, QTableItem.Always, '')

        self.OK = None
        self.Cancel = None
        self.Reset = None


    def createEditor(self):
        validationPanel = QHBox(self.table().viewport(), 'validationPanel')

        self.OK = QToolButton(validationPanel)
        self.OK.setAutoRaise(True)
        self.OK.setIconSet(QIconSet(Icons.load('button_ok_small'))) #QPixmap(Icons.tinyOK)))
        self.Cancel = QToolButton(validationPanel)
        self.Cancel.setAutoRaise(True)
        self.Cancel.setIconSet(QIconSet(Icons.load('button_cancel_small'))) #QPixmap(Icons.tinyCancel)))
        self.Reset = QToolButton(validationPanel)
        self.Reset.setIconSet(QIconSet(Icons.load('button_default_small'))) #QPixmap(Icons.defaultXPM)))
        self.Reset.setAutoRaise(True)
        self.setEnabled(False)

        return validationPanel


    def setEnabled(self, enabled):
        if enabled:
            self.Reset.setEnabled(True)
            self.OK.setEnabled(True)
            self.Cancel.setEnabled(True)
        else:
            self.Reset.setEnabled(False)
            self.OK.setEnabled(False)
            self.Cancel.setEnabled(False)
       

class FileTableItem(QTableItem):
    def __init__(self, parent, filename, filter):
        QTableItem.__init__(self, parent, QTableItem.Always, '')

        self.filter = filter
        self.cmdBrowse = None
        
        self.setFilename(filename)
            

    def setFilename(self, filename):
        self.filename = str(filename)

        if self.cmdBrowse is not None:
            QToolTip.add(self.cmdBrowse, self.filename)

        self.table().emit(SIGNAL('valueChanged(int, int)'), (self.row(), self.col()))
        
        
    def createEditor(self):
        if self.cmdBrowse is None:
            self.cmdBrowse = QPushButton('Browse', self.table().viewport())
            QToolTip.add(self.cmdBrowse, self.filename)

            QObject.connect(self.cmdBrowse, SIGNAL('clicked()'), self.browseClicked)
                    
        return self.cmdBrowse

        
    def browseClicked(self):
        import os, os.path
        newFilename = QFileDialog.getOpenFileName(os.path.dirname(self.filename) or os.getcwd(), self.filter, None, '', 'Select a file')
        
        if len(newFilename) > 0:
            self.setFilename(newFilename)
            

class ColorTableItem(QTableItem):
    def __init__(self, parent, color):
        QTableItem.__init__(self, parent, QTableItem.Always, '')

        self.cmdChangeColor = None
        self.setColor(color)
        

    def setColor(self, color):
        self.qtcolor = self.table().colorGroup().button()
         
        try:
          rgb = color.rgb()
        except:
          try:
            self.qtcolor = QColor(color)
          except:
            self.qtcolor = self.table().colorGroup().button()
            self.color = self.qtcolor.rgb()
          else:
            self.color = self.qtcolor.rgb()
        else:
          self.qtcolor=color
          self.color=rgb

        if self.cmdChangeColor is not None:
            self.cmdChangeColor.setPaletteBackgroundColor(self.qtcolor)

        self.table().emit(SIGNAL('valueChanged(int, int)'), (self.row(), self.col()))


    def createEditor(self):
        if self.cmdChangeColor is None:
            hbox = QHBox(self.table().viewport())
            self.cmdChangeColor = QPushButton('Color...', hbox)
            self.cmdResetColor = QPushButton('reset', hbox)

            QObject.connect(self.cmdChangeColor, SIGNAL('clicked()'), self.cmdChangeColorClicked)
            QObject.connect(self.cmdResetColor, SIGNAL('clicked()'), self.cmdResetColorClicked)

        return hbox


    def cmdChangeColorClicked(self):
        newColor = QColorDialog.getColor(self.qtcolor or QColor("white"), None, 'Select a color')

        if newColor.isValid():
            self.setColor(newColor)
        

    def cmdResetColorClicked(self):
        self.setColor(None)
        
        
    
class Dialog(QDialog):
    def __init__(self, propertyBag):
        QDialog.__init__(self, None, None, Qt.WDestructiveClose)
        
        #
        # create GUI
        #
        self.setCaption("Configuration Editor")
        self.propertiesTable = ConfigurationTable(self)
        self.propertiesTable.setPropertyBag(propertyBag)
        cmdClose = QPushButton('Close', self)
        
        #
        # connect signals/slots
        #
        self.connect(self.propertiesTable, PYSIGNAL('propertyChanged'), PYSIGNAL('propertyChanged'))
        self.connect(cmdClose, SIGNAL('clicked()'), self.close)

        #
        # layout
        #
        QVBoxLayout(self, 0, 0)
        self.layout().setResizeMode(QLayout.FreeResize)
        self.layout().addWidget(self.propertiesTable)
        self.layout().addWidget(cmdClose)
        
        self.setFixedHeight(500)
       












