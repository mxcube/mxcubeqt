import os
import qt
import qtui
import queue_model_objects

from widgets.data_path_widget import DataPathWidget
from McaSpectrumBrick import McaSpectrumBrick


class XRFSpectrumParametersWidget(qt.QWidget):
    def __init__(self, parent=None, name="xrf_spectrum_tab_widget"):
        qt.QWidget.__init__(self, parent, name)

        # Data Attributes
        self.xrf_spectrum_hwobj = None
        self.xrf_spectrum = queue_model_objects.XRFSpectrum()
        self._tree_view_item = None

        self.data_path_widget = DataPathWidget(self)
        self.other_parameters_gbox = qt.QHGroupBox("Other parameters", self)
        self.count_time_label = qt.QLabel("Count time:", self.other_parameters_gbox)
        self.count_time_ledit = qt.QLineEdit(
            self.other_parameters_gbox, "count_time_ledit"
        )
        self.count_time_ledit.setFixedWidth(50)

        spacer = qt.QWidget(self.other_parameters_gbox)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)

        widget_ui = os.path.join(
            os.path.dirname(__file__), "ui_files/snapshot_widget_layout.ui"
        )
        widget = qtui.QWidgetFactory.create(widget_ui)
        widget.reparent(self, qt.QPoint(0, 0))
        self.position_widget = widget
        self.position_widget.setFixedSize(457, 350)
        # self.position_widget.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)

        self.mca_spectrum = McaSpectrumBrick(self)
        self.mca_spectrum.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self.mca_spectrum.setMinimumHeight(700)

        v_layout = qt.QVBoxLayout(self)
        rone_hlayout = qt.QHBoxLayout(v_layout)
        rone_vlayout = qt.QVBoxLayout(rone_hlayout)
        rone_sv_layout = qt.QVBoxLayout(rone_hlayout)

        rone_vlayout.addWidget(self.data_path_widget)
        rone_vlayout.addWidget(self.other_parameters_gbox)
        rone_vlayout.addStretch()

        rone_sv_layout.addWidget(self.position_widget)
        rone_sv_layout.addStretch()

        v_layout.addWidget(self.mca_spectrum)
        v_layout.addStretch()

        qt.QObject.connect(
            self.data_path_widget.data_path_widget_layout.child("prefix_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._prefix_ledit_change,
        )

        qt.QObject.connect(
            self.data_path_widget.data_path_widget_layout.child("run_number_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._run_number_ledit_change,
        )

        qt.QObject.connect(
            self.count_time_ledit,
            qt.SIGNAL("textChanged(const QString &)"),
            self._count_time_ledit_change,
        )

        qt.QObject.connect(qt.qApp, qt.PYSIGNAL("tab_changed"), self.tab_changed)

    def _prefix_ledit_change(self, new_value):
        self.xrf_spectrum.set_name(str(new_value))
        self._tree_view_item.setText(0, self.xrf_spectrum.get_display_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_spectrum.set_number(int(new_value))
            self._tree_view_item.setText(0, self.xrf_spectrum.get_display_name())

    def _count_time_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_spectrum.set_count_time(float(new_value))

    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        self.xrf_spectrum = item.get_model()
        self.data_path_widget.update_data_model(self.xrf_spectrum.path_template)
        self.count_time_ledit.setText(str(self.xrf_spectrum.count_time))

        executed = self.xrf_spectrum.is_executed()

        self.data_path_widget.setEnabled(not executed)
        self.other_parameters_gbox.setEnabled(not executed)
        self.mca_spectrum.setEnabled(executed)

        image = self.xrf_spectrum.centred_position.snapshot_image
        if image:
            try:
                w = image.width()
                h = image.height()
                ratio = w / float(h)
                h2 = (
                    self.data_path_widget.height() + self.other_parameters_gbox.height()
                )
                w2 = h2 * ratio
                image = image.scale(w2, h2)
                self.position_widget.child("svideo").setPixmap(qt.QPixmap(image))
            except BaseException:
                pass

    def set_xrf_spectrum_hwobj(self, xrf_spectrum_hwobj):
        self.xrf_spectrum_hwobj = xrf_spectrum_hwobj
        if self.xrf_spectrum_hwobj:
            self.xrf_spectrum_hwobj.connect(
                "xrfSpectrumFinished", self.spectrum_finished
            )

    def spectrum_finished(self, mcaData, mcaCalib, mcaConfig):
        self.mca_spectrum.setData(mcaData, mcaCalib, mcaConfig)
