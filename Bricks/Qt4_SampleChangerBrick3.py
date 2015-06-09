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

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework import Qt4_Icons
from sample_changer import SC3
from Qt4_sample_changer_helper import *


__category__ = "Qt4_Task"


class VialView(QtGui.QWidget):
    (VIAL_UNKNOWN,VIAL_NONE,VIAL_NOBARCODE,VIAL_BARCODE,VIAL_AXIS,VIAL_ALREADY_LOADED,VIAL_NOBARCODE_LOADED)=(0,1,2,3,4,5,6)
    def __init__(self,vial_index,*args):
        QtGui.QWidget.__init__(self,*args)
        self.vialIndex=vial_index
        self.setFixedSize(20,16)
        self.pixmapUnknown=Icons.load("sample_unknown")
        self.pixmapNoBarcode=Icons.load("sample_nobarcode.png")
        self.pixmapBarcode=Icons.load("sample_barcode.png")
        self.pixmapAxis=Icons.load("sample_axis.png")
        self.pixmapAlreadyLoaded=Icons.load("sample_already_loaded.png")
        self.pixmapAlreadyLoadedNoBarcode=Icons.load("sample_already_loaded2.png")
        self.pixmaps=[self.pixmapUnknown,None,self.pixmapNoBarcode,self.pixmapBarcode,self.pixmapAxis,self.pixmapAlreadyLoaded, self.pixmapAlreadyLoadedNoBarcode]
        self.vialState=VialView.VIAL_UNKNOWN
        self.vialCode=""
    def setVial(self,vial_state):
        self.vialState=vial_state[0]
        try:
            self.vialCode=vial_state[1]
        except:
            self.vialCode=""
        self.setEnabled(self.vialState!=VialView.VIAL_NONE)
        self.setToolTip(self.vialCode)
        self.update()
    def paintEvent(self,event):
        if self.vialState is not None:
            painter = QtGui.QPainter(self)
            painter.setBrush(QtCoreQt.NoBrush)
            px=self.pixmaps[self.vialState]
            if px is not None:
                painter.drawPixmap(2,0,px)
    def getVial(self):
        return self.vialState
    def getCode(self):
        return self.vialCode
    def mouseDoubleClickEvent(self,e):
        self.emit(PYSIGNAL("doubleClicked"),(self.vialIndex,))

class VialNumberView(QtGui.QLabel):
    def __init__(self,vial_index,parent):
        QtGui.QWidget.__init__(self,str(vial_index),parent)
        self.vialIndex=vial_index
    def mouseDoubleClickEvent(self,e):
        self.emit(PYSIGNAL("doubleClicked"),(self.vialIndex,))
    def setVial(self,vial_state):
        state=vial_state[0]
        try:
            code=vial_state[1]
        except:
            code=""
        self.setToolTip(code)


