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

import gui.utils.sample_changer_helper as sc_helper
from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository.HardwareObjects.abstract.sample_changer import Container
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class VialView(QtImport.QWidget):

    (
        VIAL_UNKNOWN,
        VIAL_NONE,
        VIAL_NOBARCODE,
        VIAL_BARCODE,
        VIAL_AXIS,
        VIAL_ALREADY_LOADED,
        VIAL_NOBARCODE_LOADED,
    ) = (0, 1, 2, 3, 4, 5, 6)

    doubleClickSignal = QtImport.pyqtSignal(int)
    singleClickSignal = QtImport.pyqtSignal(int)

    def __init__(self, vial_index, *args):
        QtImport.QWidget.__init__(self, *args)
        self.vial_index = vial_index
        self.setFixedSize(20, 16)
        self.pixmaps = [
            Icons.load_pixmap("sample_unknown"),
            None,
            Icons.load_pixmap("sample_nobarcode"),
            Icons.load_pixmap("sample_barcode"),
            Icons.load_pixmap("sample_axis"),
            Icons.load_pixmap("sample_already_loaded"),
            Icons.load_pixmap("sample_already_loaded2"),
        ]
        self.vial_state = VialView.VIAL_UNKNOWN
        self.vial_code = ""

    def set_vial(self, vial_state):
        """Sets vial state"""
        self.vial_state = vial_state[0]
        try:
            self.vial_code = vial_state[1]
        except BaseException:
            self.vial_code = ""
        self.setEnabled(self.vial_state != VialView.VIAL_NONE)
        self.setToolTip(self.vial_code)
        self.update()

    def paintEvent(self, event):
        """Paints the widget"""
        if self.vial_state is not None:
            painter = QtImport.QPainter(self)
            painter.setBrush(QtImport.Qt.NoBrush)
            pixmap = self.pixmaps[self.vial_state]
            if pixmap is not None:
                painter.drawPixmap(2, 0, pixmap)

    def get_vial(self):
        """Returns vial state"""
        return self.vial_state

    def get_code(self):
        """Returns vial code"""
        return self.vial_code

    def set_selected(self, state):
        if state is True:
            Colors.set_widget_color(self, Colors.LIGHT_GREEN)
        else:
            self.setStyleSheet("background-color: rgba(255,255,255,0);")
            # Colors.set_widget_color(self, \
            #    Colors.BUTTON_ORIGINAL)

    def mousePressEvent(self, event):
        """Mouse single clicked event"""
        QtImport.QWidget.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Mouse single clicked event"""
        self.singleClickSignal.emit(self.vial_index)
        QtImport.QWidget.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """Mouse double clicked event"""
        self.doubleClickSignal.emit(self.vial_index)


class VialNumberView(QtImport.QLabel):

    doubleClickSignal = QtImport.pyqtSignal(int)
    singleClickSignal = QtImport.pyqtSignal(int)

    def __init__(self, vial_index, parent):
        QtImport.QWidget.__init__(self, str(vial_index), parent)
        self.vial_index = vial_index

    def mousePressEvent(self, event):
        """Mouse single clicked event"""
        QtImport.QWidget.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Mouse single clicked event"""
        self.singleClickSignal.emit(self.vial_index)
        QtImport.QLabel.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """Mouse double click event"""
        self.doubleClickSignal.emit(self.vial_index)

    def set_vial(self, vial_state):
        """Sets vial state"""
        try:
            code = vial_state[1]
        except BaseException:
            code = ""
        self.setEnabled(code and True or False)
        self.setToolTip(code)


