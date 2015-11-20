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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic


import Qt4_queue_item
import queue_model_objects_v1 as queue_model_objects
from BlissFramework.Utils import Qt4_widget_colors

from widgets.Qt4_confirm_dialog_widget_vertical_layout \
     import ConfirmDialogWidgetVerticalLayout


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
        self.action_item_map = {}
       
        # Graphic elements ---------------------------------------------------- 
        self.conf_dialog_layout = uic.loadUi(os.path.join(\
             os.path.dirname(__file__),
             "ui_files/Qt4_confirmation_dialog_layout.ui"))

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.conf_dialog_layout)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0) 
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
        self.conf_dialog_layout.continue_button.clicked.connect(\
             self.continue_button_click)
        self.conf_dialog_layout.cancel_button.clicked.connect(\
             self.cancel_button_click)

        # SizePolicies --------------------------------------------------------
        self.setMinimumWidth(600)

        # Other --------------------------------------------------------------- 
        self.setWindowTitle('Confirm collection')

    def set_plate_mode(self, plate_mode):
        """
        Descript. :
        """
        if plate_mode:
            snapshot_count = [0, 1]
        else:
            snapshot_count = [0, 1, 2, 4]
        self.conf_dialog_layout.take_snapshots_combo.clear()
        for item in snapshot_count:
            self.conf_dialog_layout.take_snapshots_combo.addItem(str(item))        
 
    def disable_dark_current_cbx(self):
        """
        Descript. :
        """
        self.conf_dialog_layout.force_dark_cbx.setEnabled(False)
        self.conf_dialog_layout.force_dark_cbx.setOn(False)

    def enable_dark_current_cbx(self):
        """
        Descript. :
        """
        self.conf_dialog_layout.force_dark_cbx.setEnabled(True)
        self.conf_dialog_layout.force_dark_cbx.setOn(True)
        
    def set_items(self, checked_items):
        """
        Descript. :
        """
        self.sample_items = []
        self.files_to_be_written = []
        self.checked_items = checked_items
        collection_items = []
        current_sample_item = None
        sample_treewidget_item = None
        collection_group_treewidget_item = None
        num_images = 0
        file_exists = False

        self.conf_dialog_layout.summary_treewidget.clear()
        self.conf_dialog_layout.file_treewidget.clear()

        for item in checked_items:
            info_str_list = QtCore.QStringList()
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.sample_items.append(item)
                current_sample_item = item
                if item.mounted_style:
                    info_str_list.append("Already mounted")
                else:
                    info_str_list.append("Sample mounting")
            
                info_str_list.append(item.get_model().get_name())
                sample_treewidget_item = QtGui.QTreeWidgetItem(\
                   self.conf_dialog_layout.summary_treewidget,
                   info_str_list)
                for col in range(3):
                    sample_treewidget_item.setBackground(col, \
                      QtGui.QBrush(Qt4_widget_colors.TREE_ITEM_SAMPLE))
            elif isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem): 
                info_str_list.append(item.get_model().get_name()) 
                collection_group_treewidget_item = QtGui.QTreeWidgetItem(\
                   sample_treewidget_item,
                   info_str_list)
                collection_group_treewidget_item.setExpanded(True)
            elif isinstance(item, Qt4_queue_item.SampleCentringQueueItem):
                info_str_list.append(item.get_model().get_name())
                QtGui.QTreeWidgetItem(collection_group_treewidget_item,
                                      info_str_list) 
            elif isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                info_str_list.append("Data collection")
                info_str_list.append("")
                info_str_list.append("%d image(s) with %.2f exposure time" % (\
                     item.get_model().acquisitions[0].acquisition_parameters.num_images,
                     item.get_model().acquisitions[0].acquisition_parameters.exp_time))
                collection_treewidget_item = QtGui.QTreeWidgetItem(\
                     collection_group_treewidget_item, info_str_list)
                for col in range(3):
                    collection_treewidget_item.setBackground(col, \
                      QtGui.QBrush(Qt4_widget_colors.TREE_ITEM_COLLECTION))  
             
            sample_treewidget_item.setExpanded(True)
            path_template = item.get_model().get_path_template()

            if path_template:
                collection_items.append(item)
                file_paths = path_template.get_files_to_be_written()
                num_images += len(file_paths)

                for file_path in file_paths:
                    if os.path.isfile(file_path):
                        (dir_name, file_name) = os.path.split(file_path)
                        sample_name = current_sample_item.get_model().get_display_name()
                        if sample_name is '':
                            sample_name = current_sample_item.get_model().loc_str

                        last_item = self.conf_dialog_layout.file_treewidget.topLevelItem(\
                                    (self.conf_dialog_layout.file_treewidget.topLevelItemCount() - 1)) 

                        info_str_list = QtCore.QStringList()
                        info_str_list.append(sample_name)
                        info_str_list.append(dir_name)
                        info_str_list.append(file_name)
                        file_treewidgee_item = QtGui.QTreeWidgetItem(\
                            self.conf_dialog_layout.file_treewidget,
                            info_str_list)
                        file_exists = True

        self.conf_dialog_layout.file_gbox.setEnabled(file_exists)
        self.conf_dialog_layout.interleave_cbx.setEnabled(len(checked_items) > 3)

        num_samples = len(self.sample_items)
        num_collections = len(collection_items)

        self.conf_dialog_layout.summary_treewidget.resizeColumnToContents(0)
        self.conf_dialog_layout.summary_label.setText(\
             "Collecting " + str(num_collections) + \
             " collection(s) on " + str(num_samples) + \
             " sample(s) resulting in " + \
             str(num_images) + " image(s).")


    def continue_button_click(self):
        """
        Descript. :
        """
        for item in self.checked_items:
            item_model = item.get_model()
            acq_parameters = None 
          
            if isinstance(item_model, queue_model_objects.DataCollection):
                acq_parameters = item_model.acquisitions[0].acquisition_parameters
            elif isinstance(item_model, queue_model_objects.Advanced):
                acq_parameters = item_model.reference_image_collection.\
                     acquisitions[0].acquisition_parameters 
            elif isinstance(item_model, queue_model_objects.TaskGroup):
                try:
                   item_model.interleave_num_images = \
                      int(self.conf_dialog_layout.\
                      interleave_images_num_ledit.text())
                except:
                   pass
            
            if acq_parameters: 
                acq_parameters.take_snapshots = int(self.conf_dialog_layout.\
                    take_snapshots_combo.currentText())
                acq_parameters.take_dark_current = self.conf_dialog_layout.\
                    force_dark_cbx.isChecked()
                acq_parameters.skip_existing_images = self.conf_dialog_layout.\
                    skip_existing_images_cbx.isChecked()
                
        self.continueClickedSignal.emit(self.sample_items, self.checked_items)
        self.accept()

    def cancel_button_click(self):
        """
        Descript. :
        """
        self.reject()