class SampleBox(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
         
        self.setMouseTracking(True)
        self.__bkg = self.paletteBackgroundColor()
        self.__light=self.palette().active().light()

    def mouseMoveEvent(self, e):
        QtGui.QWidget.mouseMoveEvent(self, e)
        self.setPaletteBackgroundColor(self.__light)

    def enterEvent(self, e):
        QtGui.QWidget.enterEvent(self, e)
        self.setPaletteBackgroundColor(self.__light)


    def leaveEvent(self, e):
        QtGui.QWidget.leaveEvent(self, e)
        self.setPaletteBackgroundColor(self.__bkg)


class SamplesView(QtGui.QWidget):
    SAMPLE_COUNT = 10
    CURRENT_VIAL_COLOR = QtCore.Qt.gray

    def __init__(self,parent,basket_index):
        QtGui.QWidget.__init__(self,parent)

        self.basketIndex=basket_index
        #QHBoxLayout(self)

        self.vials=[]
        self.numbers=[]
        self.loadedVial=None
        for i in range(SamplesView.SAMPLE_COUNT):
            sample_box=SampleBox(self)
            label=VialNumberView(i+1,sample_box)
            label.setVial([VialView.VIAL_UNKNOWN])
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.numbers.append(label)

            w=VialView(i+1,sample_box)
            w.setVial([VialView.VIAL_UNKNOWN])
            self.vials.append(w)

            self.layout().addWidget(sample_box)

            QtCore.QObject.connect(label, QtCore.SIGNAL("doubleClicked"),self.loadSample)
            QtCore.QObject.connect(w, QtCore.SIGNAL("doubleClicked"),self.loadSample)

        self.currentLocation=None
        self.standardColor=None

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)

    def loadSample(self,vial_index):
        state=self.vials[vial_index-1].getVial()
        if state!=VialView.VIAL_AXIS:
            self.emit(PYSIGNAL("loadThisSample"),(self.basketIndex,vial_index))

    def clearMatrices(self):
        for v in self.vials:
            v.setVial([VialView.VIAL_UNKNOWN])
        for n in self.numbers:
            n.setVial([VialView.VIAL_UNKNOWN])

    def setMatrices(self,vial_states):
        i=0
        for v in self.vials:
            try:
                state=vial_states[i]
            except IndexError:
                state=[VialView.VIAL_UNKNOWN]
            v.setVial(state)
            self.numbers[i].setVial(state)
            i+=1

    """
    def setLoadedVial(self,vial_index=None):
        if vial_index is None and self.loadedVial is not None:
            loaded_vial_index=self.loadedVial[0]
            loaded_vial_state=self.loadedVial[1]
            code=self.vials[loaded_vial_index-1].getCode()
            self.vials[loaded_vial_index-1].setVial([loaded_vial_state,code])
            self.loadedVial=None
        elif vial_index is not None:
            state=self.vials[vial_index-1].getVial()
            code=self.vials[vial_index-1].getCode()
            self.vials[vial_index-1].setVial([VialView.VIAL_AXIS,code])
            self.loadedVial=[vial_index,state]
    """

    def setCurrentVial(self,location=None):
        if self.standardColor is None:
            self.standardColor=self.numbers[0].paletteBackgroundColor()
        if self.currentLocation is not None and self.currentLocation[0]==self.basketIndex:
            self.vials[self.currentLocation[1]-1].setPaletteBackgroundColor(self.standardColor)
            self.numbers[self.currentLocation[1]-1].setPaletteBackgroundColor(self.standardColor)
        if location is not None and location[0]==self.basketIndex:
            self.vials[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
            self.numbers[location[1]-1].setPaletteBackgroundColor(SamplesView.CURRENT_VIAL_COLOR)
        self.currentLocation=location

class BasketView(QtGui.QWidget):
    def __init__(self,parent,basket_index):
        QtGui.QWidget.__init__(self,parent)

        #self.contentsBox = QVGroupBox("Basket %s" % basket_index,self)
        self.contentsBox = Qtgui.QGroupBox("Basket %s" % basket_index,self)
        self.contentsBox.setCheckable(True)
        self.basket_index = basket_index
        self.samplesView=SamplesView(self.contentsBox,basket_index)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(2)
        QtCore.QObject.connect(self.samplesView, QtCore.SIGNAL("loadThisSample"),self.loadThisSample)
        QtCore.QObject.connect(self.contentsBox, Qtcore.SIGNAL("toggled(bool)"), self.toggleBasketPresence)

        self.contentsBox.setSizePolicy(QtGui.QSizePolicy.Minimum, Qtgui.QSizePolicy.Minimum)
 
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contentsBox)
        self.setLayout(_main_vlayout)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)    

    def clearMatrices(self):
        self.samplesView.clearMatrices()

    def setMatrices(self,vial_states):
        self.samplesView.setMatrices(vial_states)

    """
    def setLoadedVial(self,vial_index=None):
        self.samplesView.setLoadedVial(vial_index)
    """

    def setCurrentVial(self,location=None):
        return
        self.samplesView.setCurrentVial(location)

    def setUnselectable(self,state):
        self.contentsBox.setCheckable(not state)

    def isChecked(self):
        if self.contentsBox.isCheckable():
            return self.contentsBox.isChecked()
        return None

    def setChecked(self,state):
        if self.contentsBox.isCheckable():
            self.contentsBox.setChecked(state)
            return state
        return None

    def loadThisSample(self,basket_index,vial_index):
        self.emit(PYSIGNAL("loadThisSample"),(basket_index,vial_index))

    def setState(self, state):
        self.setEnabled(SC_STATE_GENERAL.get(state, False))

    def toggleBasketPresence(self, on):
        self.emit(PYSIGNAL("basketPresence"), (self.basket_index, on))


class CurrentView(QtGui.QWidget):
    def __init__(self,title,parent):
        QtGui.QWidget.__init__(self,parent)

        #self.standardColor=None
        self.standardColor = QtCore.Qt.white
        self.currentSelection=1
        self.title=title

        #self.contentsBox = QVGroupBox(title,self)
        self.contentsBox = QtGui.QGroupBox(title,self)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(2)
        self.contentsBox.setAlignment(QtCore.Qt.AlignHCenter)

        self.commandsWidget=[]

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contentsBox)
        self.setLayout(_main_vlayout) 

    def selectionTextChanged(self,txt):
        if self.standardColor is None:
            self.standardColor=self.selected.editor().paletteBackgroundColor()
        if txt==str(self.currentSelection):
            if self.standardColor is not None:
                self.selected.editor().setPaletteBackgroundColor(self.standardColor)
            state=True
        else:
            self.selected.editor().setPaletteBackgroundColor(QtCore.Qt.yellow)
            state=False

    def selectedChanged(self,val):
        self.currentSelection=val
        if self.standardColor is not None:
            self.selected.editor().setPaletteBackgroundColor(self.standardColor)
        self.emit(PYSIGNAL("selectedChanged"),(val,))

    def setMatrixCode(self,code):
        if code is None or code=="":
            self.contentsBox.setTitle(self.title)
        else:
            self.contentsBox.setTitle("%s (%s)" % (self.title,code))

    def setSelected(self,val):
        self.currentSelection=val
        self.selected.blockSignals(True)
        self.selected.editor().blockSignals(True)
        self.selected.setValue(val)
        self.selected.editor().blockSignals(False)
        self.selected.blockSignals(False)

    def setState(self,state):
        enabled=SC_STATE_GENERAL.get(state, False)
        for wid in self.commandsWidget:
            wid.setEnabled(enabled)

