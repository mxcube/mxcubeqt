import qt
import os
import queue_model
import logging

from widgets.data_path_widget_horizontal_layout \
    import DataPathWidgetHorizontalLayout
from widgets.data_path_widget_vertical_layout \
    import DataPathWidgetVerticalLayout
from widgets.widget_utils import DataModelInputBinder
from BlissFramework.Utils import widget_colors


class DataPathWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, data_model = None, 
                 layout = None):
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        self._session_hwobj = None
        
        if data_model is None:
            self._data_model = queue_model.PathTemplate()
        else:
            self._data_model = data_model
        
        self._data_model_pm = DataModelInputBinder(self._data_model)


        #
        # Layout
        #
        h_layout = qt.QHBoxLayout(self)

        if layout is DataPathWidgetHorizontalLayout:
            self.data_path_widget_layout = layout(self)
        elif layout is DataPathWidgetVerticalLayout:
            self.data_path_widget_layout = layout(self)
        else:
            self.data_path_widget_layout = DataPathWidgetHorizontalLayout(self)

        h_layout.addWidget(self.data_path_widget_layout)


        #
        # Logic
        #
        self._data_model_pm.bind_value_update('prefix', 
                                              self.data_path_widget_layout.prefix_ledit,
                                              str,
                                              None)

        #self._data_model_pm.bind_value_update('directory', 
        #                                      self.data_path_widget_layout.folder_ledit,
        #                                      str,
        #                                      None)
        
        self._data_model_pm.bind_value_update('run_number', 
                                              self.data_path_widget_layout.run_number_ledit,
                                              int,
                                              qt.QIntValidator(0, 1000, self))

        qt.QObject.connect(self.data_path_widget_layout.prefix_ledit, 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._prefix_ledit_change)
        
        qt.QObject.connect(self.data_path_widget_layout.run_number_ledit, 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._run_number_ledit_change)

        qt.QObject.connect(self.data_path_widget_layout.browse_button,
                           qt.SIGNAL("clicked()"),
                           self._browse_clicked)

        qt.QObject.connect(self.data_path_widget_layout.folder_ledit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self._folder_ledit_change)


    def set_session(self, session_hwobj):
        self._session_hwobj = session_hwobj


    def _browse_clicked(self):
        get_dir = qt.QFileDialog(self)
        given_dir = self._data_model.directory

        d = str(get_dir.getExistingDirectory(given_dir, self, "",
                                             "Select a directory", 
                                             True, False))
        d = os.path.dirname(d)

        if d is not None and len(d) > 0:
            self.set_directory(d)


    def _prefix_ledit_change(self, new_value):
        self._data_model.prefix = str(new_value)
        file_name = self._data_model.get_image_file_name()
        self.data_path_widget_layout.file_name_value_label.setText(file_name)


    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._data_model.run_number = int(new_value)
            file_name = self._data_model.get_image_file_name()
            self.data_path_widget_layout.file_name_value_label.setText(file_name)


    def _folder_ledit_change(self, new_value):        
        base_image_dir = self._session_hwobj.get_base_image_directory()

        new_sub_dir = str(new_value)

        if len(new_sub_dir) > 0:
            if new_sub_dir[0] == '/':
                new_sub_dir = new_sub_dir[1:]
                
            new_directory = os.path.join(base_image_dir, str(new_sub_dir))
        else:
            new_directory = base_image_dir
            
        self._data_model.directory = new_directory
        self.data_path_widget_layout.folder_ledit.\
            setPaletteBackgroundColor(widget_colors.WHITE)


    def set_data_path(self, path):
        (dir_name, file_name) = os.path.split(path)
        self.set_directory(dir_name)
        self.data_path_widget_layout.file_name_value_label.setText(file_name)

    
    def set_directory(self, directory):
        base_image_dir = self._session_hwobj.get_base_image_directory()

        dir_parts = directory.split(base_image_dir)

        if len(dir_parts) > 1:
            sub_dir = dir_parts[1]
        
            self._data_model.directory = directory
            self.data_path_widget_layout.folder_ledit.setText(sub_dir)
            self.data_path_widget_layout.folder_ledit.\
                setPaletteBackgroundColor(widget_colors.WHITE)
        else:
            self.data_path_widget_layout.folder_ledit.\
                setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            self._data_model.directory = base_image_dir
            logging.getLogger('user_level_log').\
                info("The selected data location is invalid, please select" \
                     " a directory within: " + base_image_dir)

        self.data_path_widget_layout.base_path_label.setText(base_image_dir)


    def set_run_number(self, run_number):
        self._data_model.run_number = run_number
        self.data_path_widget_layout.run_number_ledit.\
            setText(str(run_number))


    def set_prefix(self, base_prefix):
        self._data_model.base_prefix = base_prefix
        prefix = self._data_model.get_prefix()
        self.data_path_widget_layout.prefix_ledit.setText(prefix)


    def update_data_model(self, data_model):
        self._data_model = data_model
        self.set_data_path(data_model.get_image_path())
        self._data_model_pm.set_model(data_model)


