import qtui
import qt
import os
import logging
import queue_model_objects

from widgets.widget_utils import DataModelInputBinder
from BlissFramework.Utils import widget_colors


class DataPathWidget(qt.QWidget):
    def __init__(self, parent=None, name="", fl=0, data_model=None, layout=None):
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        self._base_image_dir = None
        self._base_process_dir = None
        self.path_conflict_state = False

        if data_model is None:
            self._data_model = queue_model_objects.PathTemplate()
        else:
            self._data_model = data_model

        self._data_model_pm = DataModelInputBinder(self._data_model)

        #
        # Layout
        #
        h_layout = qt.QHBoxLayout(self)

        if layout == "vertical":
            widget = qtui.QWidgetFactory.create(
                os.path.join(
                    os.path.dirname(__file__),
                    "ui_files/data_path_widget_vertical_layout.ui",
                )
            )
        elif layout == "horizontal":
            widget = qtui.QWidgetFactory.create(
                os.path.join(
                    os.path.dirname(__file__),
                    "ui_files/data_path_widget_horizontal_layout.ui",
                )
            )
        else:
            widget = qtui.QWidgetFactory.create(
                os.path.join(
                    os.path.dirname(__file__),
                    "ui_files/data_path_widget_horizontal_layout.ui",
                )
            )

        self.data_path_widget_layout = widget
        widget.reparent(self, qt.QPoint(0, 0))
        h_layout.addWidget(self.data_path_widget_layout)

        #
        # Logic
        #
        self._data_model_pm.bind_value_update(
            "base_prefix", self.data_path_widget_layout.child("prefix_ledit"), str, None
        )

        self._data_model_pm.bind_value_update(
            "run_number",
            self.data_path_widget_layout.child("run_number_ledit"),
            int,
            qt.QIntValidator(0, 1000, self),
        )

        qt.QObject.connect(
            self.data_path_widget_layout.child("prefix_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._prefix_ledit_change,
        )

        qt.QObject.connect(
            self.data_path_widget_layout.child("run_number_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._run_number_ledit_change,
        )

        qt.QObject.connect(
            self.data_path_widget_layout.child("browse_button"),
            qt.SIGNAL("clicked()"),
            self._browse_clicked,
        )

        qt.QObject.connect(
            self.data_path_widget_layout.child("folder_ledit"),
            qt.SIGNAL("textChanged(const QString &)"),
            self._folder_ledit_change,
        )

    def _browse_clicked(self):
        get_dir = qt.QFileDialog(self)
        given_dir = self._base_image_dir

        d = str(
            get_dir.getExistingDirectory(
                given_dir, self, "", "Select a directory", True, False
            )
        )
        d = os.path.dirname(d)

        if d is not None and len(d) > 0:
            self.set_directory(d)

    def _prefix_ledit_change(self, new_value):
        self._data_model.base_prefix = str(new_value)
        file_name = self._data_model.get_image_file_name()
        file_name = file_name.replace(
            "%" + self._data_model.precision + "d",
            int(self._data_model.precision) * "#",
        )
        file_name = file_name.strip(" ")
        self.data_path_widget_layout.child("file_name_value_label").setText(file_name)

        self.emit(
            qt.PYSIGNAL("path_template_changed"),
            (self.data_path_widget_layout.child("prefix_ledit"), new_value),
        )

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.set_run_number(new_value)
            self.emit(
                qt.PYSIGNAL("path_template_changed"),
                (self.data_path_widget_layout.child("run_number_ledit"), new_value),
            )

    def _folder_ledit_change(self, new_value):
        base_image_dir = self._base_image_dir
        base_proc_dir = self._base_process_dir
        new_sub_dir = str(new_value).strip(" ")

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
        self.data_path_widget_layout.child("folder_ledit").setPaletteBackgroundColor(
            widget_colors.WHITE
        )

        self.emit(
            qt.PYSIGNAL("path_template_changed"),
            (self.data_path_widget_layout.child("folder_ledit"), new_value),
        )

    def set_data_path(self, path):
        (dir_name, file_name) = os.path.split(path)
        self.set_directory(dir_name)
        file_name = file_name.replace(
            "%" + self._data_model.precision + "d",
            int(self._data_model.precision) * "#",
        )
        self.data_path_widget_layout.child("file_name_value_label").setText(file_name)

    def set_directory(self, directory):
        base_image_dir = self._base_image_dir
        dir_parts = directory.split(base_image_dir)

        if len(dir_parts) > 1:
            sub_dir = dir_parts[1]
            self._data_model.directory = directory
            self.data_path_widget_layout.child("folder_ledit").setText(sub_dir)
        else:
            self.data_path_widget_layout.child("folder_ledit").setText("")
            self._data_model.directory = base_image_dir

        self.data_path_widget_layout.child("base_path_label").setText(base_image_dir)

    def set_run_number(self, run_number):
        self._data_model.run_number = int(run_number)
        self.data_path_widget_layout.child("run_number_ledit").setText(str(run_number))

    def set_prefix(self, base_prefix):
        self._data_model.base_prefix = str(base_prefix)
        self.data_path_widget_layout.child("prefix_ledit").setText(str(base_prefix))
        file_name = self._data_model.get_image_file_name()
        file_name = file_name.replace(
            "%" + self._data_model.precision + "d",
            int(self._data_model.precision) * "#",
        )
        self.data_path_widget_layout.child("file_name_value_label").setText(file_name)

    def update_data_model(self, data_model):
        self._data_model = data_model
        self.set_data_path(data_model.get_image_path())
        self._data_model_pm.set_model(data_model)

    def indicate_path_conflict(self, conflict):
        if conflict:
            self.data_path_widget_layout.child(
                "prefix_ledit"
            ).setPaletteBackgroundColor(widget_colors.LIGHT_RED)

            self.data_path_widget_layout.child(
                "run_number_ledit"
            ).setPaletteBackgroundColor(widget_colors.LIGHT_RED)

            self.data_path_widget_layout.child(
                "folder_ledit"
            ).setPaletteBackgroundColor(widget_colors.LIGHT_RED)

            logging.getLogger("user_level_log").error(
                "The current path settings will overwrite data"
                + " from another task. Correct the problem before adding to queue"
            )
        else:
            # We had a conflict previous, but its corrected now !
            if self.path_conflict_state:
                logging.getLogger("user_level_log").info("Path valid")

            self.data_path_widget_layout.child(
                "prefix_ledit"
            ).setPaletteBackgroundColor(widget_colors.WHITE)

            self.data_path_widget_layout.child(
                "run_number_ledit"
            ).setPaletteBackgroundColor(widget_colors.WHITE)

            self.data_path_widget_layout.child(
                "folder_ledit"
            ).setPaletteBackgroundColor(widget_colors.WHITE)

        self.path_conflict_state = conflict
