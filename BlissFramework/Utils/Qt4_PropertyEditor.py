#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import types
import weakref
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui

import PropertyBag
from BlissFramework import Qt4_Icons


class Qt4_ConfigurationTable(QtGui.QTableWidget):
    """
    Descript. :
    """

    def __init__(self, parent):
        """
        Descript. :
        """
        QtGui.QTableWidget.__init__(self, parent)

        self.setObjectName("configurationTable")
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(3)
        self.setSelectionMode(QtGui.QTableWidget.NoSelection)

        self.setHorizontalHeaderLabels([self.trUtf8('Properties'),  
                                        self.trUtf8('Values'), 
                                        self.trUtf8('')])
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.propertyBag = None

        self.cellChanged.connect(self.OnCellChanged)
        
    def clear(self):
        """
        Descript. :
        """
        for i in range(self.rowCount()):
            self.removeRow(i)
        self.setRowCount(0)
        self.propertyBag = None

        
    def setPropertyBag(self, propertyBag, showHidden=False):
        """
        Descript. :
        """
        self.clear()           
        if self.propertyBag is not None:
            for prop in self.propertyBag:
                prop._editor = None

        self.propertyBag = propertyBag

        if self.propertyBag is not None:
            self.setRowCount(len(self.propertyBag))
           
            i = 0
            self.setRowCount(len(self.propertyBag))
            for prop in self.propertyBag:
                prop._editor = weakref.ref(self)
                
                if not showHidden and prop.hidden:
                    continue

                tempTableItem = QtGui.QTableWidgetItem(prop.getName())
                tempTableItem.setFlags(QtCore.Qt.ItemIsEnabled)
                self.blockSignals(True) 
                self.setItem(i, 0, tempTableItem)
                self.setWidgetFromProperty(i, prop)
                self.blockSignals(False)
                
                validationPanel = ValidationTableItem(self)
                self.setCellWidget(i, 2, validationPanel)
                validationPanel.OK.clicked.connect(self.OnValidateClick)
                validationPanel.Cancel.clicked.connect(self.OnInvalidateClick)
                validationPanel.Reset.clicked.connect(self.OnResetClick)
                i += 1
            #self.setRowCount(i)
        self.resizeColumnsToContents()    
        
    def setWidgetFromProperty(self, row, prop):
        """
        Descript. :
        """
        if prop.getType() == 'boolean':
            newPropertyItem = QtGui.QTableWidgetItem(QtCore.QString(""))
            self.setItem(row, 1, newPropertyItem)
            if prop.getUserValue():
                self.item(row, 1).setCheckState(QtCore.Qt.Checked)
            else:
                self.item(row, 1).setCheckState(QtCore.Qt.Unchecked)
        elif prop.getType() == 'combo':
            choicesList = QtCore.QStringList()
            choices = prop.getChoices()
            for choice in choices:
                choicesList.append(choice)
            newPropertyItem = ComboBoxTableItem(self, row, 1, choicesList)
            newPropertyItem.setCurrentIndex(newPropertyItem.findText(prop.getUserValue()))
            self.setCellWidget(row, 1, newPropertyItem)
        elif prop.getType() == 'file':
            newPropertyItem = FileTableItem(self, row, 1, prop.getUserValue(), prop.getFilter())
            self.setCellWidget(row, 1, newPropertyItem)
        elif prop.getType() == 'color':
            newPropertyItem = ColorTableItem(self, row, 1, prop.getUserValue())
            self.setCellWidget(row, 1, newPropertyItem)
        else:                                           
            if prop.getUserValue() is None:
                tempTableItem = QtGui.QTableWidgetItem("")
            else:
                tempTableItem = QtGui.QTableWidgetItem(str(prop.getUserValue()))  
            self.setItem(row, 1, tempTableItem)

    def OnCellChanged(self, row, col):
        """
        Descript. :
        """
        col += 1

        item_property = self.propertyBag.getProperty(str(self.item(row, 0).text()))
        oldValue = item_property.getUserValue()

        if item_property.getType() == 'boolean':
            item_property.setValue(self.item(row, 1).checkState())
        elif item_property.getType() == 'combo':
            item_property.setValue(self.cellWidget(row, 1).currentText())
        elif item_property.getType() == 'file':
            item_property.setValue(self.cellWidget(row, 1).get_filename())
        elif item_property.getType() == 'color':
            item_property.setValue(self.cellWidget(row, 1).color)
        else: 
            try:
                item_property.setValue(str(self.item(row, 1).text()))
            except:
                logging.getLogger().error('Cannot assign value %s to property %s' % \
                        (str(self.item(row, 1).text()), item_property.getName()))

            if item_property.getUserValue() is None:
                self.item(row, 1).setText('')
            else:
                self.item(row, 1).setText(str(item_property.getUserValue()))

        if not oldValue == item_property.getUserValue():
            self.emit(QtCore.SIGNAL('propertyChanged'), item_property.getName(), 
                      oldValue, item_property.getUserValue())

    def OnValidateClick(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 1, 0) #current row, col 1, accept = 1, replace = 0
        self.activateNextCell()
        
    def OnInvalidateClick(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 0, 0) #current row, col 1, accept = 0, replace = 0

    def OnResetClick(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 0, 0)

        property = self.propertyBag.getProperty(str(self.text(self.currentRow(), 0)))

        defaultValue = property.getDefaultValue()
        if not defaultValue == None:
            property.setValue(defaultValue)
        
        self.setWidgetFromProperty(self.currentRow(), property)

    def beginEdit(self, row, col, replace):
        """
        Descript. :
        """
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(1)
            
        return QTable.beginEdit(self, row, col, replace)

    def endEdit(self, row, col, accept, replace):
        """
        Descript. :
        """
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(0)

            if accept:
                prop = self.propertyBag.getProperty(str(self.text(row, 0)))

                oldValue = prop.getUserValue()
            
                if prop.getType() == 'boolean':
                    prop.setValue(self.item(row, 1).isChecked())
                elif prop.getType() == 'combo':
                    prop.setValue(self.item(row, 1).currentText())
                else: 
                    try:
                        prop.setValue(str(self.text(row, 1)))
                    except:
                        logging.getLogger().error('Cannot assign value to property')

                    if prop.getUserValue() is None:
                        self.setText(row, 1, '')
                    else:
                        self.setText(row, 1, str(prop.getUserValue()))

                if not oldValue == prop.getUserValue():
                    self.emit(QtCore.SIGNAL('propertyChanged'), (property.getName(), oldValue, property.getUserValue(), ))

        return QTable.endEdit(self, row, col, accept, replace)


