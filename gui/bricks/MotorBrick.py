#  Project: framework2-plus
#  https://gitlab.esrf.fr/ui/framework2-plus
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

"""Motor brick

The standard Motor brick.
"""

import logging
import sys
import math

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
#import Qwt5 as qwt

__credits__ = ["Framework2-plus collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"

class MotorControlDialog(QtImport.QDialog):
    """
    Dialog to control motor.

    Long description for Motor Control Dialog
    """

    def __init__(self, parent, title):
        """
        Constructor of MotorControlDialog

        :param parent: dialog's parent
        :param caption: displayed text
        """

        super().__init__(parent)

        self.motor_widget = MotorBrick(self)

        self.setWindowTitle(title)
        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Minimum)

        # Layout --------------------------------------------------------------
        self._dialog_vlayout = QtImport.QVBoxLayout(self)
        self._dialog_vlayout.addWidget(self.motor_widget)



    def set_motor_mnemonic(self, mnemonic):
        self.motor_widget.get_property("allowConfigure").set_value(True)
        self.motor_widget.read_properties()
        self.motor_widget.set_mnemonic(mnemonic)

    def set_motor_object(self, obj):
        self.motor_widget.get_property("allowConfigure").set_value(True)
        self.motor_widget.read_properties()
        self.motor_widget.set_motor_object(obj)

    def set_position_format_string(self, format):
        self.motor_widget["formatString"] = format

    def close_clicked(self, action):
        self.accept()

    def run(self):
        self.motor_widget.run()


class StepEditor(QtImport.QFrame):
    """ Brick to handle the step a motor position changes.

    Long description for Step Editor
    """

    (LEFT_LAYOUT, RIGHT_LAYOUT) = (0,1)
    value_changed_signal = QtImport.pyqtSignal('double')
    clicked_signal = QtImport.pyqtSignal('double')

    def __init__(self, layout, initial_value, parent=None, title="", prefix=""):
        super().__init__(parent)

        self.prefix = prefix
        self.value = initial_value

        # Graphic elements-----------------------------------------------------

        self.title_label = QtImport.QLabel(title)
        self.selection_box = QtImport.QFrame()
        self.edition_box = QtImport.QFrame()

        self.txt_new_value = QtImport.QLineEdit()
        self.cmd_ok = QtImport.QPushButton()
        self.cmd_cancel = QtImport.QPushButton()

        # Layout --------------------------------------------------------------

        self.main_vertical_layout = QtImport.QVBoxLayout()
        self.selection_box_layout = QtImport.QHBoxLayout()
        self.edition_box_layout = QtImport.QHBoxLayout()

        # widget's addition order defines their position

        self.edition_box_layout.addWidget(self.txt_new_value)
        self.edition_box_layout.addWidget(self.cmd_ok)
        self.edition_box_layout.addWidget(self.cmd_cancel)
        self.edition_box.setLayout(self.edition_box_layout)

        self.selection_box_layout.addWidget(self.edition_box)

        if layout == StepEditor.RIGHT_LAYOUT:
            # logging.getLogger().error(
            #     f"Setting button text : {prefix} {initial_value} {str(initial_value)}"
            # )
            self.cmd_select_value = QtImport.QPushButton(prefix + str(initial_value))
            self.cmd_edit_value = QtImport.QPushButton("...")
            self.selection_box_layout.addWidget(self.cmd_select_value)
            self.selection_box_layout.addWidget(self.cmd_edit_value)

            # logging.getLogger().error(f"Button text : {self.cmd_select_value.text()}")
        else:
            # logging.getLogger().error(
            #     f"Setting button text : {prefix} {initial_value} {str(initial_value)}"
            # )
            self.cmd_edit_value = QtImport.QPushButton("...")
            self.cmd_select_value = QtImport.QPushButton(prefix + str(initial_value))
            self.selection_box_layout.addWidget(self.cmd_edit_value)
            self.selection_box_layout.addWidget(self.cmd_select_value)
            # logging.getLogger().error(f"Button text : {self.cmd_select_value.text()}")

        self.selection_box.setLayout(self.selection_box_layout)

        self.main_vertical_layout.addWidget(self.title_label)
        self.main_vertical_layout.addWidget(self.selection_box)

        self.setLayout(self.main_vertical_layout)

        # Qt signal/slot connections -----------------------------------------
        self.cmd_select_value.clicked.connect(self.cmd_select_value_clicked)
        self.cmd_edit_value.clicked.connect(self.cmd_edit_values_clicked)
        self.txt_new_value.returnPressed.connect(self.validate_new_value)
        self.cmd_ok.clicked.connect(self.validate_new_value)
        self.cmd_cancel.clicked.connect(self.end_edit)

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.cmd_cancel.setIcon(Icons.load_icon("button_cancel_small"))
        self.cmd_ok.setIcon(Icons.load_icon("button_ok_small"))
        self.edition_box.hide()
        self.title_label.hide()
        self.cmd_select_value.setAutoDefault(False)
        self.cmd_ok.setFixedWidth(20)
        self.cmd_cancel.setFixedWidth(20)
        self.edition_box.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)

        self.double_validator = QtImport.QDoubleValidator(self.txt_new_value)
        self.double_validator.setNotation(QtImport.QDoubleValidator.StandardNotation)
        self.txt_new_value.setValidator(self.double_validator)

    def set_title(self, title):
        self.title_label.setText(title)

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.cmd_select_value.setText(self.prefix + str(self.value))

    def set_value(self, value):
        self.value = value
        self.cmd_select_value.setText(self.prefix + str(value))

    def allow_change_value(self, allow):
        self.cmd_edit_value.show() if allow else self.cmd_edit_value.hide()

    def cmd_select_value_clicked(self):
        self.clicked_signal.emit(self.value)

    def cmd_edit_values_clicked(self):
        self.cmd_edit_value.hide()
        self.cmd_select_value.hide()
        self.edition_box.show()
        self.title_label.show()
        self.txt_new_value.setText(str(self.value))
        self.txt_new_value.selectAll()
        self.txt_new_value.setFocus()

    def end_edit(self):
        self.cmd_edit_value.show()
        self.cmd_select_value.show()
        self.title_label.hide()
        self.edition_box.hide()
        self.value_changed_signal.emit(self.value)

    def validate_new_value(self):
        try:
            self.value = float(str(self.txt_new_value.text()))
        except BaseException:
            logging.getLogger().error( f"{self.txtNewValue.text()} is not a valid float value" )
        else:
            self.cmd_select_value.setText(self.prefix + str(self.value))
            self.end_edit()

