#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from QtImport import *

import Qt4_GraphicsManager

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Graphics'


class Qt4_CameraBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None

        # Internal values -----------------------------------------------------
        self.graphics_scene_size = None
        self.graphics_scene_fixed_size = None
        self.graphics_view = None
        #self.graphics_camera_frame = None
        self.fixed_size = None 
        self.display_beam = None

        # Properties ----------------------------------------------------------       
        self.addProperty("mnemonic", "string", "/Qt4_graphics-manager")
        self.addProperty("fixedSize", "string", "")
        self.addProperty('displayBeam', 'boolean', True)
        self.addProperty('displayScale', 'boolean', True)
        self.addProperty('displayOmegaAxis', 'boolean', True)
        self.addProperty('beamDefiner', 'boolean', False)
        self.addProperty('cameraControls', 'boolean', False)

        # Graphic elements-----------------------------------------------------
        self.info_widget = QWidget(self)
        self.display_beam_size_cbox = QCheckBox("Display beam size", self)
        self.display_beam_size_cbox.setHidden(True)
        self.coord_label = QLabel(":", self)
        self.info_label = QLabel(self)
        self.camera_control_dialog = CameraControlDialog(self)

        self.popup_menu = QMenu(self)
        create_menu = self.popup_menu.addMenu("Create")
        temp_action = create_menu.addAction(
            Qt4_Icons.load_icon("VCRPlay2"),
            "Centring point with 3 clicks",
            self.create_point_click_clicked)
        temp_action.setShortcut("Ctrl+1")
        temp_action = create_menu.addAction(
            Qt4_Icons.load_icon("ThumbUp"),
            "Centring point on current position",
            self.create_point_current_clicked)
        temp_action.setShortcut("Ctrl+2")
        create_menu.addAction(Qt4_Icons.load_icon("ThumbUp"),
                              "Centring points with one click",
                              self.create_points_one_click_clicked)
        temp_action = create_menu.addAction(
            Qt4_Icons.load_icon("Line.png"),
            "Helical line",
            self.create_line_clicked)
        temp_action = create_menu.addAction(
            Qt4_Icons.load_icon("Line.png"),
            "Automatic helical line",
            self.create_auto_line_clicked) 
        temp_action.setShortcut("Ctrl+3")
        temp_action = create_menu.addAction(
            Qt4_Icons.load_icon("Grid"),
            "Grid",
            self.create_grid)
        temp_action.setShortcut("Ctrl+4")

        measure_menu = self.popup_menu.addMenu("Measure")
        self.measure_distance_action = measure_menu.addAction(\
             Qt4_Icons.load_icon("measure_distance"),
             "Distance", self.measure_distance_clicked)
        self.measure_angle_action = measure_menu.addAction(\
             Qt4_Icons.load_icon("measure_angle"),
             "Angle", self.measure_angle_clicked)
        self.measure_area_action = measure_menu.addAction(\
             Qt4_Icons.load_icon("measure_area"),
             "Area", self.measure_area_clicked)

        beam_mark_menu = self.popup_menu.addMenu("Beam mark")
        self.move_beam_mark_manual_action = beam_mark_menu.addAction(\
             "Set position manually", self.move_beam_mark_manual)
        #self.move_beam_mark_manual_action.setEnabled(False)
        self.move_beam_mark_auto_action = beam_mark_menu.addAction(\
             "Set position automaticaly", self.move_beam_mark_auto)
        #self.move_beam_mark_auto_action.setEnabled(False)
        self.display_beam_size_action = beam_mark_menu.addAction(\
             "Display size", self.display_beam_size_toggled)
        self.display_beam_size_action.setCheckable(True)

        self.define_beam_action = self.popup_menu.addAction(\
             Qt4_Icons.load_icon("Draw"),
             "Define beam size with slits",
             self.define_beam_size)
        self.define_beam_action.setEnabled(False)
        self.popup_menu.addSeparator()

        temp_action = self.popup_menu.addAction(\
             "Select all centring points",
             self.select_all_points_clicked)
        temp_action.setShortcut("Ctrl+A")
        temp_action = self.popup_menu.addAction(\
             "Deselect all items",
             self.deselect_all_items_clicked)
        temp_action.setShortcut("Ctrl+D")
        temp_action = self.popup_menu.addAction(\
             Qt4_Icons.load_icon("Delete"),
             "Clear all items",
             self.clear_all_items_clicked)
        temp_action.setShortcut("Ctrl+X")
        self.popup_menu.addSeparator()

        tools_menu = self.popup_menu.addMenu("Tools") 
        self.display_grid_action = tools_menu.addAction(\
             Qt4_Icons.load_icon("Grid"),
             "Display grid",
             self.display_grid_toggled)
        self.display_grid_action.setCheckable(True)
        self.display_histogram_action = tools_menu.addAction(\
             Qt4_Icons.load_icon("Grid"),
             "Display historgram",
             self.display_histogram_toggled)
        self.display_histogram_action.setCheckable(True)
        self.magnification_action = tools_menu.addAction(\
             Qt4_Icons.load_icon("Magnify2"),
             "Magnification tool", self.start_magnification_tool)
        #self.magnification_action.setCheckable(True)

        #self.display_histogram_action = self.popup_menu.addAction(\
        #     "Display histogram", self.display_histogram_toggled)
        #self.define_histogram_action = self.popup_menu.addAction(\
        #     "Define histogram", self.define_histogram_clicked)

        #self.display_histogram_action.setEnabled(False)
        #self.define_histogram_action.setEnabled(False)

        self.image_scale_menu = self.popup_menu.addMenu(\
             Qt4_Icons.load_icon("DocumentMag2"),
             "Image scale")
        self.image_scale_menu.setEnabled(False) 
        self.image_scale_menu.triggered.connect(\
             self.image_scale_triggered)
        self.camera_control_action = self.popup_menu.addAction(\
             "Camera control",
             self.open_camera_control_dialog)
        self.camera_control_action.setEnabled(False)

        self.popup_menu.popup(QCursor.pos())
      
        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QHBoxLayout(self.info_widget)
        _info_widget_hlayout.addWidget(self.display_beam_size_cbox)
        _info_widget_hlayout.addWidget(self.coord_label)
        _info_widget_hlayout.addStretch(0)
        _info_widget_hlayout.addWidget(self.info_label)
        _info_widget_hlayout.setSpacing(0)
        _info_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.info_widget.setLayout(_info_widget_hlayout)

        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections -----------------------------------------
        self.display_beam_size_cbox.stateChanged.connect(\
             self.display_beam_size_toggled)

        # SizePolicies --------------------------------------------------------
        self.info_widget.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Fixed)

        # Scene elements ------------------------------------------------------
        self.setMouseTracking(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == "mnemonic":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, 
                                'mouseMoved',  
                                self.mouse_moved)
                self.disconnect(self.graphics_manager_hwobj,
                                'imageScaleChanged',        
                                self.image_scaled)
                self.disconnect(self.graphics_manager_hwobj,
                                'infoMsg',
                                self.set_info_msg)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, 
                             'mouseMoved', 
                             self.mouse_moved)
                self.connect(self.graphics_manager_hwobj,
                             'imageScaleChanged',
                             self.image_scaled)
                self.connect(self.graphics_manager_hwobj,
                             'infoMsg',
                             self.set_info_msg)
                self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
                #self.graphics_camera_frame = self.graphics_manager_hwobj.get_camera_frame() 
                self.main_layout.addWidget(self.graphics_view) 
                self.main_layout.addWidget(self.info_widget)
                self.set_fixed_size()
                self.init_image_scale_list()
                self.camera_control_dialog.set_camera_hwobj(\
                     self.graphics_manager_hwobj.camera_hwobj)
        elif property_name == 'fixedSize':
            try:
                fixed_size = list(map(int, new_value.split()))
                if len(fixed_size) == 2:
                    self.fixed_size = fixed_size
                    self.set_fixed_size()
            except:
                pass 
        elif property_name == 'displayBeam':              
            self.display_beam = new_value
        elif property_name == 'displayScale':
            self.display_scale = new_value
            if self.graphics_manager_hwobj is not None:
                self.graphics_manager_hwobj.set_scale_visible(new_value)
        elif property_name == 'beamDefiner':
             self.define_beam_action.setEnabled(new_value) 
        elif property_name == 'cameraControls':
             self.camera_control_action.setEnabled(new_value) 
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def display_beam_size_toggled(self):
        self.graphics_manager_hwobj.display_beam_size(\
            self.display_beam_size_action.isChecked())

    def start_magnification_tool(self):
        self.graphics_manager_hwobj.set_magnification_mode(True)

    def set_control_mode(self, have_control):
        if have_control:
            self.graphics_manager_hwobj.hide_info_msg()
        else:
            self.graphics_manager_hwobj.display_info_msg(\
                 ["", "Controls are disabled in the Slave mode",
                  "", "Ask for control to be able to control MXCuBE"
                  ""], hide_msg=False)
    """
    def set_expert_mode(self, is_expert_mode):
        self.move_beam_mark_manual_action.setEnabled(is_expert_mode)
        self.move_beam_mark_auto_action.setEnabled(is_expert_mode)
    """

    def set_info_msg(self, msg):
        self.info_label.setText(msg)

    def set_fixed_size(self):
        if self.fixed_size and self.graphics_manager_hwobj:
            self.graphics_manager_hwobj.set_graphics_scene_size(\
                 self.fixed_size, True)
            self.graphics_view.setFixedSize(self.fixed_size[0], self.fixed_size[1]) 
            #self.info_widget.setFixedWidth(self.fixed_size[0])

    def image_scaled(self, scale_value):
        for index, action in enumerate(self.image_scale_menu.actions()):
            action.setChecked(scale_value == self.image_scale_list[index])

    def init_image_scale_list(self):
        self.image_scale_list = self.graphics_manager_hwobj.get_image_scale_list()
        if len(self.image_scale_list) > 0:
            self.image_scale_menu.setEnabled(True)
            for scale in self.image_scale_list:
                #probably there is a way to use a single method for all actions
                # by passing index. lambda function at first try did not work  
                self.image_scale_menu.addAction("%d %%" % (scale * 100), self.not_used_function)
            for action in self.image_scale_menu.actions():
                action.setCheckable(True)
            self.image_scaled(self.graphics_manager_hwobj.get_image_scale())

    def not_used_function(self, *arg):
        pass

    def image_scale_triggered(self, selected_action):
        for index, action in enumerate(self.image_scale_menu.actions()):
            if selected_action == action:
                self.graphics_manager_hwobj.set_image_scale(\
                     self.image_scale_list[index], action.isChecked())
                
    def contextMenuEvent(self, event):
        self.popup_menu.popup(QCursor.pos())

    def measure_distance_clicked(self):
        self.graphics_manager_hwobj.start_measure_distance(wait_click=True)

    def measure_angle_clicked(self):
        self.graphics_manager_hwobj.start_measure_angle(wait_click=True)

    def measure_area_clicked(self):
        self.graphics_manager_hwobj.start_measure_area(wait_click=True)

    def display_histogram_toggled(self):
        self.graphics_manager_hwobj.display_histogram(\
             self.display_histogram_action.isChecked())

    def create_point_click_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=True)

    def create_points_one_click_clicked(self):
        self.graphics_manager_hwobj.start_one_click_centring()

    def create_point_current_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=False)

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def create_auto_line_clicked(self):
        self.graphics_manager_hwobj.create_auto_line()

    def create_grid(self):
        self.graphics_manager_hwobj.create_grid()

    def move_beam_mark_manual(self):
        self.graphics_manager_hwobj.start_move_beam_mark()

    def move_beam_mark_auto(self):
        self.graphics_manager_hwobj.move_beam_mark_auto()

    def mouse_moved(self, x, y):
        self.coord_label.setText("X: <b>%d</b> Y: <b>%d</b>" %(x, y))

    def select_all_points_clicked(self):
        self.graphics_manager_hwobj.select_all_points()

    def deselect_all_items_clicked(self):
        self.graphics_manager_hwobj.de_select_all()

    def clear_all_items_clicked(self):
        self.graphics_manager_hwobj.clear_all()

    def zoom_window_clicked(self):
        self.zoom_dialog.set_camera_frame(self.graphics_manager_hwobj.\
             get_camera_frame())
        self.zoom_dialog.set_coord(100, 100)
        self.zoom_dialog.show()

    def open_camera_control_dialog(self):
        self.camera_control_dialog.show()

    def display_grid_toggled(self):
        self.graphics_manager_hwobj.display_grid(\
             self.display_grid_action.isChecked())

    def define_beam_size(self):
        self.graphics_manager_hwobj.start_define_beam()

    def display_radiation_damage_toggled(self):
        self.graphics_manager_hwobj.display_radiation_damage(\
             self.display_radiation_damage_action.isChecked())