class CurrentBasketView(CurrentView):
    def __init__(self,parent):
        CurrentView.__init__(self,"Current basket",parent)

        self.commandsBox = Qtgui.QWidget(self.contentsBox)
        #QtQGridLayout(self.commandsBox, 1, 3, 0, 2)

        self.positionLabel=QLabel("Position:",self.commandsBox)
        self.commandsBox.layout().addWidget(self.positionLabel, 0, 0)
        self.selected=QSpinBox(1,5,1,self.commandsBox)
        self.selected.setWrapping(True)
        self.commandsBox.layout().addWidget(self.selected,0,1)
        self.selected.editor().setAlignment(QWidget.AlignRight)
        QObject.connect(self.selected, SIGNAL("valueChanged(int)"), self.selectedChanged)
        QObject.connect(self.selected.editor(), SIGNAL("textChanged(const QString &)"), self.selectionTextChanged)

        self.buttonScan=QToolButton(self.commandsBox)
        self.buttonScan.setTextLabel("Scan")
        self.buttonScan.setUsesTextLabel(True)
        self.buttonScan.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.buttonScan,SIGNAL("clicked()"),self.scanBasket)
        self.commandsBox.layout().addWidget(self.buttonScan,0,2)

        self.commandsWidget.append(self.buttonScan)
        self.commandsWidget.append(self.positionLabel)
        self.commandsWidget.append(self.selected)

    def setIcons(self,scan_one_icon):
        self.buttonScan.setPixmap(Icons.load(scan_one_icon))

    def scanBasket(self):
        self.emit(PYSIGNAL("scanBasket"),())