# class StepEditor(QtImport.QWidget):
#     """ Widget to handle the motor movement step
#
#     Long description for StepEditor
#     """
#     (LEFT_LAYOUT, RIGHT_LAYOUT) = (0,1)
#
#     #define signals
#     value_changed_signal = QtImport.pyqtSignal(float)
#     clicked_signal = QtImport.pyqtSignal(float)
#
#     def __init__(self, parent, layout, initial_value, title = "", prefix = "" ):
#         super().__init__(parent)
#
#         self.prefix = prefix
#         self.value = initial_value
#
#         # Graphic elements-----------------------------------------------------
#
#         self.label_title = QtImport.QLabel(title, self)
#         selection_box = QtImport.QWidget(self)
#         selection_box_layout = QtImport.QVBoxLayout()
#
#         self.edition_box = QtImport.QWidget(selection_box)
#         edition_box_layout = QtImport.QVBoxLayout()
#
#         if layout == StepEditor.RIGHT_LAYOUT:
#             self.cmd_select_value = QtImport.QPushButton(prefix + str(initial_value), selection_box)
#             self.cmd_edit_value = QtImport.QPushButton("...", selection_box)
#
#         else:
#             self.cmd_edit_value = QtImport.QPushButton("...", selection_box)
#             self.cmd_select_value = QtImport.QPushButton(prefix + str(initial_value), selection_box)
#
#         self.txt_new_value = QtImport.QLineEdit(self.edition_box)
#         self.cmd_ok = QtImport.QPushButton(self.edition_box)
#         self.cmd_cancel = QtImport.QPushButton(self.edition_box)
#
#         # SizePolicies -/- Layout -/- Other /---------------------------
#         self.cmd_cancel.setIcon(Icons.load_icon("button_cancel_small"))
#         self.cmd_cancel.setIcon(Icons.load_icon("button_cancel_small"))
#         self.cmd_ok.setIcon(Icons.load_icon("button_ok_small"))  # Icons.tinyOK))
#         self.edition_box.hide()
#         self.label_title.hide()
#         self.setFocusProxy(self.txt_new_value)
#         self.txt_new_value.setFixedWidth(self.fontMetrics().width(" 888.888 "))
#         self.cmd_edit_value.setFixedWidth(self.fontMetrics().width(" ... "))
#         self.cmd_select_value.setFixedWidth(
#             self.fontMetrics().width(prefix + " 888.888 ")
#         )
#         self.cmd_select_value.setAutoDefault(False)
#         self.cmd_ok.setFixedWidth(20)
#         self.cmd_cancel.setFixedWidth(20)
#         self.edition_box.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)
#
#         # Qt signal/slot connections -----------------------------------------
#
#         self.cmd_select_value.clicked.connect(self.select_value_clicked)
#         self.cmd_edit_value.clicked.connect(self.edit_value_clicked)
#         self.cmd_ok.clicked.connect(self.validate_new_value)
#         self.txt_new_value.returnPressed.connect(self.validate_new_value)
#         self.cmd_cancel.clicked.connect(self.end_edit)
#
#     def set_title(self, title):
#         self.label_title.setText(title)
#
#     def set_prefix(self, prefix):
#         self.prefix = prefix
#         self.cmd_select_value.setText(self.prefix + str(self.value))
#
#     def set_value(self, value):
#         self.value = value
#         self.cmd_select_value.setText(self.prefix + str(self.value))
#
#     def allow_value_change(self, allow):
#         if allow:
#             self.cmd_edit_value.show()
#         else:
#             self.cmd_edit_value.hide()
#
#     def select_value_clicked(self):
#         self.clicked_signal.emit(self.value)
#
#     def edit_value_clicked(self):
#         self.cmd_edit_value.hide()
#         self.cmd_select_value.hide()
#         self.edition_box.hide()
#         self.label_title.show()
#         self.txt_new_value.setText(str(self.value))
#         self.txt_new_value.selectAll()
#         self.txt_new_value.setFocus()
#
#     def end_edit(self):
#         self.cmd_edit_value.show()
#         self.cmd_select_value.show()
#         self.label_title.hide()
#         self.edition_box.hide()
#         self.value_changed_signal.emit(self.value)
#
#
#     def validate_new_value(self):
#         try:
#             self.value = float(str(self.txt_new_value.text()))
#         except BaseException:
#             logging.getLogger().error(
#                 "%s is not a valid float value" % str(self.txtNewValue.text())
#             )
#         else:
#             self.cmd_select_value.setText(self.prefix + str(self.value))
#             self.end_edit()

