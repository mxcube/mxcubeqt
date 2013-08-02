import os
import queue_model_objects_v1 as queue_model_objects
import logging
import copy

from qt import *
from qttable import QTable, QTableItem

from widgets.data_path_widget import DataPathWidget
from widgets.acquisition_widget import AcquisitionWidget
from acquisition_widget_horizontal_layout import\
    AcquisitionWidgetHorizontalLayout
from widgets.widget_utils import DataModelInputBinder
from widgets.snapshot_widget_layout import\
    SnapshotWidgetLayout

from widgets.processing_widget \
    import ProcessingWidget

from queue_model_objects_v1 import COLLECTION_ORIGIN
from BlissFramework.Utils import widget_colors
from BlissFramework import Icons


class DCParametersWidget(QWidget):
    def __init__(self, parent = None, name = "parameter_widget"):
        QWidget.__init__(self, parent, name)
        self._data_collection = None
        self.add_dc_cb = None
        self._tree_view_item = None
        self.queue_controller_hwobj = None
        self.queue_model = None


        self.caution_pixmap = Icons.load("Caution2.png")
        self.path_widget = DataPathWidget(self, 'dc_params_path_widget')
        self.acq_gbox = QVGroupBox("Acquisition", self)
        self.acq_gbox.setInsideMargin(2)
        self.acq_widget = AcquisitionWidget(self.acq_gbox, 
                          layout = 'horizontal')

        self.acq_widget.setFixedHeight(170)

        self.position_widget = SnapshotWidgetLayout(self)
        self._processing_gbox = QVGroupBox('Processing', self, 
                                           'processing_gbox')

        self.processing_widget = ProcessingWidget(self._processing_gbox)
        
        v_layout = QVBoxLayout(self, 11, 10, "main_layout")
        rone_hlayout = QHBoxLayout(v_layout, 10, "rone")
        rone_vlayout = QVBoxLayout(rone_hlayout)
        rone_sv_layout = QVBoxLayout(rone_hlayout)
        
        rone_vlayout.addWidget(self.path_widget)
        rone_vlayout.addWidget(self.acq_gbox)
        rtwo_hlayout = QHBoxLayout(rone_vlayout, 10, "rtwo")
        rone_vlayout.addStretch(10)
        
        rone_sv_layout.addWidget(self.position_widget)
        rone_sv_layout.addStretch(10)
        rone_hlayout.addStretch()

        rtwo_hlayout.addWidget(self._processing_gbox)
        rtwo_hlayout.addStretch(10)
        v_layout.addStretch()


        self.connect(self.acq_widget, PYSIGNAL('mad_energy_selected'),
                     self.mad_energy_selected)

        
        self.connect(self.path_widget.data_path_widget_layout.prefix_ledit, 
                     SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)


        self.connect(self.path_widget.data_path_widget_layout.run_number_ledit,
                     SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)

        self.connect(self.path_widget,
                     PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)


    def set_bl_config(self, bl_config):
        self.acq_widget.set_bl_config(bl_config)


    def _prefix_ledit_change(self, new_value):
        prefix = self._data_collection.acquisitions[0].\
                 path_template.get_prefix()
        self._data_collection.set_name(prefix)
        self._tree_view_item.setText(0, self._data_collection.get_name())
        

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._data_collection.set_number(int(new_value))
            self._tree_view_item.setText(0, self._data_collection.get_name())


    def handle_path_conflict(self, widget, new_value):
        path_template = self._data_collection.acquisitions[0].path_template
        path_conflict = self.queue_model_hwobj.\
                        check_for_path_collisions(path_template)

        if new_value != '':
            if path_conflict:
                logging.getLogger("user_level_log").\
                    error('The current path settings will overwrite data' +\
                          ' from another task. Correct the problem before collecting')

                widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                self._tree_view_item.setPixmap(0, self.caution_pixmap)
            else:
                widget.setPaletteBackgroundColor(widget_colors.WHITE)
                self._tree_view_item.setPixmap(0, QPixmap())


    def __add_data_collection(self):
        return self.add_dc_cb(self._data_collection, self.collection_type)

    
    def mad_energy_selected(self, name, energy, state):
        path_template = self._data_collection.\
            acquisitions[0].path_template

        if state:
            path_template.mad_prefix = name
        else:
            path_template.mad_prefix = ''
            
        self.path_widget.set_prefix(path_template.base_prefix)


    def populate_parameter_widget(self, item):
        data_collection = item.get_model()
        self._tree_view_item = item
        self._data_collection = data_collection
        self._acquisition_mib = DataModelInputBinder(self._data_collection.\
                                acquisitions[0].acquisition_parameters)
        
        self.acq_widget.update_data_model(data_collection.acquisitions[0].\
                                          acquisition_parameters,
                                          data_collection.acquisitions[0].\
                                          path_template)
        
        self.path_widget.update_data_model(data_collection.\
                                           acquisitions[0].path_template)


        self.processing_widget.update_data_model(data_collection.\
                                                 processing_parameters)

        self.acq_widget.set_energies(data_collection.crystal.energy_scan_result)

        if data_collection.acquisitions[0].acquisition_parameters.\
                centred_position.snapshot_image:
            image = data_collection.acquisitions[0].\
                acquisition_parameters.centred_position.snapshot_image
            image = image.scale(427, 320)
            self.position_widget.svideo.setPixmap(QPixmap(image))

        invalid = self._acquisition_mib.validate_all()

        if invalid:
            msg = "This data collection has one or more incorrect parameters,"+\
                " correct the fields marked in red to solve the problem."

            logging.getLogger("user_level_log").\
                warning(msg)
