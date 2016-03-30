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

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework import Qt4_Icons
from sample_changer import SC3
from Qt4_sample_changer_helper import *


__category__ = "Sample changer"


class VialView(QtGui.QWidget):

    (VIAL_UNKNOWN, VIAL_NONE, VIAL_NOBARCODE, VIAL_BARCODE, VIAL_AXIS,
     VIAL_ALREADY_LOADED,VIAL_NOBARCODE_LOADED) = (0, 1, 2, 3, 4, 5, 6)

    def __init__(self,vial_index, *args):
        QtGui.QWidget.__init__(self, *args)
        self.vialIndex = vial_index
        self.setFixedSize(20, 16)
        self.pixmapUnknown = Qt4_Icons.load_pixmap("sample_unknown")
        self.pixmapNoBarcode = Qt4_Icons.load_pixmap("sample_nobarcode.png")
        self.pixmapBarcode = Qt4_Icons.load_pixmap("sample_barcode.png")
        self.pixmapAxis = Qt4_Icons.load_pixmap("sample_axis.png")
        self.pixmapAlreadyLoaded = Qt4_Icons.load_pixmap("sample_already_loaded.png")
        self.pixmapAlreadyLoadedNoBarcode = Qt4_Icons.load_pixmap("sample_already_loaded2.png")
        self.pixmaps = [self.pixmapUnknown, None, self.pixmapNoBarcode, 
                        self.pixmapBarcode, self.pixmapAxis, 
                        self.pixmapAlreadyLoaded, 
                        self.pixmapAlreadyLoadedNoBarcode]
        self.vialState = VialView.VIAL_UNKNOWN
        self.vialCode = ""
    def setVial(self,vial_state):
        self.vialState = vial_state[0]
        try:
            self.vialCode = vial_state[1]
        except:
            self.vialCode = ""
        self.setEnabled(self.vialState != VialView.VIAL_NONE)
        self.setToolTip(self.vialCode)
        self.update()

    def paintEvent(self,event):
        if self.vialState is not None:
            painter = QtGui.QPainter(self)
            painter.setBrush(QtCore.Qt.NoBrush)
            px = self.pixmaps[self.vialState]
            if px is not None:
                painter.drawPixmap(2, 0, px)

    def getVial(self):
        return self.vialState

    def getCode(self):
        return self.vialCode

    def mouseDoubleClickEvent(self,e):
        self.emit(QtCore.SIGNAL("doubleClicked"), self.vialIndex)

class VialNumberView(QtGui.QLabel):

    def __init__(self,vial_index,parent):
        QtGui.QWidget.__init__(self, str(vial_index), parent)
        self.vialIndex = vial_index

    def mouseDoubleClickEvent(self, event):
        self.emit(QtCore.SIGNAL("doubleClicked"), self.vialIndex)

    def setVial(self, vial_state):
        state = vial_state[0]
        try:
            code = vial_state[1]
        except:
            code = ""
        self.setToolTip(code)


class SampleBox(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setMouseTracking(True)
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def mouseMoveEvent(self, event):
        QtGui.QWidget.mouseMoveEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.LINE_EDIT_CHANGED)

    def enterEvent(self, event):
        QtGui.QWidget.enterEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.LINE_EDIT_CHANGED)

    def leaveEvent(self, event):
        QtGui.QWidget.leaveEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.BUTTON_ORIGINAL)

class SamplesView(QtGui.QWidget):
    SAMPLE_COUNT = 10
    CURRENT_VIAL_COLOR = QtCore.Qt.gray

    def __init__(self, parent, basket_index):
        QtGui.QWidget.__init__(self, parent)

        self.basket_index = basket_index
        self.vials = []
        self.numbers = []
        self.loaded_vial = None
        self.current_location = None
        self.standard_color = None

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        for i in range(SamplesView.SAMPLE_COUNT):
            sample_box = SampleBox(self)
            label = VialNumberView(i + 1, sample_box)
            label.setVial([VialView.VIAL_UNKNOWN])
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.numbers.append(label)

            w = VialView(i + 1, sample_box)
            w.setVial([VialView.VIAL_UNKNOWN])
            self.vials.append(w)

            sample_box.layout().addWidget(label)
            sample_box.layout().addWidget(w)
            _main_hlayout.addWidget(sample_box)

            QtCore.QObject.connect(label, QtCore.SIGNAL("doubleClicked"),self.loadSample) 
            QtCore.QObject.connect(w, QtCore.SIGNAL("doubleClicked"),self.loadSample)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)

    def loadSample(self, vial_index):
        state = self.vials[vial_index - 1].getVial()
        if state != VialView.VIAL_AXIS:
            self.emit(QtCore.SIGNAL("load_this_sample"), self.basket_index, vial_index)

    def clearMatrices(self):
        for v in self.vials:
            v.setVial([VialView.VIAL_UNKNOWN])
        for n in self.numbers:
            n.setVial([VialView.VIAL_UNKNOWN])

    def setMatrices(self, vial_states):
        i=0
        for v in self.vials:
            try:
                state = vial_states[i]
            except IndexError:
                state = [VialView.VIAL_UNKNOWN]
            v.setVial(state)
            self.numbers[i].setVial(state)
            i += 1

    def setCurrentVial(self, location = None):
        if self.standard_color is None:
            self.standard_color = self.numbers[0].paletteBackgroundColor()
        if self.current_location is not None and self.currentLocation[0] == self.basket_index:
            self.vials[self.current_location[1]-1].setPaletteBackgroundColor(self.standard_color)
            self.numbers[self.current_location[1]-1].setPaletteBackgroundColor(self.standard_color)
        if location is not None and location[0] == self.basket_index:
            self.vials[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
            self.numbers[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
        self.current_location = location

class BasketView(QtGui.QWidget):
    def __init__(self, parent, basket_index):
        QtGui.QWidget.__init__(self, parent)

        self.basket_index = basket_index

        #self.contents_widget = QVGroupBox("Basket %s" % basket_index,self)
        self.contents_widget = QtGui.QGroupBox("Basket %s" % basket_index, self)
        self.contents_widget.setCheckable(True)
        self.samplesView = SamplesView(self.contents_widget, basket_index)

        _contents_widget_vlayout = QtGui.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.samplesView)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)

        self.contents_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                           QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)    

        QtCore.QObject.connect(self.samplesView, QtCore.SIGNAL("loadThisSample"),self.load_this_sample)
        self.contents_widget.toggled.connect(self.toggleBasketPresence)


    def clearMatrices(self):
        self.samplesView.clearMatrices()

    def setMatrices(self,vial_states):
        self.samplesView.setMatrices(vial_states)

    """
    def setLoadedVial(self,vial_index=None):
        self.samplesView.setLoadedVial(vial_index)
    """

    def setCurrentVial(self, location=None):
        return
        self.samplesView.setCurrentVial(location)

    def setUnselectable(self, state):
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
        self.emit(QtCore.SIGNAL("load_this_sample"), basket_index, vial_index)

    def setState(self, state):
        self.setEnabled(SC_STATE_GENERAL.get(state, False))

    def toggleBasketPresence(self, on):
        self.emit(QtCore.SIGNAL("basketPresence"), self.basket_index, on)