class MotorSlider(QtImport.QWidget):
    """ Slider to display and control motor position

    Long description for MotorSlider
    """

    stylesheet1 = """
        .QSlider::groove:horizontal {
            background: red;
            position: absolute; /* absolutely position 4px from the left and right of the widget. setting margins on the widget should work too... */
            left: 4px; right: 4px;
            height: 15px;
        }

        .QSlider::handle:horizontal {
            height: 8px;
            background: green;
            margin: -5px -8px; /* expand outside the groove */
            border-radius: 3px;
        }

        .QSlider::add-page:horizontal {
            background: white;
        }

        .QSlider::sub-page:horizontal {
            background: pink;
        }
        """

    stylesheet2 = """
            .QSlider::handle:horizontal {
                background: #22B14C;
                border: 5px solid #B5E61D;
                width: 23px;
                height: 100px;
                margin: -24px -12px;
            }                   

        """
    def __init__(self, parent = None):
        super().__init__(parent)

        self.values_format = "%+8.4f"#"{0:8.4f}"

        # slider params:

        self.slider = QtImport.QSlider()
        self.slider.setEnabled(False)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtImport.QSlider.TicksBothSides)
        self.slider.setOrientation(QtImport.Qt.Horizontal)

        # extra controls
        min_value_text = self.values_format % self.slider.minimum()
        max_value_text = self.values_format % self.slider.maximum()
        current_value_text = self.values_format % self.slider.value()
        self.min_label = QtImport.QLabel(min_value_text)
        self.max_label = QtImport.QLabel(max_value_text)
        self.current_label = QtImport.QLabel(current_value_text)

        # layouts
        self.main_v_layout = QtImport.QVBoxLayout()
        self.labels_h_layout = QtImport.QHBoxLayout()

        self.labels_h_layout.addWidget(self.min_label)
        self.labels_h_layout.addStretch()
        self.labels_h_layout.addWidget(self.current_label)
        self.labels_h_layout.addStretch()
        self.labels_h_layout.addWidget(self.max_label)

        self.main_v_layout.addLayout(self.labels_h_layout)
        self.main_v_layout.addWidget(self.slider)

        self.setLayout(self.main_v_layout)

        # stylesheets
        self.slider.setStyleSheet(self.stylesheet1)


        self.slider.valueChanged.connect(self.value_changed)
        #def minimumSizeHint(self):

        # w = QtImport.QSlider.minimumSizeHint(self).width()
        # th = self.fontMetrics().height()
        # h = self.
    def set_position_format_string(self, format):
        # logging.getLogger().error(
        #     f"def set_position_format_string : {format}"
        # )
        self.values_format = format
        #self.repaint()

    def set_value(self, value):

        if value is not None:
            self.slider.setValue(value)
            current_value_text = self.values_format % self.slider.value()
            self.current_label.setText(current_value_text)

    def minimum(self):
        return self.slider.minimum()

    def set_range(self, min, max):
        logging.getLogger().error(f"def set_range : min {min} -max {max} " )
        if min == float("-inf") or min is None:
            min = -100#-2147483648
        if max == float("inf") or max is None:
            max = 100#2147483647
        logging.getLogger().error(f"def set_range after if : min {min} -max {max} ")
        self.slider.setRange(min, max)
        self.slider.setValue((max + min)/2)
        self.set_min(min)
        self.set_max(max)

    def set_min(self, value):
        self.slider.setMinimum(value)
        value_text = self.values_format % value
        self.min_label.setText(value_text)

    def set_max(self, value):
        self.slider.setMaximum(value)
        value_text = self.values_format % value
        self.max_label.setText(value_text)

    def value_changed(self):
        # logging.getLogger().error(
        #     f"value_changed : {self.slider.value()} - {self.values_format} - {self.values_format % self.slider.value() }"
        # )
        self.current_label.setText(self.values_format % self.slider.value())

    #def paintEvent(self, QPaintEvent):