class CurrentSampleView(CurrentView):
    def __init__(self,parent):
        CurrentView.__init__(self,"Current sample",parent)

        self.loadedMatrixCode=None
        self.loadedLocation=None

        self.loadIcon=None
        self.unloadIcon=None

        self.stateBox=QHGroupBox(self.contentsBox)
        self.stateBox.setInsideMargin(4)
        self.stateBox.setInsideSpacing(2)
        self.stateLabel=QLabel(self.stateBox)
        self.stateLabel.setAlignment(Qt.AlignHCenter)

        self.commandsBox=QWidget(self.contentsBox)
        QGridLayout(self.commandsBox, 1, 3, 0, 2)

        self.positionLabel=QLabel("Position:",self.commandsBox)
        self.commandsBox.layout().addWidget(self.positionLabel, 0, 0)
        self.selected=QSpinBox(1,10,1,self.commandsBox)
        self.selected.setWrapping(True)
        self.commandsBox.layout().addWidget(self.selected,0,1)
        self.selected.editor().setAlignment(QWidget.AlignRight)
        QObject.connect(self.selected, SIGNAL("valueChanged(int)"), self.selectedChanged)
        QObject.connect(self.selected.editor(), SIGNAL("textChanged(const QString &)"), self.selectionTextChanged)

        self.holderLengthLabel=QLabel("Holder length:",self.commandsBox)
        self.commandsBox.layout().addWidget(self.holderLengthLabel, 1, 0)
        self.holderLength=QSpinBox(19,26,1,self.commandsBox)
        self.commandsBox.layout().addWidget(self.holderLength,1,1)
        self.holderLength.editor().setAlignment(QWidget.AlignRight)
        self.holderLengthUnit=QLabel("mm",self.commandsBox)
        self.commandsBox.layout().addWidget(self.holderLengthUnit, 1, 2)
        self.holderLength.hide()
        self.holderLengthUnit.hide()
        self.holderLengthLabel.hide()

        self.buttonLoad=QToolButton(self.commandsBox)
        self.buttonLoad.setTextLabel("Mount sample")
        self.buttonLoad.setUsesTextLabel(True)
        self.buttonLoad.setTextPosition(QToolButton.BesideIcon)
        #QObject.connect(self.buttonLoad,SIGNAL("clicked()"),self.buttonClicked)
        self.commandsBox.layout().addMultiCellWidget(self.buttonLoad, 2, 2, 0, 2)
        self.buttonLoad.hide()

        self.commandsWidget.append(self.holderLengthLabel)
        self.commandsWidget.append(self.holderLength)
        self.commandsWidget.append(self.holderLengthUnit)
        self.commandsWidget.append(self.buttonLoad)
        self.commandsWidget.append(self.selected)
        self.commandsWidget.append(self.positionLabel)
        self.commandsWidget.append(self.stateBox)

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
        matrix=self.loadedMatrixCode
        if not matrix:
            if self.loadedLocation is not None:
                matrix="%d:%02d" % (self.loadedLocation[0],self.loadedLocation[1])
            else:
                matrix="sample"

        if state is None:
            self.holderLengthLabel.setEnabled(True)
            self.holderLength.setEnabled(True)
            self.holderLengthUnit.setEnabled(True)
            self.buttonLoad.setTextLabel("Mount %s" % matrix)
            self.setStateColor('UNKNOWN')
            self.setStateMsg("Unknown mounting state")
            if self.loadIcon is not None:        
                self.buttonLoad.setPixmap(self.loadIcon)
        elif state:
            self.holderLengthLabel.setEnabled(False)
            self.holderLength.setEnabled(False)
            self.holderLengthUnit.setEnabled(False)
            self.buttonLoad.setTextLabel("Unmount %s" % matrix)
            self.setStateColor('LOADED')
            self.setStateMsg("Sample is mounted")
            if self.unloadIcon is not None:
                self.buttonLoad.setPixmap(self.unloadIcon)
        else:
            self.holderLengthLabel.setEnabled(True)
            self.holderLength.setEnabled(True)
            self.holderLengthUnit.setEnabled(True)
            self.buttonLoad.setTextLabel("Mount %s" % matrix)
            self.setStateColor('UNLOADED')
            self.setStateMsg("No mounted sample")
            if self.loadIcon is not None:        
                self.buttonLoad.setPixmap(self.loadIcon)

    def setStateMsg(self,msg):
        if msg is None:
            msg=""
        self.stateLabel.setText(msg)
        self.emit(PYSIGNAL("sample_changer_state"), (msg,))

    def setStateColor(self,state):
        color = SC_SAMPLE_COLOR.get(state)
        if color  is None:
            color = QWidget.paletteBackgroundColor(self)
        else:
            self.stateLabel.setPaletteBackgroundColor(color)

    def setIcons(self,load_icon,unload_icon):
        self.loadIcon=Icons.load(load_icon)
        self.unloadIcon=Icons.load(unload_icon)
        txt=str(self.buttonLoad.textLabel()).split()[0]
        if txt=="Mount":
            self.buttonLoad.setPixmap(self.loadIcon)
        elif txt=="Unmount":
            self.buttonLoad.setPixmap(self.unloadIcon)

    def setLoadedMatrixCode(self,code):
        #print "SampleSelection.setLoadedMatrixCode",code
        self.loadedMatrixCode=code
        txt=str(self.buttonLoad.textLabel()).split()[0]
        if code is None:
            self.buttonLoad.setTextLabel("%s sample" % txt)
        else:
            self.buttonLoad.setTextLabel("%s %s" % (txt,code))

    def setLoadedLocation(self,location):
        #print "SampleSelection.setLoadedLocation",location
        self.loadedLocation=location
        if not self.loadedMatrixCode and location:
            txt=str(self.buttonLoad.textLabel()).split()[0]
            self.buttonLoad.setTextLabel("%s %d:%02d" % (txt,location[0],location[1]))

    #def buttonClicked(self):
    #    holder_len=self.getHolderLength()
    #    txt=str(self.buttonLoad.textLabel()).split()[0]
    #    if txt=="Mount":
    #        self.emit(PYSIGNAL("loadSample"),(holder_len,))
    #    elif txt=="Unmount":
    #        self.emit(PYSIGNAL("unloadSample"),(holder_len,self.loadedMatrixCode,self.loadedLocation))