class ValidationTableItem(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent=None):
        """
        Descript. : parent (QTreeWidget) : Item's QTreeWidget parent.
        """

        QtGui.QWidget.__init__(self, parent)
       
        self.OK = QtGui.QToolButton(parent)
        self.OK.setAutoRaise(True)
        self.OK.setIcon(QtGui.QIcon(Qt4_Icons.load('button_ok_small'))) #QPixmap(Icons.tinyOK)))
        self.Cancel = QtGui.QToolButton(parent)
        self.Cancel.setAutoRaise(True)
        self.Cancel.setIcon(QtGui.QIcon(Qt4_Icons.load('button_cancel_small'))) #QPixmap(Icons.tinyCancel)))
        self.Reset = QtGui.QToolButton(parent)
        self.Reset.setIcon(QtGui.QIcon(Qt4_Icons.load('button_default_small'))) #QPixmap(Icons.defaultXPM)))
        self.Reset.setAutoRaise(True)
        self.setEnabled(False)

        main_layout = QtGui.QHBoxLayout()
        main_layout.addWidget(self.OK)
        main_layout.addWidget(self.Cancel)
        main_layout.addWidget(self.Reset)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)

    def setEnabled(self, enabled):
        """
        Descript. :
        """
        if enabled:
            self.Reset.setEnabled(True)
            self.OK.setEnabled(True)
            self.Cancel.setEnabled(True)
        else:
            self.Reset.setEnabled(False)
            self.OK.setEnabled(False)
            self.Cancel.setEnabled(False)

class ComboBoxTableItem(QtGui.QComboBox):
    """
    Descript. :
    """

    def __init__(self, parent, row, col, items_list = None):
        """ 
        Descript. :
        """
        QtGui.QComboBox.__init__(self)
        if items_list is not None:
            self.addItems(items_list)  
        self.col = col
        self.row = row  
        self.parent = parent
        QtCore.QObject.connect(self, QtCore.SIGNAL('currentIndexChanged(int)'), self.current_index_changed)

    def current_index_changed(self, index): 
        """
        Descript. :
        """
        self.parent.emit(QtCore.SIGNAL('cellChanged(int, int)'), self.row, self.col) 

