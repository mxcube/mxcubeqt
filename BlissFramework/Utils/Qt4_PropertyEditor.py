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
import sys
import types
import weakref
import logging

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import PropertyBag
from BlissFramework.Utils import Qt4_widget_colors


class Qt4_ConfigurationTable(QTableWidget):
    """
    Descript. :
    """

    propertyChangedSignal = pyqtSignal(str, object, object)

    def __init__(self, parent):
        """
        Descript. :
        """
        QTableWidget.__init__(self, parent)

        self.display_hwobj = False
        self.property_bag = None

        self.setObjectName("configurationTable")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(4)
        self.setSelectionMode(QTableWidget.NoSelection)

        #self.setHorizontalHeaderLabels([self.trUtf8('Property'),  
        #                                self.trUtf8('Value'), 
        #                                self.trUtf8(''),
        #                                self.trUtf8('Comment')])
        self.setHorizontalHeaderLabels(['Property',  
                                        'Value', 
                                        '',
                                        'Comment'])
         
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cellChanged.connect(self.on_cell_changed)
        
    def clear(self):
        """
        Descript. :
        """
        for i in range(self.rowCount()):
            self.removeRow(i)
        self.setRowCount(0)
        self.property_bag = None

        
    def set_property_bag(self, property_bag, show_hidden=False, display_hwobj=False):
        """
        Descript. :
        """
        self.display_hwobj = display_hwobj
        self.clear()           

        if self.property_bag is not None:
            for prop in self.property_bag:
                prop._editor = None

        self.property_bag = property_bag

        if self.property_bag is not None:
            i = 0
            for prop in self.property_bag:
                prop._editor = weakref.ref(self)
                prop_name = prop.getName()
     
                if not show_hidden and prop.hidden:
                    continue

                if display_hwobj: 
                    if not prop_name.startswith("hwobj_"):
                        continue
                    else:
                        prop_name = prop_name.replace("hwobj_", "")
                else:
                    if prop_name.startswith("hwobj_"):
                        continue

                self.setRowCount(i + 1)
                temp_table_item = QTableWidgetItem(prop_name)
                temp_table_item.setFlags(Qt.ItemIsEnabled)
                self.blockSignals(True) 
                self.setItem(i, 0, temp_table_item)
                self.set_widget_from_property(i, prop)

                temp_table_item = QTableWidgetItem(prop.comment)
                temp_table_item.setFlags(Qt.ItemIsEnabled)
                self.setItem(i, 3, temp_table_item)
                
                self.blockSignals(False)
                
                validation_panel = ValidationTableItem(self)
                self.setCellWidget(i, 2, validation_panel)
                validation_panel.ok_button.clicked.\
                     connect(self.on_validate_click)
                validation_panel.cancel_button.clicked.\
                     connect(self.on_invalidate_click)
                validation_panel.reset_button.clicked.\
                     connect(self.on_reset_click)
                i += 1
            self.setEnabled(i > 0)    
        self.resizeColumnsToContents()
        self.setFixedHeight((self.rowCount() + 1)  * \
                            (self.rowHeight(0) + 2))
        #self.adjustSize()
        self.parent().adjustSize()
        #self.parent().resize(self.parent().sizeHint())

    def set_widget_from_property(self, row, prop):
        """Adds new property to the propery table

        :param row: selected row
        :type row: int
        :param prop: property
        :type prop: dict 
        """
        if prop.getType() == 'boolean':
            new_property_item = QTableWidgetItem("")
            self.setItem(row, 1, new_property_item)
            if prop.getUserValue():
                self.item(row, 1).setCheckState(Qt.Checked)
            else:
                self.item(row, 1).setCheckState(Qt.Unchecked)
        elif prop.getType() == 'combo':
            choicesList = []
            choices = prop.getChoices()
            for choice in choices:
                choicesList.append(choice)
            new_property_item = ComboBoxTableItem(self, row, 1, choicesList)
            new_property_item.setCurrentIndex(new_property_item.findText(prop.getUserValue()))
            self.setCellWidget(row, 1, new_property_item)
        elif prop.getType() == 'file':
            new_property_item = FileTableItem(self, row, 1, prop.getUserValue(), prop.getFilter())
            self.setCellWidget(row, 1, new_property_item)
        elif prop.getType() == 'color':
            new_property_item = ColorTableItem(self, row, 1, prop.getUserValue())
            self.setCellWidget(row, 1, new_property_item)
        else:                                           
            if prop.getUserValue() is None:
                temp_table_item = QTableWidgetItem("")
            else:
                temp_table_item = QTableWidgetItem(str(prop.getUserValue()))  
            self.setItem(row, 1, temp_table_item)
        self.resizeColumnsToContents()
        #self.parent().adjustSize()

    def on_cell_changed(self, row, col):
        """Assignes new value to the property, clicked on the the
           property table
        """
        col += 1
        prop_name = str(self.item(row, 0).text())
        if self.display_hwobj:
            prop_name = "hwobj_" + prop_name

        item_property = self.property_bag.getProperty(prop_name)
        old_value = item_property.getUserValue()

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
                        (str(self.item(row, 1).text()), prop_name))

            if item_property.getUserValue() is None:
                self.item(row, 1).setText('')
            else:
                self.item(row, 1).setText(str(item_property.getUserValue()))

        if not old_value == item_property.getUserValue():
            self.propertyChangedSignal.emit(prop_name, old_value, item_property.getUserValue())

    def on_validate_click(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 1, 0) #current row, col 1, accept = 1, replace = 0
        self.activateNextCell()
        
    def on_invalidate_click(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 0, 0) #current row, col 1, accept = 0, replace = 0

    def on_reset_click(self):
        """
        Descript. :
        """
        self.endEdit(self.currentRow(), 1, 0, 0)
        prop_name = str(self.item(row, 0).text())
        if self.display_hwobj:
            prop_name = "hwobj_" + prop_name
 

        prop = self.property_bag.getProperty(prop_name)

        default_value = prop.getDefaultValue()
        if not default_value == None:
            prop.setValue(default_value)
        
        self.set_widget_from_property(self.currentRow(), prop)

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
                prop_name = str(self.item(row, 0).text())
                if self.display_hwobj:
                    prop_name = "hwobj_" + prop_name
                prop = self.property_bag.getProperty(prop_name)

                old_value = prop.getUserValue()
            
                if prop.getType() == 'boolean':
                    prop.setValue(self.item(row, 1).isChecked())
                elif prop.getType() == 'combo':
                    prop.setValue(self.item(row, 1).currentText())
                else: 
                    try:
                        prop.setValue(str(self.text(row, 1)))
                    except:
                        logging.getLogger().error('Cannot assign value to property %s' % prop_name)

                    if prop.getUserValue() is None:
                        self.setText(row, 1, '')
                    else:
                        self.setText(row, 1, str(prop.getUserValue()))

                if not old_value == prop.getUserValue():
                    self.propertyChangedSignal.emit(prop_name, old_value, prop.getUserValue())
                    #self.emit(QtCore.SIGNAL('propertyChanged'), 
                              #(prop_name, old_value, prop.getUserValue(), ))

        return QTable.endEdit(self, row, col, accept, replace)


