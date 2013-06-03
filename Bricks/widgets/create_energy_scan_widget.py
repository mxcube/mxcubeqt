import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys

#from PyMca import QPeriodicTable
from PeriodicTableBrick import PeriodicTableBrick
from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout

class CreateEnergyScanWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Energy-scan')

        # Data attributes
        self.enery_scan = queue_model_objects.EnergyScan()
        self._path_template = queue_model_objects.PathTemplate()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 5, "main_v_layout")
        h_box = qt.QHGroupBox('Available elements', self)
        self.periodic_table = PeriodicTableBrick(h_box) #QPeriodicTable.QPeriodicTable(h_box)
        font = self.periodic_table.font()
        font.setPointSize(8)
        self.periodic_table.setFont(font)
        
        h_box.setMaximumWidth(454)
        h_box.setMaximumHeight(300)

        self._data_path_gbox = qt.QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = DataPathWidgetVerticalLayout)

        self._data_path_widget.data_path_widget_layout.file_name_label.setText('')
        self._data_path_widget.data_path_widget_layout.file_name_value_label.hide()


        v_layout.addWidget(h_box)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch()


    def set_energy_scan_hw_obj(self, mnemonic):
        self.periodic_table['mnemonic'] = mnemonic
        self.periodic_table.propertyChanged('mnemonic', '', mnemonic)


    def get_prefix_type(self):
        return 'escan'


    def approve_creation(self):
        if self.periodic_table.current_edge:
            return True
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.") 
            return False


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, dcg, sample):
        data_collections = []

        if self.periodic_table.current_edge:
            path_template = copy.deepcopy(self._path_template)
            
            energy_scan = qeue_model.EnergyScan(dcg, sample, path_template)
            energy_scan.set_name(path_template.prefix + '_' \
                                 + str(path_template.run_number))
            energy_scan.symbol = self.periodic_table.current_element
            energy_scan.edge = self.periodic_table.current_edge

            data_collections.append(energy_scan)
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.") 

        return data_collections


if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    widget = CreateEnergyScanWidget()
    app.setMainWidget(widget)
    widget.show()
    app.exec_loop()
