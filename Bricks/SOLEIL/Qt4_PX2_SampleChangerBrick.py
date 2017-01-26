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

from QtImport import *

import sys
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework import Qt4_Icons

from Qt4_sample_changer_helper import *
import PX2Cats

from SOLEIL.Qt4_SoleilCatsBrick import Qt4_SoleilCatsBrick

__category__ = "Sample changer"


class VialView(QWidget):

    (VIAL_UNKNOWN, VIAL_NONE, VIAL_NOBARCODE, VIAL_BARCODE, VIAL_AXIS,
     VIAL_ALREADY_LOADED,VIAL_NOBARCODE_LOADED, VIAL_SELECTED) = (0, 1, 2, 3, 4, 5, 6,7)

    def __init__(self,vial_index, *args):
        QWidget.__init__(self, *args)
        self.vialIndex = vial_index
        self.setFixedSize(20, 16)
        self.pixmapUnknown = Qt4_Icons.load_pixmap("sample_unknown")
        self.pixmapNoBarcode = Qt4_Icons.load_pixmap("sample_nobarcode.png")
        self.pixmapBarcode = Qt4_Icons.load_pixmap("sample_barcode.png")
        self.pixmapAxis = Qt4_Icons.load_pixmap("sample_axis.png")
        self.pixmapAlreadyLoaded = Qt4_Icons.load_pixmap("sample_already_loaded2.png")
        self.pixmapAlreadyLoadedNoBarcode = Qt4_Icons.load_pixmap("sample_already_loaded2.png")
        self.pixmapSelected = Qt4_Icons.load_pixmap("green_led.png")
        self.pixmaps = [self.pixmapUnknown, None, self.pixmapNoBarcode, 
                        self.pixmapBarcode, self.pixmapAxis, 
                        self.pixmapAlreadyLoaded, 
                        self.pixmapAlreadyLoadedNoBarcode,
                        self.pixmapSelected]
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
            painter = QPainter(self)
            painter.setBrush(Qt.NoBrush)
            px = self.pixmaps[self.vialState]
            if px is not None:
                painter.drawPixmap(2, 0, px)

    def getVial(self):
        return self.vialState

    def getCode(self):
        return self.vialCode

    def mouseDoubleClickEvent(self,e):
        self.doubleClicked.emit(self.vialIndex)
    
    def mousePressEvent(self,e):
        self.clicked.emit(self.vialIndex)

class VialNumberView(QLabel):

    def __init__(self,vial_index,parent):
        QWidget.__init__(self, str(vial_index), parent)
        self.vialIndex = vial_index

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.vialIndex)
    
    def mousePressEvent(self,e):
        self.clicked.emit(self.vialIndex)

    def setVial(self, vial_state):
        state = vial_state[0]
        try:
            code = vial_state[1]
        except:
            code = ""
        self.setToolTip(code)


class SampleBox(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setMouseTracking(True)
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.LINE_EDIT_CHANGED)

    def enterEvent(self, event):
        QWidget.enterEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.LINE_EDIT_CHANGED)

    def leaveEvent(self, event):
        QWidget.leaveEvent(self, event)
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.BUTTON_ORIGINAL)

class SamplesView(QWidget):
    SAMPLE_COUNT = PX2Cats.Basket.NO_OF_SAMPLES_PER_PUCK
    CURRENT_VIAL_COLOR = Qt.gray

    def __init__(self, parent, basket_index):
        QWidget.__init__(self, parent)

        self.basket_index = basket_index
        self.vials = []
        self.numbers = []
        self.loaded_vial = None
        self.current_location = None
        self.standard_color = None

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        for i in range(SamplesView.SAMPLE_COUNT):
            sample_box = SampleBox(self)
            label = VialNumberView(i + 1, sample_box)
            label.setVial([VialView.VIAL_UNKNOWN])
            label.setAlignment(Qt.AlignHCenter)
            self.numbers.append(label)

            w = VialView(i + 1, sample_box)
            w.setVial([VialView.VIAL_UNKNOWN])
            self.vials.append(w)

            sample_box.layout().addWidget(label)
            sample_box.layout().addWidget(w)
            _main_hlayout.addWidget(sample_box)

            w.clicked.connect(self.samplesView_selectionChanged)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, 
                           QSizePolicy.Fixed)

    def loadSample(self, vial_index):
        state = self.vials[vial_index - 1].getVial()
        if state != VialView.VIAL_AXIS:
            self.load_this_sample.emit(self.basket_index, vial_index)
        
    def clearMatrices(self):
        for v in self.vials:
            v.setVial([VialView.VIAL_UNKNOWN])
        for n in self.numbers:
            n.setVial([VialView.VIAL_UNKNOWN])
    
    def samplesView_selectionChanged(self, vial_index):
        state = self.vials[vial_index - 1].getVial()
        self.viewChanged.emit(self.basket_index, vial_index)
        
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
        #Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.BUTTON_ORIGINAL)
        if self.standard_color is None:
            #Qt4_widget_colors.BUTTON_ORIGINAL
            self.standard_color = Qt4_widget_colors.BUTTON_ORIGINAL#self.numbers[0].paletteBackgroundColor()
        if self.current_location is not None and self.currentLocation[0] == self.basket_index:
            #self.vials[self.current_location[1]-1].setPaletteBackgroundColor(self.standard_color)
            Qt4_widget_colors.set_widget_color(self.vials[self.current_location[1]-1], Qt4_widget_colors.GREEN)
            #self.numbers[self.current_location[1]-1].setPaletteBackgroundColor(self.standard_color)
            Qt4_widget_colors.set_widget_color(self.numbers[self.current_location[1]-1], Qt4_widget_colors.GREEN)
        if location is not None and location[0] == self.basket_index:
            #self.vials[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
            Qt4_widget_colors.set_widget_color(self.vials[location[1]-1], Qt4_widget_colors.GREEN)
            #self.numbers[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
            Qt4_widget_colors.set_widget_color(self.numbers[location[1]-1], Qt4_widget_colors.GREEN)
        self.current_location = location

