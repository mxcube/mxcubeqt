import logging
import math
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *

__category__ = "mxCuBE"
__author__ = "Matias Guijarro"
__version__ = 1.0


SC_STATE_COLOR = { "FAULT": "red",
                   "STANDBY": "green",
                   "MOVING": "yellow",
                   "ALARM": "purple",
                   "DISABLE": "grey",
                   "RUNNING": "yellow",
                   "UNKNOWN": "grey" }


class HorizontalSpacer(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)


class SampleBasketView(QWidget):
    def __init__(self, parent, circles_num, label="", current=-1):
        QWidget.__init__(self, parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.circles_num = circles_num
        self.radius = 75
        self.label = label
        self.current = current
        #self.__circles = []
        self.alreadyLoaded = []
        self.start_angle = 0


    def minimumSizeHint(self):
        return QSize(200, 200)


    def setLabel(self, label):
        self.label = label
        self.update()


    def setAlreadyLoaded(self, i, loaded=True):
        if loaded:
            if not i in self.alreadyLoaded:
                self.alreadyLoaded.append(i)
        else:
            try:
                idx = self.alreadyLoaded.index(i)
            except ValueError:
                pass
            else:
                del self.alreadyLoaded[idx]
        self.update()


    def setCurrent(self, current):
        self.current = current
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(Qt.NoBrush)

        D = 2*self.radius
        X = self.width() / 2
        Y = self.height() / 2
        th = self.fontMetrics().height()

        painter.drawEllipse(X - self.radius, Y - self.radius, D, D)

        painter.drawText(QRect(X-self.radius, Y-(th/2), 2*self.radius, th), Qt.AlignCenter, str(self.label))

        r = (D * math.pi)/(2.5*self.circles_num)
        a = (2.3333*r)/self.radius

        angle = self.start_angle
        for i in range(self.circles_num):
            painter.setPen(QPen(Qt.black, 1))
            if (i+1) in self.alreadyLoaded:
                painter.setBrush(QBrush(Qt.darkBlue))
            else:
                painter.setBrush(QBrush(Qt.white))

            angle += a
            x = X + self.radius*math.cos(angle) - r
            y = Y - self.radius*math.sin(angle) - r

            #self.__circles.append((x, y, r))

            painter.drawEllipse(x, y, 2*r, 2*r)

            brushColor = painter.brush().color()
            luminance = 0.3*brushColor.red() + 0.59*brushColor.green() + 0.11*brushColor.blue()
            if luminance < 127:
                painter.setPen(QPen(Qt.white, 1))

            painter.drawText(QRect(x, y - (th / 2) + r, 2*r, th), Qt.AlignCenter, str(i+1))

            if self.current == (i+1):
                painter.setPen(QPen(Qt.red, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x-0.1*r, y-0.1*r, 2*1.1*r, 2*1.1*r)


class SampleBasketSelectionWidget(QVBox):
    def __init__(self, parent, title = "", name = "", iconName = "", min = 0, max = 0):
        QVBox.__init__(self, parent)

        self.currentItem = 0 #not initialized
	self.currentMatrixCode = None
        self.name = name
        self.min = min
        self.max = max
 
        self.setMargin(5)
        self.setSpacing(5)

        titleBox = QHBox(self)
        HorizontalSpacer(titleBox)
        lblItemIcon = QLabel(titleBox)
        lblTitle = QLabel(title, titleBox)
        HorizontalSpacer(titleBox)
        titleBox.setSpacing(5)
        lblItemIcon.setPixmap(Icons.load(iconName))
        self.lblCurrentItem = QLabel(self)
        lblItemIcon.setAlignment(Qt.AlignHCenter)
        self.lblCurrentItem.setAlignment(Qt.AlignHCenter)
        cmdBox = QHBox(self)
        self.cmdPrevious = QPushButton("<", cmdBox)
        self.cmdChange = QPushButton("Change", cmdBox)
        self.cmdNext = QPushButton(">", cmdBox)

        QObject.connect(self.cmdChange, SIGNAL("clicked()"), self.cmdChangeClicked)
        QObject.connect(self.cmdPrevious, SIGNAL("clicked()"), self.cmdPreviousClicked)
        QObject.connect(self.cmdNext, SIGNAL("clicked()"), self.cmdNextClicked)


    def setItem(self, item):
        self.currentItem = item
        self.lblCurrentItem.setText("<b><h2>current: %s<br>matrix id: %s</h2></b>" % (self.currentItem or "?", self.currentMatrixCode or "?"))


    def setMatrixCode(self, matrixCode):
        self.currentMatrixCode = matrixCode
        self.lblCurrentItem.setText("<b><h2>current: %s<br>matrix id: %s</h2></b>" % (self.currentItem or "?", self.currentMatrixCode or "?"))


    def cmdChangeClicked(self):
        if self.currentItem == 0:
            return

        newItem, ok = QInputDialog.getInteger("New %s :" % self.name, "Change sample changer %s" % self.name, self.currentItem, self.min, self.max, 1)

        if ok:
            self.emit(PYSIGNAL("changeSelectedItem"), (newItem, ))


    def cmdPreviousClicked(self):
        newItem = self.currentItem - 1

        if newItem < self.min:
            return
        else:
            self.emit(PYSIGNAL("changeSelectedItem"), (newItem, ))


    def cmdNextClicked(self):
        newItem = self.currentItem + 1

        if newItem > self.max:
            return
        else:
            self.emit(PYSIGNAL("changeSelectedItem"), (newItem, ))


class SampleSelectionWidget(SampleBasketSelectionWidget):
    def __init__(self, parent):
        SampleBasketSelectionWidget.__init__(self, parent, title="Selected Sample", name="sample", iconName="vial", min=1, max=10)


class BasketSelectionWidget(SampleBasketSelectionWidget):
    def __init__(self, parent):
        SampleBasketSelectionWidget.__init__(self, parent, title="Selected Basket", name="basket", iconName="basket", min=1, max=5)

        self.cmdScanBasket = QPushButton("Scan basket for data matrix", self)

        QObject.connect(self.cmdScanBasket, SIGNAL("clicked()"), self.scanBasketClicked)


    def scanBasketClicked(self):
        self.emit(PYSIGNAL("scanBasket"), ())

    
class LoadSampleCmdWidget(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args)

        self.holderLenBox = QHBox(self)
        self.holderLenBox.setMargin(5)
        self.holderLenBox.setSpacing(5)
        holderLenIcon = QLabel(self.holderLenBox)
        holderLenIcon.setPixmap(Icons.load("holderlength"))
        QLabel("Holder length (mm) ", self.holderLenBox)
        self.spnHolderLength = QSpinBox(16, 27, 1, self.holderLenBox) 
        self.cmdLoadSample = QPushButton("", self)

        QObject.connect(self.cmdLoadSample, SIGNAL("clicked()"), self.cmdLoadSampleClicked)

        QVBoxLayout(self)
        self.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))
        self.layout().addWidget(self.holderLenBox)
        self.layout().addWidget(self.cmdLoadSample)


    def setHolderLength(self, length):
        self.spnHolderLength.setValue(length)


    def getHolderLength(self):
        return self.spnHolderLength.value() 


    def cmdLoadSampleClicked(self):
        if not self.holderLenBox.isVisible():
            holderLength = None
        else:
            holderLength = self.getHolderLength()
            
        if str(self.cmdLoadSample.text()) == "Load sample":
            self.emit(PYSIGNAL("loadSample"), (holderLength, ))
        else:
            self.emit(PYSIGNAL("unloadSample"), (holderLength, ))


    def hideHolderLength(self, hide):
        if hide:
          self.holderLenBox.hide()
        else:
          self.holderLenBox.show()


    def setLoadMode(self):
        self.spnHolderLength.setEnabled(True)
        self.cmdLoadSample.setText("Load sample")


    def setUnloadMode(self):
        self.spnHolderLength.setEnabled(False)
        self.cmdLoadSample.setText("Unload sample")


class SampleChangerBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("microdiff", "boolean", False)
        self.addProperty("mnemonic", "string", "")
        self.addProperty("defaultHolderLength", "integer", 22)

        #self.defineSignal("sampleLoaded", ())

        self.sampleChanger = None
        self.loading = False

        # GUI
        self.statusBox = QVGroupBox("Status", self)
        self.lblStatus = QLabel("", self.statusBox)
        abortResetBox = QHBox(self.statusBox)
        self.cmdReset = QToolButton(abortResetBox)
        sampleBox = QVBox(self)
        self.lblSampleLoadingState = QLabel(sampleBox)
        self.cmdBox = QGrid(3, sampleBox)
        self.basketSelectionWidget = BasketSelectionWidget(self.cmdBox)
        HorizontalSpacer(self.cmdBox)
        self.sampleSelectionWidget = SampleSelectionWidget(self.cmdBox)
        self.basketView = SampleBasketView(self.cmdBox, 5)
        self.loadSampleCmdWidget = LoadSampleCmdWidget(self.cmdBox)   
        self.sampleView = SampleBasketView(self.cmdBox, 10)

        self.statusBox.setInsideMargin(5)
        self.statusBox.setInsideSpacing(10)
        self.statusBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmdReset.setIconSet(QIconSet(Icons.load("reload")))
        self.cmdReset.setTextLabel("Reset")
        self.cmdReset.setUsesTextLabel(True)
        self.lblStatus.setAlignment(Qt.AlignHCenter)
        sampleBox.setMargin(5)
        sampleBox.setSpacing(5)
        self.lblSampleLoadingState.setAlignment(Qt.AlignHCenter)
        
        # final layout
        """
        QGridLayout(self.cmdBox, 3, 3, 5, 5)
        self.cmdBox.layout().addWidget(self.basketSelectionWidget, 0, 0)
        self.cmdBox.layout().addWidget(self.basketView, 1, 0)
        self.cmdBox.layout().addWidget(self.loadSampleCmdWidget, 2, 1, Qt.AlignBottom)
        self.cmdBox.layout().addWidget(hspacer, 0, 1)
        self.cmdBox.layout().addWidget(self.sampleSelectionWidget, 0, 2)
        self.cmdBox.layout().addWidget(self.sampleView, 1, 2)
        """

        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(self.statusBox)
        self.layout().addWidget(sampleBox)
        self.layout().addItem(QSpacerItem(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding))      

        QObject.connect(self.cmdReset, SIGNAL("clicked()"), self.resetSampleChanger)
        QObject.connect(self.basketSelectionWidget, PYSIGNAL("changeSelectedItem"), self.changeBasketClicked)
        QObject.connect(self.sampleSelectionWidget, PYSIGNAL("changeSelectedItem"), self.changeSampleClicked)
        QObject.connect(self.basketSelectionWidget, PYSIGNAL("scanBasket"), self.scanBasket)
        QObject.connect(self.loadSampleCmdWidget, PYSIGNAL("loadSample"), self.loadSample)
        QObject.connect(self.loadSampleCmdWidget, PYSIGNAL("unloadSample"), self.unloadSample)


    def propertyChanged(self, property, oldValue, newValue):
        if property == 'defaultHolderLength':
            self.loadSampleCmdWidget.setHolderLength(newValue)
        elif property == 'microdiff':
            self.loadSampleCmdWidget.hideHolderLength(newValue)
        elif property == 'mnemonic':
            if self.sampleChanger is not None:
                self.disconnect(self.sampleChanger, PYSIGNAL("sampleIsLoaded"), self.sampleLoadStateChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("statusChanged"), self.sampleChangerStatusChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("stateChanged"), self.sampleChangerStateChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("basketChanged"), self.selectedBasketChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("sampleChanged"), self.selectedSampleChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("selectedBasketDataMatrixChanged"), self.selectedBasketDataMatrixChanged)
                self.disconnect(self.sampleChanger, PYSIGNAL("selectedSampleDataMatrixChanged"), self.selectedSampleDataMatrixChanged)

            self.sampleChanger = self.getHardwareObject(newValue)

            if self.sampleChanger is not None:
                self.connect(self.sampleChanger, PYSIGNAL("sampleIsLoaded"), self.sampleLoadStateChanged)
                self.connect(self.sampleChanger, PYSIGNAL("statusChanged"), self.sampleChangerStatusChanged)
                self.connect(self.sampleChanger, PYSIGNAL("stateChanged"), self.sampleChangerStateChanged)
                self.connect(self.sampleChanger, PYSIGNAL("basketChanged"), self.selectedBasketChanged)
                self.connect(self.sampleChanger, PYSIGNAL("sampleChanged"), self.selectedSampleChanged)
                self.connect(self.sampleChanger, PYSIGNAL("selectedBasketDataMatrixChanged"), self.selectedBasketDataMatrixChanged)
                self.connect(self.sampleChanger, PYSIGNAL("selectedSampleDataMatrixChanged"), self.selectedSampleDataMatrixChanged)
            else:
                self.sampleChangerStateChanged("UNKNOWN")
                self.sampleChangerStatusChanged("?")
		self.lblSampleLoadingState.setText("<b><h1>?</h1></b>")
    

    def resetSampleChanger(self):
        self.sampleChanger.reset()


    def abortSampleChangerOperation(self):
        self.sampleChanger.abort()


    def sampleLoadStateChanged(self, loaded):
        self.loadingDone = loaded
            
        if loaded:
            self.lblSampleLoadingState.setText("<nobr><b><h1>Sample is loaded</h1></b></nobr>")

            self.loadSampleCmdWidget.setUnloadMode()
        else:
            self.lblSampleLoadingState.setText("<nobr><b><h1>No sample on axis</h1></b></nobr>")

            self.loadSampleCmdWidget.setLoadMode()


    def sampleChangerStatusChanged(self, status):
        status = status.replace("#", "")
        self.lblStatus.setText("<b><h1>%s</h1></b>" % status)


    def sampleLoadSuccess(self,already_loaded):
        self.cmdBox.setEnabled(True)


    def sampleLoadFail(self,state):
        self.cmdBox.setEnabled(True)


    def sampleUnloadSuccess(self):
        self.cmdBox.setEnabled(True)


    def sampleUnloadFail(self,state):
        self.cmdBox.setEnabled(True)


    def loadSample(self, holderLength):
        self.loading = True

        self.cmdBox.setEnabled(False)

        """
        if holderLength is not None:
            sc_holderLength = self.sampleChanger.getSCHolderLength()

            if holderLength != sc_holderLength:
                reply = QMessageBox.warning(self, "Holder length question", "Holder length in Sample Changer is currently set to %d mm, new holder length will be : %d mm. Are you sure to continue ?" % (sc_holderLength, holderLength), QMessageBox.Yes, QMessageBox.Cancel)

                if reply != QMessageBox.Yes:
                    return
        """

        self.sampleChanger.loadSample(holderLength,None,None,self.sampleLoadSuccess,self.sampleLoadFail)


    def unloadSample(self, holderLength):
        self.loading = False

        self.cmdBox.setEnabled(False)

        self.sampleChanger.unloadSample(holderLength,None,None,self.sampleUnloadSuccess,self.sampleUnloadFail)


    def sampleChangerStateChanged(self, state):
        s = SC_STATE_COLOR.get(state, "UNKNOWN")
        self.lblStatus.setPaletteBackgroundColor(QColor(s))
        self.statusBox.setTitle("Status - %s" % state)

        """
        if state == "STANDBY":
            #print "standby state, enabling cmdBox"
            if self.loading and self.loadingDone:
                self.emit(PYSIGNAL("sampleLoaded"), ())

            self.cmdBox.setEnabled(True)
        elif state == "ALARM":
            #print "alarm state, enabling cmdBox"
            self.cmdBox.setEnabled(True) 
        else:
            #print state, "disabling cmdBox"
            self.cmdBox.setEnabled(False)
        """


    def changeBasketClicked(self, basket):
        self.sampleChanger.changeSelectedBasket(basket)


    def changeSampleClicked(self, sample):
        self.sampleChanger.changeSelectedSample(sample)


    def selectedBasketChanged(self, basket):
        self.basketSelectionWidget.setItem(basket)
        self.basketView.setCurrent(basket)
        self.sampleView.setLabel("%d" % basket)


    def selectedSampleChanged(self, sample):
        self.sampleSelectionWidget.setItem(sample)
        self.sampleView.setCurrent(sample)


    def selectedBasketDataMatrixChanged(self, matrixCode):
        self.basketSelectionWidget.setMatrixCode(matrixCode)


    def selectedSampleDataMatrixChanged(self, matrixCode):
        self.sampleSelectionWidget.setMatrixCode(matrixCode)


    def scanBasket(self):
        self.sampleChanger.scanCurrentBasket()
