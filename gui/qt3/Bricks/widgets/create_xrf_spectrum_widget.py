import qt
import sys
import logging
import copy
import queue_item
import ShapeHistory as shape_history
import queue_model_objects

from create_task_base import CreateTaskBase
from widgets.widget_utils import DataModelInputBinder
from widgets.data_path_widget import DataPathWidget


class CreateXRFSpectrumWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):
        CreateTaskBase.__init__(self, parent, name, fl, "XRF-spectrum")

        self.count_time = None

        # Data attributes
        self.init_models()
        xrfspectrum_model = queue_model_objects.XRFSpectrum()
        self.xrfspectrum_mib = DataModelInputBinder(xrfspectrum_model)

        # Layout
        v_layout = qt.QVBoxLayout(self, 2, 6, "main_v_layout")

        self._data_path_gbox = qt.QVGroupBox("Data location", self, "data_path_gbox")
        self._data_path_widget = DataPathWidget(
            self._data_path_gbox, data_model=self._path_template, layout="vertical"
        )

        parameters_hor_gbox = qt.QHGroupBox("Parameters", self)

        self.count_time_label = qt.QLabel("Count time", parameters_hor_gbox)
        self.count_time_label.setFixedWidth(83)

        self.count_time_ledit = qt.QLineEdit(
            "1.0", parameters_hor_gbox, "count_time_ledit"
        )
        self.count_time_ledit.setFixedWidth(50)

        self.xrfspectrum_mib.bind_value_update(
            "count_time", self.count_time_ledit, float
        )  # ,

        spacer = qt.QWidget(parameters_hor_gbox)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)

        v_layout.addWidget(self._data_path_gbox)
        v_layout.addWidget(parameters_hor_gbox)
        v_layout.addStretch()

        self.connect(
            self._data_path_widget.data_path_widget_layout.child("run_number_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._run_number_ledit_change,
        )

        self.connect(
            self._data_path_widget.data_path_widget_layout.child("prefix_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._prefix_ledit_change,
        )

        self.connect(
            self._data_path_widget,
            qt.PYSIGNAL("path_template_changed"),
            self.handle_path_conflict,
        )

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = "raw"

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.XRFSpectrumQueueItem):
            xrfspectrum_model = tree_item.get_model()
            self.xrfspectrum_mib.set_model(xrfspectrum_model)

            if xrfspectrum_model.is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if xrfspectrum_model.get_path_template():
                self._path_template = xrfspectrum_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif not (
            isinstance(tree_item, queue_item.SampleQueueItem)
            or isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)
        ):
            self.setDisabled(True)

    def approve_creation(self):
        result = CreateTaskBase.approve_creation(self)
        selected_shapes = self._shape_history.selected_shapes

        for shape in selected_shapes:
            if isinstance(shape, shape_history.Line) or isinstance(
                shape, shape_history.CanvasGrid
            ):
                result = False

        self.count_time = None
        try:
            self.count_time = float(str(self.count_time_ledit.text()))
        except BaseException:
            logging.getLogger("user_level_log").info("Incorrect count time value.")
        return result and self.count_time

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        data_collections = []

        if self.count_time is not None:
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = self._shape_history.get_snapshot([])
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, shape_history.Point):
                    snapshot = self._shape_history.get_snapshot([shape.qub_point])
                    cpos = copy.deepcopy(shape.get_centred_positions()[0])
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)
            xrf_spectrum = queue_model_objects.XRFSpectrum(sample, path_template, cpos)
            xrf_spectrum.set_name(path_template.get_prefix())
            xrf_spectrum.set_number(path_template.run_number)
            xrf_spectrum.count_time = self.count_time
            data_collections.append(xrf_spectrum)

            self._path_template.run_number += 1
        else:
            logging.getLogger("user_level_log").info("Incorrect count time value")

        return data_collections

    # Called by the owning widget (task_toolbox_widget) when
    # one or several centred positions are selected.
    def centred_position_selection(self, positions):
        self._selected_positions = positions

        if len(self._current_selected_items) == 1 and len(positions) == 1:
            item = self._current_selected_items[0]
            pos = positions[0]
            if isinstance(pos, shape_history.Point):
                if isinstance(item, queue_item.XRFSpectrumQueueItem):
                    cpos = pos.get_centred_positions()[0]
                    snapshot = self._shape_history.get_snapshot([pos.qub_point])
                    cpos.snapshot_image = snapshot
                    item.get_model().centred_position = cpos


if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    widget = CreateXRFSpectrumWidget()
    app.setMainWidget(widget)
    widget.show()
    app.exec_loop()