class CurrentView(QtGui.QWidget):
    def __init__(self, title, parent):
        QtGui.QWidget.__init__(self, parent)

        #self.standard_color=None
        self.standard_color = QtCore.Qt.white
        self.currentSelection=1
        self.title = title

        self.contents_widget = QtGui.QGroupBox(title, self)
        self.contents_widget_hlayout = QtGui.QHBoxLayout(self.contents_widget) 
        self.contents_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.contents_widget_hlayout.setSpacing(0)
        self.contents_widget.setAlignment(QtCore.Qt.AlignHCenter)
        self.commandsWidget=[]

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.addWidget(self.contents_widget)

    def selectionTextChanged(self, txt):
        if self.standard_color is None:
            self.standard_color = Qt4_widget_colors.WHITE
        if txt == str(self.currentSelection):
            if self.standard_color is not None:
                self.selected_spinbox.editor().setPaletteBackgroundColor(self.standard_color)
        #    state = True
        else:
            Qt4_widget_colors.set_widget_color(self.selected_spinbox.lineEdit(),
                                               Qt4_widget_colors.LIGHT_YELLOW)
        #    state = False

    def selectedChanged(self, val):
        self.currentSelection = val
        if self.standard_color is not None:
            Qt4_widget_colors.set_widget_color(self.selected_spinbox.lineEdit(), 
                                               self.standard_color)
        self.emit(QtCore.SIGNAL("selectedChanged"), val)

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

    def setState(self,state):
        enabled=SC_STATE_GENERAL.get(state, False)
        for wid in self.commandsWidget:
            wid.setEnabled(enabled)

class CurrentBasketView(CurrentView):
    def __init__(self, parent):
        CurrentView.__init__(self, "Current basket", parent)

        self.position_label = QtGui.QLabel("Position:", self.contents_widget)
        self.selected_spinbox = QtGui.QSpinBox(self.contents_widget)
        #self.selected_spinbox.setWrapping(True)
        #self.selected_spinbox.editor().setAlignment(QWidget.AlignRight)

        self.scan_basket_button = QtGui.QToolButton(self.contents_widget)
        self.scan_basket_button.setText("Scan")

        self.commandsWidget.append(self.scan_basket_button)
        self.commandsWidget.append(self.position_label)
        self.commandsWidget.append(self.selected_spinbox)

        self.contents_widget_hlayout.addWidget(self.position_label)
        self.contents_widget_hlayout.addWidget(self.selected_spinbox)
        self.contents_widget_hlayout.addWidget(self.scan_basket_button)

        self.selected_spinbox.valueChanged.connect(self.selectedChanged)
        self.selected_spinbox.lineEdit().textChanged.connect(self.selectionTextChanged)
        self.scan_basket_button.clicked.connect(self.scanBasket)

    def setIcons(self,scan_one_icon):
        self.scan_basket_button.setIcon(Qt4_Icons.load(scan_one_icon))

    def scanBasket(self):
        self.emit(QtCore.SIGNAL("scanBasket"))

