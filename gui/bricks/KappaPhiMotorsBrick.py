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


from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"


class KappaPhiMotorsBrick(BaseWidget):

    STATE_COLORS = (
        Colors.LIGHT_RED,
        Colors.DARK_GRAY,
        Colors.LIGHT_GREEN,
        Colors.LIGHT_YELLOW,
        Colors.LIGHT_YELLOW,
        Colors.LIGHT_YELLOW,
    )

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("showStop", "boolean", True)
        self.add_property("defaultStep", "string", "10.0")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements-----------------------------------------------------
        _main_gbox = QtImport.QGroupBox(self)

        self.kappa_dspinbox = QtImport.QDoubleSpinBox(_main_gbox)
        self.kappa_dspinbox.setRange(-360, 360)
        self.kappaphi_dspinbox = QtImport.QDoubleSpinBox(_main_gbox)
        self.kappaphi_dspinbox.setRange(-360, 360)
        self.step_cbox = QtImport.QComboBox(_main_gbox)
        self.step_button_icon = Icons.load_icon("TileCascade2")
        self.close_button = QtImport.QPushButton(_main_gbox)
        self.stop_button = QtImport.QPushButton(_main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = QtImport.QHBoxLayout(_main_gbox)
        _main_gbox_hlayout.addWidget(QtImport.QLabel("Kappa:", _main_gbox))
        _main_gbox_hlayout.addWidget(self.kappa_dspinbox)
        _main_gbox_hlayout.addWidget(QtImport.QLabel("Phi:", _main_gbox))
        _main_gbox_hlayout.addWidget(self.kappaphi_dspinbox)
        _main_gbox_hlayout.addWidget(self.step_cbox)
        _main_gbox_hlayout.addWidget(self.close_button)
        _main_gbox_hlayout.addWidget(self.stop_button)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(_main_gbox)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        kappa_dspinbox_event = SpinBoxEvent(self.kappa_dspinbox)
        kappaphi_dspinbox_event = SpinBoxEvent(self.kappaphi_dspinbox)
        self.kappa_dspinbox.installEventFilter(kappa_dspinbox_event)
        self.kappaphi_dspinbox.installEventFilter(kappaphi_dspinbox_event)
        kappa_dspinbox_event.returnPressedSignal.connect(self.change_position)
        kappaphi_dspinbox_event.returnPressedSignal.connect(self.change_position)
        self.kappa_dspinbox.lineEdit().textEdited.connect(self.kappa_value_edited)
        self.kappaphi_dspinbox.lineEdit().textEdited.connect(self.kappaphi_value_edited)

        self.step_cbox.activated.connect(self.go_to_step)
        self.step_cbox.activated.connect(self.step_changed)
        self.step_cbox.textChanged.connect(self.step_edited)

        self.close_button.clicked.connect(self.close_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)

        # self.stop_button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
        # Other ---------------------------------------------------------------
        self.kappa_dspinbox.setAlignment(QtImport.Qt.AlignRight)
        self.kappa_dspinbox.setFixedWidth(75)
        self.kappaphi_dspinbox.setAlignment(QtImport.Qt.AlignRight)
        self.kappaphi_dspinbox.setFixedWidth(75)

        self.step_cbox.setEditable(True)
        self.step_cbox.setValidator(
            QtImport.QDoubleValidator(0, 360, 5, self.step_cbox)
        )
        self.step_cbox.setDuplicatesEnabled(False)
        self.step_cbox.setFixedHeight(27)

        self.close_button.setIcon(Icons.load_icon("Home2"))
        self.close_button.setFixedSize(27, 27)

        self.stop_button.setIcon(Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedSize(27, 27)

        self.connect(HWR.beamline.diffractometer, "kappaMotorMoved", self.kappa_motor_moved)
        self.connect(HWR.beamline.diffractometer, "kappaPhiMotorMoved", self.kappaphi_motor_moved)
        self.connect(HWR.beamline.diffractometer, "minidiffStatusChanged", self.diffractometer_state_changed)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "showStop":
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == "defaultStep":
            if new_value != "":
                self.set_line_step(float(new_value))
                self.step_changed(None)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def stop_clicked(self):
        HWR.beamline.diffractometer.stop_kappa_phi_move()

    def close_clicked(self):
        HWR.beamline.diffractometer.close_kappa()

    def change_position(self):
        HWR.beamline.diffractometer.move_kappa_and_phi(
            self.kappa_dspinbox.value(), self.kappaphi_dspinbox.value()
        )

    def kappa_value_edited(self, text):
        Colors.set_widget_color(
            self.kappa_dspinbox.lineEdit(),
            Colors.LINE_EDIT_CHANGED,
            QtImport.QPalette.Base,
        )

    def kappaphi_value_edited(self, text):
        Colors.set_widget_color(
            self.kappaphi_dspinbox.lineEdit(),
            Colors.LINE_EDIT_CHANGED,
            QtImport.QPalette.Base,
        )

    def kappa_value_accepted(self):
        HWR.beamline.diffractometer.move_kappa_and_phi(
            self.kappa_dspinbox.value(), self.kappaphi_dspinbox.value()
        )

    def kappa_motor_moved(self, value):
        self.kappa_dspinbox.blockSignals(True)
        # txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappa_dspinbox.setValue(value)
        self.kappa_dspinbox.blockSignals(False)

    def kappaphi_motor_moved(self, value):
        self.kappaphi_dspinbox.blockSignals(True)
        # txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappaphi_dspinbox.setValue(value)
        self.kappaphi_dspinbox.blockSignals(False)

    def diffractometer_state_changed(self, state):
        if HWR.beamline.diffractometer.in_plate_mode():
            self.setDisabled(True)
            return

        if state == "Ready":
            self.kappa_dspinbox.setEnabled(True)
            self.kappaphi_dspinbox.setEnabled(True)
            self.close_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            Colors.set_widget_color(
                self.kappa_dspinbox.lineEdit(),
                Colors.LIGHT_GREEN,
                QtImport.QPalette.Base,
            )
            Colors.set_widget_color(
                self.kappaphi_dspinbox.lineEdit(),
                Colors.LIGHT_GREEN,
                QtImport.QPalette.Base,
            )
        else:
            self.kappa_dspinbox.setEnabled(False)
            self.kappaphi_dspinbox.setEnabled(False)
            self.close_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            Colors.set_widget_color(
                self.kappa_dspinbox.lineEdit(),
                Colors.LIGHT_YELLOW,
                QtImport.QPalette.Base,
            )
            Colors.set_widget_color(
                self.kappaphi_dspinbox.lineEdit(),
                Colors.LIGHT_YELLOW,
                QtImport.QPalette.Base,
            )

    def go_to_step(self, step_index):
        step = str(self.step_cbox.currentText())
        if step != "":
            self.set_line_step(step)

    def set_line_step(self, val):
        self.kappa_dspinbox.setSingleStep(float(val))
        self.kappaphi_dspinbox.setSingleStep(float(val))
        found = False
        for i in range(self.step_cbox.count()):
            if float(str(self.step_cbox.itemText(i))) == float(val):
                found = True
                self.step_cbox.setItemIcon(i, self.step_button_icon)
        if not found:
            self.step_cbox.addItem(self.step_button_icon, str(val))
            self.step_cbox.setCurrentIndex(self.step_cbox.count() - 1)

    def step_changed(self, step):
        Colors.set_widget_color(
            self.step_cbox.lineEdit(), QtImport.Qt.white, QtImport.QPalette.Base
        )

    def step_edited(self, step):
        """Paints step combobox when value is edited
        """
        Colors.set_widget_color(
            self.step_cbox.lineEdit(),
            Colors.LINE_EDIT_CHANGED,
            QtImport.QPalette.Button,
        )


class SpinBoxEvent(QtImport.QObject):

    returnPressedSignal = QtImport.pyqtSignal()
    contextMenuSignal = QtImport.pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() == QtImport.QEvent.KeyPress:
            if event.key() in [QtImport.Qt.Key_Enter, QtImport.Qt.Key_Return]:
                self.returnPressedSignal.emit()

        elif event.type() == QtImport.QEvent.MouseButtonRelease:
            self.returnPressedSignal.emit()
        elif event.type() == QtImport.QEvent.ContextMenu:
            self.contextMenuSignal.emit()
        return False