class MoveBox(QtImport.QWidget):
    """Helper class"""

    # define signals
    move_motor_signal = QtImport.pyqtSignal(float)
    clicked_signal = QtImport.pyqtSignal(float)
    stop_motor_signal = QtImport.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.old_positions = []  # history of motor positions

        self.label_move = QtImport.QLabel("go to ", self)
        self.text_move = QtImport.QLineEdit("", self)
        self.cmd_move = QtImport.QPushButton("", self)
        self.cmd_move.setCheckable(True)
        self.cmd_go_back = QtImport.QPushButton("", self)
        self.cmd_stop = QtImport.QPushButton("", self)

        self.text_move.setFixedWidth(self.text_move.fontMetrics().width("8888.8888"))
        self.cmd_move.setCheckable(True)
        # QPixmap(Icons.stopXPM_small))
        self.cmd_stop.setIcon(Icons.load_icon("stop_small"))
        self.cmd_stop.setEnabled(False)
        # QPixmap(Icons.gobackXPM_small))
        self.cmd_go_back.setIcon(Icons.load_icon("goback_small"))
        # QPixmap(Icons.moveXPM_small))
        self.cmd_move.setIcon(Icons.load_icon("move_small"))
        self.cmd_go_back.setEnabled(False)


        # connections

        self.text_move.textChanged.connect(self.text_move_text_changed)
        self.cmd_move.clicked.connect(self.move_clicked)
        self.cmd_stop.clicked.connect(self.stop_motor_signal)
        self.text_move.returnPressed.connect(self.text_move_return_pressed)
        #self.text_move.textChanged.connect(self.text_move_text_changed)
        self.cmd_go_back.clicked.connect(self.go_back_clicked)

        # layout

        hboxlayout = QtImport.QHBoxLayout(self)

        hboxlayout.insertSpacerItem(
            0,
            QtImport.QSpacerItem(0, 0, QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)
        )

        hboxlayout.addWidget(self.label_move)
        hboxlayout.addWidget(self.text_move)
        hboxlayout.addWidget(self.cmd_move)
        hboxlayout.addWidget(self.cmd_go_back)
        hboxlayout.addWidget(self.cmd_stop)
        hboxlayout.insertSpacerItem(
            0,
            QtImport.QSpacerItem(0, 0, QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)
        )

        self.setLayout(hboxlayout)

    def move_clicked(self):
        self.text_move_return_pressed()

    def set_old_position(self, position):
        position = str(position)

        if len(self.old_positions) == 20:
            del self.old_positions[-1]

        if position in self.old_positions:
            return

        self.old_positions.insert(0, position)

    def text_move_return_pressed(self):
        try:
            move_position = float(str(self.text_move.text()))
            print(f"text_move_return_pressed text = {self.text_move.text()}")
            print(f"text_move_return_pressed str(text) = {str(self.text_move.text())}")
            print(f"text_move_return_pressed float(str(txt)) = {move_position}")
        except BaseException:
            self.cmd_move.setChecked(False)
        else:
            self.move_motor_signal.emit(move_position)

    def text_move_text_changed(self, text):
        if len(text) > 0 and not self.cmd_move.isChecked():
            self.cmd_move.setEnabled(True)
        else:
            self.cmd_move.setEnabled(False)

    def go_back_clicked(self):
        # show popup menu with all recorded previous positions
        old_positions_menu = QtImport.QMenu(self)
        old_positions_menu.addSection(str("<nobr><b>Last positions :</b></nobr>"))

        old_positions_menu.addSeparator()

        for i in range(len(self.old_positions)):
            receiver = lambda pos_index = i: self.go_to_old_position(pos_index)
            position_action = old_positions_menu.addAction(self.old_positions[i])
            position_action.triggered.connect(receiver)

        old_positions_menu.exec_(QtImport.QCursor.pos())

    def go_to_old_position(self, id):
        pos = self.old_positions[id]
        self.text_move.setText(pos)
        self.text_move_return_pressed()

    def set_is_moving(self, moving):
        if moving:
            self.text_move.setText("")
            self.cmd_move.setChecked(True)
            self.cmd_move.setEnabled(False)
            self.cmd_go_back.setEnabled(False)
            self.cmd_stop.setEnabled(True)
        else:
            self.cmd_move.setChecked(False)
            if len(self.text_move.text()) > 0:
                self.cmd_move.setEnabled(True)
            else:
                self.cmd_move.setEnabled(False)
            if len(self.old_positions) > 0:
                self.cmd_go_back.setEnabled(True)
            self.cmd_stop.setEnabled(False)

