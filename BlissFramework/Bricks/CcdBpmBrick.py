"""
Ccd Beam Brick

[Description]

This brick displays information coming from the bpm server of a ccd camera.
This informations are polled.
It allows to define ROI's by hand or graphically if linked with the Camera
Brick

[Properties]

bpm - string - Camera Hardware object

[Signals]

getView - {"drawing"} - emitted to get a reference on the image viewer object.
                        At returned of the emit function, the key "drawing"
                        exists and its value is the reference of the image
                        viewer or the key "drawing" does not exists which mean
                        that the image viewer object does not exists. In this
                        case, the bpm value are still polled but ROI's cannot
                        be defined graphically
beamPositionChanged - {x,y} - emitted when a new beam position is read
[Slots]

[Comments]

"""
import qt
import sys
import qttable
import qtcanvas
import time

from BlissFramework.BaseComponents import BlissWidget

from Qub.Objects.QubDrawingManager import Qub2PointSurfaceDrawingMgr
from Qub.Objects.QubDrawingEvent import QubPressedNDrag2Point

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr
from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget
from Qub.Widget.QubActionSet import QubRulerAction

__category__ = "Camera"

#############################################################################
##########                                                         ##########
##########                         BRICK                           ##########
##########                                                         ##########
#############################################################################
class CcdBpmBrick(BlissWidget):
    colorState = {
        True: '#00ee00',
        False: '#ff5555',
        }
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        """
        variables
        """
        self.drawingMgrRect = None
        self.infoDict = None

        """
        property
        """
        self.addProperty("bpm", "string", "")
        self.hwo = None

        """
        Signal
        """
        self.defineSignal('getView',())
        self.defineSignal('beamPositionChanged',())

        """
        Slot
        """

        """
        widgets
        """
        self.buildInterface()

    def bprint(self, msg):
        print("CcdBpmBrick--%s"%msg)

    def buildInterface(self):
        vlayout = qt.QVBoxLayout(self)

        """
        title
        """
        title = qt.QLabel("<B>Ccd Bpm<B>", self)
        title.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Expanding,
                                           qt.QSizePolicy.Fixed))
        vlayout.addWidget(title)

        """
        brick frame
        """
        self.frame = qt.QFrame(self)
        self.frame.setFrameShape(qt.QFrame.Box)
        self.frame.setFrameShadow(qt.QFrame.Sunken)
        vlayout.addWidget(self.frame)
        vlay = qt.QVBoxLayout(self.frame)
        vlay.setMargin(10)

        """
        create tab widget
        """
        self.tabWidget = qt.QTabWidget(self.frame)
        vlay.addWidget(self.tabWidget)

        """
        create tab for display values
        """
        self.valuesTab = qt.QWidget(None)
        self.tabWidget.addTab(self.valuesTab, "Info")

        vlayout1 = qt.QVBoxLayout(self.valuesTab)
        vlayout1.setMargin(10)

        self.exposureLabel = QubValue(self.valuesTab, "Exposure (%)", False)
        titlesize = self.exposureLabel.titleSizeHint()
        self.exposureLabel.setText("1123.1234")
        valuesize = self.exposureLabel.valueSizeHint()
        self.exposureLabel.setText("")
        vlayout1.addWidget(self.exposureLabel)
        vlayout1.addSpacing(2)

        self.gainLabel = QubValue(self.valuesTab, "Gain (%)", False)
        vlayout1.addWidget(self.gainLabel)
        vlayout1.addSpacing(2)

        self.thresholdLabel = QubValue(self.valuesTab, "Threshold (%)", False)
        vlayout1.addWidget(self.thresholdLabel)
        vlayout1.addSpacing(10)

        self.centerxLabel = QubValue(self.valuesTab, "X center", False)
        vlayout1.addWidget(self.centerxLabel)
        vlayout1.addSpacing(2)

        self.centeryLabel = QubValue(self.valuesTab, "Y center", False)
        vlayout1.addWidget(self.centeryLabel)
        vlayout1.addSpacing(2)

        self.fwhmxLabel = QubValue(self.valuesTab, "X FWHM", False)
        vlayout1.addWidget(self.fwhmxLabel)
        vlayout1.addSpacing(2)

        self.fwhmyLabel = QubValue(self.valuesTab, "Y FWHM", False)
        vlayout1.addWidget(self.fwhmyLabel)
        vlayout1.addSpacing(2)

        self.intensityLabel = QubValue(self.valuesTab, "Intensity", False)
        vlayout1.addWidget(self.intensityLabel)
        vlayout1.addSpacing(2)

        self.maxpixLabel = QubValue(self.valuesTab, "Maximum", False)
        vlayout1.addWidget(self.maxpixLabel)
        vlayout1.addSpacing(10)

        self.widthLabel = QubValue(self.valuesTab, "Im. width", False)
        vlayout1.addWidget(self.widthLabel)
        vlayout1.addSpacing(2)

        self.heightLabel = QubValue(self.valuesTab, "Im. height", False)
        vlayout1.addWidget(self.heightLabel)
        vlayout1.addSpacing(2)

        self.startxLabel = QubValue(self.valuesTab, "ROI X start", False)
        vlayout1.addWidget(self.startxLabel)
        vlayout1.addSpacing(2)

        self.endxLabel = QubValue(self.valuesTab, "ROI X end", False)
        vlayout1.addWidget(self.endxLabel)
        vlayout1.addSpacing(2)

        self.startyLabel = QubValue(self.valuesTab, "ROI Y start", False)
        vlayout1.addWidget(self.startyLabel)
        vlayout1.addSpacing(2)

        self.endyLabel = QubValue(self.valuesTab, "ROI Y end", False)
        vlayout1.addWidget(self.endyLabel)
        vlayout1.addSpacing(20)

        """
        create tab for control
        """
        self.cameraTab = qt.QWidget(None)
        self.tabWidget.addTab(self.cameraTab, "Control")

        vlayout2 = qt.QVBoxLayout(self.cameraTab)
        vlayout2.setMargin(10)

        self.exposureText = QubValue(self.cameraTab, "Exposure (%)", True)
        self.connect(self.exposureText, qt.PYSIGNAL("returnPressed"),
                     self.setExposure)
        vlayout2.addWidget(self.exposureText)
        vlayout2.addSpacing(2)

        self.gainText = QubValue(self.cameraTab, "Gain (%)", True)
        self.connect(self.gainText, qt.PYSIGNAL("returnPressed"),
                     self.setGain)
        vlayout2.addWidget(self.gainText)
        vlayout2.addSpacing(2)

        self.thresholdText = QubValue(self.cameraTab, "Threshold (%)", True)
        self.connect(self.thresholdText, qt.PYSIGNAL("returnPressed"),
                     self.setThreshold)
        vlayout2.addWidget(self.thresholdText)
        vlayout2.addSpacing(20)

        self.liveControlToggle = qt.QPushButton("Live mode", self.cameraTab)
        self.liveControlToggle.setToggleButton(True)
        self.connect(self.liveControlToggle, qt.SIGNAL("toggled(bool)"),
                     self.setLive)
        vlayout2.addWidget(self.liveControlToggle)

        self.bpmControlToggle = qt.QPushButton("BPM on", self.cameraTab)
        self.bpmControlToggle.setToggleButton(True)
        self.connect(self.bpmControlToggle, qt.SIGNAL("toggled(bool)"),
                     self.setBpm)
        vlayout2.addWidget(self.bpmControlToggle)

        vlayout2.addStretch(1)

        """
        create Tab for ROI
        """
        self.roiTab = qt.QWidget(None)
        self.tabWidget.addTab(self.roiTab, "ROI")

        vlayout3 = qt.QVBoxLayout(self.roiTab)
        vlayout3.setMargin(10)

        """
        ROI toggle button
        """
        hlayout3 = qt.QHBoxLayout(vlayout3)

        self.roiButton = qt.QPushButton("Select on Image", self.roiTab)
        self.roiButton.setToggleButton(True)
        self.connect(self.roiButton, qt.SIGNAL("toggled(bool)"),
                     self.startROISelection)
        hlayout3.addWidget(self.roiButton)

        vlayout3.addSpacing(10)

        """
        ROI values
        """
        self.startxText = QubValue(self.roiTab, "X start", True)
        vlayout3.addWidget(self.startxText)
        vlayout3.addSpacing(2)

        self.endxText = QubValue(self.roiTab, "X end", True)
        vlayout3.addWidget(self.endxText)
        vlayout3.addSpacing(2)

        self.startyText = QubValue(self.roiTab, "Y start", True)
        vlayout3.addWidget(self.startyText)
        vlayout3.addSpacing(2)

        self.endyText = QubValue(self.roiTab, "Y end", True)
        vlayout3.addWidget(self.endyText)
        vlayout3.addSpacing(10)

        hlayout2 = qt.QHBoxLayout(vlayout3)

        self.resetButton = qt.QPushButton("Reset", self.roiTab)
        self.connect(self.resetButton, qt.SIGNAL("clicked()"),
                     self.resetROI)
        hlayout2.addWidget(self.resetButton)

        hlayout2.addStretch(1)

        self.sendButton = qt.QPushButton("Send", self.roiTab)
        self.connect(self.sendButton, qt.SIGNAL("clicked()"),
                     self.sendROI)
        hlayout2.addWidget(self.sendButton)


        vlayout3.addStretch(1)

        """
        resize
        """
        self.exposureText.setTitleMinimumSize(titlesize)
        self.gainText.setTitleMinimumSize(titlesize)
        self.thresholdText.setTitleMinimumSize(titlesize)

        self.exposureLabel.setTitleMinimumSize(titlesize)
        self.gainLabel.setTitleMinimumSize(titlesize)
        self.thresholdLabel.setTitleMinimumSize(titlesize)
        self.centerxLabel.setTitleMinimumSize(titlesize)
        self.centeryLabel.setTitleMinimumSize(titlesize)
        self.fwhmxLabel.setTitleMinimumSize(titlesize)
        self.fwhmyLabel.setTitleMinimumSize(titlesize)
        self.intensityLabel.setTitleMinimumSize(titlesize)
        self.maxpixLabel.setTitleMinimumSize(titlesize)
        self.widthLabel.setTitleMinimumSize(titlesize)
        self.heightLabel.setTitleMinimumSize(titlesize)
        self.startxLabel.setTitleMinimumSize(titlesize)
        self.endxLabel.setTitleMinimumSize(titlesize)
        self.startyLabel.setTitleMinimumSize(titlesize)
        self.endyLabel.setTitleMinimumSize(titlesize)

        self.startxText.setTitleMinimumSize(titlesize)
        self.endxText.setTitleMinimumSize(titlesize)
        self.startyText.setTitleMinimumSize(titlesize)
        self.endyText.setTitleMinimumSize(titlesize)


        self.exposureText.setValueMaximumSize(valuesize)
        self.gainText.setValueMaximumSize(valuesize)
        self.thresholdText.setValueMaximumSize(valuesize)

        self.exposureLabel.setValueMaximumSize(valuesize)
        self.gainLabel.setValueMaximumSize(valuesize)
        self.thresholdLabel.setValueMaximumSize(valuesize)
        self.centerxLabel.setValueMaximumSize(valuesize)
        self.centeryLabel.setValueMaximumSize(valuesize)
        self.fwhmxLabel.setValueMaximumSize(valuesize)
        self.fwhmyLabel.setValueMaximumSize(valuesize)
        self.intensityLabel.setValueMaximumSize(valuesize)
        self.maxpixLabel.setValueMaximumSize(valuesize)
        self.widthLabel.setValueMaximumSize(valuesize)
        self.heightLabel.setValueMaximumSize(valuesize)
        self.startxLabel.setValueMaximumSize(valuesize)
        self.endxLabel.setValueMaximumSize(valuesize)
        self.startyLabel.setValueMaximumSize(valuesize)
        self.endyLabel.setValueMaximumSize(valuesize)

        self.startxText.setValueMaximumSize(valuesize)
        self.endxText.setValueMaximumSize(valuesize)
        self.startyText.setValueMaximumSize(valuesize)
        self.endyText.setValueMaximumSize(valuesize)

    def propertyChanged(self, prop, oldValue, newValue):
        if prop == "bpm":
            if self.hwo is not None:
                self.disconnect(self.hwo, qt.PYSIGNAL('imageReceived'),
                                self.imageReceived)

            self.hwo = self.getHardwareObject(newValue)

            if self.hwo is not None:
                self.connect(self.hwo, qt.PYSIGNAL('imageReceived'),
                                self.imageReceived)
                self.imageReceived()

    def run(self):
        """
        get view
        """
        view = {}
        self.emit(qt.PYSIGNAL("getView"), (view,))
        self.drawing = view["drawing"]
        self.view = view["view"]

        """
        rectangle drawing initialization
        """
        cvs = self.drawing.canvas()
        matrix = self.drawing.matrix()
        drawingobjectRect = qtcanvas.QCanvasRectangle(cvs)
        color = self.drawing.foregroundColor()

        self.drawingMgrRect = Qub2PointSurfaceDrawingMgr(cvs, matrix)
        self.drawingMgrRect.setDrawingEvent(QubPressedNDrag2Point)
        self.drawingMgrRect.addDrawingObject(drawingobjectRect)
        self.drawingMgrRect.setEndDrawCallBack(self.rectangleSelected)
        self.drawingMgrRect.setColor(color)

        qt.QWidget.connect(self.drawing, qt.PYSIGNAL("ForegroundColorChanged"),
                           self.setColor)

        self.drawing.addDrawingMgr(self.drawingMgrRect)

        """
        values initialization
        """
        self.imageReceived()
        if self.infoDict is not None:
            #change the background color
            qcolor = qt.QColor(CcdBpmBrick.colorState[self.infoDict["live"]])
            self.liveControlToggle.setPaletteBackgroundColor(qcolor)
            #change the background color
            qcolor = qt.QColor(CcdBpmBrick.colorState[self.infoDict["bpmon"]])
            self.bpmControlToggle.setPaletteBackgroundColor(qcolor)

            self.exposureText.setText("%g"%(self.infoDict["time"],))
            self.gainText.setText("%d"%(self.infoDict["gain"],))
            self.thresholdText.setText("%g"%(self.infoDict["threshold"],))

            self.startxText.setText("%d"%(self.infoDict["startx"],))
            self.endxText.setText("%d"%(self.infoDict["endx"],))
            self.startyText.setText("%d"%(self.infoDict["starty"],))
            self.endyText.setText("%d"%(self.infoDict["endy"],))

            #self.bprint("infoDict--startx=%d endx=%d starty=%d endy=%d"%(self.infoDict["startx"],
            #        self.infoDict["endx"],
            #                                                           self.infoDict["starty"],
            #                                                           self.infoDict["endy"]))

    def setColor(self, color):
        if self.drawingMgrRect is not None:
            self.drawingMgrRect.setColor(color)

    def startROISelection(self, roiOn):
        if roiOn:
            if self.drawingMgrRect is not None:
                self.drawingMgrRect.show()
                self.drawingMgrRect.startDrawing()
        else:
            if self.drawingMgrRect is not None:
                self.drawingMgrRect.hide()
                self.drawingMgrRect.stopDrawing()

    def rectangleSelected(self, drawingMgr):
        if self.hwo is not None:
            self.infoDict = self.hwo.getBpmValues()
            startx = self.infoDict["startx"]
            starty = self.infoDict["starty"]
        else:
            self.infoDict = None
            startx = 0
            starty = 0

        # self.bprint( "startx=%d , starty=%d"%(startx,starty))

        rect = drawingMgr.rect()
        (x, y, w, h) = rect.rect()

        self.startxText.setText(str(int(startx + x)))
        self.endxText.setText(str(int(startx + x + w - 1)))
        self.startyText.setText(str(int(starty + y)))
        self.endyText.setText(str(int(starty + y+h-1)))

    def imageReceived(self):
        if self.hwo is not None:
            self.infoDict = self.hwo.getBpmValues()

            self.imageWidth  = int(self.infoDict["width"])
            self.imageHeight = int(self.infoDict["height"])

            if self.liveControlToggle.isOn() != self.infoDict["live"]:
                self.liveControlToggle.setOn(self.infoDict["live"])

            if self.bpmControlToggle.isOn() != self.infoDict["bpmon"]:
                self.bpmControlToggle.setOn(self.infoDict["bpmon"])

            self.exposureLabel.setText("%g"%(self.infoDict["time"],))
            self.gainLabel.setText("%d"%(self.infoDict["gain"],))
            self.thresholdLabel.setText("%g"%(self.infoDict["threshold"],))

            if self.infoDict["centerx"] is not None:
                self.centerxLabel.setText("%d"%(self.infoDict["centerx"],))
            if self.infoDict["centery"] is not None:
                self.centeryLabel.setText("%d"%(self.infoDict["centery"],))
            if self.infoDict["fwhmx"] is not None:
                self.fwhmxLabel.setText("%d"%(self.infoDict["fwhmx"],))
            if self.infoDict["fwhmy"] is not None:
                self.fwhmyLabel.setText("%d"%(self.infoDict["fwhmy"],))
            if self.infoDict["intensity"] is not None:
                self.intensityLabel.setText("%d"%(self.infoDict["intensity"],))
            if self.infoDict["maxpix"] is not None:
                self.maxpixLabel.setText("%d"%(self.infoDict["maxpix"],))
            if self.infoDict["width"] is not None:
                self.widthLabel.setText("%d"%(self.infoDict["width"],))
            if self.infoDict["height"] is not None:
                self.heightLabel.setText("%d"%(self.infoDict["height"],))
            if self.infoDict["startx"] is not None:
                self.startxLabel.setText("%d"%(self.infoDict["startx"],))
            if self.infoDict["endx"] is not None:
                self.endxLabel.setText("%d"%(self.infoDict["endx"],))
            if self.infoDict["starty"] is not None:
                self.startyLabel.setText("%d"%(self.infoDict["starty"],))
            if self.infoDict["endy"] is not None:
                self.endyLabel.setText("%d"%(self.infoDict["endy"],))

            self.horizontal_flip = self.infoDict["fliph"]
            self.vertical_flip   = self.infoDict["flipv"]

            self.emit(qt.PYSIGNAL("beamPositionChanged"), (self.infoDict["centerx"],self.infoDict["centery"]))
        else:
            self.infoDict = None

    def resetROI(self):
        #self.bprint("resetROI -- width=%d  height=%d"%(self.imageWidth, self.imageHeight))
        self.startxText.setText("0")
        self.endxText.setText(str(self.imageWidth - 1))
        self.startyText.setText("0")
        self.endyText.setText(str(self.imageHeight - 1))
        self.sendROI()

    def sendROI(self):
        fromx = int(self.startxText.text())
        tox   = int(self.endxText.text())
        fromy = int(self.startyText.text())
        toy   = int(self.endyText.text())

        #self.bprint("SendROI (fromx=%d tox=%d fromy=%d toy=%d)"%(fromx,tox,fromy,toy))

        if self.hwo is not None:
            if self.horizontal_flip:
                fromx = (self.imageWidth-1) - fromx
                tox   = (self.imageWidth-1) - tox
            if self.vertical_flip:
                fromy = (self.imageHeight-1) - fromy
                toy   = (self.imageHeight-1) - toy
            self.hwo.setROI(fromx, tox, fromy, toy)

        else:
            self.bprint("self.hwo == None")

    def setExposure(self):
        exposure = float(str(self.exposureText.text()))

        if self.hwo is not None:
            self.hwo.setExposure(exposure)

    def setGain(self):
        gain = int(str(self.gainText.text()))

        if self.hwo is not None:
            self.hwo.setGain(gain)

    def setThreshold(self):
        threshold = int(str(self.thresholdText.text()))

        if self.hwo is not None:
            self.hwo.setThreshold(threshold)

    def setLive(self, liveOn):
        if self.hwo is not None:
            self.hwo.setLive(liveOn)
            #change the background color
            qcolor = qt.QColor(CcdBpmBrick.colorState[liveOn])
            self.liveControlToggle.setPaletteBackgroundColor(qcolor)

    def setBpm(self, bpmOn):
        if self.hwo is not None:
            self.hwo.setBpm(bpmOn)
            #change the background color
            qcolor = qt.QColor(CcdBpmBrick.colorState[bpmOn])
            self.bpmControlToggle.setPaletteBackgroundColor(qcolor)


