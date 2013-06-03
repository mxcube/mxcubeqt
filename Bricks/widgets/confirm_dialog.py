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
        
        # Layout
        qt.QVBoxLayout(self)
        self.dialog_layout_widget = ConfirmDialogWidgetVerticalLayout(self)
        self.layout().addWidget(self.dialog_layout_widget)

        qt.QObject.connect(self.dialog_layout_widget.continue_button,
                           qt.SIGNAL("clicked()"),
                           self.continue_button_click)

        qt.QObject.connect(self.dialog_layout_widget.cancel_button,
                           qt.SIGNAL("clicked()"),
                           self.cancel_button_click)

        self.dialog_layout_widget.missing_one_cbx.hide()
        self.dialog_layout_widget.missing_two_cbx.hide()


    def set_items(self, checked_items):
        self.sample_items = []
        self.files_to_be_written = []
        self.checked = checked_items
        collection_items = []
        current_sample_item = None
        num_images = 0

        self.dialog_layout_widget.file_list_view.clear()

        for item in checked_items:
            if isinstance(item, queue_item.SampleQueueItem):
                self.sample_items.append(item)
                current_sample_item = item                
            if isinstance(item.get_model(), queue_model_objects.DataCollection) or\
                   isinstance(item.get_model(), queue_model_objects.Characterisation):
                collection_items.append(item)
                file_paths = item.get_model().get_files_to_be_written()
                num_images += len(file_paths)
                
                for fp in file_paths:
                    (dir_name, f_name) = os.path.split(fp)
                    sample_name = current_sample_item.get_model().get_display_name()

                    if sample_name is '':
                        sample_name = current_sample_item.get_model().loc_str
                    
                    fl = FileListViewItem(self.dialog_layout_widget.file_list_view,
                                         sample_name, dir_name, f_name)

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
            if isinstance(item.get_model(), queue_model.DataCollection):
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_snapshots = dialog_layout_widget.take_snapshosts_cbx.isOn()
                item.get_model().acquisitions[0].acquisition_parameters.\
                    take_dark_current = dialog_layout_widget.force_dark_cbx.isOn()
                item.get_model().acquisitions[0].acquisition_parameters.\
                    skip_existing_images = dialog_layout_widget.skip_existing_images_cbx.isOn()
        
        self.emit(qt.PYSIGNAL("continue_clicked"), (self.sample_items,))
        self.accept()


    def cancel_button_click(self):
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
