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

import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_widget_utils import DataModelInputBinder
from BlissFramework.Utils import Qt4_widget_colors


class DataPathWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = '', fl = 0, data_model = None, 
                 layout = None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._base_image_dir = None
        self._base_process_dir = None
        self.path_conflict_state = False
        
        if data_model is None:
            self._data_model = queue_model_objects.PathTemplate()
        else:
            self._data_model = data_model
        
        self._data_model_pm = DataModelInputBinder(self._data_model)

        # Graphic elements ----------------------------------------------------
        if layout == "vertical":
            self.data_path_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                "ui_files/Qt4_data_path_widget_vertical_layout.ui"))
        else:
            self.data_path_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                "ui_files/Qt4_data_path_widget_horizontal_layout.ui"))

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.data_path_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Qt signal/slot connections ------------------------------------------ 
        self.connect(self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"),
                     self._prefix_ledit_change)

        self.connect(self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"),
                           self._run_number_ledit_change)

        self.connect(self.data_path_widget.findChild(QtGui.QPushButton, 'browse_button'),
                     QtCore.SIGNAL("clicked()"),
                     self._browse_clicked)

        self.connect(self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"),
                     self._folder_ledit_change)

        # Other ---------------------------------------------------------------
        self._data_model_pm.bind_value_update('base_prefix', 
             self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit'), 
             str, None)
        
        self._data_model_pm.bind_value_update('run_number', 
             self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit'),
             int, QtGui.QIntValidator(0, 1000, self))

        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.GROUP_BOX_GRAY)

    def _browse_clicked(self):
        get_dir = QtGui.QFileDialog(self)
        given_dir = self._base_image_dir

        d = str(get_dir.getExistingDirectory(self, given_dir,
                                             "Select a directory", 
                                             QtGui.QFileDialog.ShowDirsOnly))
        d = os.path.dirname(d)

        if d is not None and len(d) > 0:
            self.set_directory(d)

    def _prefix_ledit_change(self, new_value):
        self._data_model.base_prefix = str(new_value)
        file_name = self._data_model.get_image_file_name()
        file_name = file_name.replace('%' + self._data_model.precision + 'd',
                                      int(self._data_model.precision) * '#' )
        file_name = file_name.strip(' ')
        self.data_path_widget.findChild(QtGui.QLabel, 
                                        'file_name_value_label').setText(file_name)
        
        self.emit(QtCore.SIGNAL('path_template_changed'),
                  self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit'),
                  new_value)

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.set_run_number(new_value)
            self.emit(QtCore.SIGNAL('path_template_changed'),
                      self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit'),
                      new_value)

    def _folder_ledit_change(self, new_value):        
        base_image_dir = self._base_image_dir
        base_proc_dir = self._base_process_dir
        new_sub_dir = str(new_value).strip(' ')

        if len(new_sub_dir) > 0:
            if new_sub_dir[0] == os.path.sep:
                new_sub_dir = new_sub_dir[1:]
            new_image_directory = os.path.join(base_image_dir, str(new_sub_dir))
            new_proc_dir = os.path.join(base_proc_dir, str(new_sub_dir))
        else:
            new_image_directory = base_image_dir
            new_proc_dir = base_proc_dir
            
        self._data_model.directory = new_image_directory
        self._data_model.process_directory = new_proc_dir 
        Qt4_widget_colors.set_widget_color(self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit'), 
                                           Qt4_widget_colors.WHITE)

        self.emit(QtCore.SIGNAL('path_template_changed'),
                  self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit'),
                  new_value)

    def set_data_path(self, path):
        (dir_name, file_name) = os.path.split(path)
        self.set_directory(dir_name)
        file_name = file_name.replace('%' + self._data_model.precision + 'd',
                                      int(self._data_model.precision) * '#' )
        self.data_path_widget.findChild(QtGui.QLabel, 'file_name_value_label').setText(file_name)
    
    def set_directory(self, directory):
        base_image_dir = self._base_image_dir
        dir_parts = directory.split(base_image_dir)

        if len(dir_parts) > 1:
            sub_dir = dir_parts[1]        
            self._data_model.directory = directory
            self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit').setText(sub_dir)
        else:
            self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit').setText('')
            self._data_model.directory = base_image_dir

        self.data_path_widget.findChild(QtGui.QLineEdit, 'base_path_ledit').setText(base_image_dir)

    def set_run_number(self, run_number):
        self._data_model.run_number = int(run_number)
        self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit').\
            setText(str(run_number))

    def set_prefix(self, base_prefix):
        self._data_model.base_prefix = str(base_prefix)
        self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit').setText(str(base_prefix))
        file_name = self._data_model.get_image_file_name()
        file_name = file_name.replace('%' + self._data_model.precision + 'd',
                                      int(self._data_model.precision) * '#' )
        self.data_path_widget.findChild(QtGui.QLabel, 'file_name_value_label').setText(file_name)

    def update_data_model(self, data_model):
        self._data_model = data_model
        self.set_data_path(data_model.get_image_path())
        self._data_model_pm.set_model(data_model)

    def indicate_path_conflict(self, conflict):
        if conflict:
            self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit').\
                setPaletteBackgroundColor(Qt4_widget_colors.LIGHT_RED)
            
            self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit').\
                setPaletteBackgroundColor(Qt4_widget_colors.LIGHT_RED)

            self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit').\
                setPaletteBackgroundColor(Qt4_widget_colors.LIGHT_RED)

            logging.getLogger("user_level_log").\
                error('The current path settings will overwrite data' +\
                          ' from another task. Correct the problem before adding to queue')
        else:
            # We had a conflict previous, but its corrected now !
            if self.path_conflict_state:
                logging.getLogger("user_level_log").info('Path valid')

            Qt4_widget_colors.set_widget_color(self.data_path_widget.findChild(QtGui.QLineEdit, 'prefix_ledit'),
                                               Qt4_widget_colors.WHITE)
            Qt4_widget_colors.set_widget_color(self.data_path_widget.findChild(QtGui.QLineEdit, 'run_number_ledit'),
                                               Qt4_widget_colors.WHITE)
            Qt4_widget_colors.set_widget_color(self.data_path_widget.findChild(QtGui.QLineEdit, 'folder_ledit'),
                                               Qt4_widget_colors.WHITE)

        self.path_conflict_state = conflict
            