class MotorBrick(BaseWidget):
    """ Brick to handle a motor.

    Long description for Motor Brick
    """

    def __init__(self, *args):
        super().__init__(*args)

        #BaseComponents.BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        self.motor_hwobj = None  # hardware object
        self.control_dialog = None

        # Graphic elements-----------------------------------------------------

        self.frame = QtImport.QGroupBox()
        self.frame_layout = QtImport.QVBoxLayout()

        self.step_slider_panel = QtImport.QWidget()
        step_slider_panel_layout = QtImport.QHBoxLayout()

        self.move_box = MoveBox()


        self.step_backward = StepEditor(
            StepEditor.LEFT_LAYOUT, 20, None, "new step:", "-"
        )

        self.slider = MotorSlider()

        self.step_forward = StepEditor(
            StepEditor.RIGHT_LAYOUT, 20, None, "new step:", "+"
        )
        self.motor_position_label = self.slider.current_label
        self.name_position_box = QtImport.QFrame()
        self.name_position_box_layout = QtImport.QHBoxLayout()
        self.motor_name_label = QtImport.QLabel()
        self.position_label = QtImport.QLabel()

        # Layout --------------------------------------------------------------
        step_slider_panel_layout.addWidget(self.step_backward)
        step_slider_panel_layout.addWidget(self.slider)
        step_slider_panel_layout.addWidget(self.step_forward)
        self.step_slider_panel.setLayout(step_slider_panel_layout)

        self.frame_layout.addWidget(self.step_slider_panel)
        self.frame_layout.addWidget(self.move_box, 0, QtImport.Qt.AlignCenter)
        self.frame.setLayout(self.frame_layout)

        self.name_position_box_layout.addWidget(self.motor_name_label)
        self.name_position_box_layout.addWidget(self.position_label)

        self.name_position_box.setLayout(self.name_position_box_layout)


        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Fixed)
        self.frame.setFlat(False)
        #self.frame.setInsideMargin(5)
        #self.frame.setInsideSpacing(5)
        self.step_backward.allow_change_value(False)
        self.step_slider_panel.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Fixed)
        self.name_position_box.hide()
        self.name_position_box.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)
        self.name_position_box.setFrameStyle(QtImport.QFrame.Panel | QtImport.QFrame.Raised)
        self.name_position_box.setLineWidth(1)
        self.name_position_box.setMidLineWidth(0)
        self.motor_name_label.setAlignment(QtImport.Qt.AlignLeft | QtImport.Qt.AlignVCenter)
        self.position_label.setAlignment(QtImport.Qt.AlignRight | QtImport.Qt.AlignVCenter)

        self.main_layout = QtImport.QVBoxLayout()#, 5, 5)  # GridLayout(self, 2, 1, 5, 5)
        self.main_layout.addWidget(self.name_position_box, 0, QtImport.Qt.AlignTop)
        self.main_layout.addWidget(self.frame, 0, QtImport.Qt.AlignCenter)

        self.setLayout(self.main_layout)

        # Qt signal/slot connections -----------------------------------------
        self.move_box.move_motor_signal.connect(self.move_motor)
        self.move_box.stop_motor_signal.connect(self.stop_motor)
        self.step_forward.clicked_signal.connect(self.step_forward_clicked)
        self.step_forward.value_changed_signal.connect(self.step_forward_value_changed)
        self.step_backward.clicked_signal.connect(self.step_backward_clicked)

        # define properties

        self.add_property("appearance", "combo", ("tiny", "normal"), "normal")
        self.add_property("allowConfigure", "boolean", True)
        self.add_property("mnemonic", "string", "")
        self.add_property("allowDoubleClick", "boolean", False)
        self.add_property("formatString", "formatString", "+##.####")  # %+8.4f
        self.add_property("dialogCaption", "string", "", hidden=True)

    def slot_position(self, new_position):
        # print "MotorBrick.slot_position",newPosition
        # uname = self.motor_hwobj.userName.ljust(6).replace(' ', '&nbsp;')

        if new_position is None:
            pos = self.get_property("formatString").get_user_value()
            new_position = self.slider.minimum()
        else:
            pos = self["formatString"] % new_position
            # pos.replace(' ', '&nbsp;')

        self.slider.set_value(new_position)
        print(f'slot_position : new_position {new_position} - pos : {pos}')
        self.position_label.setText('<nobr><font face="courier">%s</font></nobr>' % pos)

    def slot_status(self, state):
        state = state - 1
        color = [
            self.palette().window(),
            Colors.LIGHT_GREEN,
            Colors.YELLOW,
            Colors.LIGHT_RED,
            self.palette().window(),
        ]

        palette = QtImport.QPalette()
        palette.setColor(QtImport.QPalette.Window, color[state])
        self.motor_name_label.setPalette(palette)
        self.position_label.setPalette(palette)
        self.motor_position_label.setPalette(palette)

        if state == 2:  # start moving
            self.move_box.set_old_position(self.motor_hwobj.getPosition())
        elif state == 3:  # moving
            self.step_forward.setEnabled(False)
            self.step_backward.setEnabled(False)
            self.move_box.set_is_moving(True)
        else:
            self.step_forward.setEnabled(True)
            self.step_backward.setEnabled(True)
            self.move_box.set_is_moving(False)

    def limit_changed(self, limits):
        self.slider.set_range(limits[0], limits[1])

    def move_motor(self, new_position):
        print(f"Motor Brick move_motor new_position = {new_position}")
        self.motor_hwobj.move(new_position)

    def stop_motor(self):
        self.motor_hwobj.stop()

    # def cmd_configure_clicked(self):
    #     configureDialog = ConfigureDialog(self, self.motor_hwobj)
    #     configureDialog.exec_loop()

    def step_forward_clicked(self, value):
        current_position = self.motor_hwobj.getPosition()
        self.move_motor(current_position + value)

    def step_forward_value_changed(self, value):
        logging.getLogger().error(
            f"MotorBrick step_forward_value_changed : {value}"
        )
        self.step_backward.set_value(value)
        self.step_forward.set_value(value)
        self.motor_hwobj.GUIstep = value

    def step_backward_clicked(self, value):
        currentPosition = self.motor_hwobj.getPosition()
        self.move_motor(currentPosition - value)

    def motor_ready(self):
        self.setEnabled(True)

    def motor_not_ready(self):
        self.setEnabled(False)

    def stop(self):
        if self.control_dialog is not None:
            self.control_dialog.hide()

    def set_mnemonic(self, mne):
        self["mnemonic"] = mne

    def set_motor_object(self, obj):
        if self.motor_hwobj is not None:
            # self.disconnect(self.motor_hwobj, PYSIGNAL("deviceReady"), self.motor_ready)
            # self.disconnect(self.motor_hwobj, PYSIGNAL("deviceNotReady"), self.motor_not_ready)
            # self.disconnect(self.motor_hwobj, PYSIGNAL("positionChanged"), self.slot_position)
            # self.disconnect(self.motor_hwobj, PYSIGNAL("stateChanged"), self.slot_status)
            # self.disconnect(self.motor_hwobj, PYSIGNAL("limitsChanged"), self.limit_changed)

            # TODO : change HardwareRepository/BaseHardwareObject.py -> class Device : declare signals!!

            self.disconnect(self.motor_hwobj, "deviceReady", self.motor_ready)
            self.disconnect(self.motor_hwobj, "deviceNotReady", self.motor_not_ready)
            self.disconnect(self.motor_hwobj, "positionChanged", self.slot_position)
            self.disconnect(self.motor_hwobj, "stateChanged", self.slot_status)
            self.disconnect(self.motor_hwobj, "limitsChanged", self.limit_changed)

            # self.motor_hwobj.deviceReady.disconnect(self.motor_ready)
            # self.motor_hwobj.deviceNotReady.disconnect(self.motor_not_ready)
            # self.motor_hwobj.positionChanged.disconnect(self.slot_position)
            # self.motor_hwobj.stateChanged.disconnect(self.slot_status)
            # self.motor_hwobj.limitsChanged.disconnect(self.limit_changed)

            if self.control_dialog is not None:
                self.control_dialog.close(True)
                self.control_dialog = None

        self.motor_hwobj = obj

        if self.motor_hwobj is not None:
            self.setEnabled(True)

            # self.connect(self.motor_hwobj, PYSIGNAL("deviceReady"), self.motor_ready)
            # self.connect(self.motor_hwobj, PYSIGNAL("deviceNotReady"), self.motor_not_ready)
            # self.connect(self.motor_hwobj, PYSIGNAL("positionChanged"), self.slot_position)
            # self.connect(self.motor_hwobj, PYSIGNAL("stateChanged"), self.slot_status)
            # self.connect(self.motor_hwobj, PYSIGNAL("limitsChanged"), self.limit_changed)

            self.connect(self.motor_hwobj, "deviceReady", self.motor_ready)
            self.connect(self.motor_hwobj, "deviceNotReady", self.motor_not_ready)
            self.connect(self.motor_hwobj, "positionChanged", self.slot_position)
            self.connect(self.motor_hwobj, "stateChanged", self.slot_status)
            self.connect(self.motor_hwobj, "limitsChanged", self.limit_changed)

            # self.motor_hwobj.deviceReady.connect(self.motor_ready)
            # self.motor_hwobj.deviceNotReady.connect(self.motor_not_ready)
            # self.motor_hwobj.positionChanged.connect(self.slot_position)
            # self.motor_hwobj.stateChanged.connect(self.slot_status)
            # self.motor_hwobj.limitsChanged.connect(self.limit_changed)

            self.frame.setTitle(self.motor_hwobj.username + " :")
            self.motor_name_label.setText(
                '<nobr><font face="courier"><b>%s</b></font></nobr>'
                % self.motor_hwobj.username
            )

            step = 1.0
            if hasattr(self.motor_hwobj, "GUIStep"):
                if self.motor_hwobj.GUIStep is not None:
                    step = self.motor_hwobj.GUIStep

            self.step_backward.set_value(step)
            self.step_forward.set_value(step)

            if self.motor_hwobj.isReady():
                self.limit_changed(self.motor_hwobj.getLimits())
                self.slot_position(self.motor_hwobj.getPosition())
                self.slot_status(self.motor_hwobj.getState())
                self.motor_ready()
            else:
                self.motor_not_ready()

    def mouseDoubleClickEvent(self, mouseEvent):
        print (f'mouseDoubleClickEvent is running {self.is_running()} - {self.get_property("allowDoubleClick").value} - {self.get_property("appearance").value}')
        if (
                self.is_running()
                and self.get_property("allowDoubleClick").value == 1
                and self.get_property("appearance").value == "tiny"
        ):
            #
            # show full motor_hwobj control in another window
            #
            print (f'mouseDoubleClickEvent inside if')
            if self.control_dialog is None:
                print (f'mouseDoubleClickEvent control_dialog is NONE')
                self.control_dialog = MotorControlDialog(
                    self, self["dialogCaption"] or self.motor_hwobj.username
                )
                self.control_dialog.set_motor_mnemonic(self["mnemonic"])

            self.control_dialog.set_position_format_string(self["formatString"])
            self.control_dialog.show()
            self.control_dialog.activateWindow()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "appearance":
            if new_value == "tiny":
                self.main_layout.setContentsMargins(2, 2, 2, 2)
                self.main_layout.setSpacing(0)
                self.frame.hide()
                self.name_position_box.show()
                self.updateGeometry()
            elif new_value == "normal":
                self.step_slider_panel.show()
                self.main_layout.setContentsMargins(2, 2, 2, 2)
                self.main_layout.setSpacing(5)
                self.frame.show()
                self.name_position_box.hide()
                self.updateGeometry()
        elif property_name == "formatString":
            # tmp = self["formatString"]
            # logging.getLogger().error(
            #     f"""property_changed property_name == "formatString" {tmp}"""
            # )
            self.slider.set_position_format_string(self["formatString"])

            if self.motor_hwobj is not None and self.motor_hwobj.isReady():
                self.slot_position(self.motor_hwobj.getPosition())
                return

            self.slot_position(None)
        elif property_name == "allowConfigure":
            pass
        elif property_name == "allowDoubleClick":
            pass
        elif property_name == "mnemonic":
            if self.motor_hwobj is not None:

                self.disconnect(self.motor_hwobj, "deviceReady", self.motor_ready)
                self.disconnect(self.motor_hwobj, "deviceNotReady", self.motor_not_ready)
                self.disconnect(self.motor_hwobj, "positionChanged", self.slot_position)
                self.disconnect(self.motor_hwobj, "stateChanged", self.slot_status)
                self.disconnect(self.motor_hwobj, "limitsChanged", self.limit_changed)

                if self.control_dialog is not None:
                    self.control_dialog.close(True)
                    self.control_dialog = None

            self.motor_hwobj = self.get_hardware_object(new_value)

            print(type(self.motor_hwobj))
            print(dir(self.motor_hwobj))

            if self.motor_hwobj is not None:
                self.setEnabled(True)

                self.connect(self.motor_hwobj, "deviceReady", self.motor_ready)
                self.connect(self.motor_hwobj, "deviceNotReady", self.motor_not_ready)
                self.connect(self.motor_hwobj, "positionChanged", self.slot_position)
                self.connect(self.motor_hwobj, "stateChanged", self.slot_status)
                self.connect(self.motor_hwobj, "limitsChanged", self.limit_changed)

                self.frame.setTitle(self.motor_hwobj.username + " :")
                self.motor_name_label.setText(
                    '<nobr><font face="courier"><b>%s</b></font></nobr>'
                    % self.motor_hwobj.username
                )

                step = 1.0
                if hasattr(self.motor_hwobj, "GUIStep"):
                    if self.motor_hwobj.GUIStep is not None:
                        step = self.motor_hwobj.GUIStep
                else:
                    logging.getLogger().error(f"self.motor_hwobj has no GUIStep attribute")

                # try:
                #     s = self.motor_hwobj.GUIstep
                # except BaseException:
                #     s = 1

                self.step_backward.set_value(step)
                self.step_forward.set_value(step)

                if self.motor_hwobj.isReady():
                    self.limit_changed(self.motor_hwobj.getLimits())
                    self.slot_position(self.motor_hwobj.getPosition())
                    self.slot_status(self.motor_hwobj.getState())
                    self.motor_ready()
                else:
                    self.motor_not_ready()
            else:
                self.frame.setTitle("motor_hwobj :")
                self.motor_name_label.setText(
                    '<nobr><font face="courier"><b>-</b></font></nobr>'
                )
                self.step_backward.set_value(1)
                self.step_forward.set_value(1)
                self.setEnabled(False)


