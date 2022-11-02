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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from os.path import expanduser

from mxcubeqt.utils import qt_import
from mxcubeqt.utils.widget_utils import DataModelInputBinder

from mxcubecore.model import (
    queue_model_objects,
    queue_model_enumerables,
)

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class ProcessingWidget(qt_import.QWidget):

    enableProcessingSignal = qt_import.pyqtSignal(bool, bool)

    def __init__(self, parent=None, name=None, fl=0, data_model=None):

        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        if data_model is None:
            self._model = queue_model_objects.ProcessingParameters()
        else:
            self._model = data_model

        self._model_mib = DataModelInputBinder(self._model)

        self.processing_widget = qt_import.load_ui_file(
            "processing_widget_vertical_layout.ui"
        )

        self.main_layout = qt_import.QVBoxLayout(self)
        self.main_layout.addWidget(self.processing_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.processing_widget.space_group_combo.addItems(
            queue_model_enumerables.XTAL_SPACEGROUPS
        )

        self._model_mib.bind_value_update(
            "cell_a", self.processing_widget.a_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "cell_alpha", self.processing_widget.alpha_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "cell_b", self.processing_widget.b_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "cell_beta", self.processing_widget.beta_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "cell_c", self.processing_widget.c_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "cell_gamma", self.processing_widget.gamma_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "num_residues", self.processing_widget.num_residues_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "resolution_cutoff", self.processing_widget.resolution_cutoff_ledit, float, None
        )

        self._model_mib.bind_value_update(
            "pdb_file", self.processing_widget.pdb_file_ledit, str, None
        )

        self.processing_widget.space_group_combo.activated.connect(
            self._space_group_change
        )
        self.processing_widget.run_offline_processing_cbox.stateChanged.connect(
            self._run_offline_processing_toggled
        )
        self.processing_widget.run_online_processing_cbox.stateChanged.connect(
            self._run_online_processing_toggled
        )
        self.processing_widget.pdb_file_browse_button.clicked.connect(self._browse_clicked)

        self.processing_widget.resolution_cutoff_label.setHidden(True)
        self.processing_widget.resolution_cutoff_ledit.setHidden(True)
        self.processing_widget.pdb_file_label.setHidden(True)
        self.processing_widget.pdb_file_ledit.setHidden(True)
        self.processing_widget.pdb_file_browse_button.setHidden(True)

        if HWR.beamline.offline_processing_methods:
            cbox_text = "Run offline processing ("
            for method in HWR.beamline.offline_processing_methods:
                cbox_text += "%s, " % method
            cbox_text = cbox_text[:-2] + ")"
            self.processing_widget.run_offline_processing_cbox.setText(cbox_text)
            self.processing_widget.run_offline_processing_cbox.setChecked(HWR.beamline.run_offline_processing)
        else:
            self.processing_widget.run_offline_processing_cbox.setChecked(False)
            self.processing_widget.run_offline_processing_cbox.setEnabled(False)

        if HWR.beamline.online_processing_methods:
            cbox_text = "Run online processing ("
            for method in HWR.beamline.online_processing_methods:
                cbox_text += "%s, " % method
            cbox_text = cbox_text[:-2] + ")"
            self.processing_widget.run_online_processing_cbox.setText(cbox_text)
            self.processing_widget.run_online_processing_cbox.setChecked(HWR.beamline.run_online_processing)
        else:
            self.processing_widget.run_online_processing_cbox.setChecked(False)
            self.processing_widget.run_online_processing_cbox.setEnabled(False)


    def _space_group_change(self, index):
        self._model.space_group = queue_model_enumerables.XTAL_SPACEGROUPS[index]

    def _set_space_group(self, space_group):
        index = 0

        if space_group in queue_model_enumerables.XTAL_SPACEGROUPS:
            index = queue_model_enumerables.XTAL_SPACEGROUPS.index(space_group)

        self._space_group_change(index)
        self.processing_widget.space_group_combo.setCurrentIndex(index)

    def update_data_model(self, model):
        self._model = model
        self._model_mib.set_model(model)
        self._set_space_group(model.space_group)

    def _run_offline_processing_toggled(self, state):
        self.enableProcessingSignal.emit(
            self.processing_widget.run_offline_processing_cbox.isChecked(),
            self.processing_widget.run_online_processing_cbox.isChecked(),
        )

    def _run_online_processing_toggled(self, state):
        self.enableProcessingSignal.emit(
            self.processing_widget.run_offline_processing_cbox.isChecked(),
            self.processing_widget.run_online_processing_cbox.isChecked(),
        )

    def _browse_clicked(self):
        file_dialog = qt_import.QFileDialog(self)

        pdb_filename = str(
            file_dialog.getOpenFileName(
                self, "Select a PDB file", expanduser("~")
            )
        )
        self._model.pdb_file = pdb_filename
        self.processing_widget.pdb_file_ledit.setText(pdb_filename)

    def get_processing_state(self):
        return self.processing_widget.run_offline_processing_cbox.isChecked(), \
               self.processing_widget.run_online_processing_cbox.isChecked()
