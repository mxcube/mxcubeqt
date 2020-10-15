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

"""Volpi brick

The standard Volpi brick.
"""

import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class VolpiBrick(BaseWidget):
    """ Brick to handle a Volpi.
   
    A QDial to handle it : from 0 to 100%
    """

    def __init__(self, *args):
        """VolpiBrick constructor

        Arguments:
        :params args:
        """
        super(VolpiBrick, self).__init__(*args)

        # Hardware objects ----------------------------------------------------

        self.volpi_hwobj = None  # hardware object
        
        # Graphic elements-----------------------------------------------------

        self.frame = QtImport.QGroupBox()
        self.frame_layout = QtImport.QVBoxLayout()
        
        self.power_bar = PowerBar(["#5e4fa2", "#3288bd", "#66c2a5", "#abdda4", "#e6f598", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d53e4f", "#9e0142",
        "#006837", "#1a9850", "#66bd63", "#a6d96a", "#d9ef8b", "#ffffbf", "#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026"])
        self.power_bar.setMinimum(0)
        self.power_bar.setMaximum(100)
        self.power_bar.setSingleStep(1)
        self.power_bar.setNotchesVisible(True)

        self.position_spinbox = QtImport.QSpinBox()
        self.position_spinbox.setMinimum(0)
        self.position_spinbox.setMaximum(100)
        self.position_spinbox.setFixedSize(75, 27)
        
        self.step_button = QtImport.QPushButton()
        self.step_button_icon = Icons.load_icon("TileCascade2")
        self.step_button.setIcon(self.step_button_icon)
        self.step_button.setToolTip("Changes the volpi step")
        self.step_button.setFixedSize(27, 27)

        # Layout --------------------------------------------------------------
        
        self.frame_layout.addWidget(self.power_bar)
        self.frame.setLayout(self.frame_layout)
        
        self.main_layout = QtImport.QHBoxLayout()
        self.main_layout.addWidget(self.frame, 0, QtImport.Qt.AlignCenter)
        self.main_layout.addWidget(self.position_spinbox)
        self.main_layout.addWidget(self.step_button)

        self.setLayout(self.main_layout)

        # Qt signal/slot connections -----------------------------------------
        self.power_bar.value_changed.connect(self.value_changed)
        self.position_spinbox.valueChanged.connect(self.value_changed)

        self.step_button.clicked.connect(self.open_step_editor)
        
        # define properties
        self.add_property("mnemonic", "string", "")
        self.add_property("showBar", "boolean", False)
        self.add_property("showDial", "boolean", False)
        self.add_property("showStep", "boolean", True)
        self.add_property("stepValue", "string", 5)

        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1

        # slots -------------------------------------------
        self.define_slot("zoom_changed", ())

        # initialization -------------------

    def zoom_changed(self, new_position_dict):
        new_light_value = new_position_dict['light']
        self.value_changed(new_light_value)

    def value_changed(self, new_intensity):
        """set volpi to new value."""
        self.power_bar.blockSignals(True)
        self.position_spinbox.blockSignals(True)
        
        self.power_bar.setValue(new_intensity)
        self.position_spinbox.setValue(new_intensity)
        self.volpi_hwobj.set_value(new_intensity)
        
        self.power_bar.blockSignals(False)
        self.position_spinbox.blockSignals(True)
        
    def set_mnemonic(self, mne):
        """set mnemonic."""
        self["mnemonic"] = mne

    def set_volpi_object(self, volpi_ho_name=None):
        """set volpi's hardware object."""
        if self.volpi_hwobj is not None:
            
            self.disconnect(self.volpi_hwobj, "intensityChanged", self.slot_intensity)
            
        if volpi_ho_name is not None:
            self.volpi_hwobj = self.get_hardware_object(volpi_ho_name)

        if self.volpi_hwobj is not None:
            self.setEnabled(True)
            
            self.connect(self.volpi_hwobj, "intensityChanged", self.slot_intensity)
            # if self.volpi_hwobj.is_ready():
            #     self.slot_position(self.volpi_hwobj.get_position())
            #     self.slot_status(self.volpi_hwobj.get_state())
            #     self.volpi_ready()
            # else:
            #     self.volpi_not_ready()

        self.update_gui()

    def volpi_ready(self):
        """Set volpi enable."""
        self.setEnabled(True)
    
    def volpi_not_ready(self):
        """Set volpi not enable."""
        self.setEnabled(False)
    
    def slot_intensity(self, new_intensity):
        self.value_changed(new_intensity)
    
    def property_changed(self, property_name, old_value, new_value):
        """Property changed in GUI designer and when launching app."""
        if property_name == "mnemonic":
                self.set_volpi_object(new_value)
        
        elif property_name == "showBar":
            self.power_bar.setBarVisible(new_value)
            if self.power_bar.dialAndBarInvible():
                self.frame.setVisible(False)
            if new_value:
                self.frame.setVisible(True)
        elif property_name == "showDial":
            self.power_bar.setDialVisible(new_value)
            if self.power_bar.dialAndBarInvible():
                self.frame.setVisible(False)
            if new_value:
                self.frame.setVisible(True)
        elif property_name == "showStep":
            self.step_button.show()
        elif property_name == "stepValue":
            self.position_spinbox.setSingleStep(int(new_value))
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
    
    def update_gui(self):
        if self.volpi_hwobj is not None:
            self.frame.setEnabled(True)
            if self.volpi_hwobj.is_ready():
                self.volpi_hwobj.update_values()
        else:
            self.frame.setEnabled(False)

    def open_step_editor(self):
        if self.is_running():
            if self.step_editor is None:
                self.step_editor = StepEditorDialog(self)
            self.step_editor.set_motor(
                self.motor_hwobj, self, self["label"], self["default_steps"]
            )
            s = self.font().pointSize()
            f = self.step_editor.font()
            f.setPointSize(s)
            self.step_editor.setFont(f)
            self.step_editor.updateGeometry()
            self.step_editor.show()