class ValidationTableItem(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent=None):
        """
        Descript. : parent (QTreeWidget) : Item's QTreeWidget parent.
        """

        QWidget.__init__(self, parent)
       
        self.ok_button = QToolButton(parent)
        self.ok_button.setAutoRaise(True)
        self.ok_button.setIcon(Qt4_Icons.load_icon('button_ok_small'))
        self.cancel_button = QToolButton(parent)
        self.cancel_button.setAutoRaise(True)
        self.cancel_button.setIcon(Qt4_Icons.load_icon('button_cancel_small'))
        self.reset_button = QToolButton(parent)
        self.reset_button.setIcon(Qt4_Icons.load_icon('button_default_small'))
        self.reset_button.setAutoRaise(True)
        self.setEnabled(False)

        _main_layout = QHBoxLayout(self)
        _main_layout.addWidget(self.ok_button)
        _main_layout.addWidget(self.cancel_button)
        _main_layout.addWidget(self.reset_button)
        _main_layout.setSpacing(0)
        _main_layout.setContentsMargins(0,0,0,0)

    def setEnabled(self, enabled):
        """
        Descript. :
        """
        if enabled:
            self.reset_button.setEnabled(True)
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(False)
            self.ok_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

class ComboBoxTableItem(QComboBox):
    """
    Descript. :
    """

    def __init__(self, parent, row, col, items_list = None):
        """ 
        Descript. :
        """
        QComboBox.__init__(self)
        if items_list is not None:
            self.addItems(items_list)  
        self.col = col
        self.row = row  
        self.parent = parent
        self.currentIndexChanged.connect(self.current_index_changed)

    def current_index_changed(self, index): 
        """
        Descript. :
        """
        self.parent.cellChanged.emit(self.row, self.col) 

