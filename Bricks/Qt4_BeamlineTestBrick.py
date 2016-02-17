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
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "Test"


RESULT_ICONS = ("Delete2", "Check")

class Qt4_BeamlineTestBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beamline_test_hwobj = None

        # Internal variables --------------------------------------------------
        self.available_test = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("mnemonic", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.beamline_test_widget = uic.loadUi(os.path.join(\
             os.path.dirname(__file__), 
            'widgets/ui_files/Qt4_beamline_test_widget_layout.ui'))

        self.test_toolbox = self.beamline_test_widget.test_toolbox
        self.test_queue_page = self.beamline_test_widget.queue_toolbox_page
        self.test_com_page = self.beamline_test_widget.com_toolbox_page
        self.test_focus_page = self.beamline_test_widget.focus_toolbox_page
        self.test_ppu_page = self.beamline_test_widget.ppu_toolbox_page
        self.test_profile_page = self.beamline_test_widget.profile_toolbox_page

        self.com_device_table = self.beamline_test_widget.comm_device_table
        self.current_test_listbox = self.beamline_test_widget.current_test_listbox
        self.available_test_listbox = self.beamline_test_widget.available_test_listbox
        self.test_result_browser = QtGui.QTextBrowser(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QHBoxLayout(self)
        _main_vlayout.addWidget(self.beamline_test_widget)
        _main_vlayout.addWidget(self.test_result_browser)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.beamline_test_widget.add_button.clicked.connect(\
             self.add_test_button_clicked)

        self.beamline_test_widget.remove_button.clicked.connect(\
             self.remove_test_button_clicked)

        self.beamline_test_widget.run_test_button.clicked.connect(\
             self.run_test_clicked)

        self.beamline_test_widget.test_focus_button.clicked.connect(
             self.test_focus_button_pressed)

        self.beamline_test_widget.focus_modes_combo.activated.connect(\
             self.set_focus_mode_pressed)

        # Other ---------------------------------------------------------------
        #self.beamline_test_widget.setFixedWidth(600)

        self.test_result_browser.setSizePolicy(\
             QtGui.QSizePolicy.MinimumExpanding,
             QtGui.QSizePolicy.MinimumExpanding)

    def setExpertMode(self, expert):
        self.setEnabled(expert)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'icons':
            icons_list=newValue.split()
        elif propertyName == 'mnemonic':
            if self.beamline_test_hwobj is not None:
                self.disconnect(self.beamline_test_hwobj, 
                                QtCore.SIGNAL('deviceCommunicationTested'), 
                                self.update_com_status)
                self.disconnect(self.beamline_test_hwobj, 
                                QtCore.SIGNAL('focModeChanged'), 
                                self.update_focus_status)
                self.disconnect(self.beamline_test_hwobj, 
                                QtCore.SIGNAL('ppuStatusChanged'), 
                                self.update_ppu_status)
                self.disconnect(self.beamline_test_hwobj, 
                                QtCore.SIGNAL('testFinished'), 
                                self.test_finished)
            self.beamline_test_hwobj = self.getHardwareObject(newValue)
            if self.beamline_test_hwobj is not None:
                self.init_com_table()                
                self.init_test_queue()
                self.connect(self.beamline_test_hwobj, 
                             QtCore.SIGNAL('deviceCommunicationTested'), 
                             self.update_com_status)
                self.connect(self.beamline_test_hwobj, 
                             QtCore.SIGNAL('focModeChanged'), 
                             self.update_focus_status)
                self.connect(self.beamline_test_hwobj,
                             QtCore.SIGNAL('ppuStatusChanged'),
                             self.update_ppu_status)
                self.connect(self.beamline_test_hwobj,
                             QtCore.SIGNAL('testFinished'),
                             self.test_finished)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def add_test_button_clicked(self):
        self.current_test_listbox.insertItem(self.available_test_listbox.currentText())

    def remove_test_button_clicked(self):
        self.current_test_listbox.takeItem(self.current_test_listbox.item(\
             self.current_test_listbox.currentItem()))

    def run_test_clicked(self):
        test_list = []
        if self.test_toolbox.currentItem() == self.test_queue_page:
            for item_index in range(self.current_test_listbox.count()):
                item_key = self.available_test.keys()[self.available_test.\
                    values().index(self.current_test_listbox.text(item_index))]
                test_list.append(item_key)
        elif self.test_toolbox.currentItem() == self.test_com_page:
            test_list = ['com']
        elif self.test_toolbox.currentItem() == self.test_focus_page:
            test_list = ['focus']
        elif self.test_toolbox.currentItem() == self.test_ppu_page:
            test_list = ['ppu']
        elif self.test_toolbox.currentItem() == self.test_profile_page:
            test_list = ['profile']
        self.beamline_test_hwobj.start_test_queue(test_list)

    def test_finished(self, html_filename):
        if html_filename:
            self.test_result_browser.setSource(html_filename)
            self.test_result_browser.reload() 

    def test_focus_button_pressed(self):
        self.test_focus_mode()

    def update_com_status(self, device_index, status):
        self.beamline_test_widget.progress_bar.setProgress(device_index)
        #self.com_device_table.setPixmap(device_index, 0, Icons.load(self.icon_list[int(status)]))
        if device_index == len(self.com_device_list) - 1:
            self.beamline_test_widget.progress_bar.reset()            

    def update_focus_status(self):
        self.test_focus_mode()

    def update_ppu_status(self, is_error, status_text):
        self.beamline_test_widget.ppu_test_button.setEnabled(True)
        if is_error:
            self.beamline_test_widget.ppu_status_label.setText(\
                 "<font color='red'>PPU is not running properly</font>")
        else:
            self.beamline_test_widget.ppu_status_label.setText(\
                 "<font color='black'>PPU is running properly</font>")
        self.beamline_test_widget.ppu_status_textbrowser.setText(status_text)
        self.beamline_test_widget.ppu_restart_button.setEnabled(is_error)  
                  
    def init_com_table(self):
        self.com_device_list = self.beamline_test_hwobj.get_device_list()

        if self.com_device_list:
              row = 0
              self.com_device_table.setRowCount(len(self.com_device_list))
              for device in self.com_device_list:
                  row += 1
                  for info_index, info in enumerate(device):
                      temp_table_item = QtGui.QTableWidgetItem(info)
                      self.com_device_table.setItem(row - 1, info_index, temp_table_item)
               
              print "todo..."       
              #for col in range(self.com_device_table.columnCount()):
              #     self.com_device_table.adjustColumn(col)
              #self.com_device_table.adjustSize()
              self.beamline_test_widget.progress_bar.setMaximum(len(self.com_device_list))

    def init_test_queue(self):
        self.available_test = self.beamline_test_hwobj.get_available_tests()
        for key, value in self.available_test.iteritems():
            self.available_test_listbox.addItem(value)
        current_test_queue = self.beamline_test_hwobj.get_test_list()
        for item in current_test_queue:
            self.current_test_listbox.addItem(item)

    def test_focus_mode(self):
        active_mode, beam_size = self.beamline_test_hwobj.get_focus_mode()
        print 111
        print active_mode, beam_size 
        if active_mode is None:
            self.beamline_test_widget.focus_mode_label.setText(\
                 "<font color='red'>No focusing mode detected<font>")
        else:
            self.beamline_test_widget.focus_mode_label.setText(\
                 "<font color='black'>%s mode detected<font>" % active_mode)
        focus_modes = self.beamline_test_hwobj.get_focus_mode_names()
        focus_modes_table = self.beamline_test_widget.focus_modes_table
        focus_modes_combo = self.beamline_test_widget.focus_modes_combo
        
        if focus_modes:
            focus_modes_table.setColumnCount(len(focus_modes))
            focus_modes_combo.clear()
            hor_labels = QtCore.QStringList(focus_modes)
            focus_modes_table.setHorizontalHeaderLabels(hor_labels)
            #for col, mode in enumerate(focus_modes):
            #    #focus_modes_table.horizontalHeader().setLabel(col, mode)
            #    #self.focus_modesCount += 1
            #    focus_modes_combo.insertItem(mode)
        if active_mode:
            focus_modes_combo.setCurrentText(active_mode)
        focus_motors_list = self.beamline_test_hwobj.get_focus_motors()
        if focus_motors_list:
            ver_labels = QtCore.QStringList()
            focus_modes_table.setRowCount(len(focus_motors_list))
            for row, motor in enumerate(focus_motors_list):
                ver_labels.append(motor['motorName'])
                for col, mode in enumerate(focus_modes):
                    item_text = "%.3f/%.3f" %(motor['focusingModes'][mode], motor['position'])
                    res = (mode in motor['focMode'])
                    if res:
                        temp_table_item = QtGui.QTableWidgetItem(item_text) 
                        temp_table_item.setBackground(Qt4_widget_colors.LIGHT_GREEN)
                    else:
                        temp_table_item = QtGui.QTableWidgetItem(item_text)
                        temp_table_item.setBackground(Qt4_widget_colors.LIGHT_RED)
                    focus_modes_table.setItem(row, col, temp_table_item) 
            focus_modes_table.setVerticalHeaderLabels(ver_labels)
            #for col in range(focus_modes_table.numCols()):
            #    focus_modes_table.adjustColumn(col)

    def set_focus_mode_pressed(self, item_index):
        self.beamline_test_hwobj.set_focus_mode(\
             self.beamline_test_widget.focus_modes_combo.currentText())
