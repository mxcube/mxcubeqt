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

from PyQt4 import QtCore
from PyQt4 import QtGui

import Qt4_queue_item
import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_confirm_dialog_widget_vertical_layout \
     import ConfirmDialogWidgetVerticalLayout


class FileTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QTreeWidgetItem.__init__(self, args[0])
        self.setText(0, args[2])
        self.setText(1, args[3])
        self.setText(2, args[4]) 
        self.brush = QtGui.QBrush(QtCore.Qt.black)
        self.__normal_brush = QtGui.QBrush(QtCore.Qt.black)
        
    def set_brush(self, qt_brush):
        """
        Descript. :
        """
        self.brush = qt_brush

class ConfirmDialog(QtGui.QDialog):
    """
    Descript. :
    """
    continueClickedSignal = QtCore.pyqtSignal(list, list)

    def __init__(self, parent = None, name = None, flags = 0):
        """
        Descript. :
        """

        QtGui.QDialog.__init__(self, parent, 
              QtCore.Qt.WindowFlags(flags | QtCore.Qt.WindowStaysOnTopHint))

        if name is not None:
            self.setObjectName(name) 

        # Internal variab;es --------------------------------------------------
        self.ready_event = False
        self.checked_items = []
        self.sample_items = []
        self.files_to_be_written = []
        self.item_run_number_list = []
        self.queue_model_hwobj = None
       
        # Graphic elements ---------------------------------------------------- 
        self.dialog_layout_widget = ConfirmDialogWidgetVerticalLayout(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.dialog_layout_widget)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0) 
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
        self.dialog_layout_widget.continue_button.clicked.connect(\
             self.continue_button_click)
        self.dialog_layout_widget.cancel_button.clicked.connect(\
             self.cancel_button_click)

        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        self.dialog_layout_widget.force_dark_cbx.setChecked(True)
        self.dialog_layout_widget.missing_one_cbx.hide()
        self.dialog_layout_widget.missing_two_cbx.hide()
        self.setWindowTitle('Confirm collection')

    def set_plate_mode(self, plate_mode):
        """
        Descript. :
        """
        self.dialog_layout_widget.snapshots_list = [0, 1] if plate_mode \
             else [0, 1, 2, 4]
        self.dialog_layout_widget.languageChange()
 
    def disable_dark_current_cbx(self):
        """
        Descript. :
        """
        self.dialog_layout_widget.force_dark_cbx.setEnabled(False)
        self.dialog_layout_widget.force_dark_cbx.setOn(False)

    def enable_dark_current_cbx(self):
        """
        Descript. :
        """
        self.dialog_layout_widget.force_dark_cbx.setEnabled(True)
        self.dialog_layout_widget.force_dark_cbx.setOn(True)
        
    def set_items(self, checked_items):
        """
        Descript. :
        """
        self.sample_items = []
        self.files_to_be_written = []
        self.checked_items = checked_items
        collection_items = []
        current_sample_item = None
        num_images = 0

        self.dialog_layout_widget.file_tree_widget.clear()

        for item in checked_items:
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.sample_items.append(item)
                current_sample_item = item                                

            path_template = item.get_model().get_path_template()

            if path_template:
#                 if item.get_model().is_executed():
#                     self.item_run_number_list.append((item, path_template.run_number))

#                     # Increase the run-number for re-collect
#                     new_run_number = self.queue_model_hwobj.\
#                                      get_next_run_number(path_template,
#                                                          exclude_current = False)
#                     item.get_model().set_number(new_run_number)
#                     path_template.run_number = new_run_number

                collection_items.append(item)
                file_paths = path_template.get_files_to_be_written()
                num_images += len(file_paths)

                for file_path in file_paths:
                    (dir_name, f_name) = os.path.split(file_path)
                    sample_name = current_sample_item.get_model().get_display_name()

                    if sample_name is '':
                        sample_name = current_sample_item.get_model().loc_str

                    #last_item =  self.dialog_layout_widget.file_tree_widget.lastItem()
                    last_item = self.dialog_layout_widget.file_tree_widget.topLevelItem(\
                                (self.dialog_layout_widget.file_tree_widget.topLevelItemCount() - 1)) 

                    file_treewidgee_item = FileTreeWidgetItem(self.dialog_layout_widget.file_tree_widget,
                                            last_item, sample_name, dir_name, f_name)

                    if os.path.isfile(file_path):
                        file_treewidgee_item.set_brush(QtGui.QBrush(QtCore.Qt.red))

        num_samples = len(self.sample_items)
        num_collections = len(collection_items)

        self.dialog_layout_widget.\
            summary_label.setText("Collecting " + str(num_collections) + \
                                  " collection(s) on " + str(num_samples) + \
                                  " sample(s) resulting in " + \
                                  str(num_images) + " image(s).")


    def continue_button_click(self):
        """
        Descript. :
        """
        for item in self.checked_items:
            if isinstance(item.get_model(), queue_model_objects.DataCollection):
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_snapshots = int(self.dialog_layout_widget.take_snapshots_cbox.currentText())
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_dark_current = self.dialog_layout_widget.force_dark_cbx.isChecked()
                item.get_model().acquisitions[0].acquisition_parameters.\
                    skip_existing_images = self.dialog_layout_widget.skip_existing_images_cbx.isChecked()
        
        self.continueClickedSignal.emit(self.sample_items, self.checked_items)
        #self.emit(QtCore.SIGNAL("continue_clicked"), self.sample_items, self.checked_items)
        self.accept()


    def cancel_button_click(self):
        """
        Descript. :
        """
        self.reject()
