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
import string
import logging

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.utils.widget_utils import DataModelInputBinder

from mxcubecore.model import queue_model_objects


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class DataPathWidget(qt_import.QWidget):

    pathTemplateChangedSignal = qt_import.pyqtSignal()

    def __init__(self, parent=None, name="", fl=0, data_model=None, layout=None):

        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)
        self.parent = parent

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._base_image_dir = ""
        self._base_process_dir = ""
        self.path_conflict_state = False
        self.enable_macros = False

        if data_model is None:
            self._data_model = queue_model_objects.PathTemplate()
        else:
            self._data_model = data_model

        self._data_model_pm = DataModelInputBinder(self._data_model)

        # Graphic elements ----------------------------------------------------
        if layout == "vertical":
            self.data_path_layout = qt_import.load_ui_file(
                "data_path_widget_vertical_layout.ui"
            )
        else:
            self.data_path_layout = qt_import.load_ui_file(
                "data_path_widget_horizontal_layout.ui"
            )

        # Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.data_path_layout)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.data_path_layout.prefix_ledit.textChanged.connect(
            self._prefix_ledit_change
        )
        self.data_path_layout.run_number_ledit.textChanged.connect(
            self._run_number_ledit_change
        )
        self.data_path_layout.browse_button.clicked.connect(self._browse_clicked)
        self.data_path_layout.folder_ledit.textChanged.connect(
            self._folder_ledit_change
        )
        self.data_path_layout.compression_cbox.clicked.connect(
            self._compression_toggled
        )

        # Other ---------------------------------------------------------------
        self._data_model_pm.bind_value_update(
            "base_prefix", self.data_path_layout.prefix_ledit, str, None
        )

        self._data_model_pm.bind_value_update(
            "run_number",
            self.data_path_layout.run_number_ledit,
            int,
            qt_import.QIntValidator(0, 1000, self),
        )

        self._data_model_pm.bind_value_update(
            "compression", self.data_path_layout.compression_cbox, bool, None
        )

    def set_base_image_directory(self, base_image_dir):
        self._base_image_dir = base_image_dir

    def set_base_process_directory(self, base_process_dir):
        self._base_process_dir = base_process_dir

    def _browse_clicked(self):
        file_dialog = qt_import.QFileDialog(self)
        file_dialog.setNameFilter("%s*" % self._base_image_dir)

        selected_dir = str(
            file_dialog.getExistingDirectory(
                self, "Select a directory", str(self._base_image_dir), qt_import.QFileDialog.ShowDirsOnly
            )
        )
        if selected_dir is not None and len(selected_dir) > 0 and selected_dir.startswith(self._base_image_dir):
            self.set_directory(selected_dir)
        else:
            msg = "Selected directory do not start " +\
                  "with the base directory %s" % self._base_image_dir
            logging.getLogger("GUI").error(msg)

    def _prefix_ledit_change(self, new_value):
        cursor_pos = self.data_path_layout.prefix_ledit.cursorPosition()

        if len(new_value) > 0:
            available_chars = (
                string.ascii_lowercase + string.ascii_uppercase + string.digits + "-_"
            )
            if self.enable_macros:
                available_chars += "%"
            new_value = "".join(i for i in str(new_value) if i in available_chars)
            new_value = new_value.replace("\\", "")

        if len(new_value) > 50:
            logging.getLogger("GUI").error(
                "Current prefix is to long (max 50 characters are allowed)"
            )
            new_value = new_value[:-1]

        self.data_path_layout.prefix_ledit.setText(new_value)
        self.data_path_layout.prefix_ledit.setCursorPosition(cursor_pos)

        self._data_model.base_prefix = str(new_value)
        self.update_file_name()
        self.pathTemplateChangedSignal.emit()

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._data_model.run_number = int(new_value)
            self.data_path_layout.run_number_ledit.setText(str(new_value))

            self.update_file_name()
            self.pathTemplateChangedSignal.emit()
        else:
            # self.data_path_layout.run_number_ledit.setText(str(self._data_model.run_number))
            colors.set_widget_color(
                self.data_path_layout.folder_ledit, colors.LIGHT_YELLOW
            )

    def _folder_ledit_change(self, new_value):
        base_image_dir = self._base_image_dir
        base_proc_dir = self._base_process_dir
        new_sub_dir = str(new_value).strip(" ")

        cursor_pos = self.data_path_layout.folder_ledit.cursorPosition()
        if len(new_value) > 0:
            available_chars = (
                string.ascii_lowercase + string.ascii_uppercase + string.digits + "-_/"
            )
            if self.enable_macros:
                available_chars += "%"
            new_value = "".join(i for i in str(new_value) if i in available_chars)
            # new_value = new_value.replace("\\", "")

        new_sub_dir = str(new_value).strip(" ")
        self.data_path_layout.folder_ledit.setText(new_value)
        self.data_path_layout.folder_ledit.setCursorPosition(cursor_pos)

        if len(new_sub_dir) > 0:
            if new_sub_dir[0] == os.path.sep:
                new_sub_dir = new_sub_dir[1:]
            new_image_directory = os.path.join(base_image_dir, str(new_sub_dir))
            new_proc_dir = os.path.join(base_proc_dir, str(new_sub_dir))
        else:
            new_image_directory = base_image_dir
            new_proc_dir = base_proc_dir

        self._data_model.directory = new_image_directory
        self._data_model.process_directory = new_proc_dir
        colors.set_widget_color(self.data_path_layout.folder_ledit, colors.WHITE)

        self.pathTemplateChangedSignal.emit()

    def _compression_toggled(self, state):
        if hasattr(self.parent, "_tree_brick"):
            if self.parent._tree_brick:
                self.parent._tree_brick.compression_state = state

        queue_model_objects.Characterisation.set_char_compression(state)
        self._data_model.compression = state
        self.update_file_name()
        self.pathTemplateChangedSignal.emit()

    def update_file_name(self):
        """
        updates filename if prefix or run number changed
        at start values are initalized before precision is set.
        so a check for isdigit is done to be on the safe side
        """
        if str(self._data_model.precision).isdigit():
            file_name = self._data_model.get_image_file_name()
            file_name = file_name.replace(
                "%" + str(self._data_model.precision) + "d",
                int(self._data_model.precision) * "#",
            )
            file_name = file_name.strip(" ")
            self.data_path_layout.file_name_value_label.setText(file_name)

    def set_data_path(self, path):
        (dir_name, file_name) = os.path.split(path)
        if self._data_model.precision:
            precision = self._data_model.precision
        else:
            precision = "05"

        self.set_directory(dir_name)
        file_name = file_name.replace(
            "%" + str(self._data_model.precision) + "d",
            int(precision) * "#",
        )
        self.data_path_layout.file_name_value_label.setText(file_name)

    def set_directory(self, directory):
        self._data_model.directory = str(directory)

        if len(directory.split("/")) != len(self._base_image_dir.split("/")):
            dir_parts = directory.split("/")
            sub_dir = os.path.join(*dir_parts[len(self._base_image_dir.split("/")) :])
            self.data_path_layout.folder_ledit.setText(sub_dir)
        else:
            self.data_path_layout.folder_ledit.setText("")
            self._data_model.directory = self._base_image_dir

        self.data_path_layout.base_path_ledit.setText(self._base_image_dir)

    # def set_run_number(self, run_number):
    #    """
    #    Descript. :
    #    """
    #    self._data_model.run_number = int(run_number)
    #    self.data_path_layout.run_number_ledit.setText(str(run_number))

    def set_prefix(self, base_prefix):
        self._data_model.base_prefix = str(base_prefix)
        self.data_path_layout.prefix_ledit.setText(str(base_prefix))
        file_name = self._data_model.get_image_file_name()
        file_name = file_name.replace(
            "%" + str(self._data_model.precision) + "d",
            int(self._data_model.precision) * "#",
        )
        self.data_path_layout.file_name_value_label.setText(file_name)

    def update_data_model(self, data_model):
        self._data_model = data_model
        self.set_data_path(data_model.get_image_path())
        self._data_model_pm.set_model(data_model)
        self.data_path_layout.browse_button.setEnabled(os.path.exists(self._base_image_dir))

    def indicate_path_conflict(self, conflict):
        if conflict:
            colors.set_widget_color(
                self.data_path_layout.prefix_ledit,
                colors.LIGHT_RED,
                qt_import.QPalette.Base,
            )
            colors.set_widget_color(
                self.data_path_layout.run_number_ledit,
                colors.LIGHT_RED,
                qt_import.QPalette.Base,
            )
            colors.set_widget_color(
                self.data_path_layout.folder_ledit,
                colors.LIGHT_RED,
                qt_import.QPalette.Base,
            )

            logging.getLogger("GUI").error(
                "The current path settings will overwrite data "
                + "from another task. Correct the problem before "
                + "adding to queue"
            )
        else:
            # We had a conflict previous, but its corrected now !
            if self.path_conflict_state:
                logging.getLogger("GUI").info("Path valid")

                colors.set_widget_color(
                    self.data_path_layout.prefix_ledit,
                    colors.WHITE,
                    qt_import.QPalette.Base,
                )
                colors.set_widget_color(
                    self.data_path_layout.run_number_ledit,
                    colors.WHITE,
                    qt_import.QPalette.Base,
                )
                colors.set_widget_color(
                    self.data_path_layout.folder_ledit,
                    colors.WHITE,
                    qt_import.QPalette.Base,
                )
        self.path_conflict_state = conflict