class BasketView(QWidget):
    def __init__(self, parent, basket_index):
        QWidget.__init__(self, parent)

        self.basket_index = basket_index

        #self.contents_widget = QVGroupBox("Basket %s" % basket_index,self)
        self.contents_widget = QGroupBox("Basket %s" % str(basket_index+1), self)
        self.contents_widget.setCheckable(True)
        self.samplesView = SamplesView(self.contents_widget, basket_index)

        _contents_widget_vlayout = QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.samplesView)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)

        self.contents_widget.setSizePolicy(QSizePolicy.Minimum, 
                                           QSizePolicy.Minimum)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, 
                           QSizePolicy.Fixed)    
                           
        self.samplesView.load_this_sample.connect(self.load_this_sample)
        self.samplesView.viewChanged.connect(self.selected_view_changed)
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
        
    def selected_view_changed(self,basket_index, vial_index):
        self.viewChanged.emit(basket_index, vial_index)
        
    def selected_changed(self,vial_index):
        self.selectedChanged.emit(vial_index)
        
    def load_this_sample(self, basket_index, vial_index):
        self.load_this_sample.emit(basket_index, vial_index)

    def setState(self, state):
        self.setEnabled(SC_STATE_GENERAL.get(state, False))

    def toggleBasketPresence(self, on):
        self.basketPresence.emit(self.basket_index, on)



class CurrentView(QWidget):
    def __init__(self, title, parent):
        QWidget.__init__(self, parent)

        #self.standard_color=None
        self.standard_color = Qt.white
        self.currentSelection=-1
        
        self.currentLoad=-1
        self.title = title

        self.contents_widget = QGroupBox(title, self)
        self.contents_widget_hlayout = QHBoxLayout(self.contents_widget) 
        self.contents_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.contents_widget_hlayout.setSpacing(0)
        self.contents_widget.setAlignment(Qt.AlignHCenter)
        self.commandsWidget=[]

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.addWidget(self.contents_widget)

    def selectionTextChanged(self, txt):
        if txt == str(self.currentSelection):
            self.selected_spinbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        else:
            self.selected_spinbox.setStyleSheet("background-color: rgb(254, 254, 121);")

    def selectedChanged(self, val):
        tmp = self.currentSelection
        self.currentSelection = val
        if tmp == -1:
            self.selectedChanged.emit(val)
        else :
            if self.standard_color is not None:
                Qt4_widget_colors.set_widget_color(self.selected_spinbox.lineEdit(), 
                                                   self.standard_color)
            if self.currentLoad == self.currentSelection:
                self.selected_spinbox.setStyleSheet("background-color: rgb(255, 255, 255);")
            else:
                self.selected_spinbox.setStyleSheet("background-color: rgb(254, 254, 121);")
            self.selectedChanged.emit(val)

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

        self.position_label = QLabel("Position:", self.contents_widget)
        self.selected_spinbox = QSpinBox(self.contents_widget)
       
        
        #self.selected_spinbox.setWrapping(True)
        #self.selected_spinbox.editor().setAlignment(QWidget.AlignRight)

        self.scan_basket_button = QToolButton(self.contents_widget)
        self.scan_basket_button.setText("Scan")
        self.scan_basket_button.hide()
        self.scan_basket_button.setEnabled(False)
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
        self.scanBasket.emit()