class QubValue(qt.QWidget):

    (Horizontal, Vertical) = (0, 1)

    def __init__(self, parent, title, editable=True, orientation=Horizontal):
        qt.QWidget.__init__(self, parent)

        self.title = title
        self.orientation = orientation
        self.editable = editable

        if self.orientation == QubValue.Horizontal:
            self.layout = qt.QHBoxLayout(self)
        else:
            self.layout = qt.QVBoxLayout(self)

        self.titleWidget = qt.QLabel(title, self)
        self.layout.addWidget(self.titleWidget)

        self.layout.addSpacing(5)

        if self.editable:
            self.valueWidget = qt.QLineEdit(self)
            self.connect(self.valueWidget, qt.SIGNAL("returnPressed()"),
                         self.__returnPressed)
        else:
            self.valueWidget = qt.QLabel(self)
            self.valueWidget.setFrameShape(qt.QFrame.Box)
            self.valueWidget.setFrameShadow(qt.QFrame.Plain)
        self.layout.addWidget(self.valueWidget)

    def __returnPressed(self):
        self.emit(qt.PYSIGNAL("returnPressed"),())

    def setText(self, text):
        self.valueWidget.setText(text)

    def setTitle(self, text):
        self.titleWidget.setText(text)

    def setValueMaximumSize(self, size):
        self.valueWidget.setMaximumSize(size)

    def setTitleMaximumSize(self, size):
        self.titleWidget.setMaximumSize(size)

    def setValueMinimumSize(self, size):
        self.valueWidget.setMinimumSize(size)

    def setTitleMinimumSize(self, size):
        self.titleWidget.setMinimumSize(size)

    def text(self):
        return self.valueWidget.text()

    def valueSizeHint(self):
        return self.valueWidget.sizeHint()

    def titleSizeHint(self):
        return self.titleWidget.sizeHint()

