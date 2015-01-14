import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys
import ShapeHistory as shape_history

from PeriodicTableBrick import PeriodicTableBrick
from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget


class CreateEnergyScanWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Energy-scan')

        # Data attributes
        self.init_models()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 5, "main_v_layout")
        h_box = qt.QHGroupBox('Available elements', self)
        self.periodic_table = PeriodicTableBrick(h_box)
        font = self.periodic_table.font()
        font.setPointSize(8)
        self.periodic_table.setFont(font)
        
        h_box.setMaximumWidth(470)
        h_box.setMaximumHeight(310)

        self._data_path_gbox = qt.QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = 'vertical')

        v_layout.addWidget(h_box)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch()


        self.connect(self._data_path_widget.data_path_widget_layout.child('prefix_ledit'), 
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)


        self.connect(self._data_path_widget.data_path_widget_layout.child('run_number_ledit'),
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)
        
        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)


    def init_models(self):
        CreateTaskBase.init_models(self)
        self.enery_scan = queue_model_objects.EnergyScan()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = 'raw'


    def set_energy_scan_hwobj(self, energy_scan_hwobj):
        self.periodic_table.periodicTable.\
            setElements(energy_scan_hwobj.getElements())


    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        escan_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.EnergyScanQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)    

            if escan_model.get_path_template():
                self._path_template = escan_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not(isinstance(tree_item, queue_item.SampleQueueItem) or \
                     isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)):
            self.setDisabled(True)


    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)
        
        selected_shapes = self._shape_history.selected_shapes
        for shape in selected_shapes:
            if isinstance(shape, shape_history.Line):
                base_result = False
 
        selected_edge = False
        
        if self.periodic_table.current_edge:
            selected_edge = True
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.") 

        return base_result and selected_edge


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        data_collections = []

        if self.periodic_table.current_edge:
            
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = self._shape_history.get_snapshot([])
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, shape_history.Point):
                    snapshot = self._shape_history.\
                               get_snapshot([shape.qub_point])

                    cpos = copy.deepcopy(shape.get_centred_positions()[0])
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)
           
            energy_scan = queue_model_objects.EnergyScan(sample,
                                                         path_template,
                                                         cpos)
            energy_scan.set_name(path_template.get_prefix())
            energy_scan.set_number(path_template.run_number)
            energy_scan.element_symbol = self.periodic_table.current_element
            energy_scan.edge = self.periodic_table.current_edge

            data_collections.append(energy_scan)
            self._path_template.run_number += 1
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
