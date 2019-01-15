#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os

import QtImport
from gui.utils import Icons


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


class XrayImagingResultsWidget(QtImport.QWidget):
    def __init__(self, parent=None, name=None, fl=0, xray_imaging_params=None):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self.beamline_setup_hwobj = None
        self.xray_imaging_hwobj = None

        # Internal variables --------------------------------------------------
        self.current_image_num = 0
        self.total_image_num = 0

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        results_gbox = QtImport.QGroupBox("Results", self)
        self.live_view_cbox = QtImport.QCheckBox("Live view", results_gbox)
        self.live_view_cbox.setChecked(True)
        self.graphics_view_widget = QtImport.QWidget(results_gbox)
        self._results_widget = QtImport.load_ui_file(
            "xray_imaging_results_widget_layout.ui"
        )
        tools_gbox = QtImport.QGroupBox("Tools", self)
        self.start_centering_button = QtImport.QPushButton(
            "Start centering", tools_gbox
        )
        self.accept_centering_button = QtImport.QPushButton(
            "Create centering point", tools_gbox
        )

        # Layout --------------------------------------------------------------
        self._graphics_view_widget_vlayout = QtImport.QVBoxLayout(
            self.graphics_view_widget
        )
        self._graphics_view_widget_vlayout.setSpacing(0)
        self._graphics_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)

        __results_gbox_vlayout = QtImport.QVBoxLayout(results_gbox)
        __results_gbox_vlayout.addWidget(self.live_view_cbox)
        __results_gbox_vlayout.addWidget(self.graphics_view_widget)
        __results_gbox_vlayout.addWidget(self._results_widget)
        __results_gbox_vlayout.setSpacing(2)
        __results_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        __tools_gbox_vlayout = QtImport.QHBoxLayout(tools_gbox)
        __tools_gbox_vlayout.addWidget(self.start_centering_button)
        __tools_gbox_vlayout.addWidget(self.accept_centering_button)
        __tools_gbox_vlayout.addStretch()
        __tools_gbox_vlayout.setSpacing(2)
        __tools_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        __main_vlayout = QtImport.QVBoxLayout(self)
        __main_vlayout.addWidget(results_gbox)
        __main_vlayout.addWidget(tools_gbox)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.live_view_cbox.stateChanged.connect(self.live_view_state_changed)

        self._results_widget.data_browse_button.clicked.connect(
            self.data_browse_button_clicked
        )
        self._results_widget.ff_browse_button.clicked.connect(
            self.ff_browse_button_clicked
        )
        self._results_widget.load_images_button.clicked.connect(
            self.load_images_button_clicked
        )

        self._results_widget.first_image_button.clicked.connect(
            self.first_image_button_clicked
        )
        self._results_widget.prev_image_button.clicked.connect(
            self.prev_image_button_clicked
        )
        self._results_widget.next_image_button.clicked.connect(
            self.next_image_button_clicked
        )
        self._results_widget.last_image_button.clicked.connect(
            self.last_image_button_clicked
        )
        self._results_widget.minus_quarter_button.clicked.connect(
            self.minus_quater_button_clicked
        )
        self._results_widget.last_image_button.clicked.connect(
            self.last_image_button_clicked
        )
        self._results_widget.plus_quarter_button.clicked.connect(
            self.plus_quater_button_clicked
        )

        self._results_widget.image_slider.valueChanged.connect(
            self.slider_value_changed
        )
        self._results_widget.image_spinbox.valueChanged.connect(
            self.spinbox_value_changed
        )

        self._results_widget.play_button.clicked.connect(self.play_button_clicked)
        self._results_widget.stop_button.clicked.connect(self.stop_button_clicked)
        self._results_widget.repeat_cbox.stateChanged.connect(self.repeat_state_changed)
        self._results_widget.ff_apply_cbox.stateChanged.connect(
            self.ff_apply_state_changed
        )

        self.start_centering_button.clicked.connect(self.start_centering_clicked)
        self.accept_centering_button.clicked.connect(self.accept_centering_clicked)

        # Other ---------------------------------------------------------------
        self._results_widget.first_image_button.setIcon(Icons.load_icon("VCRRewind"))
        self._results_widget.prev_image_button.setIcon(Icons.load_icon("VCRPlay4"))
        self._results_widget.next_image_button.setIcon(Icons.load_icon("VCRPlay2"))
        self._results_widget.last_image_button.setIcon(
            Icons.load_icon("VCRFastForward2")
        )
        self._results_widget.play_button.setIcon(Icons.load_icon("VCRPlay"))
        self._results_widget.stop_button.setIcon(Icons.load_icon("Stop2"))

    def populate_widget(self, item):
        data_model = item.get_model()
        acq_params = data_model.acquisition.acquisition_parameters
        imaging_params = data_model.xray_imaging_parameters
        path_template = data_model.acquisition.path_template
        self._results_widget.data_path_ledit.setText(path_template.get_image_path() % 1)
        if imaging_params.ff_pre or imaging_params.ff_post:
            ff_file_path = os.path.join(
                path_template.directory, "ff_" + path_template.get_image_file_name() % 1
            )
            self._results_widget.ff_path_ledit.setText(ff_file_path)
            self._results_widget.ff_path_label.setEnabled(True)
            self._results_widget.ff_path_ledit.setEnabled(True)
        else:
            self._results_widget.ff_path_ledit.setText("")
            self._results_widget.ff_path_label.setEnabled(False)
            self._results_widget.ff_path_ledit.setEnabled(False)

        self.xray_imaging_hwobj.set_osc_start(acq_params.osc_start)

    def set_beamline_setup_hwobj(self, beamline_setup_hwobj):
        self.beamline_setup_hwobj = beamline_setup_hwobj
        self.xray_imaging_hwobj = beamline_setup_hwobj.xray_imaging_hwobj
        if self.xray_imaging_hwobj is not None:
            self.xray_imaging_hwobj.connect("imageInit", self.image_init)
            self.xray_imaging_hwobj.connect("imageLoaded", self.image_loaded)

            self.graphics_view = self.xray_imaging_hwobj.get_graphics_view()
            self._graphics_view_widget_vlayout.addWidget(self.graphics_view)
            self.graphics_view_widget.setFixedSize(
                self.graphics_view.scene().width(), self.graphics_view.scene().height()
            )

            self.setDisabled(False)
        else:
            self.setDisabled(True)

    def image_init(self, image_descr_dict):
        self.total_image_num = image_descr_dict
        self.current_image_num = 0
        self._results_widget.image_slider.setMinimum(0)
        self._results_widget.image_slider.setMaximum(self.total_image_num - 1)
        self._results_widget.image_spinbox.setMinimum(1)
        self._results_widget.image_spinbox.setMaximum(self.total_image_num)
        self.refresh_gui()

    def image_loaded(self, index):
        self.current_image_num = index
        # self._results_widget.data_path_ledit.setText(filename)
        self.refresh_gui()

    def live_view_state_changed(self, state):
        self.xray_imaging_hwobj.set_live_view_state(state)

    def ff_apply_state_changed(self, state):
        self.xray_imaging_hwobj.set_ff_apply(state)

    def data_browse_button_clicked(self):
        file_dialog = QtImport.QFileDialog(self)
        # TODO get from datapath widget
        # file_dialog.setNameFilter("%s*" % self._base_image_dir)
        base_image_dir = os.environ["HOME"]

        selected_filename = str(
            file_dialog.getOpenFileName(self, "Select an image", base_image_dir)
        )
        self._results_widget.data_path_ledit.setText(selected_filename)

    def ff_browse_button_clicked(self):
        file_dialog = QtImport.QFileDialog(self)
        # TODO get from datapath widget
        # file_dialog.setNameFilter("%s*" % self._base_image_dir)
        base_image_dir = os.environ["HOME"]

        selected_filename = str(
            file_dialog.getOpenFileName(self, "Select an image", base_image_dir)
        )
        self._results_widget.ff_path_ledit.setText(selected_filename)

    def load_images_button_clicked(self):
        self.xray_imaging_hwobj.load_images(
            str(self._results_widget.data_path_ledit.text()),
            str(self._results_widget.ff_path_ledit.text()),
        )

    def first_image_button_clicked(self):
        self.xray_imaging_hwobj.display_image(0)

    def prev_image_button_clicked(self):
        self.xray_imaging_hwobj.display_image(self.current_image_num - 1)

    def next_image_button_clicked(self):
        self.xray_imaging_hwobj.display_image(self.current_image_num + 1)

    def last_image_button_clicked(self):
        self.xray_imaging_hwobj.display_image(self.total_image_num - 1)

    def minus_quater_button_clicked(self):
        self.xray_imaging_hwobj.display_relative_image(-90)

    def plus_quater_button_clicked(self):
        self.xray_imaging_hwobj.display_relative_image(90)

    def slider_value_changed(self, value):
        self.xray_imaging_hwobj.display_image(value)

    def spinbox_value_changed(self, value):
        self.xray_imaging_hwobj.display_image(value - 1)

    def play_button_clicked(self):
        self.xray_imaging_hwobj.play_images(
            repeat=self._results_widget.repeat_cbox.isChecked()
        )

    def stop_button_clicked(self):
        self.xray_imaging_hwobj.stop_image_play()

    def repeat_state_changed(self, state):
        self.xray_imaging_hwobj.set_repeate_image_play(state)

    def start_centering_clicked(self):
        self.xray_imaging_hwobj.start_centering()

    def accept_centering_clicked(self):
        self.beamline_setup_hwobj.shape_history_hwobj.accept_centring()

    def refresh_gui(self):
        self._results_widget.image_slider.blockSignals(True)
        self._results_widget.image_slider.setValue(self.current_image_num)
        self._results_widget.image_slider.blockSignals(False)

        self._results_widget.image_spinbox.blockSignals(True)
        self._results_widget.image_spinbox.setValue(self.current_image_num)
        self._results_widget.image_spinbox.blockSignals(False)

        self._results_widget.prev_image_button.setDisabled(self.current_image_num == 0)
        self._results_widget.next_image_button.setDisabled(
            self.current_image_num == self.total_image_num - 1
        )