class CurrentSampleView(CurrentView):
    def __init__(self,parent):
        CurrentView.__init__(self, "Current sample", parent)

        self.loaded_matrix_code = None
        self.loaded_location = None
        self.load_icon = None
        self.unload_icon = None

        _current_sample_view_widget = QtGui.QWidget(self.contents_widget)

        self.state_label = QtGui.QLabel("unknown", _current_sample_view_widget)
        self.state_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.commands_widget = QtGui.QWidget(_current_sample_view_widget)
        self.position_label = QtGui.QLabel("Position:",self.commands_widget)
        self.selected_spinbox = QtGui.QSpinBox(self.commands_widget)
        self.selected_spinbox.setRange(1, 10)
        self.selected_spinbox.setSingleStep(1)
        self.selected_spinbox.setWrapping(True)
        self.selected_spinbox.lineEdit().setAlignment(QtCore.Qt.AlignRight)

        self.holderLengthLabel = QtGui.QLabel("Holder length:", self.commands_widget)
        self.holderLength = QtGui.QSpinBox(self.commands_widget)
        self.holderLength.setRange(19, 26)
        self.holderLength.setSingleStep(1)
        self.holderLength.lineEdit().setAlignment(QtCore.Qt.AlignRight)
        self.holderLengthUnit = QtGui.QLabel("mm", self.commands_widget)
        self.holderLength.setEnabled(False)
        self.holderLengthUnit.setEnabled(False)
        self.holderLengthLabel.setEnabled(False)

        self.buttonLoad = QtGui.QToolButton(self.commands_widget)
        self.buttonLoad.setText("Mount sample")
        #self.buttonLoad.setTextPosition(QToolButton.BesideIcon)
        self.buttonLoad.hide()

        _commands_widget_gridlayout = QtGui.QGridLayout(self.commands_widget)
        _commands_widget_gridlayout.addWidget(self.position_label, 0, 0)
        _commands_widget_gridlayout.addWidget(self.selected_spinbox, 0, 1)
        _commands_widget_gridlayout.addWidget(self.holderLengthLabel, 1, 0)
        _commands_widget_gridlayout.addWidget(self.holderLength,1, 1)
        _commands_widget_gridlayout.addWidget(self.holderLengthUnit, 1, 2)
        #_commands_widget_gridlayout.addWidget(self.buttonLoad, 2, 0, 2, 2)
        #self.commands_widget.setLayout(_commands_widget_gridlayout)

        _current_sample_view_widget_vlayout = QtGui.QVBoxLayout(_current_sample_view_widget)
        _current_sample_view_widget_vlayout.addWidget(self.state_label)
        _current_sample_view_widget_vlayout.addWidget(self.commands_widget)
        _current_sample_view_widget_vlayout.setSpacing(0)
        _current_sample_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)
        #_current_sample_view_widget.setLayout(_current_sample_view_widget_vlayout)

        self.contents_widget_hlayout.addWidget(_current_sample_view_widget)

        self.selected_spinbox.valueChanged.connect(self.selectedChanged)
        self.selected_spinbox.lineEdit().textChanged.connect(self.selectionTextChanged)

        self.commandsWidget.append(self.holderLengthLabel)
        self.commandsWidget.append(self.holderLength)
        self.commandsWidget.append(self.holderLengthUnit)
        self.commandsWidget.append(self.buttonLoad)
        self.commandsWidget.append(self.selected_spinbox)
        self.commandsWidget.append(self.position_label)
        self.commandsWidget.append(self.state_label)

    def setHolderLength(self,length):
        self.holderLength.setValue(length)

    def getHolderLength(self):
        if not self.holderLength.isVisible():
            holder_len=None
        else:
            holder_len=self.holderLength.value()
        return holder_len

    def hideHolderLength(self,hide):
        if hide:
            self.holderLengthLabel.hide()
            self.holderLength.hide()
            self.holderLengthUnit.hide()
        else:
            self.holderLengthLabel.show()
            self.holderLength.show()
            self.holderLengthUnit.show()

    def setLoaded(self,state):
        matrix=self.loaded_matrix_code
        if not matrix:
            if self.loaded_location is not None:
                matrix = "%d:%02d" % (self.loaded_location[0], self.loaded_location[1])
            else:
                matrix = "sample"

        if state is None:
            self.holderLengthLabel.setEnabled(True)
            self.holderLength.setEnabled(True)
            self.holderLengthUnit.setEnabled(True)
            self.buttonLoad.setText("Mount %s" % matrix)
            self.setStateColor('UNKNOWN')
            self.setStateMsg("Unknown mounting state")
            if self.load_icon is not None:        
                self.buttonLoad.setIcon(self.load_icon)
        elif state:
            self.holderLengthLabel.setEnabled(False)
            self.holderLength.setEnabled(False)
            self.holderLengthUnit.setEnabled(False)
            self.buttonLoad.setText("Unmount %s" % matrix)
            self.setStateColor('LOADED')
            self.setStateMsg("Sample is mounted")
            if self.unload_icon is not None:
                self.buttonLoad.setIcon(self.unload_icon)
        else:
            self.holderLengthLabel.setEnabled(True)
            self.holderLength.setEnabled(True)
            self.holderLengthUnit.setEnabled(True)
            self.buttonLoad.setText("Mount %s" % matrix)
            self.setStateColor('UNLOADED')
            self.setStateMsg("No mounted sample")
            if self.load_icon is not None:        
                self.buttonLoad.setIcon(self.load_icon)

    def setStateMsg(self,msg):
        if msg is None:
            msg=""
        self.state_label.setText(msg)
        self.emit(QtCore.SIGNAL("sample_changer_state"), (msg,))

    def setStateColor(self,state):
        color = SC_SAMPLE_COLOR.get(state)
        if color  is None:
            color = Qt4_widget_colors.LINE_EDIT_ORIGINAL
        else:
            Qt4_widget_colors.set_widget_color(self.state_label, color)

    def setIcons(self,load_icon,unload_icon):
        self.load_icon = Qt4_Icons.load_icon(load_icon)
        self.unload_icon = Qt4_Icons.load_icon(unload_icon)
        txt=str(self.buttonLoad.text()).split()[0]
        if txt == "Mount":
            self.buttonLoad.setIcon(self.load_icon)
        elif txt == "Unmount":
            self.buttonLoad.setIcon(self.unload_icon)

    def setLoadedMatrixCode(self,code):
        #print "SampleSelection.setLoadedMatrixCode",code
        self.loaded_matrix_code=code
        txt=str(self.buttonLoad.text()).split()[0]
        if code is None:
            self.buttonLoad.setText("%s sample" % txt)
        else:
            self.buttonLoad.setText("%s %s" % (txt,code))

    def setLoadedLocation(self,location):
        #print "SampleSelection.setLoadedLocation",location
        self.loaded_location=location
        if not self.loaded_matrix_code and location:
            txt=str(self.buttonLoad.text()).split()[0]
            self.buttonLoad.setText("%s %d:%02d" % (txt,location[0],location[1]))

    #def buttonClicked(self):
    #    holder_len=self.getHolderLength()
    #    txt=str(self.buttonLoad.textLabel()).split()[0]
    #    if txt=="Mount":
    #        self.emit(QtCore.SIGNAL("loadSample"),(holder_len,))
    #    elif txt=="Unmount":
    #        self.emit(QtCore.SIGNAL("unloadSample"),(holder_len,self.loaded_matrix_code,self.loaded_location))

