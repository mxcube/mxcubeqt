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

import api

from gui.BaseComponents import BaseWidget
from gui.utils import Colors, Icons, QtImport
from gui.utils.sample_changer_helper import SC_STATE_COLOR, SampleChanger

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "EMBL"


class SCViewBrick(BaseWidget):
    """Inherited from BaseWidget"""

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.axis_camera = None
        self.sc_camera = None

        # Properties ----------------------------------------------------------
        self.add_property("hwobj_axis_camera", "string", "")
        self.add_property("hwobj_sc_camera", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        status_widget = QtImport.QWidget(self)
        status_label = QtImport.QLabel("Status: ", status_widget)
        self.status_ledit = QtImport.QLineEdit(status_widget)
         
        self.camera_live_cbx = QtImport.QCheckBox("Live view", self)
        self.camera_live_cbx.setChecked(False)

        self.progress_bar = QtImport.QProgressBar(self)
        self.progress_bar.setMinimum(0)

        camera_widget = QtImport.QWidget(self)

        self.axis_view = QtImport.QGraphicsView(camera_widget)
        axis_scene = QtImport.QGraphicsScene(self.axis_view)
        self.axis_view.setScene(axis_scene)
        self.axis_camera_pixmap_item = QtImport.QGraphicsPixmapItem()
        axis_scene.addItem(self.axis_camera_pixmap_item)

        self.sc_view = QtImport.QGraphicsView(camera_widget)
        sc_scene = QtImport.QGraphicsScene(self.sc_view)
        self.sc_view.setScene(sc_scene)
        self.sc_camera_pixmap_item = QtImport.QGraphicsPixmapItem()
        sc_scene.addItem(self.sc_camera_pixmap_item)

        # Layout --------------------------------------------------------------
        _status_widget_hlayout = QtImport.QHBoxLayout(status_widget)
        _status_widget_hlayout.addWidget(status_label)
        _status_widget_hlayout.addWidget(self.status_ledit)

        _camera_widget_hlayout = QtImport.QHBoxLayout(camera_widget)
        _camera_widget_hlayout.addWidget(self.axis_view)
        _camera_widget_hlayout.addWidget(self.sc_view)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(status_widget)
        _main_vlayout.addWidget(self.camera_live_cbx)
        _main_vlayout.addWidget(camera_widget)
        _main_vlayout.addWidget(self.progress_bar)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.camera_live_cbx.stateChanged.connect(self.camera_live_state_changed)

        if api.sample_changer is not None:  
            self.connect(
                api.sample_changer,
                SampleChanger.STATUS_CHANGED_EVENT,
                self.sample_changer_status_changed,
            )
            self.connect(api.sample_changer, "progressInit", self.init_progress)
            self.connect(api.sample_changer, "progressStep", self.step_progress)
            self.connect(api.sample_changer, "progressStop", self.stop_progress)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "hwobj_axis_camera":
            self.axis_camera = self.get_hardware_object(new_value)
            image_dimensions = self.axis_camera.get_image_dimensions()
            self.axis_view.setFixedSize(image_dimensions[0], image_dimensions[1])
            self.connect(self.axis_camera, "imageReceived", self.axis_camera_frame_received)
        elif property_name == "hwobj_sc_camera":
            self.sc_camera = self.get_hardware_object(new_value)
            image_dimensions = self.sc_camera.get_image_dimensions()
            self.sc_view.setFixedSize(image_dimensions[0], image_dimensions[1])
            self.connect(self.sc_camera, "imageReceived", self.sc_camera_frame_received)
            
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def camera_live_state_changed(self, state):
        print state
        self.axis_camera.set_video_live(state)
        self.sc_camera.set_video_live(state)

    def axis_camera_frame_received(self, camera_frame):
        self.axis_camera_pixmap_item.setPixmap(camera_frame)

    def sc_camera_frame_received(self, camera_frame):
        self.sc_camera_pixmap_item.setPixmap(camera_frame)

    def sample_changer_status_changed(self, status):
        self.status_ledit.setText(status)
        if status == "Loading":
            self.camera_live_cbx.setEnabled(False)
            Colors.set_widget_color(
                 self.status_ledit, Colors.LIGHT_GREEN, QtImport.QPalette.Base
            )
            self.axis_camera.set_video_live(True)
            self.sc_camera.set_video_live(True)
        else:
            self.camera_live_cbx.setEnabled(True)
            Colors.set_widget_color(
                 self.status_ledit, Colors.WHITE, QtImport.QPalette.Base
            )
            if not self.camera_live_cbx.isChecked():
                self.axis_camera.set_video_live(False)
                self.sc_camera.set_video_live(False)

    def stop_progress(self, *args):
        self.progress_bar.reset()

    def step_progress(self, step, msg=None):
        self.progress_bar.setValue(step)

    def init_progress(self, progress_type, number_of_steps, use_dialog=False):
        self.progress_bar.reset()
        self.progress_bar.setMaximum(number_of_steps)