class DialogButtonsBar(QtImport.QWidget):
    DEFAULT_MARGIN = 6
    DEFAULT_SPACING = 6

    def __init__(self, parent, button1="OK", button2="Cancel", button3=None, callback=None, margin=6, spacing=6):
        super().__init__(parent)

        self.callback = callback
        spacer = QtImport.QWidget(self)
        spacer.setSizePolicy(QtImport.QSizePolicy.Expanding,QtImport.QSizePolicy.Fixed)

        # Layout --------------------------------------------------------------
        self._dialog_vlayout = QtImport.QVBoxLayout(self,margin,spacing)
        self._dialog_vlayout.addWidget(spacer)

        if button1 is not None:
            self.button1 = QtImport.QPushButton(button1, self)
            self._dialog_vlayout.addWidget(self.button1)
            self.button1.clicked.connect(self.button1_clicked)

        if button2 is not None:
            self.button2 = QtImport.QPushButton(button1, self)
            self._dialog_vlayout.addWidget(self.button2)
            self.button2.clicked.connect(self.button2_clicked)

        if button3 is not None:
            self.button3 = QtImport.QPushButton(button1, self)
            self._dialog_vlayout.addWidget(self.button3)
            self.button3.clicked.connect(self.button3_clicked)

        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Fixed)
        self.setLayout(self._dialog_vlayout)

    def button1_clicked(self):
        if callable(self.callback):
            self.callback(str(self.button1.text()))

    def button2_clicked(self):
        if callable(self.callback):
            self.callback(str(self.button2.text()))

    def button3_clicked(self):
        if callable(self.callback):
            self.callback(str(self.button3.text()))
