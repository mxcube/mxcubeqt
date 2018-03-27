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

"""Qt4_BeamlineTestBrick
   
   Widget allows to run tests defined in the hardware object.
   As a result a html page and pdf are generated.
"""

import os

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_webview_widget import WebViewWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Test"


class Qt4_BeamlineTestBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beamline_test_hwobj = None
        self.unittest_hwobj = None

        # Internal variables --------------------------------------------------
        self.available_tests = None
        self.com_device_list = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("mnemonic", "string", "")
        self.addProperty("hwobj_unittest", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.beamline_test_widget = loadUi(os.path.join(\
             os.path.dirname(__file__), 
            'widgets/ui_files/Qt4_beamline_test_widget_layout.ui'))

        self.test_toolbox = self.beamline_test_widget.test_toolbox
        self.test_queue_page = self.beamline_test_widget.queue_toolbox_page
        self.test_com_page = self.beamline_test_widget.com_toolbox_page
        self.test_focus_page = self.beamline_test_widget.focus_toolbox_page
        self.test_ppu_page = self.beamline_test_widget.ppu_toolbox_page

        self.com_device_table = self.beamline_test_widget.comm_device_table
        #self.current_test_listwidget = self.beamline_test_widget.current_test_listbox
        self.available_tests_listwidget = self.beamline_test_widget.\
             available_tests_listwidget

        _web_view_widget = QWidget(self)
        _load_last_test_button = QPushButton("View last results", \
             _web_view_widget)
        self.test_result_browser = WebViewWidget(_web_view_widget)

        # Layout --------------------------------------------------------------
        _web_view_widget_vlayout = QVBoxLayout(_web_view_widget)
        _web_view_widget_vlayout.addWidget(_load_last_test_button)
        _web_view_widget_vlayout.addWidget(self.test_result_browser)
        _web_view_widget_vlayout.setSpacing(2)
        _web_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(self.beamline_test_widget)
        _main_vlayout.addWidget(_web_view_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.beamline_test_widget.execute_all_button.clicked.connect(\
             self.execute_all_tests_clicked)
        self.beamline_test_widget.test_button.clicked.connect(\
             self.execute_test_clicked)
        self.beamline_test_widget.focus_modes_combo.activated.connect(\
             self.set_focus_mode_pressed)
        self.available_tests_listwidget.itemDoubleClicked.connect(\
             self.available_tests_double_clicked) 
         
        _load_last_test_button.clicked.connect(self.load_latest_test_results)
        self.beamline_test_widget.ppu_restart_button.clicked.connect(self.restart_ppu)

        # Other ---------------------------------------------------------------
        #self.beamline_test_widget.setFixedWidth(600)
        self.test_result_browser.setSizePolicy(\
             QSizePolicy.Expanding,
             QSizePolicy.Expanding)
        _load_last_test_button.setFixedWidth(200)

        self.test_toolbox.setCurrentWidget(self.test_queue_page)  
        self.beamline_test_widget.setFixedWidth(700)
        self.test_result_browser.navigation_bar.setHidden(True)
        #self.beamline_test_widget.splitter.setSizes([500, 1200])

    def restart_ppu(self):
        self.beamline_test_hwobj.ppu_restart_all()

    def setExpertMode(self, expert):
        self.setEnabled(expert)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'mnemonic':
            if self.beamline_test_hwobj is not None:
                self.disconnect(self.beamline_test_hwobj, 
                                'progressStep', 
                                self.update_test_progress)
                self.disconnect(self.beamline_test_hwobj, 
                                'focusingModeChanged', 
                                self.update_focus_status)
                self.disconnect(self.beamline_test_hwobj, 
                                'ppuStatusChanged', 
                                self.update_ppu_status)
                self.disconnect(self.beamline_test_hwobj, 
                                'testFinished', 
                                self.test_finished)
            self.beamline_test_hwobj = self.getHardwareObject(new_value)
            if self.beamline_test_hwobj is not None:
                self.init_com_table()                
                self.init_test_queue()
                self.connect(self.beamline_test_hwobj, 
                             'progressStep', 
                             self.update_test_progress)
                self.connect(self.beamline_test_hwobj, 
                             'focusingModeChanged', 
                             self.update_focus_status)
                self.connect(self.beamline_test_hwobj,
                             'ppuStatusChanged',
                             self.update_ppu_status)
                self.connect(self.beamline_test_hwobj,
                             'testFinished',
                             self.test_finished)
                self.update_focus_status(None, None)
                self.beamline_test_hwobj.update_values()
        #elif property_name == 'hwobj_unittest':
        #    self.unittest_hwobj = self.getHardwareObject(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def execute_test_clicked(self):
        test_list = []
        if self.test_toolbox.currentWidget() == self.test_queue_page:
            test_list = self.available_tests.keys()
        elif self.test_toolbox.currentWidget() == self.test_com_page:
            test_list = ['com']
        elif self.test_toolbox.currentWidget() == self.test_focus_page:
            test_list = ['focusing']
            self.test_focus_mode()
        elif self.test_toolbox.currentWidget() == self.test_ppu_page:
            test_list = ['ppu']
        self.beamline_test_hwobj.start_test_queue(test_list, create_report=False)

    def execute_all_tests_clicked(self):
        self.beamline_test_hwobj.start_test_queue(\
             self.available_tests.keys())

    def test_finished(self, html_filename):
        self.beamline_test_widget.progress_bar.reset()
        self.beamline_test_widget.progress_bar.setDisabled(True)
        self.beamline_test_widget.progress_msg_ledit.setText("")
        if html_filename:
            self.test_result_browser.set_url(html_filename)

    def test_focus_button_pressed(self):
        self.test_focus_mode()

    def update_test_progress(self, progress_value, progress_msg):
        #self.beamline_test_widget.progress_bar.setMaximum(\
        #     progress_info["progress_total"])
        self.beamline_test_widget.progress_bar.setValue(progress_value)
        self.beamline_test_widget.progress_bar.setEnabled(True)
        self.beamline_test_widget.progress_msg_ledit.setText(progress_msg)

    def update_focus_status(self, focus_mode, beam_size):
        self.test_focus_mode()

    def update_ppu_status(self, is_error, status_text):
        if is_error:
            self.beamline_test_widget.ppu_status_label.setText(\
                 "<font color='red'>PPU is not running properly</font>")
        else:
            self.beamline_test_widget.ppu_status_label.setText(\
                 "<font color='black'>PPU is running properly</font>")
        self.beamline_test_widget.ppu_status_textbrowser.setText(status_text)
        self.beamline_test_widget.ppu_restart_button.setEnabled(is_error)  
                  
    def init_com_table(self):
        try:
            self.com_device_list = self.beamline_test_hwobj.get_device_list()
        except:
            self.com_device_list = None

        if self.com_device_list:
            row = 0
            self.com_device_table.setRowCount(len(self.com_device_list))
            for device in self.com_device_list:
                row += 1
                for info_index, info in enumerate(device):
                    temp_table_item = QTableWidgetItem(info)
                    self.com_device_table.setItem(row - 1, info_index, temp_table_item)
            #for col in range(self.com_device_table.columnCount()):
            #     self.com_device_table.adjustColumn(col)
            #self.com_device_table.adjustSize()
            self.beamline_test_widget.progress_bar.setMaximum(len(self.com_device_list))
        else:
            self.test_com_page.setEnabled(False)

    def init_test_queue(self):
        self.available_tests = self.beamline_test_hwobj.get_available_tests()
        for value in self.available_tests.values():
            self.available_tests_listwidget.addItem(value)

    def test_focus_mode(self):
        if not hasattr(self.beamline_test_hwobj, "get_focus_mode"):
            self.test_focus_page.setEnabled(False)
            return

        active_mode, beam_size = self.beamline_test_hwobj.get_focus_mode()

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
            hor_labels = QStringList(focus_modes)
            focus_modes_table.setHorizontalHeaderLabels(hor_labels)
            for col, mode in enumerate(focus_modes):
                focus_modes_combo.addItem(mode)
        if active_mode:
            focus_modes_combo.setCurrentIndex(\
                 focus_modes_combo.findText(active_mode))
        else:
            focus_modes_combo.setCurrentIndex(-1) 

        focus_motors_list = self.beamline_test_hwobj.get_focus_motors()
        if focus_motors_list:
            ver_labels = QStringList()
            focus_modes_table.setRowCount(len(focus_motors_list))
            for row, motor in enumerate(focus_motors_list):
                ver_labels.append(motor['motorName'])
                for col, mode in enumerate(focus_modes):
                    item_text = "%.3f/%.3f" % (motor['focusingModes'][mode], motor['position'])
                    res = (mode in motor['focMode'])
                    if res:
                        temp_table_item = QTableWidgetItem(item_text) 
                        temp_table_item.setBackground(Qt4_widget_colors.LIGHT_GREEN)
                    else:
                        temp_table_item = QTableWidgetItem(item_text)
                        temp_table_item.setBackground(Qt4_widget_colors.LIGHT_RED)
                    focus_modes_table.setItem(row, col, temp_table_item) 
            focus_modes_table.setVerticalHeaderLabels(ver_labels)

    def set_focus_mode_pressed(self, item_index):
        self.beamline_test_hwobj.set_focus_mode(\
             self.beamline_test_widget.focus_modes_combo.currentText())

    def load_latest_test_results(self):
        html_filename = self.beamline_test_hwobj.get_result_html()
        if html_filename:
            self.test_result_browser.set_url(html_filename) 
        else:
            self.test_result_browser.set_static_page(\
                "<center><h1>Test result file not found</h1></center>") 

    def available_tests_double_clicked(self, listwidget_item):
        test_name = self.available_tests.keys()[self.available_tests.values().\
             index(listwidget_item.text())]
        self.beamline_test_hwobj.start_test_queue([test_name])
