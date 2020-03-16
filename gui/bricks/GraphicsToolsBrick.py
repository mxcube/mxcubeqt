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

from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Graphics"


class GraphicsToolsBrick(BaseWidget):
    """
    Brick is like a menu in the menubar or/and in the toolbbr
    """

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.target_menu = None
        self.image_scale_list = []

        # Properties ----------------------------------------------------------
        self.add_property(
            "targetMenu", "combo", ("menuBar", "toolBar", "both"), "menuBar"
        )
        self.add_property("beamDefiner", "boolean", False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.tools_menu = None
        self.measure_distance_action = None
        self.measure_angle_action = None
        self.measure_area_action = None
        self.define_beam_action = None
        self.move_beam_mark_manual_action = None
        self.move_beam_mark_auto_action = None
        self.display_beam_size_action = None
        self.display_grid_action = None
        self.magnification_action = None
        self.image_scale_menu = None

        # Layout --------------------------------------------------------------

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def run(self):
        self.tools_menu = QtImport.QMenu("Graphics", self)

        _create_menu = self.tools_menu.addMenu("Create")
        temp_action = _create_menu.addAction(
            Icons.load_icon("VCRPlay2"),
            "Centring point with 3 clicks",
            self.create_point_click_clicked,
        )
        temp_action.setShortcut("Ctrl+1")
        temp_action = _create_menu.addAction(
            Icons.load_icon("ThumbUp"),
            "Centring point on current position",
            self.create_point_current_clicked,
        )
        temp_action.setShortcut("Ctrl+2")
        temp_action = _create_menu.addAction(
            Icons.load_icon("Line.png"), "Helical line", self.create_line_clicked
        )
        temp_action.setShortcut("Ctrl+3")
        temp_action = _create_menu.addAction(
            Icons.load_icon("Line.png"),
            "Automatic helical line",
            self.create_auto_line_clicked,
        )
        temp_action = _create_menu.addAction(
            Icons.load_icon("Grid"), "Grid", self.create_grid_clicked
        )
        temp_action.setShortcut("Ctrl+G")

        _measure_menu = self.tools_menu.addMenu("Measure")
        self.measure_distance_action = _measure_menu.addAction(
            Icons.load_icon("measure_distance"),
            "Distance",
            self.measure_distance_clicked,
        )
        self.measure_angle_action = _measure_menu.addAction(
            Icons.load_icon("measure_angle"), "Angle", self.measure_angle_clicked
        )
        self.measure_area_action = _measure_menu.addAction(
            Icons.load_icon("measure_area"), "Area", self.measure_area_clicked
        )

        _beam_mark_menu = self.tools_menu.addMenu("Beam mark")
        self.move_beam_mark_manual_action = _beam_mark_menu.addAction(
            "Set position manualy", self.move_beam_mark_manual
        )
        self.move_beam_mark_manual_action.setEnabled(False)
        self.move_beam_mark_auto_action = _beam_mark_menu.addAction(
            "Set position automaticaly", self.move_beam_mark_auto
        )
        self.move_beam_mark_auto_action.setEnabled(False)
        self.display_beam_size_action = _beam_mark_menu.addAction(
            "Display size", self.display_beam_size_toggled
        )
        self.display_beam_size_action.setCheckable(True)
        self.define_beam_action = _beam_mark_menu.addAction(
            "Define size with slits", self.define_beam_size
        )
        self.define_beam_action.setEnabled(self["beamDefiner"])

        self.tools_menu.addSeparator()

        temp_action = self.tools_menu.addAction(
            "Select all centring points", self.select_all_points_clicked
        )
        temp_action.setShortcut("Ctrl+A")
        temp_action = self.tools_menu.addAction(
            "Deselect all items", self.deselect_all_items_clicked
        )
        temp_action.setShortcut("Ctrl+D")
        temp_action = self.tools_menu.addAction(
            Icons.load_icon("Delete"), "Clear all items", self.clear_all_items_clicked
        )
        temp_action.setShortcut("Ctrl+X")

        self.tools_menu.addSeparator()

        self.display_grid_action = self.tools_menu.addAction(
            "Display grid", self.display_grid_toggled
        )
        self.display_grid_action.setCheckable(True)
        self.magnification_action = self.tools_menu.addAction(
            Icons.load_icon("Magnify2"),
            "Magnification tool",
            self.start_magnification_tool,
        )

        self.image_scale_menu = self.tools_menu.addMenu(
            Icons.load_icon("DocumentMag2"), "Image scale"
        )
        self.image_scale_menu.setEnabled(False)
        self.init_image_scale_list()
        self.image_scale_menu.triggered.connect(self.image_scale_triggered)

        # self.camera_control_action = self.tools_menu.addAction(\
        #     "Camera control", self.open_camera_control_dialog)
        # self.camera_control_action.setEnabled(False)

        if self.target_menu == "menuBar":
            if BaseWidget._menubar is not None:
                BaseWidget._menubar.insert_menu(self.tools_menu, 3)
        elif self.target_menu == "toolBar":
            if BaseWidget._toolbar is not None:
                for action in self.tools_menu.actions():
                    BaseWidget._toolbar.addAction(action)
        else:
            if BaseWidget._menubar is not None:
                BaseWidget._menubar.insert_menu(self.tools_menu, 2)

            if BaseWidget._toolbar is not None:
                for action in self.tools_menu.actions():
                    BaseWidget._toolbar.addAction(action)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "targetMenu":
            self.target_menu = new_value
        # elif property_name == 'cameraControls':
        #    self.camera_control_action.setEnabled(new_value)
        # elif property_name == 'beamDefiner':
        #     self.define_beam_action.setEnabled(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def init_image_scale_list(self):
        self.image_scale_list = HWR.beamline.sample_view.get_image_scale_list()
        if len(self.image_scale_list) > 0:
            self.image_scale_menu.setEnabled(True)
            for scale in self.image_scale_list:
                # probably there is a way to use a single method for all actions
                # by passing index. lambda function at first try did not work
                self.image_scale_menu.addAction(
                    "%d %%" % (scale * 100), self.not_used_function
                )
            for action in self.image_scale_menu.actions():
                action.setCheckable(True)
            self.image_scaled(HWR.beamline.sample_view.get_image_scale())

    def image_scaled(self, scale_value):
        for index, action in enumerate(self.image_scale_menu.actions()):
            action.setChecked(scale_value == self.image_scale_list[index])

    def not_used_function(self, *arg):
        pass

    def image_scale_triggered(self, selected_action):
        for index, action in enumerate(self.image_scale_menu.actions()):
            if selected_action == action:
                HWR.beamline.sample_view.set_image_scale(
                    self.image_scale_list[index], action.isChecked()
                )

    def set_expert_mode(self, expert):
        if self.move_beam_mark_manual_action:
            self.move_beam_mark_manual_action.setEnabled(expert)
        if self.move_beam_mark_auto_action:
            self.move_beam_mark_auto_action.setEnabled(expert)

    def measure_distance_clicked(self):
        HWR.beamline.sample_view.start_measure_distance(wait_click=True)

    def measure_angle_clicked(self):
        HWR.beamline.sample_view.start_measure_angle(wait_click=True)

    def measure_area_clicked(self):
        HWR.beamline.sample_view.start_measure_area(wait_click=True)

    def create_point_click_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.start_centring(tree_click=True)

    def create_point_current_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.start_centring()

    def create_line_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.create_line()

    def create_auto_line_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.create_auto_line()

    def create_grid_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.create_grid()

    def select_all_points_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.select_all_points()

    def deselect_all_items_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.de_select_all()

    def clear_all_items_clicked(self):
        if self.isEnabled():
            HWR.beamline.sample_view.clear_all()

    def move_beam_mark_manual(self):
        HWR.beamline.sample_view.start_move_beam_mark()

    def move_beam_mark_auto(self):
        HWR.beamline.sample_view.move_beam_mark_auto()

    def display_grid_toggled(self):
        HWR.beamline.sample_view.display_grid(self.display_grid_action.isChecked())

    def define_beam_size(self):
        HWR.beamline.sample_view.start_define_beam()

    def open_camera_control_dialog(self):
        self.camera_control_dialog.show()

    def display_beam_size_toggled(self):
        HWR.beamline.sample_view.display_beam_size(
            self.display_beam_size_action.isChecked()
        )

    def start_magnification_tool(self):
        HWR.beamline.sample_view.set_magnification_mode(True)