class FileTableItem(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, row, col, filename, file_filter):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self)

        self.file_filter = file_filter
        self.parent = parent
        self.col = col
        self.row = row

        self.cmdBrowse = QtGui.QPushButton('Browse', self.parent.viewport())

        main_layout = QtGui.QHBoxLayout()
        main_layout.addWidget(self.cmdBrowse)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout) 

        QtCore.QObject.connect(self.cmdBrowse, QtCore.SIGNAL('clicked()'), self.browse_clicked)      
        self.set_filename(filename)

    def set_filename(self, filename):
        """
        Descript. :
        """
        self.filename = str(filename)

        if self.cmdBrowse is not None:
            self.cmdBrowse.setToolTip(self.filename)

        self.parent.emit(QtCore.SIGNAL('cellChanged(int, int)'), self.row, self.col)

    def get_filename(self):
        """
        Descript. :
        """
        return self.filename        
        
    def browse_clicked(self):
        """
        Descript. :
        """
        new_filename = QtGui.QFileDialog.getOpenFileName(
                             self, os.path.dirname(self.filename) or os.getcwd(), 
                             self.file_filter, '', 'Select a file')
        
        if len(new_filename) > 0:
            self.set_filename(new_filename)

            
class ColorTableItem(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, row, col, color):
        """
        Descript. :
        """
        QtGui.QTableWidget.__init__(self, parent)

        self.col = col
        self.row = row
        self.parent = parent

        self.cmdChangeColor = QtGui.QPushButton('Color...', parent)
        self.cmdResetColor = QtGui.QPushButton('reset', parent)

        main_layout = QtGui.QHBoxLayout()
        main_layout.addWidget(self.cmdChangeColor)
        main_layout.addWidget(self.cmdResetColor)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)

        self.cmdChangeColor.clicked.connect(self.cmdChangeColorClicked)
        self.cmdResetColor.clicked.connect(self.cmdResetColorClicked)
        self.setColor(color)

        #main_layout = QtGui.QVBoxLayout()
        #main_layout.addWidget(hbox) 
        #self.setLayout(main_layout) 

    def setColor(self, color):
        """
        Descript. :
        """
        try:
          rgb = color.rgb()
        except:
          try:
            self.qtcolor = QtGui.QColor(color)
          except:
            self.qtcolor = QtGui.QtColor(QtCore.Qt.green)
            self.color = self.qtcolor.rgb()
          else:
            self.color = self.qtcolor.rgb()
        else:
          self.qtcolor=color
          self.color=rgb

        if self.cmdChangeColor is not None: 
            palette = self.cmdChangeColor.palette()
            palette.setColor(QtGui.QPalette.Button, self.qtcolor)
            #palette.setColor(QtGui.QPalette.Inactive, self.qtcolor)

            self.cmdChangeColor.setPalette(palette)
            #                    setStyleSheet("background-color: red")
            #self.cmdChangeColor.setPaletteBackgroundColor(self.qtcolor)

        self.parent.emit(QtCore.SIGNAL('cellChanged(int, int)'), self.row, self.col)

    def cmdChangeColorClicked(self):
        """
        Descript. :
        """
        newColor = QtGui.QColorDialog.getColor(self.qtcolor or QtGui.QColor("white"), None, 'Select a color')
        if newColor.isValid():
            self.setColor(newColor)

    def cmdResetColorClicked(self):
        """
        Descript. :
        """
        self.setColor(None)
    

class Dialog(QtGui.QDialog):
    """
    Descript. :
    """

    def __init__(self, propertyBag):
        """
        Descript. :
        """
        QtGui.QDialog.__init__(self, None, None, Qt.WDestructiveClose)

        self.setCaption("Configuration Editor")
        self.propertiesTable = ConfigurationTable(self)
        self.propertiesTable.setPropertyBag(propertyBag)
        cmdClose = QPushButton('Close', self)
        
        self.connect(self.propertiesTable, PYSIGNAL('propertyChanged'), PYSIGNAL('propertyChanged'))
        self.connect(cmdClose, SIGNAL('clicked()'), self.close)

        QVBoxLayout(self, 0, 0)
        self.layout().setResizeMode(QLayout.FreeResize)
        self.layout().addWidget(self.propertiesTable)
        self.layout().addWidget(cmdClose)
        
        self.setFixedHeight(500)