class StatusView(QtGui.QWidget):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.in_expert_mode=False
        self.last_sc_in_use=False

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots --------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.contents_widget = QtGui.QGroupBox("Unknown", self)
        self.box1 = QtGui.QWidget(self.contents_widget)

        self.status_label = QtGui.QLabel("", self.box1)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)

        #flags=self.status_label.alignment()|QtCore.Qt.WordBreak
        #self.status_label.setAlignment(flags)

        self.reset_button = QtGui.QToolButton(self.box1)
        self.reset_button.setText("Reset")
        self.reset_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                        QtGui.QSizePolicy.Fixed)
        self.reset_button.setEnabled(False)

        self.sc_can_load_radiobutton = QtGui.QRadioButton(\
             "Sample changer can load/unload", self.contents_widget)
        self.minidiff_can_move_radiobutton = QtGui.QRadioButton(\
             "Minidiff motors can move", self.contents_widget)

        # Layout --------------------------------------------------------------
        _box1_hlayout = QtGui.QHBoxLayout(self.box1)
        _box1_hlayout.addWidget(self.status_label)
        _box1_hlayout.addWidget(self.reset_button)
        _box1_hlayout.setSpacing(2)
        _box1_hlayout.setContentsMargins(2, 2, 2, 2)

        _contents_widget_vlayout = QtGui.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.box1)
        _contents_widget_vlayout.addWidget(self.sc_can_load_radiobutton)
        _contents_widget_vlayout.addWidget(self.minidiff_can_move_radiobutton)
        _contents_widget_vlayout.setSpacing(2)
        _contents_widget_vlayout.setContentsMargins(2, 2, 2, 2) 

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.reset_button.clicked.connect(self.resetSampleChanger)
        self.sc_can_load_radiobutton.clicked.connect(self.sampleChangerMoveToLoadingPos)
        self.minidiff_can_move_radiobutton.clicked.connect(self.minidiffGetControl)

    def setIcons(self,reset_icon):
        self.reset_button.setIcon(Qt4_Icons.load_icon(reset_icon))

    def setStatusMsg(self, status):
        #print "SAMPLE CHANGER MSG IS",status
        self.status_label.setToolTip(status)
        status = status.strip()
        self.status_label.setText(status)
        self.emit(QtCore.SIGNAL("status_msg_changed"), (status, Qt4_widget_colors.LINE_EDIT_ORIGINAL))

    def setState(self,state):
        #logging.getLogger().debug('SampleChangerBrick2: state changed (%s)' % state)
        color = SC_STATE_COLOR.get(state, None)
        if color is None:
            color = Qt4_widget_colors.LINE_EDIT_ORIGINAL
        else:
            Qt4_widget_colors.set_widget_color(self.status_label, color)

        state_str = SampleChangerState.tostring(state)
        self.contents_widget.setTitle(state_str)
        
        enabled=SC_STATE_GENERAL.get(state, False)
        self.status_label.setEnabled(enabled)
        if state==SampleChangerState.Fault:
            self.reset_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(enabled and self.in_expert_mode)
        self.sc_can_load_radiobutton.setEnabled(enabled)
        self.minidiff_can_move_radiobutton.setEnabled(enabled)

    def setExpertMode(self,state):
        self.in_expert_mode=state
        self.reset_button.setEnabled(state)
        self.minidiff_can_move_radiobutton.setEnabled(state)
        if state:
            self.sc_can_load_radiobutton.setEnabled(self.last_sc_in_use)
        else:
            self.sc_can_load_radiobutton.setEnabled(False)

    def hideOperationalControl(self,is_microdiff):
        if is_microdiff:
            self.sc_can_load_radiobutton.hide()
            self.minidiff_can_move_radiobutton.hide()
        else:
            self.sc_can_load_radiobutton.show()
            self.minidiff_can_move_radiobutton.show()

    def setSampleChangerUseStatus(self,in_use):
        self.last_sc_in_use=in_use
        self.sc_can_load_radiobutton.setEnabled(in_use and self.in_expert_mode)

    def setSampleChangerLoadStatus(self,can_load):
        self.setSampleChangerUseStatus(self.last_sc_in_use)
        self.sc_can_load_radiobutton.setChecked(can_load)

    def setMinidiffStatus(self,can_move):
        self.minidiff_can_move_radiobutton.setEnabled(self.in_expert_mode)
        self.minidiff_can_move_radiobutton.setChecked(can_move)

    def resetSampleChanger(self):
        self.emit(QtCore.SIGNAL("resetSampleChanger"),())

    def sampleChangerMoveToLoadingPos(self):
        if not self.sc_can_load_radiobutton.isChecked():
            self.sc_can_load_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.emit(QtCore.SIGNAL("sampleChangerToLoadingPosition"),())

    def minidiffGetControl(self):
        if not self.minidiff_can_move_radiobutton.isChecked():
            self.minidiff_can_move_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.emit(QtCore.SIGNAL("minidiffGetControl"),())