class CameraControlDialog(QDialog):

    def __init__(self, parent = None, name = None, flags = 0):
        QDialog.__init__(self, parent,
              Qt.WindowFlags(flags | Qt.WindowStaysOnTopHint))

        # Internal variables --------------------------------------------------
        self.camera_hwobj = None


        # Graphic elements ----------------------------------------------------
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_doublespinbox = QDoubleSpinBox(self)
        self.contrast_checkbox = QCheckBox("auto", self)
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_doublespinbox = QDoubleSpinBox(self)
        self.brightness_checkbox = QCheckBox("auto", self)
        self.gain_slider = QSlider(Qt.Horizontal, self)
        self.gain_doublespinbox = QDoubleSpinBox(self)
        self.gain_checkbox = QCheckBox("auto", self)
        self.gamma_slider = QSlider(Qt.Horizontal, self)
        self.gamma_doublespinbox = QDoubleSpinBox(self)
        self.gamma_checkbox = QCheckBox("auto", self)
        self.exposure_time_slider = QSlider(Qt.Horizontal, self)
        self.exposure_time_doublespinbox = QDoubleSpinBox(self) 
        self.exposure_time_checkbox = QCheckBox("auto", self)
        __close_button = QPushButton('Close', self)
        # Layout --------------------------------------------------------------
        __main_gridlayout = QGridLayout(self)
        __main_gridlayout.addWidget(QLabel('Contrast:', self), 0, 0)
        __main_gridlayout.addWidget(self.contrast_slider, 0, 1)
        __main_gridlayout.addWidget(self.contrast_doublespinbox, 0, 2)
        __main_gridlayout.addWidget(self.contrast_checkbox, 0, 3)
        __main_gridlayout.addWidget(QLabel('Brightness:', self), 1, 0)
        __main_gridlayout.addWidget(self.brightness_slider, 1, 1)
        __main_gridlayout.addWidget(self.brightness_doublespinbox, 1, 2)
        __main_gridlayout.addWidget(self.brightness_checkbox, 1, 3)
        __main_gridlayout.addWidget(QLabel('Gain:', self), 2, 0)
        __main_gridlayout.addWidget(self.gain_slider, 2, 1)
        __main_gridlayout.addWidget(self.gain_doublespinbox, 2, 2)
        __main_gridlayout.addWidget(self.gain_checkbox, 2, 3)
        __main_gridlayout.addWidget(QLabel('Gamma:', self), 3, 0) 
        __main_gridlayout.addWidget(self.gamma_slider, 3, 1)
        __main_gridlayout.addWidget(self.gamma_doublespinbox, 3, 2)
        __main_gridlayout.addWidget(self.gamma_checkbox, 3, 3)
        __main_gridlayout.addWidget(QLabel('Exposure time (ms):', self), 4, 0)
        __main_gridlayout.addWidget(self.exposure_time_slider, 4, 1)
        __main_gridlayout.addWidget(self.exposure_time_doublespinbox, 4, 2)      
        __main_gridlayout.addWidget(self.exposure_time_checkbox, 4, 3)      
        __main_gridlayout.addWidget(__close_button, 6, 2)
        __main_gridlayout.setSpacing(2)
        __main_gridlayout.setContentsMargins(5, 5, 5, 5)
        __main_gridlayout.setSizeConstraint(QLayout.SetFixedSize)

        # Qt signal/slot connections ------------------------------------------
        self.contrast_slider.valueChanged.connect(self.set_contrast)
        self.contrast_doublespinbox.valueChanged.connect(self.set_contrast)
        self.contrast_checkbox.stateChanged.connect(self.set_contrast_auto)
        self.brightness_slider.valueChanged.connect(self.set_brightness)
        self.brightness_doublespinbox.valueChanged.connect(self.set_brightness)
        self.brightness_checkbox.stateChanged.connect(self.set_brightness_auto)
        self.gain_slider.valueChanged.connect(self.set_gain)
        self.gain_doublespinbox.valueChanged.connect(self.set_gain)
        self.gain_checkbox.stateChanged.connect(self.set_gain_auto)
        self.gamma_slider.valueChanged.connect(self.set_gamma)
        self.gamma_doublespinbox.valueChanged.connect(self.set_gamma)
        self.gamma_checkbox.stateChanged.connect(self.set_gamma_auto)
        self.exposure_time_slider.valueChanged.connect(self.set_exposure_time)
        self.exposure_time_doublespinbox.valueChanged.connect(self.set_exposure_time)
        self.exposure_time_checkbox.stateChanged.connect(self.set_exposure_time_auto)

        __close_button.clicked.connect(self.close)

        # SizePolicies --------------------------------------------------------
        self.contrast_slider.setFixedWidth(200)
        self.brightness_slider.setFixedWidth(200)
        self.gain_slider.setFixedWidth(200)
        self.gamma_slider.setFixedWidth(200)
        self.exposure_time_slider.setFixedWidth(200)
        __close_button.setSizePolicy(QSizePolicy.Fixed, 
                                     QSizePolicy.Fixed)

        # Other --------------------------------------------------------------- 
        self.setModal(True)
        self.setWindowTitle("Camera controls")

    def set_camera_hwobj(self, camera_hwobj):
        self.camera_hwobj = camera_hwobj

        # get attribute value
        try:
            contrast_value = self.camera_hwobj.get_contrast()
        except AttributeError:
            contrast_value = None
        try:
            brightness_value = self.camera_hwobj.get_brightness()
        except AttributeError:
            brightness_value = None
        try:
            gain_value = self.camera_hwobj.get_gain()
        except AttributeError:
            gain_value = None
        try:
            gamma_value = self.camera_hwobj.get_gamma()
        except AttributeError:
            gamma_value = None
        try:
            exposure_time_value = self.camera_hwobj.get_exposure_time()
        except AttributeError:
            exposure_time_value = None

        # get attribute auto state
        try:
            contrast_auto = self.camera_hwobj.get_contrast_auto()
        except AttributeError:
            contrast_auto = None
        try:
            brightness_auto = self.camera_hwobj.get_brightness_auto()
        except AttributeError:
            brightness_auto = None
        try:
            gain_auto = self.camera_hwobj.get_gain_auto()
        except AttributeError:
            gain_auto = None
        try:
            gamma_auto = self.camera_hwobj.get_gamma_auto()
        except AttributeError:
            gamma_auto = None
        try:
            exposure_time_auto = self.camera_hwobj.get_exposure_time_auto()
        except AttributeError:
            exposure_time_auto = None

        # get attribute range
        try:
            contrast_min_max = self.camera_hwobj.get_contrast_min_max()
        except AttributeError:
            contrast_min_max = (0, 100)
        try:
            brightness_min_max = self.camera_hwobj.get_brightness_min_max()
        except AttributeError:
            brightness_min_max = (0, 100)
        try:
            gain_min_max = self.camera_hwobj.get_gain_min_max()
        except AttributeError:
            gain_min_max = (0, 100)
        try:
            gamma_min_max = self.camera_hwobj.get_gamma_min_max()
        except AttributeError:
            gamma_min_max = (0, 100)
        try:
            exposure_time_min_max = self.camera_hwobj.get_exposure_time_min_max()
        except AttributeError:
            exposure_time_min_max = (0, 100)

        self.contrast_slider.setDisabled(contrast_value is None)
        self.contrast_doublespinbox.setDisabled(contrast_value is None)
        self.contrast_checkbox.setDisabled(contrast_auto is None or contrast_value is None)
        self.brightness_slider.setDisabled(brightness_value is None)
        self.brightness_doublespinbox.setDisabled(brightness_value is None)
        self.brightness_checkbox.setDisabled(brightness_auto is None or brightness_value is None)
        self.gain_slider.setDisabled(gain_value is None)
        self.gain_doublespinbox.setDisabled(gain_value is None)
        self.gain_checkbox.setDisabled(gain_auto is None or gain_value is None)
        self.gamma_slider.setDisabled(gamma_value is None)
        self.gamma_doublespinbox.setDisabled(gamma_value is None)
        self.gamma_checkbox.setDisabled(gamma_auto is None or gamma_value is None)
        self.exposure_time_slider.setDisabled(exposure_time_value is None)
        self.exposure_time_doublespinbox.setDisabled(exposure_time_value is None)
        self.exposure_time_checkbox.setDisabled(exposure_time_auto is None or exposure_time_value is None)

        if contrast_value:
            self.contrast_slider.setValue(contrast_value)
            self.contrast_slider.setRange(contrast_min_max[0], contrast_min_max[1])
            self.contrast_doublespinbox.setValue(contrast_value)
            self.contrast_doublespinbox.setRange(contrast_min_max[0], contrast_min_max[1])
            self.contrast_checkbox.blockSignals(True)
            self.contrast_checkbox.setChecked(bool(contrast_auto))
            self.contrast_checkbox.blockSignals(False)
        if brightness_value:
            self.brightness_slider.setValue(brightness_value)
            self.brightness_slider.setRange(brightness_min_max[0], brightness_min_max[1])
            self.brightness_doublespinbox.setValue(brightness_value)
            self.brightness_doublespinbox.setRange(brightness_min_max[0], brightness_min_max[1])
            self.brightness_checkbox.blockSignals(True)
            self.brightness_checkbox.setChecked(bool(brightness_auto))
            self.brightness_checkbox.blockSignals(False)
        if gain_value:
            self.gain_slider.setValue(gain_value)
            self.gain_slider.setRange(gain_min_max[0], gain_min_max[1])
            self.gain_doublespinbox.setValue(gain_value)
            self.gain_doublespinbox.setRange(gain_min_max[0], gain_min_max[1])
            self.gain_checkbox.blockSignals(True)
            self.gain_checkbox.setChecked(bool(gain_auto))
            self.gain_checkbox.blockSignals(False)
        if gamma_value:
            self.gamma_slider.setValue(gamma_value)
            self.gamma_slider.setRange(gamma_min_max[0], gamma_min_max[1])
            self.gamma_doublespinbox.setValue(gamma_value)
            self.gamma_doublespinbox.setRange(gamma_min_max[0], gamma_min_max[1])
            self.gamma_checkbox.blockSignals(True)
            self.gamma_checkbox.setChecked(bool(gamma_auto))
            self.gamma_checkbox.blockSignals(False)
        if exposure_time_value:
            self.exposure_time_slider.setValue(exposure_time_value)
            self.exposure_time_slider.setRange(exposure_time_min_max[0], exposure_time_min_max[1])
            self.exposure_time_doublespinbox.setValue(exposure_time_value)
            self.exposure_time_doublespinbox.setRange(exposure_time_min_max[0], exposure_time_min_max[1])
            self.exposure_time_checkbox.blockSignals(True)
            self.exposure_time_checkbox.setChecked(bool(exposure_time_auto))
            self.exposure_time_checkbox.blockSignals(False)

    def set_contrast(self, value):
        self.contrast_slider.setValue(value)
        self.contrast_doublespinbox.setValue(value)
        self.camera_hwobj.set_contrast(value)

    def set_brightness(self, value):
        self.brightness_slider.setValue(value)
        self.brightness_doublespinbox.setValue(value)
        self.camera_hwobj.set_brightness(value)

    def set_gain(self, value):
        self.gain_slider.setValue(value)
        self.gain_doublespinbox.setValue(value)
        self.camera_hwobj.set_gain(value)

    def set_gamma(self, value):
        self.gamma_slider.setValue(value)
        self.gamma_doublespinbox.setValue(value)
        self.camera_hwobj.set_gamma(value)

    def set_exposure_time(self, value):
        self.exposure_time_slider.setValue(value)
        self.exposure_time_doublespinbox.setValue(value)
        self.camera_hwobj.set_exposure_time(value) 

    def set_contrast_auto(self, state):
        state = bool(state)
        self.camera_hwobj.set_contrast_auto(state)
        value = self.camera_hwobj.get_contrast()
        self.contrast_slider.setValue(value)
        self.contrast_doublespinbox.setValue(value)

    def set_brightness_auto(self, state):
        state = bool(state)
        self.camera_hwobj.set_brightness_auto(state)
        value = self.camera_hwobj.get_brightness()
        self.brightness_slider.setValue(value)
        self.brightness_doublespinbox.setValue(value)

    def set_gain_auto(self, state):
        state = bool(state)
        self.camera_hwobj.set_gain_auto(state)
        value = self.camera_hwobj.get_gain()
        self.gain_slider.setValue(value)
        self.gain_doublespinbox.setValue(value)

    def set_gamma_auto(self, state):
        state = bool(state)
        self.camera_hwobj.set_gamma_auto(state)
        value = self.camera_hwobj.get_gamma()
        self.gamma_slider.setValue(value)
        self.gamma_doublespinbox.setValue(value)

    def set_exposure_time_auto(self, state):
        state = bool(state)
        self.camera_hwobj.set_exposure_time_auto(state)
        value = self.camera_hwobj.get_exposure_time()
        self.exposure_time_slider.setValue(value)
        self.exposure_time_doublespinbox.setValue(value)