class _Bar(QtImport.QWidget):

    clickedValue = QtImport.pyqtSignal(int)

    def __init__(self, steps, *args, **kwargs):
        super(_Bar, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QtImport.QSizePolicy.MinimumExpanding,
            QtImport.QSizePolicy.MinimumExpanding
        )

        if isinstance(steps, list):
            # list of colours.
            self.n_steps = len(steps)
            self.steps = steps

        elif isinstance(steps, int):
            # int number of bars, defaults to red.
            self.n_steps = steps
            self.steps = ['red'] * steps

        else:
            raise TypeError('steps must be a list or int')

        self._bar_solid_percent = 0.8
        self._background_color = QtImport.QColor('black')
        self._padding = 4.0  # n-pixel gap around edge.
                
    def paintEvent(self, e):
        painter = QtImport.QPainter(self)

        brush = QtImport.QBrush()
        brush.setColor(self._background_color)
        brush.setStyle(QtImport.Qt.SolidPattern)
        rect = QtImport.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # Get current state.
        parent = self.parent()
        vmin, vmax = parent.minimum(), parent.maximum()
        value = parent.value()
        
        # Define our canvas.
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        # Draw the bars.
        step_size = d_height / self.n_steps
        bar_height = step_size * self._bar_solid_percent
        bar_spacer = step_size * (1 - self._bar_solid_percent) / 2

        # Calculate the y-stop position, from the value in range.
        pc = (value - vmin) / (vmax - vmin)
        n_steps_to_draw = int(pc * self.n_steps)

        for n in range(n_steps_to_draw):
            brush.setColor(QtImport.QColor(self.steps[n]))
            rect = QtImport.QRect(
                self._padding,
                self._padding + d_height - ((1 + n) * step_size) + bar_spacer,
                d_width,
                bar_height
            )
            painter.fillRect(rect, brush)

        painter.end()

    def sizeHint(self):
        return QtImport.QSize(40, 120)

    def _trigger_refresh(self):
        self.update()

    def _calculate_clicked_value(self, e):
        parent = self.parent()
        vmin, vmax = parent.minimum(), parent.maximum()
        d_height = self.size().height() + (self._padding * 2)
        step_size = d_height / self.n_steps
        click_y = e.y() - self._padding - step_size / 2

        pc = (d_height - click_y) / d_height
        value = vmin + pc * (vmax - vmin)
        self.clickedValue.emit(value)

    def mouseMoveEvent(self, e):
        self._calculate_clicked_value(e)

    def mousePressEvent(self, e):
        self._calculate_clicked_value(e)


