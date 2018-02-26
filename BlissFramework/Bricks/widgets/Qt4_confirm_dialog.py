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

from QtImport import *

import Qt4_queue_item
import queue_model_objects_v1 as queue_model_objects
from BlissFramework.Utils import Qt4_widget_colors


class ConfirmDialog(QDialog):
    """
    Descript. :
    """
    continueClickedSignal = pyqtSignal(list, list)

    def __init__(self, parent=None, name=None, flags=0):
        """
        Descript. :
        """

        QDialog.__init__(self, parent, Qt.WindowFlags(flags | Qt.WindowStaysOnTopHint))

        if name is not None:
            self.setObjectName(name) 

        # Internal variables --------------------------------------------------
        self.checked_items = []
        self.sample_items = []
       
        # Graphic elements ---------------------------------------------------- 
        self.conf_dialog_layout = loadUi(os.path.join(\
             os.path.dirname(__file__),
             "ui_files/Qt4_confirmation_dialog_layout.ui"))

        # Layout --------------------------------------------------------------
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.conf_dialog_layout)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0) 

        # Qt signal/slot connections ------------------------------------------
        self.conf_dialog_layout.continue_button.clicked.connect(\
             self.continue_button_click)
        self.conf_dialog_layout.cancel_button.clicked.connect(\
             self.cancel_button_click)

        # SizePolicies --------------------------------------------------------
        self.setMinimumWidth(1200)

        # Other --------------------------------------------------------------- 
        self.setWindowTitle('Confirm collection')

    def set_plate_mode(self, plate_mode):
        """Sets plate mode"""
        if plate_mode:
            snapshot_count = [0, 1]
            self.conf_dialog_layout.take_video_cbx.setEnabled(False)
            self.conf_dialog_layout.take_video_cbx.setChecked(False)
        else:
            snapshot_count = [0, 1, 2, 4]
        self.conf_dialog_layout.take_snapshots_combo.clear()
        for item in snapshot_count:
            self.conf_dialog_layout.take_snapshots_combo.addItem(str(item))        
        self.conf_dialog_layout.take_snapshots_combo.setCurrentIndex(1)
 
    def disable_dark_current_cbx(self):
        self.conf_dialog_layout.force_dark_cbx.setEnabled(False)
        self.conf_dialog_layout.force_dark_cbx.setChecked(False)

    def enable_dark_current_cbx(self):
        self.conf_dialog_layout.force_dark_cbx.setEnabled(True)
        self.conf_dialog_layout.force_dark_cbx.setChecked(True)
        
    def set_items(self, checked_items):
        """Populates information about items to be collected"""
        self.sample_items = []
        self.checked_items = checked_items

        collection_items = []
        current_sample_item = None
        sample_treewidget_item = None
        collection_group_treewidget_item = None
        num_images = 0
        file_exists = False
        interleave_items = 0

        self.conf_dialog_layout.summary_treewidget.clear()
        self.conf_dialog_layout.file_treewidget.clear()
        self.conf_dialog_layout.interleave_cbx.setChecked(False)
        self.conf_dialog_layout.interleave_images_num_ledit.setText("")
        self.conf_dialog_layout.inverse_cbx.setChecked(False)
        self.conf_dialog_layout.inverse_beam_num_images_ledit.setText("")

        for item in checked_items:
            #item_type_name = ""
            info_str_list = []
            acq_parameters = None
            path_template = None
            item_model = item.get_model()
            item_type_name = item_model.get_display_name()
            
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.sample_items.append(item)
                current_sample_item = item
                info_str_list.append(item_model.get_name())
                if item.mounted_style:
                    info_str_list.append("Already mounted")
                else:
                    info_str_list.append("Sample mounting") 
                sample_treewidget_item = QTreeWidgetItem(\
                   self.conf_dialog_layout.summary_treewidget,
                   info_str_list)
                for col in range(13):
                    sample_treewidget_item.setBackground(col, \
                      QBrush(Qt4_widget_colors.TREE_ITEM_SAMPLE))
                sample_treewidget_item.setExpanded(True)
            elif isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem): 
                info_str_list.append(item_type_name) 
                collection_group_treewidget_item = QTreeWidgetItem(\
                   sample_treewidget_item,
                   info_str_list)
                collection_group_treewidget_item.setExpanded(True)
            elif isinstance(item, Qt4_queue_item.SampleCentringQueueItem):
                info_str_list.append(item_type_name)
                QTreeWidgetItem(collection_group_treewidget_item,
                                      info_str_list) 
            elif isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                acq_parameters = item_model.acquisitions[0].\
                     acquisition_parameters
                if not item_model.is_helical() and not item_model.is_mesh():
                    interleave_items += 1
            elif isinstance(item, Qt4_queue_item.CharacterisationQueueItem):
                acq_parameters = item_model.reference_image_collection.\
                    acquisitions[0].acquisition_parameters
                self.conf_dialog_layout.take_snapshots_combo.setCurrentIndex(\
                    self.conf_dialog_layout.take_snapshots_combo.count() - 1)
            elif isinstance(item, Qt4_queue_item.XrayCenteringQueueItem):
                acq_parameters = item_model.reference_image_collection.\
                     acquisitions[0].acquisition_parameters

            path_template = item_model.get_path_template()

            if acq_parameters and path_template:
                info_str_list.append(item_type_name)
                info_str_list.append("")
                info_str_list.append(path_template.directory)
                #This part is also in Qt4_data_path_widget. Mote to PathTemplate
                file_name = path_template.get_image_file_name()
                file_name = file_name.replace('%' + path_template.precision + \
                      'd', int(path_template.precision) * '#' )
                file_name = file_name.strip(' ')
                info_str_list.append(file_name)
                info_str_list.append("%.3f keV" %acq_parameters.energy)
                info_str_list.append("%.2f A" %acq_parameters.resolution)
                info_str_list.append("%.2f %%" %acq_parameters.transmission)
                info_str_list.append("%.1f" %acq_parameters.osc_start)
                info_str_list.append(str(acq_parameters.osc_range))
                info_str_list.append(str(acq_parameters.num_images))
                info_str_list.append("%s s" % str(acq_parameters.exp_time))
                info_str_list.append(str(acq_parameters.num_images * \
                                         acq_parameters.osc_range))
                info_str_list.append("%s s" % str(acq_parameters.num_images * \
                                                  acq_parameters.exp_time))

                collection_treewidget_item = QTreeWidgetItem(\
                     collection_group_treewidget_item, info_str_list)
                for col in range(13):
                    collection_treewidget_item.setBackground(col, \
                      QBrush(Qt4_widget_colors.TREE_ITEM_COLLECTION))  
             
                collection_items.append(item)
                file_paths = path_template.get_files_to_be_written()
                num_images += acq_parameters.num_images

                if len(file_paths) > 20:
                    file_paths = (file_paths[:20])

                for file_path in file_paths:
                    if os.path.exists(file_path):
                        (dir_name, file_name) = os.path.split(file_path)
                        sample_name = current_sample_item.get_model().\
                            get_display_name()
                        if sample_name is '':
                            sample_name = current_sample_item.get_model().loc_str
                        file_str_list = []
                        file_str_list.append(sample_name)
                        file_str_list.append(dir_name)
                        file_str_list.append(file_name)

                        file_treewidgee_item = QTreeWidgetItem(\
                             self.conf_dialog_layout.file_treewidget,
                             file_str_list)
                        file_treewidgee_item.setTextColor(1, Qt.red)
                        file_treewidgee_item.setTextColor(2, Qt.red)
                        file_exists = True

        self.conf_dialog_layout.file_gbox.setEnabled(file_exists)
        self.conf_dialog_layout.interleave_cbx.setEnabled(interleave_items > 1)
        self.conf_dialog_layout.inverse_cbx.setEnabled(interleave_items == 1)

        num_samples = len(self.sample_items)
        num_collections = len(collection_items)

        for col_index in range(self.conf_dialog_layout.summary_treewidget.columnCount()):
            if col_index != 2:
                self.conf_dialog_layout.summary_treewidget.\
                     resizeColumnToContents(col_index)
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
            elif isinstance(item_model, queue_model_objects.Characterisation):
                acq_parameters = item_model.reference_image_collection.\
                     acquisitions[0].acquisition_parameters
            elif isinstance(item_model, queue_model_objects.XrayCentering):
                acq_parameters = item_model.reference_image_collection.\
                     acquisitions[0].acquisition_parameters 
            elif isinstance(item_model, queue_model_objects.TaskGroup):
                try:
                    item_model.interleave_num_images = \
                      int(self.conf_dialog_layout.\
                      interleave_images_num_ledit.text())
                except:
                    pass
                try:
                    item_model.inverse_beam_num_images = \
                      int(self.conf_dialog_layout.\
                          inverse_beam_num_images_ledit.text())
                except:
                    pass
            if acq_parameters: 
                acq_parameters.take_snapshots = int(self.conf_dialog_layout.\
                    take_snapshots_combo.currentText())
                acq_parameters.take_video = self.conf_dialog_layout.\
                    take_video_cbx.isChecked()
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