class SCCheckBox(QtGui.QCheckBox):
    def setMyState(self,state):
        try:
            enabled=SC_STATE_GENERAL[str(state)]
        except:
            enabled=False
        self.setEnabled(enabled)

class ScanBasketsView(QtGui.QWidget):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self,parent)

        self.scan_all_icon = None
        self.standard_color = None
 
        self.commandsWidget = []

        self.scan_all_baskets_button = QtGui.QToolButton(self)
        self.scan_all_baskets_button.setText("Scan selected baskets")
        #self.scan_all_baskets_button.setUsesTextLabel(True)
        #self.scan_all_baskets_button.setTextPosition(QToolButton.BesideIcon)

        self.buttonSelect = QtGui.QToolButton(self)
        self.buttonSelect.setText("Select")
        #self.buttonSelect.setUsesTextLabel(True)
        #self.buttonSelect.setTextPosition(QToolButton.BesideIcon)
        self.buttonSelect.setEnabled(False)
        self.buttonSelect.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Fixed)

        self.commandsWidget.append(self.scan_all_baskets_button)
        self.commandsWidget.append(self.buttonSelect)

        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(self.scan_all_baskets_button)
        _main_hlayout.addWidget(self.buttonSelect)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        self.scan_all_baskets_button.clicked.connect(self.scanAllBaskets)
        self.buttonSelect.clicked.connect(self.selectBasketsSamples)

    def setIcons(self, scan_all_icon, scan_select):
        self.scan_all_icon = Qt4_Icons.load(scan_all_icon)
        self.scan_all_baskets_button.setIcon(self.scan_all_icon)
        self.buttonSelect.setIcon(Qt4_Icons.load(scan_select))

    def scanAllBaskets(self):
        self.emit(QtCore.SIGNAL("scanAllBaskets"))

    def selectBasketsSamples(self):
        self.emit(QtCore.SIGNAL("selectBasketsSamples"))

    def setState(self,state):
        enabled=SC_STATE_GENERAL.get(state, False)
        for wid in self.commandsWidget:
            wid.setEnabled(enabled)

    def showSelectButton(self,show):
        if show:
            self.buttonSelect.show()
        else:
            self.buttonSelect.hide()