class SampleBox(QtImport.QWidget):

    singleClickSignal = QtImport.pyqtSignal(int)

    def __init__(self, *args):
        QtImport.QWidget.__init__(self, *args)
        self.selected = False
        self.basket_index = None
        self.vial_index = None

        self.setMouseTracking(True)
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def set_vial_index(self, basket_index, vial_index):
        self.basket_index = basket_index
        self.vial_index = vial_index

    def set_selected(self, state):
        self.selected = state
        if self.selected:
            Colors.set_widget_color(self, Colors.LIGHT_GREEN)
        else:
            self.setStyleSheet("background-color: rgba(255,255,255,0);")
            # Colors.set_widget_color(self, \
            #    Colors.BUTTON_ORIGINAL)

    def mouseMoveEvent(self, event):
        QtImport.QWidget.mouseMoveEvent(self, event)
        Colors.set_widget_color(self, Colors.LINE_EDIT_CHANGED)

    def mousePressEvent(self, event):
        QtImport.QWidget.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Mouse single clicked event"""
        self.singleClickSignal.emit(self.vial_index)
        QtImport.QWidget.mouseReleaseEvent(self, event)

    def enterEvent(self, event):
        QtImport.QWidget.enterEvent(self, event)
        if not self.selected:
            Colors.set_widget_color(self, Colors.LINE_EDIT_CHANGED)

    def leaveEvent(self, event):
        QtImport.QWidget.leaveEvent(self, event)
        if not self.selected:
            # set transparent color
            self.setStyleSheet("background-color: rgba(255,255,255,0);")


class SamplesView(QtImport.QWidget):

    CURRENT_VIAL_COLOR = QtImport.Qt.gray
    loadSampleSignal = QtImport.pyqtSignal(int, int)
    selectSampleSignal = QtImport.pyqtSignal(int, int)

    def __init__(self, parent, basket_index, no_samples=10, max_per_row=None):

        if max_per_row is None:
            max_per_row = no_samples

        QtImport.QWidget.__init__(self, parent)

        self.basket_index = basket_index
        self.no_samples = no_samples
        self.vials = []
        self.numbers = []
        self.sample_boxes = []
        self.loaded_vial = None
        self.current_location = None
        self.standard_color = None

        _main_hlayout = QtImport.QGridLayout(self)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(2, 20, 2, 2)

        rowno = 0
        colno = 0
        for index in range(self.no_samples):
            sample_box = SampleBox(self)
            label = VialNumberView(index + 1, sample_box)
            label.set_vial([VialView.VIAL_UNKNOWN])
            label.setAlignment(QtImport.Qt.AlignHCenter)
            self.numbers.append(label)

            vial_view = VialView(index + 1, sample_box)
            vial_view.set_vial([VialView.VIAL_UNKNOWN])
            self.vials.append(vial_view)

            sample_box.layout().addWidget(label)
            sample_box.layout().addWidget(vial_view)
            _main_hlayout.addWidget(sample_box, rowno, colno)
            colno += 1
            if colno >= max_per_row:
                rowno += 1
                colno = 0
            self.sample_boxes.append(sample_box)
            sample_box.set_vial_index(basket_index, index)

            label.singleClickSignal.connect(self.user_select_this_sample)
            vial_view.singleClickSignal.connect(self.user_select_this_sample)

            label.doubleClickSignal.connect(self.load_sample)
            vial_view.doubleClickSignal.connect(self.load_sample)

        self.setSizePolicy(
            QtImport.QSizePolicy.MinimumExpanding, QtImport.QSizePolicy.Fixed
        )

    def load_sample(self, vial_index):
        """Loads sample"""
        state = self.vials[vial_index - 1].get_vial()
        if state != VialView.VIAL_AXIS:
            self.loadSampleSignal.emit(self.basket_index, vial_index)

    def user_select_this_sample(self, vial_index):
        state = self.vials[vial_index - 1].get_vial()
        if state != VialView.VIAL_AXIS:
            self.selectSampleSignal.emit(self.basket_index, vial_index)

    def select_sample(self, vial_index):
        s = self.sample_boxes[vial_index - 1]
        s.set_selected(True)

    def reset_selection(self):
        for s in self.sample_boxes:
            s.set_selected(False)

    def clear_matrices(self):
        for vial in self.vials:
            vial.set_vial([VialView.VIAL_UNKNOWN])
        for number in self.numbers:
            number.set_vial([VialView.VIAL_UNKNOWN])

    def set_matrices(self, vial_states):
        index = 0
        for vial in self.vials:
            try:
                state = vial_states[index]
            except IndexError:
                state = [VialView.VIAL_UNKNOWN]
            vial.set_vial(state)
            self.numbers[index].set_vial(state)
            index += 1

    def set_current_vial(self, location=None):
        if self.standard_color is None:
            self.standard_color = self.numbers[0].paletteBackgroundColor()

        if (
            self.current_location is not None
            and self.currentLocation[0] == self.basket_index
        ):

            self.vials[self.current_location[1] - 1].setStyleSheet(
                "background-color: none;"
            )
            self.numbers[self.current_location[1] - 1].setStyleSheet(
                "background-color: none;"
            )
        if location is not None and location[0] == self.basket_index:
            self.vials[self.current_location[1] - 1].setStyleSheet(
                "background-color: #e0e000;"
            )
            self.numbers[self.current_location[1] - 1].setStyleSheet(
                "background-color: #e0e000;"
            )
        self.current_location = location


class BasketView(QtImport.QWidget):

    loadSampleSignal = QtImport.pyqtSignal(int, int)
    selectSampleSignal = QtImport.pyqtSignal(int, int)
    basketPresenceSignal = QtImport.pyqtSignal(int, bool)

    def __init__(
        self,
        parent,
        basket_index,
        vials_per_basket=10,
        max_per_row=None,
        basket_label="Basket",
    ):
        QtImport.QWidget.__init__(self, parent)

        self.basket_index = basket_index
        self.vials_per_basket = vials_per_basket
        self.basket_label = basket_label

        self.contents_widget = QtImport.QGroupBox(
            "%s %s" % (self.basket_label, basket_index + 1), self
        )
        obj_name = "basket_%d" % (basket_index + 1)
        self.contents_widget.setObjectName(obj_name)
        self.contents_widget.setStyleSheet(
            "#%s {border: 1px solid gray;border-radius: 5px;}" % obj_name
        )
        self.contents_widget.setCheckable(True)
        self.samples_view = SamplesView(
            self.contents_widget, basket_index, self.vials_per_basket, max_per_row
        )

        _contents_widget_vlayout = QtImport.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.samples_view)
        _contents_widget_vlayout.setSpacing(1)
        _contents_widget_vlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)
        _main_vlayout.setSpacing(1)
        _main_vlayout.setContentsMargins(1, 1, 1, 1)

        self.contents_widget.setSizePolicy(
            QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Minimum
        )
        self.setSizePolicy(
            QtImport.QSizePolicy.MinimumExpanding, QtImport.QSizePolicy.Fixed
        )

        self.samples_view.loadSampleSignal.connect(self.load_this_sample)
        self.samples_view.selectSampleSignal.connect(self.user_select_this_sample)
        self.contents_widget.toggled.connect(self.toggle_basket_presence)

    def set_title(self, title):
        self.contents_widget.setTitle("Basket %s" % title)

    def clear_matrices(self):
        self.samples_view.clear_matrices()

    def set_matrices(self, vial_states):
        self.samples_view.set_matrices(vial_states)

    def set_current_vial(self, location=None):
        self.samples_view.set_current_vial(location)

    def set_unselectable(self, state):
        self.contents_widget.setCheckable(not state)

    def isChecked(self):
        if self.contents_widget.isCheckable():
            return self.contents_widget.isChecked()
        return None

    def setChecked(self, state):
        if self.contents_widget.isCheckable():
            self.contents_widget.setChecked(state)
            return state
        return None

    def load_this_sample(self, basket_index, vial_index):
        self.loadSampleSignal.emit(basket_index, vial_index)

    def user_select_this_sample(self, basket_index, vial_index):
        self.selectSampleSignal.emit(basket_index, vial_index)

    def select_sample(self, vial_index):
        self.samples_view.select_sample(vial_index)

    def reset_selection(self):
        self.samples_view.reset_selection()

    def setState(self, state):
        self.setEnabled(sc_helper.SC_STATE_GENERAL.get(state, False))

    def toggle_basket_presence(self, on):
        self.basketPresenceSignal.emit(self.basket_index, on)


class CurrentView(QtImport.QWidget):
    def __init__(self, title, parent):
        QtImport.QWidget.__init__(self, parent)

        # self.standard_color=None
        self.standard_color = QtImport.Qt.white
        self.currentSelection = 1
        self.title = title

        self.contents_widget = QtImport.QGroupBox(title, self)
        self.contents_widget_hlayout = QtImport.QHBoxLayout(self.contents_widget)
        self.contents_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.contents_widget_hlayout.setSpacing(0)
        self.contents_widget.setAlignment(QtImport.Qt.AlignLeft)
        self.commands_widget_list = []

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.addWidget(self.contents_widget)

    def selectionTextChanged(self, txt):
        if self.standard_color is None:
            self.standard_color = Colors.WHITE
        if txt == str(self.currentSelection):
            if self.standard_color is not None:
                self.selected_spinbox.editor().setPaletteBackgroundColor(
                    self.standard_color
                )
        #    state = True
        else:
            Colors.set_widget_color(
                self.selected_spinbox.lineEdit(), Colors.LIGHT_YELLOW
            )
        #    state = False

    def selectedChanged(self, val):
        self.currentSelection = val
        if self.standard_color is not None:
            Colors.set_widget_color(
                self.selected_spinbox.lineEdit(), self.standard_color
            )
        self.selectedChangedSignal.emit(val)

    def setMatrixCode(self, code):
        if code is None or code == "":
            self.contents_widget.setTitle(self.title)
        else:
            self.contents_widget.setTitle("%s (%s)" % (self.title, code))

    def setSelected(self, val):
        self.currentSelection = val
        self.selected_spinbox.blockSignals(True)
        self.selected_spinbox.lineEdit().blockSignals(True)
        self.selected_spinbox.setValue(val)
        self.selected_spinbox.lineEdit().blockSignals(False)
        self.selected_spinbox.blockSignals(False)

    def setState(self, state):
        enabled = sc_helper.SC_STATE_GENERAL.get(state, False)
        for widget in self.commands_widget_list:
            widget.setEnabled(enabled)


class CurrentBasketView(CurrentView):
    def __init__(self, parent):
        CurrentView.__init__(self, "Current basket", parent)

        self.position_label = QtImport.QLabel("Position:", self.contents_widget)
        self.selected_spinbox = QtImport.QSpinBox(self.contents_widget)
        # self.selected_spinbox.setWrapping(True)
        # self.selected_spinbox.editor().setAlignment(QWidget.AlignRight)

        self.scan_basket_button = QtImport.QToolButton(self.contents_widget)
        self.scan_basket_button.setText("Scan")

        self.commands_widget_list.append(self.scan_basket_button)
        self.commands_widget_list.append(self.position_label)
        self.commands_widget_list.append(self.selected_spinbox)

        self.contents_widget_hlayout.addWidget(self.position_label)
        self.contents_widget_hlayout.addWidget(self.selected_spinbox)
        self.contents_widget_hlayout.addWidget(self.scan_basket_button)

        self.selected_spinbox.valueChanged.connect(self.selectedChanged)
        self.selected_spinbox.lineEdit().textChanged.connect(self.selectionTextChanged)
        self.scan_basket_button.clicked.connect(self.scanBasket)

    def setIcons(self, scan_one_icon):
        self.scan_basket_button.setIcon(Icons.load_icon(scan_one_icon))

    def scanBasket(self):
        self.scanBasketSignal.emit()


class CurrentSampleView(CurrentView):

    sampleChangerStateSignal = QtImport.pyqtSignal(str)

    def __init__(self, parent):
        CurrentView.__init__(self, "Current sample", parent)

        self.loaded_matrix_code = None
        self.loaded_location = None
        self.load_icon = None
        self.unload_icon = None

        _current_sample_view_widget = QtImport.QWidget(self.contents_widget)
        self.state_label = QtImport.QLabel("unknown", _current_sample_view_widget)
        self.state_label.setAlignment(QtImport.Qt.AlignHCenter)

        self.commands_widget = QtImport.QWidget(_current_sample_view_widget)
        self.position_label = QtImport.QLabel("Position:", self.commands_widget)
        self.selected_spinbox = QtImport.QSpinBox(self.commands_widget)
        self.selected_spinbox.setRange(1, 10)
        self.selected_spinbox.setSingleStep(1)
        self.selected_spinbox.setWrapping(True)
        self.selected_spinbox.lineEdit().setAlignment(QtImport.Qt.AlignRight)

        self.holder_length_label = QtImport.QLabel(
            "Holder length:", self.commands_widget
        )
        self.holder_length_spinbox = QtImport.QSpinBox(self.commands_widget)
        self.holder_length_spinbox.setRange(19, 26)
        self.holder_length_spinbox.setSingleStep(1)
        self.holder_length_spinbox.lineEdit().setAlignment(QtImport.Qt.AlignRight)
        self.holder_length_spinboxUnit = QtImport.QLabel("mm", self.commands_widget)
        self.holder_length_spinbox.setEnabled(False)
        self.holder_length_spinboxUnit.setEnabled(False)
        self.holder_length_label.setEnabled(False)

        self.load_button = QtImport.QToolButton(self.commands_widget)
        self.load_button.setText("Mount sample")
        # self.load_button.setTextPosition(QToolButton.BesideIcon)
        self.load_button.hide()

        _commands_widget_gridlayout = QtImport.QGridLayout(self.commands_widget)
        _commands_widget_gridlayout.addWidget(self.position_label, 0, 0)
        _commands_widget_gridlayout.addWidget(self.selected_spinbox, 0, 1)
        _commands_widget_gridlayout.addWidget(self.holder_length_label, 1, 0)
        _commands_widget_gridlayout.addWidget(self.holder_length_spinbox, 1, 1)
        _commands_widget_gridlayout.addWidget(self.holder_length_spinboxUnit, 1, 2)
        # _commands_widget_gridlayout.addWidget(self.load_button, 2, 0, 2, 2)
        # self.commands_widget.setLayout(_commands_widget_gridlayout)

        _current_sample_view_widget_vlayout = QtImport.QVBoxLayout(
            _current_sample_view_widget
        )
        _current_sample_view_widget_vlayout.addWidget(self.state_label)
        _current_sample_view_widget_vlayout.addWidget(self.commands_widget)
        _current_sample_view_widget_vlayout.setSpacing(0)
        _current_sample_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)
        # _current_sample_view_widget.setLayout(_current_sample_view_widget_vlayout)

        self.contents_widget_hlayout.addWidget(_current_sample_view_widget)

        self.selected_spinbox.valueChanged.connect(self.selectedChanged)
        self.selected_spinbox.lineEdit().textChanged.connect(self.selectionTextChanged)

        self.commands_widget_list.append(self.holder_length_label)
        self.commands_widget_list.append(self.holder_length_spinbox)
        self.commands_widget_list.append(self.holder_length_spinboxUnit)
        self.commands_widget_list.append(self.load_button)
        self.commands_widget_list.append(self.selected_spinbox)
        self.commands_widget_list.append(self.position_label)
        self.commands_widget_list.append(self.state_label)

    def setHolderLength(self, length):
        self.holder_length_spinbox.setValue(length)

    def getHolderLength(self):
        if not self.holder_length_spinbox.isVisible():
            holder_len = None
        else:
            holder_len = self.holder_length_spinbox.value()
        return holder_len

    def hideHolderLength(self, hide):
        if hide:
            self.holder_length_label.hide()
            self.holder_length_spinbox.hide()
            self.holder_length_spinboxUnit.hide()
        else:
            self.holder_length_label.show()
            self.holder_length_spinbox.show()
            self.holder_length_spinboxUnit.show()

    def setLoaded(self, state):

        matrix = self.loaded_matrix_code

        if not matrix:
            if self.loaded_location is not None:
                matrix = "%d:%02d" % (self.loaded_location[0], self.loaded_location[1])
            else:
                matrix = "sample"

        if state is None:
            self.holder_length_label.setEnabled(True)
            self.holder_length_spinbox.setEnabled(True)
            self.holder_length_spinboxUnit.setEnabled(True)
            self.load_button.setText("Mount %s" % matrix)
            self.setStateColor("UNKNOWN")
            self.setStateMsg("Unknown mounting state")
            if self.load_icon is not None:
                self.load_button.setIcon(self.load_icon)
        elif state:
            self.holder_length_label.setEnabled(False)
            self.holder_length_spinbox.setEnabled(False)
            self.holder_length_spinboxUnit.setEnabled(False)
            self.load_button.setText("Unmount %s" % matrix)
            self.setStateColor("LOADED")
            self.setStateMsg("Sample is mounted")
            if self.unload_icon is not None:
                self.load_button.setIcon(self.unload_icon)
        else:
            self.holder_length_label.setEnabled(True)
            self.holder_length_spinbox.setEnabled(True)
            self.holder_length_spinboxUnit.setEnabled(True)
            self.load_button.setText("Mount %s" % matrix)
            self.setStateColor("UNLOADED")
            self.setStateMsg("No mounted sample")
            if self.load_icon is not None:
                self.load_button.setIcon(self.load_icon)

    def setStateMsg(self, msg):
        if msg is None:
            msg = ""
        self.state_label.setText(msg)
        self.sampleChangerStateSignal.emit(msg)

    def setStateColor(self, state):
        color = sc_helper.SC_SAMPLE_COLOR.get(state)
        if color is None:
            color = Colors.LINE_EDIT_ORIGINAL
        else:
            Colors.set_widget_color(self.state_label, color)

    def setIcons(self, load_icon, unload_icon):
        self.load_icon = Icons.load_icon(load_icon)
        self.unload_icon = Icons.load_icon(unload_icon)
        txt = str(self.load_button.text()).split()[0]
        if txt == "Mount":
            self.load_button.setIcon(self.load_icon)
        elif txt == "Unmount":
            self.load_button.setIcon(self.unload_icon)

    def setLoadedMatrixCode(self, code):
        self.loaded_matrix_code = code
        txt = str(self.load_button.text()).split()[0]
        if code is None:
            self.load_button.setText("%s sample" % txt)
        else:
            self.load_button.setText("%s %s" % (txt, code))

    def setLoadedLocation(self, location):
        self.loaded_location = location
        if not self.loaded_matrix_code and location:
            txt = str(self.load_button.text()).split()[0]
            self.load_button.setText("%s %d:%02d" % (txt, location[0], location[1]))

    def set_number_samples(self, number_of_samples):
        self.selected_spinbox.setRange(1, number_of_samples)


class StatusView(QtImport.QWidget):

    statusMsgChangedSignal = QtImport.pyqtSignal(str, QtImport.QColor)
    resetSampleChangerSignal = QtImport.pyqtSignal()

    def __init__(self, parent):
        QtImport.QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.in_expert_mode = False
        self.last_sc_in_use = False

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots --------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.contents_widget = QtImport.QGroupBox("Unknown", self)
        self.box1 = QtImport.QWidget(self.contents_widget)

        self.status_label = QtImport.QLabel("", self.box1)
        self.status_label.setAlignment(QtImport.Qt.AlignCenter)

        # flags=self.status_label.alignment()|QtCore.Qt.WordBreak
        # self.status_label.setAlignment(flags)

        self.reset_button = QtImport.QToolButton(self.box1)
        self.reset_button.setText("Reset")
        self.reset_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.reset_button.setEnabled(False)

        self.sc_can_load_radiobutton = QtImport.QRadioButton(
            "Sample changer can load/unload", self.contents_widget
        )
        self.minidiff_can_move_radiobutton = QtImport.QRadioButton(
            "Minidiff motors can move", self.contents_widget
        )

        # Layout --------------------------------------------------------------
        _box1_hlayout = QtImport.QHBoxLayout(self.box1)
        _box1_hlayout.addWidget(self.status_label)
        _box1_hlayout.addWidget(self.reset_button)
        _box1_hlayout.setSpacing(2)
        _box1_hlayout.setContentsMargins(2, 2, 2, 2)

        _contents_widget_vlayout = QtImport.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.box1)
        _contents_widget_vlayout.addWidget(self.sc_can_load_radiobutton)
        _contents_widget_vlayout.addWidget(self.minidiff_can_move_radiobutton)
        _contents_widget_vlayout.setSpacing(2)
        _contents_widget_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.reset_button.clicked.connect(self.reset_sample_changer)
        self.sc_can_load_radiobutton.clicked.connect(self.sampleChangerMoveToLoadingPos)
        self.minidiff_can_move_radiobutton.clicked.connect(self.minidiffGetControl)

    def setIcons(self, reset_icon):
        self.reset_button.setIcon(Icons.load_icon(reset_icon))

    def setStatusMsg(self, status):
        self.status_label.setToolTip(status)
        status = status.strip()
        self.status_label.setText(status)
        self.statusMsgChangedSignal.emit(status, Colors.LINE_EDIT_ORIGINAL)

    def setState(self, state):
        color = sc_helper.SC_STATE_COLOR.get(state, None)
        if color is None:
            color = Colors.LINE_EDIT_ORIGINAL
        else:
            Colors.set_widget_color(self.status_label, color)

        state_str = sc_helper.SampleChangerState.tostring(state)
        self.contents_widget.setTitle(state_str)

        enabled = sc_helper.SC_STATE_GENERAL.get(state, False)
        self.status_label.setEnabled(enabled)
        if state in (
            sc_helper.SampleChangerState.Fault,
            sc_helper.SampleChangerState.Alarm,
        ):
            self.reset_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(enabled and self.in_expert_mode)
        self.sc_can_load_radiobutton.setEnabled(enabled)
        self.minidiff_can_move_radiobutton.setEnabled(enabled)

    def set_expert_mode(self, state):
        self.in_expert_mode = state
        self.reset_button.setEnabled(state)
        self.minidiff_can_move_radiobutton.setEnabled(state)
        if state:
            self.sc_can_load_radiobutton.setEnabled(self.last_sc_in_use)
        else:
            self.sc_can_load_radiobutton.setEnabled(False)

    def hideOperationalControl(self, is_microdiff):
        if is_microdiff:
            self.sc_can_load_radiobutton.hide()
            self.minidiff_can_move_radiobutton.hide()
        else:
            self.sc_can_load_radiobutton.show()
            self.minidiff_can_move_radiobutton.show()

    def setSampleChangerUseStatus(self, in_use):
        self.last_sc_in_use = in_use
        self.sc_can_load_radiobutton.setEnabled(in_use and self.in_expert_mode)

    def setSampleChangerLoadStatus(self, can_load):
        self.setSampleChangerUseStatus(self.last_sc_in_use)
        self.sc_can_load_radiobutton.setChecked(can_load)

    def setMinidiffStatus(self, can_move):
        self.minidiff_can_move_radiobutton.setEnabled(self.in_expert_mode)
        self.minidiff_can_move_radiobutton.setChecked(can_move)

    def reset_sample_changer(self):
        self.resetSampleChangerSignal.emit()

    def sampleChangerMoveToLoadingPos(self):
        if not self.sc_can_load_radiobutton.isChecked():
            self.sc_can_load_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.sampleChangerToLoadingPositionSignal.emit()

    def minidiffGetControl(self):
        if not self.minidiff_can_move_radiobutton.isChecked():
            self.minidiff_can_move_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.minidiffGetControlSignal.emit()


class SCCheckBox(QtImport.QCheckBox):
    def setMyState(self, state):
        try:
            enabled = sc_helper.SC_STATE_GENERAL[str(state)]
        except BaseException:
            enabled = False
        self.setEnabled(enabled)


class ScanBasketsView(QtImport.QWidget):
    def __init__(self, parent):
        QtImport.QWidget.__init__(self, parent)

        self.scan_all_icon = None
        self.standard_color = None
        self.commands_widget_list = []

        self.scan_all_baskets_button = QtImport.QToolButton(self)
        self.scan_all_baskets_button.setText("Scan selected baskets")
        # self.scan_all_baskets_button.setUsesTextLabel(True)
        # self.scan_all_baskets_button.setTextPosition(QToolButton.BesideIcon)

        self.buttonSelect = QtImport.QToolButton(self)
        self.buttonSelect.setText("Select")
        # self.buttonSelect.setUsesTextLabel(True)
        # self.buttonSelect.setTextPosition(QToolButton.BesideIcon)
        self.buttonSelect.setEnabled(False)
        self.buttonSelect.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )

        self.commands_widget_list.append(self.scan_all_baskets_button)
        self.commands_widget_list.append(self.buttonSelect)

        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(self.scan_all_baskets_button)
        _main_hlayout.addWidget(self.buttonSelect)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        self.scan_all_baskets_button.clicked.connect(self.scanAllBaskets)
        self.buttonSelect.clicked.connect(self.select_baskets_samples)

    def setIcons(self, scan_all_icon, scan_select):
        self.scan_all_icon = Icons.load(scan_all_icon)
        self.scan_all_baskets_button.setIcon(self.scan_all_icon)
        self.buttonSelect.setIcon(Icons.load(scan_select))

    def scanAllBaskets(self):
        # self.scanAllBasketsSignal.emit()
        pass

    def select_baskets_samples(self):
        self.selectBasketsSamplesSignal.emit()

    def setState(self, state):
        enabled = sc_helper.SC_STATE_GENERAL.get(state, False)
        for widget in self.commands_widget_list:
            widget.setEnabled(enabled)

    def showSelectButton(self, show):
        if show:
            self.buttonSelect.show()
        else:
            self.buttonSelect.hide()


class SampleChangerBrick(BaseWidget):

    sampleGotLoadedSignal = QtImport.pyqtSignal()
    default_basket_label = "Basket"

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.add_property("mnemonic", "string", "")
        self.add_property("basketCount", "string", "5")
        self.add_property("basketLabel", "string", "Basket")
        self.add_property("defaultHolderLength", "integer", 22)
        self.add_property("icons", "string", "")
        self.add_property("showSelectButton", "boolean", False)
        self.add_property("doubleClickLoads", "boolean", True)
        self.add_property("singleClickSelection", "boolean", False)

        self.define_signal("scanBasketUpdate", ())
        self.define_signal("sampleGotLoaded", ())

        # Emitted when the status of the hwobj changes,
        # original intended receiver is TreeBrick.
        self.define_signal("status_msg_changed", ())
        self.define_slot("setSession", ())
        self.define_slot("setCollecting", ())

        self.in_expert_mode = None
        self.basket_count = ""
        self.basket_label = None
        self.basket_per_column_default = 9
        self.baskets = []
        self.last_basket_checked = ()

        self.vials_per_basket = (
            10
        )  # default is 10. it can be changed with basketCount property

        self.single_click_selection = False
        self.user_selected_sample = (None, None)

        self.contents_widget = QtImport.QWidget(self)
        self.status = self.build_status_view(self.contents_widget)
        self.switch_to_sample_transfer_button = QtImport.QPushButton(
            "Switch to Sample Transfer mode", self.contents_widget
        )
        self.test_sample_changer_button = QtImport.QPushButton(
            "Test sample changer", self.contents_widget
        )
        self.current_basket_view = CurrentBasketView(self.contents_widget)
        self.current_sample_view = CurrentSampleView(self.contents_widget)

        self.sc_contents_gbox = QtImport.QGroupBox("Contents", self)
        self.sc_contents_gbox.setAlignment(QtImport.Qt.AlignHCenter)
        self.reset_baskets_samples_button = QtImport.QPushButton(
            "Reset sample changer contents", self.sc_contents_gbox
        )

        self.double_click_loads_cbox = SCCheckBox(
            "Double-click loads the sample", self.sc_contents_gbox
        )
        self.double_click_loads_cbox.setEnabled(False)
        self.scan_baskets_view = ScanBasketsView(self.sc_contents_gbox)

        # operations widget builds simple action buttons
        #   overwrite 'build_operations_widget()' method in derived class
        #   to put content.  Otherwise empty and hidden by default
        #   See SampleChangerSimple.py (derived from this class)
        self.operations_widget = QtImport.QWidget(self)
        self.build_operations_widget()

        self.baskets_grid_layout = QtImport.QGridLayout()
        self.baskets_grid_layout.setSpacing(4)
        self.baskets_grid_layout.setContentsMargins(2, 2, 2, 2)

        self.current_sample_view.setStateMsg("Unknown smart magnet state")
        self.current_sample_view.setStateColor("UNKNOWN")
        self.status.setStatusMsg("Unknown sample changer status")
        self.status.setState("UNKNOWN")

        # self.basketsSamplesSelectionDialog = BasketsSamplesSelection(self)

        self.sc_contents_gbox_vlayout = QtImport.QVBoxLayout(self.sc_contents_gbox)
        self.sc_contents_gbox_vlayout.addWidget(self.reset_baskets_samples_button)
        self.sc_contents_gbox_vlayout.addWidget(self.double_click_loads_cbox)
        self.sc_contents_gbox_vlayout.addWidget(self.scan_baskets_view)
        self.sc_contents_gbox_vlayout.addWidget(self.operations_widget)
        self.operations_widget.hide()
        self.sc_contents_gbox_vlayout.addLayout(self.baskets_grid_layout)
        self.sc_contents_gbox_vlayout.setSpacing(0)
        self.sc_contents_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _contents_widget_vlayout = QtImport.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.status)
        _contents_widget_vlayout.addWidget(self.switch_to_sample_transfer_button)
        _contents_widget_vlayout.addWidget(self.test_sample_changer_button)
        _contents_widget_vlayout.addWidget(self.current_basket_view)
        _contents_widget_vlayout.addWidget(self.current_sample_view)
        _contents_widget_vlayout.addWidget(self.sc_contents_gbox)
        _contents_widget_vlayout.setSpacing(0)
        _contents_widget_vlayout.addStretch(0)
        _contents_widget_vlayout.setContentsMargins(0, 0, 0, 0)
        self.contents_widget.setLayout(_contents_widget_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.test_sample_changer_button.clicked.connect(self.test_sample_changer)
        self.reset_baskets_samples_button.clicked.connect(self.resetBasketsSamplesInfo)
        # self.status.resetSampleChangerSignal.connect(self.resetSampleChanger)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "icons":
            icons_list = new_value.split()

            try:
                self.status.setIcons(icons_list[0])
            except IndexError:
                pass

            try:
                self.current_basket_view.setIcons(icons_list[1])
            except IndexError:
                pass

            try:
                self.scan_baskets_view.setIcons(icons_list[2], icons_list[3])
            except IndexError:
                pass

            try:
                self.current_sample_view.setIcons(icons_list[5], icons_list[6])
            except IndexError:
                pass

        elif property_name == "basketLabel":
            self.basket_label = new_value
            if self.basket_count is not None and self.basket_label is not None:
                self.build_basket_view()

        elif property_name == "basketCount":
            self.basket_count = new_value

            if self.basket_count is not None and self.basket_label is not None:
                self.build_basket_view()

        elif property_name == "mnemonic":
             if HWR.beamline.sample_changer is not None:
                self.connect(
                    HWR.beamline.sample_changer,
                    sc_helper.SampleChanger.STATUS_CHANGED_EVENT,
                    self.sc_status_changed,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    sc_helper.SampleChanger.STATE_CHANGED_EVENT,
                    self.sc_state_changed,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    sc_helper.SampleChanger.INFO_CHANGED_EVENT,
                    self.infoChanged,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    sc_helper.SampleChanger.SELECTION_CHANGED_EVENT,
                    self.selectionChanged,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    sc_helper.SampleChanger.LOADED_SAMPLE_CHANGED_EVENT,
                    self.loadedSampleChanged,
                )
                self.sc_status_changed(HWR.beamline.sample_changer.getStatus())
                self.sc_state_changed(HWR.beamline.sample_changer.get_state())
                self.infoChanged()
                self.selectionChanged()
                self.loadedSampleChanged(HWR.beamline.sample_changer.getLoadedSample())
        elif property_name == "showSelectButton":
            self.scan_baskets_view.showSelectButton(new_value)
            for basket in self.baskets:
                basket.set_unselectable(new_value)
        elif property_name == "defaultHolderLength":
            self.current_sample_view.setHolderLength(new_value)
        elif property_name == "doubleClickLoads":
            self.double_click_loads_cbox.setChecked(new_value)
        elif property_name == "singleClickSelection":
            self.single_click_selection = new_value
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def build_basket_view(self):
        parts = self.basket_count.split(":")
        self.basket_count = int(parts[0])
        self.basket_per_column = self.basket_per_column_default

        if len(parts) > 1:
            self.basket_per_column = int(parts[1])

        if len(parts) > 2:
            self.vials_per_basket = int(parts[2])

        if len(parts) > 3:
            self.vials_per_row = int(parts[3])
        else:
            self.vials_per_row = None

        self.current_sample_view.set_number_samples(self.vials_per_basket)

        for basket_index in range(self.basket_count):
            temp_basket = BasketView(
                self.sc_contents_gbox,
                basket_index + 1,
                self.vials_per_basket,
                self.vials_per_row,
                self.basket_label,
            )
            temp_basket.loadSampleSignal.connect(self.load_this_sample)
            temp_basket.selectSampleSignal.connect(self.user_select_this_sample)
            temp_basket.setChecked(False)
            temp_basket.setEnabled(False)
            self.baskets.append(temp_basket)
            basket_row = basket_index % self.basket_per_column
            basket_column = int(basket_index / self.basket_per_column)
            self.baskets_grid_layout.addWidget(temp_basket, basket_row, basket_column)

    def build_status_view(self, container):
        return StatusView(container)

    def build_operations_widget(self):
        pass

    def status_msg_changed(self, msg, color):
        self.statusMsgChangedSignal.emit(msg, color)

    def selectionChanged(self):
        sample = HWR.beamline.sample_changer.getSelectedSample()
        basket = HWR.beamline.sample_changer.getSelectedComponent()
        if sample is None:
            self.current_sample_view.setSelected(0)
        else:
            self.current_sample_view.setSelected(sample.getIndex() + 1)
        if basket is None:
            self.current_basket_view.setSelected(0)
        else:
            self.current_basket_view.setSelected(basket.getIndex() + 1)

    def instanceModeChanged(self, mode):
        if mode == BaseWidget.INSTANCE_MODE_SLAVE:
            self.basketsSamplesSelectionDialog.reject()

    def basketTransferModeChanged(self, basket_transfer):
        self.switch_to_sample_transfer_button.setEnabled(basket_transfer)

    def switchToSampleTransferMode(self):
        HWR.beamline.sample_changer.changeMode(
            sc_helper.SampleChangerMode.Normal, wait=False
        )

    def loadedSampleChanged(self, sample):
        if sample is None:
            # get current location in SC
            sample = HWR.beamline.sample_changer.getSelectedSample()
            loaded = False
        else:
            loaded = True

        if sample is None:
            # basket transfer mode?
            barcode = ""
            location = (-1, -1)
        else:
            barcode = sample.getID()
            location = sample.getCoords()

        self.current_sample_view.setLoadedMatrixCode(barcode)
        self.current_sample_view.setLoadedLocation(location)
        self.current_sample_view.setLoaded(loaded)

        self.infoChanged()

        if loaded:
            self.sampleGotLoadedSignal.emit()

    def setCollecting(self, enabled_state):
        self.setEnabled(enabled_state)

    def reset_sample_changer(self):
        return self.resetSampleChanger()

    def resetSampleChanger(self):
        HWR.beamline.sample_changer.reset()

    def resetBasketsSamplesInfo(self):
        HWR.beamline.sample_changer.clearInfo()

    def set_expert_mode(self, state):
        self.in_expert_mode = state
        if HWR.beamline.sample_changer is not None:
            self.status.set_expert_mode(state)

    def run(self):
        if self.in_expert_mode is not None:
            self.set_expert_mode(self.in_expert_mode)
        try:
            self.matrixCodesChanged(HWR.beamline.sample_changer.getMatrixCodes())
        except BaseException:
            pass

    def sampleLoadSuccess(self):
        pass

    def sampleLoadFail(self):
        pass

    def sampleUnloadSuccess(self):
        pass

    def sampleUnloadFail(self, state):
        self.sample_changer_hwobjStateChanged(state)

    def sc_status_changed(self, status):
        self.status.setStatusMsg(status)

    def sc_state_changed(self, state, previous_state=None):
        self.status.setState(state)
        self.current_basket_view.setState(state)
        self.current_sample_view.setState(state)
        for basket in self.baskets:
            basket.setState(state)
        # self.double_click_loads_cbox.setMyState(state)
        self.scan_baskets_view.setState(state)
        self.reset_baskets_samples_button.setEnabled(
            sc_helper.SC_STATE_GENERAL.get(state, False)
        )

    def sampleChangerCanLoad(self, can_load):
        self.status.setSampleChangerLoadStatus(can_load)

    def sampleChangerInUse(self, in_use):
        self.status.setSampleChangerUseStatus(in_use)

    def minidiffCanMove(self, can_move):
        self.status.setMinidiffStatus(can_move)

    def sampleChangerToLoadingPosition(self):
        if not HWR.beamline.sample_changer.sampleChangerToLoadingPosition():
            self.status.setSampleChangerLoadStatus(
                HWR.beamline.sample_changer.sampleChangerCanLoad()
            )

    def minidiffGetControl(self):
        if not HWR.beamline.sample_changer.minidiffGetControl():
            self.status.setMinidiffStatus(HWR.beamline.sample_changer.minidiffCanMove())

    def changeBasket(self, basket_number):
        address = Container.Basket.getBasketAddress(basket_number)
        HWR.beamline.sample_changer.select(address, wait=False)

    def changeSample(self, sample_number):
        basket_index = HWR.beamline.sample_changer.getSelectedComponent().getIndex()
        basket_number = basket_index + 1
        address = Container.Pin.getSampleAddress(basket_number, sample_number)
        HWR.beamline.sample_changer.select(address, wait=False)

    def user_select_this_sample(self, basket_index, vial_index):
        if self.single_click_selection:
            self.user_selected_sample = (basket_index, vial_index)
            self.reset_selection()
            self.select_sample(basket_index, vial_index)

    def reset_selection(self):
        for basket in self.baskets:
            basket.reset_selection()

    def select_sample(self, basket_no, sample_no):
        basket = self.baskets[basket_no]
        basket.select_sample(sample_no)

    def load_this_sample(self, basket_index, vial_index):
        if self.double_click_loads_cbox.isChecked():
            # holder_len = self.current_sample_view.getHolderLength()
            HWR.beamline.sample_changer.load((basket_index, vial_index), wait=False)

    def loadSample(self, holder_len):
        HWR.beamline.sample_changer.load(
            holder_len,
            None,
            None,
            self.sampleLoadSuccess,
            self.sampleLoadFail,
            wait=False,
        )

    def unloadSample(self, holder_len, matrix_code, location):
        if matrix_code:
            location = None
        HWR.beamline.sample_changer.unload(
            holder_len,
            matrix_code,
            location,
            self.sampleUnloadSuccess,
            self.sampleUnloadFail,
            wait=False,
        )

    def clear_matrices(self):
        for basket in self.baskets:
            basket.clear_matrices()
        self.scanBasketUpdateSignal.emit()

    def sampleChangerContentsChanged(self, baskets):
        self.clear_matrices()

        index = 0
        for basket in baskets:
            self.baskets[index].blockSignals(True)
            self.baskets[index].setChecked(basket is not None)
            self.baskets[index].blockSignals(False)
            index = index + 1

    def scanBasket(self):
        if not self["showSelectButton"]:
            self.baskets[self.current_basket_view.selected.value() - 1].setChecked(True)
        HWR.beamline.sample_changer.scan(
            HWR.beamline.sample_changer.getSelectedComponent(),
            recursive=True,
            wait=False
        )

    def scanAllBaskets(self):
        baskets_to_scan = []
        for index, basket_checkbox in enumerate(self.baskets):
            baskets_to_scan.append(
                Container.Basket.getBasketAddress(index + 1)
                if basket_checkbox.isChecked()
                else None
            )
        HWR.beamline.sample_changer.scan(
            filter(None, baskets_to_scan), recursive=True, wait=False
        )

    def infoChanged(self):
        baskets_at_sc = HWR.beamline.sample_changer.getComponents()
        presences = []

        for basket in baskets_at_sc:
            presences.append(
                [[VialView.VIAL_UNKNOWN]] * self.vials_per_basket
                if basket.isPresent()
                else [[VialView.VIAL_NONE]] * self.vials_per_basket
            )

        for sample in HWR.beamline.sample_changer.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            vial_index = sample.getIndex()
            basket_code = sample.getContainer().getID()
            if sample.isPresent():
                if matrix:
                    if sample.hasBeenLoaded():
                        presences[basket_index][vial_index] = [
                            VialView.VIAL_ALREADY_LOADED,
                            matrix,
                        ]
                    else:
                        presences[basket_index][vial_index] = [
                            VialView.VIAL_BARCODE,
                            matrix,
                        ]
                else:
                    if sample.hasBeenLoaded():
                        presences[basket_index][vial_index] = [
                            VialView.VIAL_NOBARCODE_LOADED,
                            matrix,
                        ]
                    else:
                        presences[basket_index][vial_index] = [
                            VialView.VIAL_NOBARCODE,
                            matrix,
                        ]
            else:
                presences[basket_index][vial_index] = [VialView.VIAL_NONE, ""]

            if sample.isLoaded():
                presences[basket_index][vial_index] = [VialView.VIAL_AXIS, matrix]

        for basket_index in range(self.basket_count):
            presence = presences[basket_index]
            self.baskets[basket_index].set_matrices(presence)

    def select_baskets_samples(self):
        retval = self.basketsSamplesSelectionDialog.exec_loop()

        if retval == QtImport.QDialog.Accepted:
            HWR.beamline.sample_changer.resetBasketsInformation()

            for (basket, samples) in self.basketsSamplesSelectionDialog.result.items():
                for index in range(self.vials_per_basket):
                    basket_input = [basket, index + 1, 0, 0, 0]
                for sample in samples:
                    basket_input[1] = sample
                    basket_input[2] = 1
                    HWR.beamline.sample_changer.setBasketSampleInformation(basket_input)

    def test_sample_changer(self):
        HWR.beamline.sample_changer.run_test()