class FileTableItem(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, row, col, filename, file_filter):
        """
        Descript. :
        """
        QWidget.__init__(self)

        self.file_filter = file_filter
        self.parent = parent
        self.col = col
        self.row = row

        self.cmdBrowse = QPushButton('Browse', self.parent.viewport())

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.cmdBrowse)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout) 

        self.cmdBrowse.clicked.connect(self.browse_clicked)      
        self.set_filename(filename)

    def set_filename(self, filename):
        """
        Descript. :
        """
        self.filename = str(filename)

        if self.cmdBrowse is not None:
            self.cmdBrowse.setToolTip(self.filename)

        self.parent.cellChanged.emit(self.row, self.col)

    def get_filename(self):
        """
        Descript. :
        """
        return self.filename        
        
    def browse_clicked(self):
        """
        Descript. :
        """
        new_filename = QFileDialog.getOpenFileName(
                             self, os.path.dirname(self.filename) or os.getcwd(), 
                             self.file_filter, '', 'Select a file')
        
        if len(new_filename) > 0:
            self.set_filename(new_filename)

            
class ColorTableItem(QWidget):
    """
    Descript. :
    """

    #cellChangedSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent, row, col, color):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self.col = col
        self.row = row
        self.parent = parent

        self.change_color_button = QPushButton('Color...', parent)
        self.reset_color_button = QPushButton('reset', parent)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.change_color_button)
        main_layout.addWidget(self.reset_color_button)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        self.change_color_button.clicked.connect(self.change_color_clicked)
        self.reset_color_button.clicked.connect(self.reset_color_clicked)
        self.set_color(color)

        #main_layout = QtGui.QVBoxLayout()
        #main_layout.addWidget(hbox) 
        #self.setLayout(main_layout) 

    def set_color(self, color):
        """
        Descript. :
        """
        if not color:
            self.qtcolor = None
            self.color = None
            Qt4_widget_colors.set_widget_color(\
                self.change_color_button,
                Qt4_widget_colors.BUTTON_ORIGINAL,
                QPalette.Button)
        else:         
            try:
                rgb = color.rgb()
            except:
                try:
                    self.qtcolor = QColor(color)
                except:
                    self.qtcolor = QtColor(Qt.green)
                    self.color = self.qtcolor.rgb()
                else:
                    self.color = self.qtcolor.rgb()
            else:
                self.qtcolor = color
                self.color = rgb
        
            Qt4_widget_colors.set_widget_color(self.change_color_button,
                                               self.qtcolor,
                                               QPalette.Button)
        self.parent.cellChanged.emit(self.row, self.col)

    def change_color_clicked(self):
        """Opens color dialog to choose color"""

        new_color = QColorDialog.getColor(\
            self.qtcolor or QColor("white"), None, 'Select a color')
        if new_color.isValid():
            self.set_color(new_color)

    def reset_color_clicked(self):
        """Resets color"""

        self.set_color(None)