class CurrentSampleView(CurrentView):
    def __init__(self,parent):
        CurrentView.__init__(self, "Current sample", parent)

        self.loaded_matrix_code = None
        self.loaded_location = None
        self.load_icon = None
        self.unload_icon = None

        _current_sample_view_widget = QWidget(self.contents_widget)

        self.state_label = QLabel("unknown", _current_sample_view_widget)
        self.state_label.setAlignment(Qt.AlignHCenter)

        self.commands_widget = QWidget(_current_sample_view_widget)
        self.position_label = QLabel("Position:",self.commands_widget)
        self.selected_spinbox = QSpinBox(self.commands_widget)
        self.selected_spinbox.setRange(1, PX2Cats.Basket.NO_OF_SAMPLES_PER_PUCK)
        self.selected_spinbox.setSingleStep(1)
        self.selected_spinbox.setWrapping(True)
        self.selected_spinbox.lineEdit().setAlignment(Qt.AlignRight)

        self.holderLengthLabel = QLabel("Holder length:", self.commands_widget)
        self.holderLength = QSpinBox(self.commands_widget)
        self.holderLength.setRange(19, 26)
        self.holderLength.setSingleStep(1)
        self.holderLength.lineEdit().setAlignment(Qt.AlignRight)
        self.holderLengthUnit = QLabel("mm", self.commands_widget)
        self.holderLength.setEnabled(False)
        self.holderLengthUnit.setEnabled(False)
        self.holderLengthLabel.setEnabled(False)

        self.buttonLoad = QToolButton(self.commands_widget)
        self.buttonLoad.setText("Mount sample")
        #self.buttonLoad.setTextPosition(QToolButton.BesideIcon)
        self.buttonLoad.hide()

        _commands_widget_gridlayout = QGridLayout(self.commands_widget)
        _commands_widget_gridlayout.addWidget(self.position_label, 0, 0)
        _commands_widget_gridlayout.addWidget(self.selected_spinbox, 0, 1)
        _commands_widget_gridlayout.addWidget(self.holderLengthLabel, 1, 0)
        _commands_widget_gridlayout.addWidget(self.holderLength,1, 1)
        _commands_widget_gridlayout.addWidget(self.holderLengthUnit, 1, 2)
        _commands_widget_gridlayout.addWidget(self.buttonLoad, 2, 2)
        self.commands_widget.setLayout(_commands_widget_gridlayout)

        _current_sample_view_widget_vlayout = QVBoxLayout(_current_sample_view_widget)
        _current_sample_view_widget_vlayout.addWidget(self.state_label)
        _current_sample_view_widget_vlayout.addWidget(self.commands_widget)
        _current_sample_view_widget_vlayout.setSpacing(0)
        _current_sample_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)
        _current_sample_view_widget.setLayout(_current_sample_view_widget_vlayout)

        self.contents_widget_hlayout.addWidget(_current_sample_view_widget)

        self.selected_spinbox.valueChanged.connect(self.selectedChanged)
        self.selected_spinbox.lineEdit().textChanged.connect(self.selectionTextChanged)
        self.buttonLoad.clicked.connect(self.actionButtonClicked)
        
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
    
    #pas utilise 
    def setLoaded(self,state):
        #logging.getLogger("user_level_log").info("----------setLoaded state is %s " % str(state))
        
        matrix=self.loaded_matrix_code
        #logging.getLogger("user_level_log").info("----------setLoaded matrix is %s" % str(matrix))
        #logging.getLogger("user_level_log").info("----------setLoaded loaded_location is %s" % str(self.loaded_location))        
        if not matrix:
            if self.loaded_location is not None:
                matrix = "%d : %02d" % (self.loaded_location[0], self.loaded_location[1])
            else:
                matrix = "sample"
        #logging.getLogger("user_level_log").info("----------setLoaded matrix II is %s" % str(matrix))
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
        self.sample_changer_state.emit(msg)

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
            
    def actionButtonClicked(self):
        txt=str(self.buttonLoad.text()).split()[0]
        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>....... position is %s %d : %02d" % (txt, self.loaded_location[0], self.loaded_location[1]))
        holder_len= 22 #self.getHolderLength()
        if txt=="Mount":
            self.loadSample.emit(holder_len)
        elif txt=="Unmount":
            self.unloadSample.emit(holder_len,self.loaded_matrix_code,self.loaded_location)

class StatusView(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.in_expert_mode=False
        self.last_sc_in_use=False

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots --------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.contents_widget = QGroupBox("Unknown", self)
        self.contents_widget.setTitle("Cats PX2 Status")
        self.box1 = QWidget(self.contents_widget)

        self.status_label = QLabel("", self.box1)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.reset_button = QToolButton(self.box1)
        self.reset_button.setText("Reset")
        self.reset_button.setSizePolicy(QSizePolicy.Fixed, 
                                        QSizePolicy.Fixed)
        self.reset_button.setEnabled(False)

        self.sc_can_load_radiobutton = QRadioButton(\
             "Sample changer can load/unload", self.contents_widget)
        self.minidiff_can_move_radiobutton = QRadioButton(\
             "Minidiff motors can move", self.contents_widget)
        
        # Layout --------------------------------------------------------------
        _box1_hlayout = QHBoxLayout(self.box1)
        _box1_hlayout.addWidget(self.status_label)
        _box1_hlayout.addWidget(self.reset_button)
        _box1_hlayout.setSpacing(2)
        _box1_hlayout.setContentsMargins(2, 2, 2, 2)

        _contents_widget_vlayout = QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.box1)
        _contents_widget_vlayout.addWidget(self.sc_can_load_radiobutton)
        _contents_widget_vlayout.addWidget(self.minidiff_can_move_radiobutton)
        _contents_widget_vlayout.setSpacing(2)
        _contents_widget_vlayout.setContentsMargins(2, 2, 2, 2) 

        _main_vlayout = QVBoxLayout(self)
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
        self.status_msg_changed.emit(status, Qt4_widget_colors.LINE_EDIT_ORIGINAL)

    def setState(self,state):
        #logging.getLogger().debug('SampleChangerBrick2: state changed (%s)' % state)
        color = SC_STATE_COLOR.get(state, None)
        if color is None:
            color = Qt4_widget_colors.LIGHT_RED#LINE_EDIT_ORIGINAL
        else:
            Qt4_widget_colors.set_widget_color(self.status_label, color)

        #state_str = SampleChangerState.tostring(state)
        #self.contents_widget.setTitle(state_str)
        
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
        self.resetSampleChanger.emit()

    def sampleChangerMoveToLoadingPos(self):
        if not self.sc_can_load_radiobutton.isChecked():
            self.sc_can_load_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.sampleChangerToLoadingPosition.emit()

    def minidiffGetControl(self):
        if not self.minidiff_can_move_radiobutton.isChecked():
            self.minidiff_can_move_radiobutton.setChecked(True)
            return
        self.sc_can_load_radiobutton.setEnabled(False)
        self.minidiff_can_move_radiobutton.setEnabled(False)
        self.sc_can_load_radiobutton.setChecked(False)
        self.minidiff_can_move_radiobutton.setChecked(False)
        self.minidiffGetControl.emit()