class PowerBar(QtImport.QWidget):
    """
    Custom Qt Widget to show a power bar and dial.
    Demonstrating compound and custom-drawn widget.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    value_changed = QtImport.pyqtSignal(int)

    def __init__(self, steps=5, *args, **kwargs):
        super(PowerBar, self).__init__(*args, **kwargs)

        layout = QtImport.QVBoxLayout()
        self._bar = _Bar(steps)
        layout.addWidget(self._bar)

        # Create the QDial widget and set up defaults.
        # - we provide accessors on this class to override.
        self._dial = QtImport.QDial()
        self._dial.setNotchesVisible(True)
        self._dial.setWrapping(False)
        self._dial.valueChanged.connect(self._bar._trigger_refresh)
        self._dial.valueChanged.connect(self.slot_value_changed)

        # Take feedback from click events on the meter.
        self._bar.clickedValue.connect(self._dial.setValue)

        layout.addWidget(self._dial)
        self.setLayout(layout)
        # now, _dial and _bar have a parent() a PowerBar object
        

    def __getattr__(self, name):
        if name in self.__dict__:
            return self[name]

        return getattr(self._dial, name)

    def setValue(self, new_value):
        self._dial.setValue(new_value)

    def setColor(self, color):
        self._bar.steps = [color] * self._bar.n_steps
        self._bar.update()

    def setColors(self, colors):
        self._bar.n_steps = len(colors)
        self._bar.steps = colors
        self._bar.update()

    def setBarPadding(self, i):
        self._bar._padding = int(i)
        self._bar.update()

    def setBarSolidPercent(self, f):
        self._bar._bar_solid_percent = float(f)
        self._bar.update()

    def setBackgroundColor(self, color):
        self._bar._background_color = QtImport.QColor(color)
        self._bar.update()

    def slot_value_changed(self, new_value):
        self.value_changed.emit(new_value)
    
    def setDialVisible(self, visible):
        self._dial.setVisible(visible)

    def setBarVisible(self, visible):
        self._bar.setVisible(visible)
    
    def dialAndBarInvible(self):
        return (not self._bar.isVisible() and not self._dial.isVisible())

class StepEditorDialog(QtImport.QDialog):
    def __init__(self, parent):

        QtImport.QDialog.__init__(self, parent)
        # Graphic elements-----------------------------------------------------
        # self.main_gbox = QtGui.QGroupBox('Motor step', self)
        # box2 = QtGui.QWidget(self)
        self.grid = QtImport.QWidget(self)
        label1 = QtImport.QLabel("Current:", self)
        self.current_step = QtImport.QLineEdit(self)
        self.current_step.setEnabled(False)
        label2 = QtImport.QLabel("Set to:", self)
        self.new_step = QtImport.QLineEdit(self)
        self.new_step.setAlignment(QtImport.Qt.AlignRight)
        self.new_step.setValidator(QtImport.QDoubleValidator(self))

        self.button_box = QtImport.QWidget(self)
        self.apply_button = QtImport.QPushButton("Apply", self.button_box)
        self.close_button = QtImport.QPushButton("Dismiss", self.button_box)

        # Layout --------------------------------------------------------------
        self.button_box_layout = QtImport.QHBoxLayout(self.button_box)
        self.button_box_layout.addWidget(self.apply_button)
        self.button_box_layout.addWidget(self.close_button)

        self.grid_layout = QtImport.QGridLayout(self.grid)
        self.grid_layout.addWidget(label1, 0, 0)
        self.grid_layout.addWidget(self.current_step, 0, 1)
        self.grid_layout.addWidget(label2, 1, 0)
        self.grid_layout.addWidget(self.new_step, 1, 1)

        self.main_layout = QtImport.QVBoxLayout(self)
        self.main_layout.addWidget(self.grid)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections -----------------------------------------
        self.new_step.returnPressed.connect(self.apply_clicked)
        self.apply_button.clicked.connect(self.apply_clicked)
        self.close_button.clicked.connect(self.accept)

        # SizePolicies --------------------------------------------------------
        self.close_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Minimum)

        # Other ---------------------------------------------------------------
        self.setWindowTitle("Motor step editor")
        self.apply_button.setIcon(Icons.load_icon("Check"))
        self.close_button.setIcon(Icons.load_icon("Delete"))

    def set_motor(self, motor, brick, name, default_step):
        self.motor_hwobj = motor
        self.brick = brick

        if name is None or name == "":
            name = motor.username
        self.setWindowTitle(name)
        self.setWindowTitle("%s step editor" % name)
        self.current_step.setText(str(brick.get_line_step()))

    def apply_clicked(self):
        try:
            val = float(str(self.new_step.text()))
        except ValueError:
            return
        self.brick.set_line_step(val)
        self.new_step.setText("")
        self.current_step.setText(str(val))
        self.close()