class Qt4_SampleChangerBrick3(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.addProperty("basketCount", "integer", 5)
        self.addProperty("defaultHolderLength", "integer", 22)
        self.addProperty("icons", "string", "")
        self.addProperty("showSelectButton", "boolean", False)
        self.addProperty("doubleClickLoads", "boolean", True)

        self.defineSignal("scanBasketUpdate", ())
        self.defineSignal("sampleGotLoaded", ())

        # Emitted when the status of the hwobj changes,
        # original intended receiver is TreeBrick.
        self.defineSignal("status_msg_changed", ())
        self.defineSlot('setSession',())
        self.defineSlot('setCollecting',())

        self.sample_changer_hwobj = None
        self.in_expert_mode = None
        self.basket_count = None
        self.baskets = [] 
        self.last_basket_checked = ()

        self.contents_widget = QtGui.QWidget(self)
        self.status = StatusView(self.contents_widget)
        self.switch_to_sample_transfer_button = QtGui.QPushButton(\
             "Switch to Sample Transfer mode", self.contents_widget)
        self.test_sample_changer_button = QtGui.QPushButton(\
             "Test sample changer", self.contents_widget)
        self.current_basket_view = CurrentBasketView(self.contents_widget)
        self.current_sample_view = CurrentSampleView(self.contents_widget)

        self.sc_contents_gbox = QtGui.QGroupBox("Contents", self)
        self.sc_contents_gbox.setAlignment(QtCore.Qt.AlignHCenter)
        self.reset_baskets_samples_button = QtGui.QPushButton(\
             "Reset sample changer contents", self.sc_contents_gbox)
 
        self.double_click_loads_cbox = SCCheckBox("Double-click loads the sample",self.sc_contents_gbox)
        self.double_click_loads_cbox.setEnabled(False)
        self.scan_baskets_view = ScanBasketsView(self.sc_contents_gbox)

        self.current_sample_view.setStateMsg("Unknown smart magnet state")
        self.current_sample_view.setStateColor("UNKNOWN")
        self.status.setStatusMsg("Unknown sample changer status")
        self.status.setState("UNKNOWN")

        #self.basketsSamplesSelectionDialog = BasketsSamplesSelection(self)

        self.sc_contents_gbox_vlayout = QtGui.QVBoxLayout(self.sc_contents_gbox)
        self.sc_contents_gbox_vlayout.addWidget(self.reset_baskets_samples_button)
        self.sc_contents_gbox_vlayout.addWidget(self.double_click_loads_cbox)
        self.sc_contents_gbox_vlayout.addWidget(self.scan_baskets_view) 
        self.sc_contents_gbox_vlayout.setSpacing(0)
        self.sc_contents_gbox_vlayout.setContentsMargins(0, 0, 0, 0) 

        _contents_widget_vlayout = QtGui.QVBoxLayout(self.contents_widget)
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

        self.main_vlayout = QtGui.QVBoxLayout(self)
        self.main_vlayout.addWidget(self.contents_widget)
        self.main_vlayout.setSpacing(0)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)
        
        self.test_sample_changer_button.clicked.connect(self.test_sample_changer)
        self.reset_baskets_samples_button.clicked.connect(self.resetBasketsSamplesInfo)

        """
        QObject.connect(self.status,QtCore.SIGNAL("sampleChangerToLoadingPosition"),self.sample_changer_hwobjToLoadingPosition)
        QObject.connect(self.status,QtCore.SIGNAL("minidiffGetControl"),self.minidiffGetControl)
        QObject.connect(self.status,QtCore.SIGNAL("resetSampleChanger"),self.resetSampleChanger)
        QObject.connect(self.switch_to_sample_transfer_button, QtCore.SIGNAL("clicked()"), self.switchToSampleTransferMode)
 
        QObject.connect(self.current_basket_view,QtCore.SIGNAL("selectedChanged"),self.changeBasket)
        QObject.connect(self.current_basket_view,QtCore.SIGNAL("scanBasket"),self.scanBasket)

        QObject.connect(self.current_sample_view,QtCore.SIGNAL("selectedChanged"),self.changeSample)
        QObject.connect(self.current_sample_view,QtCore.SIGNAL("loadSample"),self.loadSample)
        QObject.connect(self.current_sample_view,QtCore.SIGNAL("unloadSample"),self.unloadSample)

        QObject.connect(self.scanBaskets,QtCore.SIGNAL("scanAllBaskets"),self.scanAllBaskets)
        QObject.connect(self.scanBaskets,QtCore.SIGNAL("selectBasketsSamples"),self.selectBasketsSamples)
        QObject.connect(self.status, QtCore.SIGNAL("status_msg_changed"), self.status_msg_changed)
        
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        self.contents_widget.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        """

    def propertyChanged(self, property_name, oldValue, newValue):
        if property_name == 'icons':
            icons_list=newValue.split()

            try:
                self.status.setIcons(icons_list[0])
            except IndexError:
                pass

            try:
                self.current_basket_view.setIcons(icons_list[1])
            except IndexError:
                pass

            try:
                self.scan_baskets_view.setIcons(icons_list[2],icons_list[3])
            except IndexError:
                pass

            try:
                self.current_sample_view.setIcons(icons_list[5],icons_list[6])
            except IndexError:
                pass
        elif property_name == 'basketCount':
            self.basket_count = newValue
           
            for basket_index in range(self.basket_count):
                temp_basket = BasketView(self.sc_contents_gbox, basket_index)
                QtCore.QObject.connect(temp_basket, QtCore.SIGNAL("load_this_sample"),self.load_this_sample)
                temp_basket.setChecked(False)
                temp_basket.setEnabled(False)
                self.baskets.append(temp_basket)
                self.sc_contents_gbox_vlayout.addWidget(temp_basket)
        elif property_name == 'mnemonic':
            self.sample_changer_hwobj = self.getHardwareObject(newValue)
            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, SampleChanger.STATUS_CHANGED_EVENT, self.sc_status_changed)
                self.connect(self.sample_changer_hwobj, SampleChanger.STATE_CHANGED_EVENT, self.sc_state_changed)
                self.connect(self.sample_changer_hwobj, SampleChanger.INFO_CHANGED_EVENT, self.infoChanged)
                self.connect(self.sample_changer_hwobj, SampleChanger.SELECTION_CHANGED_EVENT, self.selectionChanged)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("sampleChangerCanLoad"), self.sampleChangerCanLoad)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("minidiffCanMove"), self.minidiff_can_move_radiobutton)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("sampleChangerInUse"), self.sampleChangerInUse)
                self.connect(self.sample_changer_hwobj, SampleChanger.LOADED_SAMPLE_CHANGED_EVENT, self.loadedSampleChanged)
                 
                #self.current_sample_view.hideHolderLength(self.sample_changer_hwobj.isMicrodiff())
                #self.status.hideOperationalControl(self.sample_changer_hwobj.isMicrodiff())
                self.sc_status_changed(self.sample_changer_hwobj.getStatus())
                self.sc_state_changed(self.sample_changer_hwobj.getState())
                self.infoChanged()
                self.selectionChanged()
                #self.sample_changer_hwobjInUse(self.sampleChanger.sampleChangerInUse())
                #self.sample_changer_hwobjCanLoad(self.sampleChanger.sampleChangerCanLoad())
                #self.minidiff_can_move_radiobutton(self.sample_changer_hwobj.minidiffCanMove())
                self.loadedSampleChanged(self.sample_changer_hwobj.getLoadedSample())
                #self.basketTransferModeChanged(self.sample_changer_hwobj.getBasketTransferMode())
        elif property_name == 'showSelectButton':
            self.scan_baskets_view.showSelectButton(newValue)
            for basket in self.baskets:
                basket.setUnselectable(newValue)
        elif property_name == 'defaultHolderLength':
            self.current_sample_view.setHolderLength(newValue)
        #elif property_name == 'doubleClickLoads':
        #    self.double_click_loads_cbox.setChecked(False) #newValue)
        else:
            BlissWidget.propertyChanged(self,property_name,oldValue,newValue)

    def status_msg_changed(self, msg, color):
        self.emit(QtCore.SIGNAL("status_msg_changed"), (msg, color))

    def selectionChanged(self):
        sample = self.sample_changer_hwobj.getSelectedSample()
        basket = self.sample_changer_hwobj.getSelectedComponent()
        if sample is None:
            self.current_sample_view.setSelected(0)
        else:
            self.current_sample_view.setSelected(sample.getIndex()+1)
        if basket is None:
            self.current_basket_view.setSelected(0)
        else:
            self.current_basket_view.setSelected(basket.getIndex()+1)

    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.basketsSamplesSelectionDialog.reject()

    def basketTransferModeChanged(self, basket_transfer):
        self.switch_to_sample_transfer_button.setEnabled(basket_transfer)

    def switchToSampleTransferMode(self):
        self.sample_changer_hwobj.changeMode(SampleChangerMode.Normal, wait=False)

    def loadedSampleChanged(self,sample):
        if sample is None:
            # get current location in SC
            sample = self.sample_changer_hwobj.getSelectedSample()
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

        if loaded:
            self.emit(QtCore.SIGNAL("sampleGotLoaded"),())


    def setCollecting(self,enabled_state):
        self.setEnabled(enabled_state)

    def resetSampleChanger(self):
        self.sample_changer_hwobj.reset()

    def resetBasketsSamplesInfo(self):
        self.sample_changer_hwobj.clearInfo()
 
    def setSession(self,session_id):
        pass

    def setExpertMode(self,state):
        self.in_expert_mode=state
        if self.sample_changer_hwobj is not None:
            self.status.setExpertMode(state)

    def run(self):
        if self.in_expert_mode is not None:
            self.setExpertMode(self.in_expert_mode)
        try:
            self.matrixCodesChanged(self.sample_changer_hwobj.getMatrixCodes())
        except:
            pass

        
    def sampleLoadSuccess(self):
        pass

    def sampleLoadFail(self):
        pass

    def sampleUnloadSuccess(self):
        pass

    def sampleUnloadFail(self,state):
        self.sample_changer_hwobjStateChanged(state)

    def sc_status_changed(self,status):
        self.status.setStatusMsg(status)

    def sc_state_changed(self, state, previous_state=None):
        logging.getLogger().debug('SampleChangerBrick3: state changed (%s)' % state)
        self.status.setState(state)
        self.current_basket_view.setState(state)
        self.current_sample_view.setState(state)
        for basket in self.baskets:
            basket.setState(state)
        #self.double_click_loads_cbox.setMyState(state)
        self.scan_baskets_view.setState(state)
        self.reset_baskets_samples_button.setEnabled(SC_STATE_GENERAL.get(state, False))

    def sampleChangerCanLoad(self,can_load):
        self.status.setSampleChangerLoadStatus(can_load)

    def sampleChangerInUse(self,in_use):
        self.status.setSampleChangerUseStatus(in_use)

    def minidiffCanMove(self,can_move):
        self.status.setMinidiffStatus(can_move)

    def sampleChangerToLoadingPosition(self):
        if not self.sample_changer_hwobj.sampleChangerToLoadingPosition():
            self.status.setSampleChangerLoadStatus(self.sample_changer_hwobj.sampleChangerCanLoad())

    def minidiffGetControl(self):
        if not self.sample_changer_hwobj.minidiffGetControl():
            self.status.setMinidiffStatus(self.sample_changer_hwobj.minidiffCanMove())

    def changeBasket(self,basket_number):
        address = SC3.Basket.getBasketAddress(basket_number)
        self.sample_changer_hwobj.select(address, wait=False)

    def changeSample(self,sample_number):
        basket_index = self.sample_changer_hwobj.getSelectedComponent().getIndex()
        basket_number = basket_index + 1
        address = SC3.Pin.getSampleAddress(basket_number, sample_number)
        self.sample_changer_hwobj.select(address, wait=False) 

    def load_this_sample(self,basket_index,vial_index):
        if self.double_click_loads_cbox.isChecked():
            sample_loc=(basket_index,vial_index)
            holder_len=self.current_sample_view.getHolderLength()
            self.sample_changer_hwobj.load(holder_len,None,sample_loc,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)

    def loadSample(self,holder_len):
        self.sample_changer_hwobj.load(holder_len,None,None,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)

    def unloadSample(self,holder_len,matrix_code,location):
        if matrix_code:
            location=None
        self.sample_changer_hwobj.unload(holder_len,matrix_code,location,self.sampleUnloadSuccess,self.sampleUnloadFail,wait=False)

    def clearMatrices(self):
        for basket in self.baskets:
            basket.clearMatrices()
        self.emit(QtCore.SIGNAL("scanBasketUpdate"),(None,))

    def sampleChangerContentsChanged(self, baskets):
        self.clearMatrices()

        i=0
        for b in baskets:
          self.baskets[i].blockSignals(True)
          self.baskets[i].setChecked(b is not None)
          self.baskets[i].blockSignals(False)
          i=i+1

    def scanBasket(self):
        if not self['showSelectButton']:
            self.baskets[self.current_basket_view.selected.value()-1].setChecked(True)
        self.sample_changer_hwobj.scan(self.sampleChanger.getSelectedComponent(), recursive=True, wait=False)

    def scanAllBaskets(self):
        baskets_to_scan = []
        for i, basket_checkbox in enumerate(self.baskets):
          baskets_to_scan.append(SC3.Basket.getBasketAddress(i+1) if basket_checkbox.isChecked() else None)
         
        self.sample_changer_hwobj.scan(filter(None, baskets_to_scan), recursive=True, wait=False)

    def infoChanged(self):
        baskets_at_sc = self.sample_changer_hwobj.getComponents()        
        presences = []
        for basket in baskets_at_sc:
            presences.append([[VialView.VIAL_UNKNOWN]] * 10 if \
               basket.isPresent() else [[VialView.VIAL_NONE]]*10)
     
        for sample in self.sample_changer_hwobj.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            vial_index = sample.getIndex()   
            basket_code = sample.getContainer().getID()  
            if sample.isPresent():
                if matrix:
                    if sample.hasBeenLoaded():
                        presences[basket_index][vial_index] = \
                            [VialView.VIAL_ALREADY_LOADED, matrix] 
                    else:
                        presences[basket_index][vial_index] = \
                            [VialView.VIAL_BARCODE, matrix]
                else:
                    if sample.hasBeenLoaded(): 
                        presences[basket_index][vial_index] = \
                           [VialView.VIAL_NOBARCODE_LOADED, matrix]
                    else:
                        presences[basket_index][vial_index] = \
                           [VialView.VIAL_NOBARCODE, matrix]
            else:     
                presences[basket_index][vial_index] = [VialView.VIAL_NONE, ""]
            if sample.isLoaded():
                presences[basket_index][vial_index] = [VialView.VIAL_AXIS, matrix]

        for basket_index in range(self.basket_count):
            presence = presences[basket_index]
            self.baskets[basket_index].setMatrices(presence)

    def selectBasketsSamples(self):
        retval=self.basketsSamplesSelectionDialog.exec_loop()

        if retval == QDialog.Accepted:
            self.sample_changer_hwobj.resetBasketsInformation()

            for basket, samples in self.basketsSamplesSelectionDialog.result.iteritems():
                for i in range(10):
                    input=[basket, i+1, 0, 0, 0]
                
                for sample in samples:
                    input[1]=sample
                    input[2]=1
                    self.sample_changer_hwobj.setBasketSampleInformation(input)

    def test_sample_changer(self):
        self.sample_changer_hwobj.run_test() 