class SCCheckBox(QCheckBox):
    def setMyState(self,state):
        try:
            enabled=SC_STATE_GENERAL[str(state)]
        except:
            enabled=False
        self.setEnabled(enabled)

class ScanBasketsView(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)

        self.scan_all_icon = None
        self.standard_color = None
 
        self.commandsWidget = []

        self.scan_all_baskets_button = QToolButton(self)
        self.scan_all_baskets_button.setText("Scan selected baskets")
        self.scan_all_baskets_button.hide()
        #self.scan_all_baskets_button.setUsesTextLabel(True)
        #self.scan_all_baskets_button.setTextPosition(QToolButton.BesideIcon)

        self.buttonSelect = QToolButton(self)
        self.buttonSelect.setText("Select")
        #self.buttonSelect.setUsesTextLabel(True)
        #self.buttonSelect.setTextPosition(QToolButton.BesideIcon)
        self.buttonSelect.setEnabled(False)
        self.buttonSelect.setSizePolicy(QSizePolicy.Fixed,
                                        QSizePolicy.Fixed)

        self.commandsWidget.append(self.scan_all_baskets_button)
        self.commandsWidget.append(self.buttonSelect)

        _main_hlayout = QHBoxLayout(self)
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
        self.scanAllBaskets.emit()

    def selectBasketsSamples(self):
        self.selectBasketsSamples.emit()

    def setState(self,state):
        enabled=SC_STATE_GENERAL.get(state, False)
        for wid in self.commandsWidget:
            wid.setEnabled(enabled)

    def showSelectButton(self,show):
        if show:
            self.buttonSelect.show()
        else:
            self.buttonSelect.hide()

