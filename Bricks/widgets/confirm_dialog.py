import os
import qt
import queue_item
import queue_model_objects_v1 as queue_model_objects

from widgets.confirm_dialog_widget_vertical_layout \
     import ConfirmDialogWidgetVerticalLayout

class FileListViewItem(qt.QListViewItem):

    def __init__(self, *args, **kwargs):
        qt.QListViewItem.__init__(self, *args)
        self.brush = qt.QBrush(qt.Qt.black)
        self.__normal_brush = qt.QBrush(qt.Qt.black)
        
        
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


class ConfirmDialog(qt.QDialog):
    def __init__(self, parent = None, name = None, fl = 0):
        qt.QWidget.__init__(self, parent, name, fl)

        # Attributes
        self.ready_event = False
        self.checked_items = []
        self.sample_items = []
        self.files_to_be_written = []
        self.item_run_number_list = []
        self.queue_model_hwobj = None
        
        # Layout
        qt.QVBoxLayout(self)
        self.dialog_layout_widget = ConfirmDialogWidgetVerticalLayout(self)
        #self.dialog_layout_widget.child('take_snapshosts_cbx').hide()
        self.dialog_layout_widget.child('file_list_view').setSorting(-1)
        self.layout().addWidget(self.dialog_layout_widget)

        qt.QObject.connect(self.dialog_layout_widget.continue_button,
                           qt.SIGNAL("clicked()"),
                           self.continue_button_click)

        qt.QObject.connect(self.dialog_layout_widget.cancel_button,
                           qt.SIGNAL("clicked()"),
                           self.cancel_button_click)

        self.dialog_layout_widget.force_dark_cbx.setOn(True)

        self.dialog_layout_widget.missing_one_cbx.hide()
        self.dialog_layout_widget.missing_two_cbx.hide()
        self.setCaption('Confirm collection')


    def set_plate_mode(self, plate_mode):
        self.dialog_layout_widget.snapshots_list = [1,0] if plate_mode else [4,1,2,0]
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
            if isinstance(item, queue_item.SampleQueueItem):
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
            acq_params = None
            if isinstance(item.get_model(), queue_model_objects.DataCollection):
                acq_params = item.get_model().acquisitions[0].acquisition_parameters
            elif isinstance(item.get_model(), queue_model_objects.Characterisation):
                acq_params = item.get_model().reference_image_collection.acquisitions[0].acquisition_parameters
            if acq_params is None:
                continue
            acq_params.take_snapshots = int(self.dialog_layout_widget.take_snapshots_cbox.currentText())
            acq_params.take_dark_current = self.dialog_layout_widget.force_dark_cbx.isOn()
            acq_params.skip_existing_images = self.dialog_layout_widget.skip_existing_images_cbx.isOn()
        
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
