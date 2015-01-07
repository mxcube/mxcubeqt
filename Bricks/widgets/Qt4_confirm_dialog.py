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
     import Qt4_ConfirmDialogWidgetVerticalLayout


class Qt4_FileListViewItem(QtGui.QTreeWidgetItem):

    def __init__(self, *args, **kwargs):
        QtGui.QListViewItem.__init__(self, *args)
        self.brush = QtGui.QBrush(qt.Qt.black)
        self.__normal_brush = QtGui.QBrush(QtCore.Qt.black)
        
        
    def paintCell(self, painter, color_group, column, width, align):
        try:
            painter.save()
            
            color_group = qt.QColorGroup(color_group)
            color_group.setColor(qt.QColorGroup.Text, self.brush.color())
            color_group.setBrush(qt.QColorGroup.Text, self.brush)
        
            qt.QListViewItem.paintCell(self, painter, color_group, 
                                       column, width, align)
        finally:
            painter.restore()


    def set_brush(self, qt_brush):
        self.brush = qt_brush


class Qt4_ConfirmDialog(QtGui.QDialog):
    def __init__(self, parent = None, name = None, fl = 0):
        QtGui.QWidget.__init__(self, parent, 
              QtCore.Qt.WindowFlags(fl | QtCore.Qt.WindowStaysOnTopHint))

        if name is not None:
            self.setObjectName(name) 

        # Attributes
        self.ready_event = False
        self.checked_items = []
        self.sample_items = []
        self.files_to_be_written = []
        self.item_run_number_list = []
        self.queue_model_hwobj = None
        
        # Layout
        self.main_layout = QtGui.QVBoxLayout(self)
        self.dialog_layout_widget = Qt4_ConfirmDialogWidgetVerticalLayout(self)
        #self.dialog_layout_widget.child('take_snapshosts_cbx').hide()
        """self.dialog_layout_widget.child('file_list_view').setSorting(-1)"""

        self.main_layout.addWidget(self.dialog_layout_widget)
        self.setLayout(self.main_layout)

        QtCore.QObject.connect(self.dialog_layout_widget.continue_button,
                               QtCore.SIGNAL("clicked()"),
                               self.continue_button_click)

        QtCore.QObject.connect(self.dialog_layout_widget.cancel_button,
                               QtCore.SIGNAL("clicked()"),
                               self.cancel_button_click)

        self.dialog_layout_widget.force_dark_cbx.setOn(True)

        self.dialog_layout_widget.missing_one_cbx.hide()
        self.dialog_layout_widget.missing_two_cbx.hide()
        self.setWindowTitle('Confirm collection')


    def set_plate_mode(self, plate_mode):
        self.dialog_layout_widget.snapshots_list = [0,1] if plate_mode else [0,1,2,4]
        self.dialog_layout_widget.languageChange()
 
 
    def disable_dark_current_cbx(self):
        self.dialog_layout_widget.force_dark_cbx.setEnabled(False)
        self.dialog_layout_widget.force_dark_cbx.setOn(False)


    def enable_dark_current_cbx(self):
        self.dialog_layout_widget.force_dark_cbx.setEnabled(True)
        self.dialog_layout_widget.force_dark_cbx.setOn(True)
        

    def set_items(self, checked_items):
        self.sample_items = []
        self.files_to_be_written = []
        self.checked_items = checked_items
        collection_items = []
        current_sample_item = None
        num_images = 0

        self.dialog_layout_widget.file_list_view.clear()

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

                for fp in file_paths:
                    (dir_name, f_name) = os.path.split(fp)
                    sample_name = current_sample_item.get_model().get_display_name()

                    if sample_name is '':
                        sample_name = current_sample_item.get_model().loc_str

                    last_item =  self.dialog_layout_widget.child('file_list_view').lastItem()
                    fl = FileListViewItem(self.dialog_layout_widget.file_list_view,
                                          last_item, sample_name, dir_name, f_name)

                    if os.path.isfile(fp):
                            fl.set_brush(qt.QBrush(qt.Qt.red))

        num_samples = len(self.sample_items)
        num_collections = len(collection_items)

        self.dialog_layout_widget.\
            summary_label.setText("Collecting " + str(num_collections) + \
                                  " collection(s) on " + str(num_samples) + \
                                  " sample(s) resulting in " + \
                                  str(num_images) + " image(s).")


    def continue_button_click(self):
        for item in self.checked_items:
            if isinstance(item.get_model(), queue_model_objects.DataCollection):
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_snapshots = int(self.dialog_layout_widget.take_snapshots_cbox.currentText())
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_dark_current = self.dialog_layout_widget.force_dark_cbx.isOn()
                item.get_model().acquisitions[0].acquisition_parameters.\
                    skip_existing_images = self.dialog_layout_widget.skip_existing_images_cbx.isOn()
        
        self.emit(qt.PYSIGNAL("continue_clicked"), (self.sample_items, self.checked_items))
        self.accept()


    def cancel_button_click(self):
#         for item, run_number in self.item_run_number_list:
#             item.get_model().set_number(run_number)
#             path_template = item.get_model().get_path_template()
#             path_template.run_number = run_number
                    
        self.reject()


if __name__ == "__main__":
    a = qt.QApplication(sys.argv)
    qt.QObject.connect(a, qt.SIGNAL("lastWindowClosed()"),
                       a, qt.SLOT("quit()"))
    
    w = ConfirmDialog()
    #a.setMainWidget(w)
    w.setModal(True)
    w.show()
    a.exec_loop()