class StatusView(QtGui.QWidget):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)

        self.contentsBox= QtGui.QGroupBox("Unknown",self) #vertical

        #self.contentsBox.setInsideMargin(4)
        #self.contentsBox.setInsideSpacing(2)
        #self.contentsBox.setAlignment(Qt.AlignHCenter)

        self.box1=QHBox(self.contentsBox, 'content_box')

        self.lblStatus = QLabel("",self.box1)
        self.lblStatus.setAlignment(Qt.AlignCenter)
        flags=self.lblStatus.alignment()|Qt.WordBreak
        self.lblStatus.setAlignment(flags)

        self.buttonReset = QToolButton(self.box1)
        self.buttonReset.setTextLabel("Reset")
        self.buttonReset.setUsesTextLabel(True)
        self.buttonReset.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.buttonReset.setEnabled(False)
        QObject.connect(self.buttonReset,SIGNAL("clicked()"),self.resetSampleChanger)

        self.box2=QVBox(self.contentsBox)
        self.scCanLoad=QRadioButton("Sample changer can load/unload",self.box2)
        QObject.connect(self.scCanLoad,SIGNAL("clicked()"),self.sampleChangerMoveToLoadingPos)
        self.minidiffCanMove=QRadioButton("Minidiff motors can move",self.box2)
        QObject.connect(self.minidiffCanMove,SIGNAL("clicked()"),self.minidiffGetControl)

        #self.contentsBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)    
        QVBoxLayout(self)
        self.layout().addWidget(self.contentsBox)

        self.inExpert=False
        self.lastSCInUse=False

    def setIcons(self,reset_icon):
        self.buttonReset.setPixmap(Icons.load(reset_icon))

    def setStatusMsg(self, status):
        #print "SAMPLE CHANGER MSG IS",status
        QToolTip.add(self.lblStatus,status)
        status = status.strip()
        self.lblStatus.setText(status)
        color = self.lblStatus.paletteBackgroundColor()
        self.emit(PYSIGNAL("status_msg_changed"), (status, color))

    def setState(self,state):
        #logging.getLogger().debug('SampleChangerBrick2: state changed (%s)' % state)
        color = SC_STATE_COLOR.get(state, None)
        if color is None:
            color = QWidget.paletteBackgroundColor(self)
        else:
            self.lblStatus.setPaletteBackgroundColor(color)

        state_str = SampleChangerState.tostring(state)
        self.contentsBox.setTitle(state_str)
        
        enabled=SC_STATE_GENERAL.get(state, False)
        self.lblStatus.setEnabled(enabled)
        if state==SampleChangerState.Fault:
            self.buttonReset.setEnabled(True)
        else:
            self.buttonReset.setEnabled(enabled and self.inExpert)
        self.box2.setEnabled(enabled)

    def setExpertMode(self,state):
        self.inExpert=state
        self.buttonReset.setEnabled(state)
        self.minidiffCanMove.setEnabled(state)
        if state:
            self.scCanLoad.setEnabled(self.lastSCInUse)
        else:
            self.scCanLoad.setEnabled(False)

    def hideOperationalControl(self,is_microdiff):
        if is_microdiff:
            self.scCanLoad.hide()
            self.minidiffCanMove.hide()
        else:
            self.scCanLoad.show()
            self.minidiffCanMove.show()

    def setSampleChangerUseStatus(self,in_use):
        self.lastSCInUse=in_use
        self.scCanLoad.setEnabled(in_use and self.inExpert)

    def setSampleChangerLoadStatus(self,can_load):
        self.setSampleChangerUseStatus(self.lastSCInUse)
        self.scCanLoad.setChecked(can_load)

    def setMinidiffStatus(self,can_move):
        self.minidiffCanMove.setEnabled(self.inExpert)
        self.minidiffCanMove.setChecked(can_move)

    def resetSampleChanger(self):
        self.emit(PYSIGNAL("resetSampleChanger"),())

    def sampleChangerMoveToLoadingPos(self):
        if not self.scCanLoad.isChecked():
            self.scCanLoad.setChecked(True)
            return
        self.scCanLoad.setEnabled(False)
        self.minidiffCanMove.setEnabled(False)
        self.scCanLoad.setChecked(False)
        self.minidiffCanMove.setChecked(False)
        self.emit(PYSIGNAL("sampleChangerToLoadingPosition"),())

    def minidiffGetControl(self):
        if not self.minidiffCanMove.isChecked():
            self.minidiffCanMove.setChecked(True)
            return
        self.scCanLoad.setEnabled(False)
        self.minidiffCanMove.setEnabled(False)
        self.scCanLoad.setChecked(False)
        self.minidiffCanMove.setChecked(False)
        self.emit(PYSIGNAL("minidiffGetControl"),())

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

        self.scanAllIcon = None
        self.standardColor=None

        self.commandsWidget=[]

        self.buttonScanAll=QToolButton(self)
        self.buttonScanAll.setTextLabel("Scan selected baskets")
        self.buttonScanAll.setUsesTextLabel(True)
        self.buttonScanAll.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.buttonScanAll,SIGNAL("clicked()"),self.scanAllBaskets)

        self.buttonSelect=QToolButton(self)
        self.buttonSelect.setTextLabel("Select")
        self.buttonSelect.setUsesTextLabel(True)
        self.buttonSelect.setTextPosition(QToolButton.BesideIcon)
        self.buttonSelect.hide()
        self.buttonSelect.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        QObject.connect(self.buttonSelect,SIGNAL("clicked()"), self.selectBasketsSamples)

        self.commandsWidget.append(self.buttonScanAll)
        self.commandsWidget.append(self.buttonSelect)

        QHBoxLayout(self)
        self.layout().addWidget(self.buttonScanAll)
        self.layout().addWidget(self.buttonSelect)

    def setIcons(self,scan_all_icon,scan_select):
        self.scanAllIcon=Icons.load(scan_all_icon)
        self.buttonScanAll.setPixmap(self.scanAllIcon)
        self.buttonSelect.setPixmap(Icons.load(scan_select))

    def scanAllBaskets(self):
        self.emit(PYSIGNAL("scanAllBaskets"),())

    def selectBasketsSamples(self):
        self.emit(PYSIGNAL("selectBasketsSamples"), ())

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

        self.sampleChanger = None

        self.inExpert=None
        self.lastBasketChecked=()

        #self.contentsBox=QVBox(self)
        #self.contentsBox.setSpacing(10)
        
        #self.contentsBox.setInsideMargin(4)
        #self.contentsBox.setInsideSpacing(2)

        _mount_label = QtGui.QLabel("<b><i>NEW: Mount/unmount samples by right-clicking on the data collection tree on the left</b></i>", self)
        self.status=StatusView(self)
        self.switch_to_sample_transfer_button = QtGui.QPushButton("Switch to Sample Transfer mode", self)
        self.currentBasket=CurrentBasketView(self)
        self.currentSample=CurrentSampleView(self)
        #VerticalSpacer(self.contentsBox)
        self.sc_contents_gbox = QtGui.QGroupBox("Contents", self)
        #self.sc_contents_gbox.setInsideMargin(4)
        #self.sc_contents_gbox.setInsideSpacing(2)
        #self.sc_contents_gbox.setAlignment(Qt.AlignHCenter)
        self.reset_baskets_samples_button = QtGui.QPushButton("Reset sample changer contents", self.sc_contents_gbox)
        QtCore.QObject.connect(self.reset_baskets_samples_button, QtCore.SIGNAL("clicked()"), self.resetBasketsSamplesInfo)

        self.basket1=BasketView(self.sc_contents_gbox,1)
        self.basket2=BasketView(self.sc_contents_gbox,2)
        self.basket3=BasketView(self.sc_contents_gbox,3)
        self.basket4=BasketView(self.sc_contents_gbox,4)
        self.basket5=BasketView(self.sc_contents_gbox,5)
        self.baskets=(self.basket1,self.basket2,self.basket3,self.basket4,self.basket5)
 
        for i in range(5):
          QtCore.QObject.connect(self.baskets[i], QtCore.SIGNAL("loadThisSample"),self.loadThisSample)
          self.baskets[i].setChecked(False)
          self.baskets[i].setEnabled(False)

        self.doubleClickLoads=SCCheckBox("Double-click loads the sample",self.sc_contents_gbox)
        self.doubleClickLoads.hide()

        self.scanBaskets=ScanBasketsView(self.sc_contents_gbox)

        self.currentSample.setStateMsg("Unknown smart magnet state")
        self.currentSample.setStateColor("UNKNOWN")
        self.status.setStatusMsg("Unknown sample changer status")
        self.status.setState("UNKNOWN")

        self.basketsSamplesSelectionDialog = BasketsSamplesSelection(self)

        VerticalSpacer(self.contentsBox)
        QVBoxLayout(self)
        self.layout().addWidget(self.contentsBox)

        QObject.connect(self.status,PYSIGNAL("sampleChangerToLoadingPosition"),self.sampleChangerToLoadingPosition)
        QObject.connect(self.status,PYSIGNAL("minidiffGetControl"),self.minidiffGetControl)
        QObject.connect(self.status,PYSIGNAL("resetSampleChanger"),self.resetSampleChanger)
        QObject.connect(self.switch_to_sample_transfer_button, SIGNAL("clicked()"), self.switchToSampleTransferMode)
 
        QObject.connect(self.currentBasket,PYSIGNAL("selectedChanged"),self.changeBasket)
        QObject.connect(self.currentBasket,PYSIGNAL("scanBasket"),self.scanBasket)

        QObject.connect(self.currentSample,PYSIGNAL("selectedChanged"),self.changeSample)
        QObject.connect(self.currentSample,PYSIGNAL("loadSample"),self.loadSample)
        QObject.connect(self.currentSample,PYSIGNAL("unloadSample"),self.unloadSample)

        QObject.connect(self.scanBaskets,PYSIGNAL("scanAllBaskets"),self.scanAllBaskets)
        QObject.connect(self.scanBaskets,PYSIGNAL("selectBasketsSamples"),self.selectBasketsSamples)
        QObject.connect(self.status, PYSIGNAL("status_msg_changed"), self.status_msg_changed)
        
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        self.contentsBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)

    def propertyChanged(self, propertyName, oldValue, newValue):

        BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
        return

        if propertyName == 'icons':
            icons_list=newValue.split()

            try:
                self.status.setIcons(icons_list[0])
            except IndexError:
                pass

            try:
                self.currentBasket.setIcons(icons_list[1])
            except IndexError:
                pass

            try:
                self.scanBaskets.setIcons(icons_list[2],icons_list[3])
            except IndexError:
                pass

            try:
                self.currentSample.setIcons(icons_list[5],icons_list[6])
            except IndexError:
                pass

        elif propertyName == 'mnemonic':
            self.sampleChanger = self.getHardwareObject(newValue)
            if self.sampleChanger is not None:
                self.connect(self.sampleChanger, SampleChanger.STATUS_CHANGED_EVENT, self.sampleChangerStatusChanged)
                self.connect(self.sampleChanger, SampleChanger.STATE_CHANGED_EVENT, self.sampleChangerStateChanged)
                self.connect(self.sampleChanger, SampleChanger.INFO_CHANGED_EVENT, self.infoChanged)
                self.connect(self.sampleChanger, SampleChanger.SELECTION_CHANGED_EVENT, self.selectionChanged)
                #self.connect(self.sampleChanger, PYSIGNAL("sampleChangerCanLoad"), self.sampleChangerCanLoad)
                #self.connect(self.sampleChanger, PYSIGNAL("minidiffCanMove"), self.minidiffCanMove)
                #self.connect(self.sampleChanger, PYSIGNAL("sampleChangerInUse"), self.sampleChangerInUse)
                self.connect(self.sampleChanger, SampleChanger.LOADED_SAMPLE_CHANGED_EVENT, self.loadedSampleChanged)
                 
                #self.currentSample.hideHolderLength(self.sampleChanger.isMicrodiff())
                #self.status.hideOperationalControl(self.sampleChanger.isMicrodiff())
                self.sampleChangerStatusChanged(self.sampleChanger.getStatus())
                self.sampleChangerStateChanged(self.sampleChanger.getState())
                self.infoChanged()
                self.selectionChanged()
                #self.sampleChangerInUse(self.sampleChanger.sampleChangerInUse())
                #self.sampleChangerCanLoad(self.sampleChanger.sampleChangerCanLoad())
                #self.minidiffCanMove(self.sampleChanger.minidiffCanMove())
                self.loadedSampleChanged(self.sampleChanger.getLoadedSample())
                #self.basketTransferModeChanged(self.sampleChanger.getBasketTransferMode())
        elif propertyName == 'showSelectButton':
            self.scanBaskets.showSelectButton(newValue)
            for basket in self.baskets:
                basket.setUnselectable(newValue)
        elif propertyName == 'defaultHolderLength':
            self.currentSample.setHolderLength(newValue)
        elif propertyName == 'doubleClickLoads':
            self.doubleClickLoads.setChecked(False) #newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def status_msg_changed(self, msg, color):
        self.emit(PYSIGNAL("status_msg_changed"), (msg, color))

    def selectionChanged(self):
        sample = self.sampleChanger.getSelectedSample()
        basket = self.sampleChanger.getSelectedComponent()
        if sample is None:
            self.currentSample.setSelected(0)
        else:
            self.currentSample.setSelected(sample.getIndex()+1)
        if basket is None:
            self.currentBasket.setSelected(0)
        else:
            self.currentBasket.setSelected(basket.getIndex()+1)

    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.basketsSamplesSelectionDialog.reject()

    def basketTransferModeChanged(self, basket_transfer):
        self.switch_to_sample_transfer_button.setEnabled(basket_transfer)

    def switchToSampleTransferMode(self):
        self.sampleChanger.changeMode(SampleChangerMode.Normal, wait=False)

    def loadedSampleChanged(self,sample):
        if sample is None:
            # get current location in SC
            sample = self.sampleChanger.getSelectedSample()
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
 
        self.currentSample.setLoadedMatrixCode(barcode)
        self.currentSample.setLoadedLocation(location)
        self.currentSample.setLoaded(loaded)

        if loaded:
            self.emit(PYSIGNAL("sampleGotLoaded"),())


    def setCollecting(self,enabled_state):
        self.setEnabled(enabled_state)

    def resetSampleChanger(self):
        self.sampleChanger.reset()

    def resetBasketsSamplesInfo(self):
        self.sampleChanger.clearInfo()
 
    def setSession(self,session_id):
        pass

    def setExpertMode(self,state):
        self.inExpert=state
        if self.sampleChanger is not None:
            self.status.setExpertMode(state)

    def run(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)
        try:
            self.matrixCodesChanged(self.sampleChanger.getMatrixCodes())
        except:
            pass

        
    def sampleLoadSuccess(self):
        pass

    def sampleLoadFail(self):
        pass

    def sampleUnloadSuccess(self):
        pass

    def sampleUnloadFail(self,state):
        self.sampleChangerStateChanged(state)

    def sampleChangerStatusChanged(self,status):
        self.status.setStatusMsg(status)

    def sampleChangerStateChanged(self, state, previous_state=None):
        logging.getLogger().debug('SampleChangerBrick3: state changed (%s)' % state)
        self.status.setState(state)
        self.currentBasket.setState(state)
        self.currentSample.setState(state)
        for basket in self.baskets:
            basket.setState(state)
        #self.doubleClickLoads.setMyState(state)
        self.scanBaskets.setState(state)
        self.reset_baskets_samples_button.setEnabled(SC_STATE_GENERAL.get(state, False))

    def sampleChangerCanLoad(self,can_load):
        self.status.setSampleChangerLoadStatus(can_load)

    def sampleChangerInUse(self,in_use):
        self.status.setSampleChangerUseStatus(in_use)

    def minidiffCanMove(self,can_move):
        self.status.setMinidiffStatus(can_move)

    def sampleChangerToLoadingPosition(self):
        if not self.sampleChanger.sampleChangerToLoadingPosition():
            self.status.setSampleChangerLoadStatus(self.sampleChanger.sampleChangerCanLoad())

    def minidiffGetControl(self):
        if not self.sampleChanger.minidiffGetControl():
            self.status.setMinidiffStatus(self.sampleChanger.minidiffCanMove())

    def changeBasket(self,basket_number):
        address = SC3.Basket.getBasketAddress(basket_number)
        self.sampleChanger.select(address, wait=False)

    def changeSample(self,sample_number):
        basket_index = self.sampleChanger.getSelectedComponent().getIndex()
        basket_number = basket_index + 1
        address = SC3.Pin.getSampleAddress(basket_number, sample_number)
        self.sampleChanger.select(address, wait=False) 

    def loadThisSample(self,basket_index,vial_index):
        return
        if self.doubleClickLoads.isChecked():
            sample_loc=(basket_index,vial_index)
            holder_len=self.currentSample.getHolderLength()
            self.sampleChanger.load(holder_len,None,sample_loc,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)

    def loadSample(self,holder_len):
        self.sampleChanger.load(holder_len,None,None,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)

    def unloadSample(self,holder_len,matrix_code,location):
        if matrix_code:
            location=None
        self.sampleChanger.unload(holder_len,matrix_code,location,self.sampleUnloadSuccess,self.sampleUnloadFail,wait=False)

    def clearMatrices(self):
        for basket in self.baskets:
            basket.clearMatrices()
        self.emit(PYSIGNAL("scanBasketUpdate"),(None,))

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
            self.baskets[self.currentBasket.selected.value()-1].setChecked(True)
        self.sampleChanger.scan(self.sampleChanger.getSelectedComponent(), recursive=True, wait=False)

    def scanAllBaskets(self):
        baskets_to_scan = []
        for i, basket_checkbox in enumerate(self.baskets):
          baskets_to_scan.append(SC3.Basket.getBasketAddress(i+1) if basket_checkbox.isChecked() else None)
         
        self.sampleChanger.scan(filter(None, baskets_to_scan), recursive=True, wait=False)

    def infoChanged(self):
        baskets = self.sampleChanger.getComponents()
        
        presences = []
        for basket in baskets:
            presences.append([[VialView.VIAL_UNKNOWN]]*10 if basket.isPresent() else [[VialView.VIAL_NONE]]*10)
     
        for sample in self.sampleChanger.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            vial_index = sample.getIndex()   
            basket_code = sample.getContainer().getID()  
            if sample.isPresent():
              if matrix:
                presences[basket_index][vial_index]=[VialView.VIAL_ALREADY_LOADED, matrix] if sample.hasBeenLoaded() else [VialView.VIAL_BARCODE,matrix]
              else:
                presences[basket_index][vial_index]=[VialView.VIAL_NOBARCODE_LOADED, matrix] if sample.hasBeenLoaded() else [VialView.VIAL_NOBARCODE,matrix]
            else:     
               presences[basket_index][vial_index]=[VialView.VIAL_NONE, ""]
            if sample.isLoaded():
               presences[basket_index][vial_index]=[VialView.VIAL_AXIS,matrix]

        for i, basket in enumerate(self.baskets):
            presence=presences[i]
            basket.setMatrices(presence)
        
        #self.emit(PYSIGNAL("scanBasketUpdate"),(cleared_matrix_codes,))

    def selectBasketsSamples(self):
        retval=self.basketsSamplesSelectionDialog.exec_loop()

        if retval == QDialog.Accepted:
            self.sampleChanger.resetBasketsInformation()

            for basket, samples in self.basketsSamplesSelectionDialog.result.iteritems():
                for i in range(10):
                    input=[basket, i+1, 0, 0, 0]
                
                for sample in samples:
                    input[1]=sample
                    input[2]=1
                    self.sampleChanger.setBasketSampleInformation(input)

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

        for i in range(5):
            self.samplesBoxes.append(QHBox(samples_group, 'sample_group'))
            QLabel("Basket %s :" % str(i+1), self.samplesBoxes[-1])
            self.txtPresentSamples.append(QLineEdit(self.samplesBoxes[-1]))
            self.txtPresentSamples[-1].setText("1-10")
            self.samplesBoxes[-1].show()
        
        QObject.connect(self.txtPresentBaskets, SIGNAL("textChanged(const QString&)"), self.presentBasketsChanged)
        QObject.connect(self.cmdResetContents, SIGNAL("clicked()"), self.resetContents)
        QObject.connect(self.cmdOk, SIGNAL("clicked()"), self.setSampleChangerContents)
        QObject.connect(self.cmdCancel, SIGNAL("clicked()"), self.reject)

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