class Qt4_PX2_SampleChangerBrick(BlissWidget):
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
        self.loadedCoord = [-1,-1]

        self.contents_widget = QWidget(self)
        self.status = StatusView(self.contents_widget)
        #self.switch_to_sample_transfer_button = QPushButton(\
        #     "Switch to Sample Transfer mode", self.contents_widget)
        #self.test_sample_changer_button = QPushButton(\
        #     "Test sample changer", self.contents_widget)
        self.current_basket_view = CurrentBasketView(self.contents_widget)
        self.current_sample_view = CurrentSampleView(self.contents_widget)

        self.sc_contents_gbox = QGroupBox("Contents", self)
        self.sc_contents_gbox.setAlignment(Qt.AlignHCenter)
        #self.reset_baskets_samples_button = QPushButton(\
        #     "Reset sample changer contents", self.sc_contents_gbox)
        
        
        # a developper
        self.double_click_loads_cbox = SCCheckBox("Double-click loads the sample",self.sc_contents_gbox)
        self.double_click_loads_cbox.setEnabled(False)
        self.scan_baskets_view = ScanBasketsView(self.sc_contents_gbox)
        self.double_click_loads_cbox.hide()

        self.current_sample_view.setStateMsg("Unknown smart magnet state")
        self.current_sample_view.setStateColor("UNKNOWN")
        self.status.setStatusMsg("Unknown sample changer status")
        self.status.setState("UNKNOWN")
        
        self.sc_command_gbox = QGroupBox("Command", self)
        self.sc_command_gbox.setAlignment(Qt.AlignHCenter)
        
        #load ui file
        #pathfile = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "."))
        self.widget_command = Qt4_SoleilCatsBrick(self)
        
        #self.basketsSamplesSelectionDialog = BasketsSamplesSelection(self)

        self.sc_contents_gbox_vlayout = QVBoxLayout(self.sc_contents_gbox)
        #self.sc_contents_gbox_vlayout.addWidget(self.reset_baskets_samples_button)
        self.sc_contents_gbox_vlayout.addWidget(self.double_click_loads_cbox)
        self.sc_contents_gbox_vlayout.addWidget(self.scan_baskets_view) 
        self.sc_contents_gbox_vlayout.setSpacing(0)
        self.sc_contents_gbox_vlayout.setContentsMargins(0, 0, 0, 0) 

        _contents_widget_vlayout = QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.status)
        #_contents_widget_vlayout.addWidget(self.switch_to_sample_transfer_button)
        #_contents_widget_vlayout.addWidget(self.test_sample_changer_button)
        _contents_widget_vlayout.addWidget(self.current_basket_view)
        _contents_widget_vlayout.addWidget(self.current_sample_view)
        _contents_widget_vlayout.addWidget(self.sc_contents_gbox)
        _contents_widget_vlayout.addWidget(self.sc_command_gbox)
        _contents_widget_vlayout.addWidget(self.widget_command)
        _contents_widget_vlayout.setSpacing(0)
        _contents_widget_vlayout.addStretch(0)
        _contents_widget_vlayout.setContentsMargins(0, 0, 0, 0)
        self.contents_widget.setLayout(_contents_widget_vlayout)

        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.contents_widget)
        self.main_vlayout.setSpacing(0)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)
        
        #self.test_sample_changer_button.clicked.connect(self.test_sample_changer)
        #self.reset_baskets_samples_button.clicked.connect(self.resetBasketsSamplesInfo)
        # ->QT5 evolution !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.widget_command.widget.btLoadSample.clicked.connect(self._load)
        self.widget_command.widget.btWash.clicked.connect(self._wash)
        self.widget_command.widget.btUnloadSample.clicked.connect(self._unload)
        self.widget_command.widget.btAbort.clicked.connect(self._abort)
        
        #self.widget_command.widget.btLoadSample.setEnabled(False)
        #self.widget_command.widget.btWash.setEnabled(False)
        #self.widget_command.widget.btUnloadSample.setEnabled(False)
        #self.widget_command.widget.btAbort.setEnabled(False)
        
        self.current_basket_view.selectedChanged.connect(self.changeBasket)
        self.current_sample_view.selectedChanged.connect(self.changeSample)
        
    
    def _load(self):
        logging.getLogger("user_level_log").info("---------------------------------------------------> _load")
        #return
        try:
            if self.sample_changer_hwobj is not None:
                logging.getLogger("user_level_log").info("---------------------------------------------------> _load")
                self.sample_changer_hwobj.load(wait=False)
        except:
            QMessageBox.warning(self, "Error",str(sys.exc_info()[1]))
    
    def _wash(self):
        logging.getLogger("user_level_log").info("---------------------------------------------------> _wash")
        try:
            if self.sample_changer_hwobj is not None:
                logging.getLogger("user_level_log").info("---------------------------------------------------> _load")
                self.sample_changer_hwobj.load(wash=True, wait=False)
        except:
            QMessageBox.warning(self, "Error",str(sys.exc_info()[1]))
    
    def _unload(self):
        logging.getLogger("user_level_log").info("---------------------------------------------------> _unload")
        try:
            if self.sample_changer_hwobj is not None:
                self.sample_changer_hwobj.unload(wait=False)
        except:
            QMessageBox.warning(self, "Error",str(sys.exc_info()[1]))
    
    def _abort(self):
        logging.getLogger("user_level_log").info("---------------------------------------------------> Abort")
        if self.sample_changer_hwobj is not None:
            self.sample_changer_hwobj.abort()
    
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
                self.current_sample_view.setIcons(icons_list[4],icons_list[5])
            except IndexError:
                pass
        elif property_name == 'basketCount':
            self.basket_count = newValue
           
            for basket_index in range(self.basket_count):
                temp_basket = BasketView(self.sc_contents_gbox, basket_index)
                temp_basket.load_this_sample.connect(self.load_this_sample)
                temp_basket.viewChanged.connect(self.selected_view_changed)
                temp_basket.setChecked(False)
                temp_basket.setEnabled(False)
                self.baskets.append(temp_basket)
                self.sc_contents_gbox_vlayout.addWidget(temp_basket)
        elif property_name == 'mnemonic':
            self.sample_changer_hwobj = self.getHardwareObject(newValue)            
            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, SampleChanger.TASK_FINISHED_EVENT, self.onTaskFinished)
                self.connect(self.sample_changer_hwobj, SampleChanger.STATUS_CHANGED_EVENT, self.sc_status_changed)
                self.connect(self.sample_changer_hwobj, SampleChanger.STATE_CHANGED_EVENT, self.sc_state_changed)
                self.connect(self.sample_changer_hwobj, SampleChanger.INFO_CHANGED_EVENT, self.infoChanged)
                self.connect(self.sample_changer_hwobj, SampleChanger.SELECTION_CHANGED_EVENT, self.selectionChanged)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("sampleChangerCanLoad"), self.sampleChangerCanLoad)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("minidiffCanMove"), self.minidiff_can_move_radiobutton)
                #self.connect(self.sample_changer_hwobj, QtCore.SIGNAL("sampleChangerInUse"), self.sampleChangerInUse)
                self.connect(self.sample_changer_hwobj, SampleChanger.LOADED_SAMPLE_CHANGED_EVENT, self.loadedSampleChanged)
                 
                self.current_sample_view.hideHolderLength(True)#self.sample_changer_hwobj.isMicrodiff())
                self.status.hideOperationalControl(True)#self.sample_changer_hwobj.isMicrodiff())
                self.sc_status_changed(self.sample_changer_hwobj.getStatus())
                self.sc_state_changed(self.sample_changer_hwobj.getState())
                self.infoChanged()
                #self.selectionChanged()#init value in spinbox
                #self.sample_changer_hwobjInUse(self.sampleChanger.sampleChangerInUse())
                #self.sample_changer_hwobjCanLoad(self.sampleChanger.sampleChangerCanLoad())
                #self.minidiff_can_move_radiobutton(self.sample_changer_hwobj.minidiffCanMove())
                self.loadedSampleChanged(self.sample_changer_hwobj.getLoadedSample())
                self.selectionChanged()
                #self.basketTransferModeChanged(self.sample_changer_hwobj.getBasketTransferMode())
                #PX2_self.onStateChanged(self.device.getState(),None)
                #PX2_self.onStatusChanged(self.device.getStatus())
                #PX2_self._createTable()       
            #else:
            #    self.sc_state_changed(SampleChanger.SampleChangerState.Unknown,None)
            #   self.sc_status_changed("")
                #self._clearTable()
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
        self.status_msg_changed.emit(msg, color)

    def selectionChanged(self):
        logging.info("XXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       Qt4_SampleChangerBrick3 selectionChanged ")
        sample = self.sample_changer_hwobj.getSelectedSample()
        basket = self.sample_changer_hwobj.getSelectedComponent()
        logging.info("XXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       Qt4_SampleChangerBrick3 sample %s" % str(sample))
        logging.info("XXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       Qt4_SampleChangerBrick3 basket %s" % str())
        if sample is None:
            self.current_sample_view.setSelected(self.loadedCoord[1])
        else:
            self.current_sample_view.setSelected(sample.getIndex()+1)
        if basket is None:
            self.current_basket_view.setSelected(self.loadedCoord[0])
        else:
            self.current_basket_view.setSelected(basket.getIndex()+1)
    
    
    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.basketsSamplesSelectionDialog.reject()

    def basketTransferModeChanged(self, basket_transfer):
        self.switch_to_sample_transfer_button.setEnabled(basket_transfer)

    # def switchToSampleTransferMode(self):
    #    self.sample_changer_hwobj.changeMode(SampleChangerMode.Normal, wait=False)
    
    def onTaskFinished(self,task,ret,exception):
        pass
    
    def loadedSampleChanged(self,sample):
        logging.info("XXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       Qt4_SampleChangerBrick3 loadedSampleChanged is %s " % str(sample))
        if sample is None:
            # get current location in SC
            sample = self.sample_changer_hwobj.getSelectedSample()
            loaded = False
        else:
            loaded = True

        if sample is None:
            # basket transfer mode?
            barcode = ""
            location = None #(-1, -1)
        else:
            barcode = sample.getID()
            location = sample.getCoords()
        self.current_basket_view.setMatrixCode(barcode)
        self.current_sample_view.setLoadedMatrixCode(barcode)
        self.current_sample_view.setLoadedLocation(location)
        self.current_sample_view.setLoaded(loaded)
        if location is not None:
            self.loadedCoord = location
            try:            
                self.current_basket_view.selected_spinbox.setValue(int(location[0]))
            except:
                import traceback
                logging.error(traceback.format_exc())
                    
            try:            
                self.current_sample_view.selected_spinbox.setValue(int(location[1]))
            except:
                import traceback
                logging.error(traceback.format_exc())
        if None not in self.loadedCoord:
            logging.info("XXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       Qt4_SampleChangerBrick3 loadedCoord is %s " % str(self.loadedCoord))
            self.current_basket_view.currentLoad = self.loadedCoord[0]
            self.current_sample_view.currentLoad = self.loadedCoord[1]
            
        if loaded:
            self.sampleGotLoaded.emit()


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
        pass
        #self.sample_changer_hwobjStateChanged(state)

    def sc_status_changed(self,status):
        #logging.getLogger("user_level_log").info(">>>>>>##########################  PX2 SampleChangerBrick3 sc_status_changed : %s" % str(status))
        self.widget_command.widget.txtState.setText(status)
        self.status.setStatusMsg(status)

    def sc_state_changed(self, state, previous_state=None):
        logging.info("################################################# sc_state_changed ########################################################")
        #logging.getLogger("user_level_log").info(">>>>>>######################## PX2  SampleChangerBrick3 sc_state_changed : %s" % str(state))
        self.status.setState(state)
        #logging.getLogger("user_level_log").info(">>>>>>######################## PX2  SampleChangerBrick3 SC_STATE_GENERAL.get(state,FaLSE) : %s" % str(SC_STATE_GENERAL.get(state,False)))
        
        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>. sample_changer_hwobj .getSelected %s" % str(self.sample_changer_hwobj.getSelectedSample()))
        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>changeSample sample_changer_hwobj .getLoadedSample %s" % str(self.sample_changer_hwobj.getLoadedSample()))
        testSelection = False
        if self.sample_changer_hwobj.getSelectedSample() is not None:
            testSelection = self.sample_changer_hwobj.getSelectedSample()==self.sample_changer_hwobj.getLoadedSample()
        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> #################   changeSample sample_changer_hwobj test %s" % str(testSelection))
        #self.widget_command.widget.setEnabled(SC_STATE_GENERAL.get(state, False))
        self.widget_command.widget.btLoadSample.setEnabled(SC_STATE_GENERAL.get(state, False) and not testSelection)
        self.widget_command.widget.btWash.setEnabled(SC_STATE_GENERAL.get(state, False) and testSelection)
        self.widget_command.widget.btUnloadSample.setEnabled(SC_STATE_GENERAL.get(state, False) and testSelection)
        #self.widget_command.widget.btAbort.setEnabled(False)
        #Abort is always True
        self.widget_command.widget.btAbort.setEnabled(True)
        self.current_basket_view.setState(state)
        self.current_sample_view.setState(state)
        for basket in self.baskets:
            basket.setState(state)
        #self.double_click_loads_cbox.setMyState(state)
        self.scan_baskets_view.setState(state)
        #self.reset_baskets_samples_button.setEnabled(SC_STATE_GENERAL.get(state, False))
        logging.info("################################################# sc_state_changed  END ########################################################")
    """
    def _updateButtons(self):
        selected_sample = self._getSelectedSample()
        if self.sample_changer_hwobj is None or not self.sample_changer_hwobj.isReady():
            self.widget.btLoadSample.setEnabled(False) 
            self.widget.btUnloadSample.setEnabled(False)
            self.widget.btAbort.setEnabled(False)
            #self.widget.lvSC.setEnabled(False)
        else:
            charging = (self.sample_changer_hwobj.getState() == SampleChanger.SampleChangerState.Charging)
            ready = (self.sample_changer_hwobj.getState() == SampleChanger.SampleChangerState.Ready)
            #standby = (self.sample_changer_hwobj.getState() == SampleChanger.SampleChangerState.StandBy)
            #moving = (self.sample_changer_hwobj.getState() in [SampleChanger.SampleChangerState.Moving, SampleChanger.SampleChangerState.Loading, SampleChanger.SampleChangerState.Unloading])
            self.widget.btLoadSample.setEnabled(ready and not charging and (selected_sample is not None) and selected_sample.isPresent() and (selected_sample != self._loadedSample))
            self.widget.btUnloadSample.setEnabled(ready and not charging and self.sample_changer_hwobj.hasLoadedSample())
            #self.widget.lvSC.setEnabled(ready or standby or charging)
        self.widget.btAbort.setEnabled(self.sample_changer_hwobj is not None and not self.sample_changer_hwobj.isReady())
    """
    
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
        #logging.getLogger("user_level_log").info(">> changeBasket no : %s" % str(basket_number))
        address = PX2Cats.Basket.getBasketAddress(basket_number)
        logging.getLogger("user_level_log").info("####################    changeBasket adress no : %s" % str(address))
        #logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>changeBasket  sample_changer_hwobj .getLoadedSample %s" % str(self.sample_changer_hwobj.getLoadedSample()))
        self.sample_changer_hwobj.select(address, wait=False)

    def changeSample(self,sample_number):
        logging.getLogger("user_level_log").info("##############################    changeSample   ###########################################")
        try :
            basket_number = self.sample_changer_hwobj.getSelectedComponent().getIndex() +1
        except:
            logging.info(">>>>>>>>>>>>>>>>>>.................. ERRORRRR ")
            basket_number = self.current_basket_view.selected_spinbox.value() +1
        finally:
            logging.info(">>>>>>>>>>>>>>>>>>.................. self.sc_hwobj.select %s - %s" %  (str(basket_number), str(sample_number)))
            address = PX2Cats.Pin.getSampleAddress(basket_number, sample_number)
            logging.info(">>>>>>>>>>>>>>>>>>.................. self.sc_hwobj. address = %s" %  str(address))
            
        #basket_index = self.sample_changer_hwobj.getSelectedComponent().getIndex()
        #basket_number = basket_index + 1
        #logging.getLogger("user_level_log").info("---------------------         >> changeSample basket_index no : %s" % str(basket_index))
        #address = PX2Cats.Pin.getSampleAddress(basket_number, sample_number)
        #logging.getLogger("user_level_log").info("---------------------         >> changeSample address no : %s" % str(address))
        #logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>. sample_changer_hwobj .getSelected %s" % str(self.sample_changer_hwobj.getSelectedSample()))
        #logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>changeSample sample_changer_hwobj .getLoadedSample %s" % str(self.sample_changer_hwobj.getLoadedSample()))
        #logging.getLogger("user_level_log").info("###############################     FIN       ##########################################")
        self.sample_changer_hwobj.select(address, wait=False) 
    
    def selected_view_changed(self,basket_index,vial_index):
        logging.getLogger("user_level_log").info("selected_view_changed basket_index %s and vial_index %s" % (str(basket_index), str(vial_index)))
        try:
            self.current_basket_view.selected_spinbox.setValue(int(basket_index)+1)
        except:
            import traceback
            logging.error(traceback.format_exc())
                    
        try:            
            self.current_sample_view.selected_spinbox.setValue(int(vial_index))
        except:
            import traceback
            logging.error(traceback.format_exc())
        
    def load_this_sample(self,basket_index,vial_index):
        logging.getLogger("user_level_log").info("load_this_sample basket_index %s and vial_index %s" % (str(basket_index), str(vial_index)))
        """
        if self.double_click_loads_cbox.isChecked():
            sample_loc=(basket_index,vial_index)
            holder_len=self.current_sample_view.getHolderLength()
            self.sample_changer_hwobj.load(holder_len,None,sample_loc,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)"""
    #SC        
    def loadSample(self,holder_len):
        
        logging.getLogger("user_level_log").info(".......................>>>>>>>>>>>>>>>>>>>>>>>>>>> loadSample %s!!!!!" % str(self.loaded_location))
        #self.sample_changer_hwobj.load(holder_len,None,None,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)
    #SC

    def unloadSample(self,holder_len,matrix_code,location):
        if matrix_code:
            location=None
        #logging.getLogger("user_level_log").info(".......................>>>>>>>>>>>>>>>>>>>>>>>>>>> unloadSample !!!!!")
        #logging.getLogger("user_level_log").info(".......................>>>>>>>>>>>>>>>>>>>>>>>>>>> matrix_code is %" % str(matrix_code))
        #logging.getLogger("user_level_log").info(".......................>>>>>>>>>>>>>>>>>>>>>>>>>>> location is %" % str(location))
        #self.sample_changer_hwobj.unload(holder_len,matrix_code,location,self.sampleUnloadSuccess,self.sampleUnloadFail,wait=False)

    def clearMatrices(self):
        for basket in self.baskets:
            basket.clearMatrices()
        self.scanBasketUpdate.emit(None)

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
          baskets_to_scan.append(PX2Cats.Basket.getBasketAddress(i+1) if basket_checkbox.isChecked() else None)
         
        self.sample_changer_hwobj.scan(filter(None, baskets_to_scan), recursive=True, wait=False)

    def infoChanged(self):
        baskets_at_sc = self.sample_changer_hwobj.getComponents()
        #logging.info(">>>>>>>>>>>>>>>>>>    InfoChanged     <<<<<<<<<<<<<<<<<<<<<<<<<baskets_at_sc")
        #logging.info(">>>>>>>>>>>>>>>>>>    baskets_at_sc is %s" % str(baskets_at_sc))
        presences = []
        for basket in baskets_at_sc:
            presences.append([[VialView.VIAL_UNKNOWN]] * SamplesView.SAMPLE_COUNT if \
               basket.isPresent() else [[VialView.VIAL_NONE]]*SamplesView.SAMPLE_COUNT)
        #logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>> presences is >>>>>>>>>>>>>>>>>>>> %s.." % str(presences))
        #logging.info(">>>>>>>>>>>>>>>>>>    sample_changer_hwobj.getSampleList is %s" % str(self.sample_changer_hwobj.getSampleList()))
        for sample in self.sample_changer_hwobj.getSampleList():
            matrix = sample.getID() or ""
            #logging.info(">>>>>>>>>>>>>>>>>>    matrix is %s" % str(matrix))
            basket_index = sample.getContainer().getIndex()
            #logging.info(">>>>>>>>>>>>>>>>>>    basket_index is %s" % str(basket_index))
            vial_index = sample.getIndex()
            #logging.info(">>>>>>>>>>>>>>>>>>    vial_index is %s" % str(vial_index))
            basket_code = sample.getContainer().getID()
            #logging.info(">>>>>>>>>>>>>>>>>>    basket_code is %s" % str(basket_code))
            #logging.info(">>>>>>>>>>>>>>>>>>    sample.isPresent() is %s" % str(sample.isPresent()))
            #logging.info(">>>>>>>>>>>>>>>>>>    sample.hasBeenLoaded() is %s" % str(sample.hasBeenLoaded()))
            #logging.info(">>>>>>>>>>>>>>>>>>    sample.isLoaded() is %s" % str(sample.isLoaded()))
            if sample.isPresent():
                if matrix:
                    if sample.hasBeenLoaded():
                        presences[basket_index][vial_index] = \
                            [VialView.VIAL_ALREADY_LOADED, matrix] 
                    else:
                        if basket_code :
                            presences[basket_index][vial_index] = \
                                [VialView.VIAL_BARCODE, matrix]
                        else :
                            presences[basket_index][vial_index] = \
                                [VialView.VIAL_NOBARCODE, matrix]
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
        #logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>> presences after is >>>>>>>>>>>>>>>>>>>> %s.." % str(presences))
        for basket_index in range(self.basket_count):
            presence = presences[basket_index]
            self.baskets[basket_index].setMatrices(presence)
        #logging.info("AAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaaaaaaaaaa >>>>>>>>>>>>>>>>>>    baskets is %s" % str(self.baskets))
        #self._updateButtons()

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

class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

class VerticalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)

class BasketsSamplesSelection(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)

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
            QLabel("Basket %s :" % str(i+1), self.samplesBoxes[-1])
            self.txtPresentSamples.append(QLineEdit(self.samplesBoxes[-1]))
            self.txtPresentSamples[-1].setText("1-10")
            self.samplesBoxes[-1].show()
        
        self.txtPresentBaskets.textChanged.connect(self.presentBasketsChanged)
        self.cmdResetContents.clicked.connect(self.resetContents)
        self.cmdOk.clicked.connect(self.setSampleChangerContents)
        self.cmdCancel.clicked.connect(self.reject)

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