class HorizontalSpacer(QtGui.QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

class VerticalSpacer(QtGui.QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)

class BasketsSamplesSelection(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)

        self.samplesBoxes = []
        self.txtPresentSamples = []
        self.result = {}

        self.setCaption("Basket and Sample selection")
        self.cmdResetContents = QPushButton("Reset basket and sample data", self)
        baskets_box = QHBox(self, 'basket_box')
        baskets_box.setSpacing(5)
        baskets_box.setMargin(5)
        QLabel("Select baskets :", baskets_box)
        self.txtPresentBaskets = QLineEdit(baskets_box)
        self.txtPresentBaskets.setText("1-5")
        samples_group = QVGroupBox("Select samples", self)
        samples_group.setInsideMargin(5)
        samples_group.setInsideSpacing(5)
        buttons_box = QWidget(self)
        self.cmdOk = QPushButton("Set contents", buttons_box)
        self.cmdCancel = QPushButton("Cancel", buttons_box)
        QGridLayout(buttons_box, 2, 2, 5, 5)
        buttons_box.layout().addWidget(self.cmdOk, 0, 1)
        buttons_box.layout().addWidget(self.cmdCancel, 1, 1)

        #TODO
        for i in range(10):
            self.samplesBoxes.append(QHBox(samples_group, 'sample_group'))
            QtGui.QLabel("Basket %s :" % str(i+1), self.samplesBoxes[-1])
            self.txtPresentSamples.append(QLineEdit(self.samplesBoxes[-1]))
            self.txtPresentSamples[-1].setText("1-10")
            self.samplesBoxes[-1].show()
        
        QObject.connect(self.txtPresentBaskets, QtCore.SIGNAL("textChanged(const QString&)"), self.presentBasketsChanged)
        QObject.connect(self.cmdResetContents, QtCore.SIGNAL("clicked()"), self.resetContents)
        QObject.connect(self.cmdOk, QtCore.SIGNAL("clicked()"), self.setSampleChangerContents)
        QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.reject)

        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(self.cmdResetContents)
        self.layout().addWidget(baskets_box)
        self.layout().addWidget(samples_group)
        self.layout().addWidget(buttons_box)

    def presentBasketsChanged(self, txt):
        selection = [x-1 for x in parse_range(str(txt))]

        for i in range(5):
            self.samplesBoxes[i].hide()       
                
        for i in selection:
            self.samplesBoxes[i].show()

    def setSampleChangerContents(self):
        self.result = {}

        for i in range(5):
            try:
                sb = self.samplesBoxes[i]
                if sb.isShown():
                    ps = self.txtPresentSamples[i]
                    self.result[i+1]=parse_range(str(self.txtPresentSamples[i].text()))
            except:
                continue
            
        self.done(1)

    def resetContents(self):
        self.txtPresentBaskets.setText("")
        self.result = {}

        for i in range(5):
            try:
                self.samplesBoxes[i].hide()
            except:
                continue

        self.done(0)

def handle_range(r):
    lim = r.split("-")

    if len(lim)==2:
        try:
            ll=int(lim[0])
            hl=int(lim[1])
        except:
            return []
        else:
            return range(ll,hl+1,1)
    elif len(lim)==1:
        try:
            n = int(lim[0])
        except:
            return []
        else:
            if n<0:
                return []
            return [n]
    return []

def parse_range(s):
    selection = []
    ranges = s.split(";")

    for i in range(len(ranges)):
        selection += handle_range(ranges[i].strip())

    selection.sort()

    return tuple(selection)
