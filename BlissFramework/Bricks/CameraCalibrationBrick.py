"""
Camera Calibration Brick

[Description]

This brick allows to calibrate the display of a frame grabber.
The different features are:
    - 2 clicks calibration procedure using 2 motors displacement defined in
      the interface
    - Display of the calibration in both axis for different zoom values
    - Saving of the calibration of both axis for different zoom values

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save calibration for both axis
                for each zoom positions

vertical motor - string - Motor used to calibrate vertical axis

horizontal motor - string - Motor used to calibrate horizontal axis

[Signals]

getView - {"drawing"} - emitted to get a reference on the image viewer object.
                        At returned of the emit function, the key "drawing"
                        exists and its value is the reference of the image
                        viewer or the key "drawing" does not exists which mean
                        that the image viewer object does not exists.

"ChangePixelCalibration" - (YCalib, ZCalib) - Emitted when pixel calibration
                                              change.

[Slots]

getCalibration - {"ycalib", "zcalib"} - Display the new pixel size calibration
                                        changed by another object

useExpertMode - get the expoert mode signal:
                  - Disables the brick in non-expert mode.

[Comments]


"""
import qt
import sys
import qttable

from BlissFramework.BaseComponents import BlissWidget
from Qub.Objects.QubDrawingManager import QubPointDrawingMgr
from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget

__category__ = "Camera"

#############################################################################
##########                                                         ##########
##########                         BRICK                           ##########
##########                                                         ##########
#############################################################################
class CameraCalibrationBrick(BlissWidget):
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        """
        variables
        """
        self.firstTime = True
        self.YCalib  = None
        self.ZCalib  = None
        self.calibration = 0
        self.drawing = None
        self.y1 = 0
        self.z1 = 0
        self.y2 = 0
        self.z2 = 0
        self.drawingMgr = None

        """
        property
        """
        self.addProperty("zoom", "string", "")
        self.addProperty("vertical motor", "string", "")
        self.addProperty("horizontal motor", "string", "")
        self.hwZoom = None
        self.hmot   = None
        self.vmot   = None

        """
        signals
        """
        self.defineSignal('getView',())
        self.defineSignal("ChangePixelCalibration", ())

        """
        slots
        """
        self.defineSlot('getCalibration',())
        self.defineSlot('useExpertMode',())

        self.buildInterface()

    def buildInterface(self):
        vlayout = qt.QVBoxLayout(self)

        title = qt.QLabel("<B>Pixel Size Calibration<B>", self)
        title.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Expanding,
                                           qt.QSizePolicy.Fixed))
        vlayout.addWidget(title)

        self.calibFrame = qt.QFrame(self)
        self.calibFrame.setFrameShape(qt.QFrame.Box)
        self.calibFrame.setFrameShadow(qt.QFrame.Sunken)
        vlayout.addWidget(self.calibFrame)

        vlayout1 = qt.QVBoxLayout(self.calibFrame)
        vlayout1.setMargin(10)

        self.table = qttable.QTable(0,3, self.calibFrame)
        self.table.setFocusPolicy(qt.QWidget.NoFocus)
        self.table.setSelectionMode(qttable.QTable.NoSelection)
        self.table.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Minimum,
                                                qt.QSizePolicy.Minimum))
        self.table.verticalHeader().hide()
        self.table.setLeftMargin(0)
        self.table.setReadOnly(True)

        header = self.table.horizontalHeader()
        header.setLabel(0, "Zoom")
        header.setLabel(1, "Y Size (nm)")
        header.setLabel(2, "Z Size (nm)")

        self.table.clearSelection(True)

        vlayout1.addWidget(self.table)

        vlayout1.addSpacing(10)
        f1 = qt.QFrame(self.calibFrame)
        f1.setFrameShape(qt.QFrame.HLine)
        f1.setFrameShadow(qt.QFrame.Sunken)
        vlayout1.addWidget(f1)
        vlayout1.addSpacing(10)

        self.saveButton = qt.QPushButton("Save Current Calibration",
                                         self.calibFrame)
        self.connect(self.saveButton, qt.SIGNAL("clicked()"),
                     self.saveCalibration)
        vlayout1.addWidget(self.saveButton)

        vlayout1.addSpacing(10)
        f1 = qt.QFrame(self.calibFrame)
        f1.setFrameShape(qt.QFrame.HLine)
        f1.setFrameShadow(qt.QFrame.Sunken)
        vlayout1.addWidget(f1)
        vlayout1.addSpacing(10)

        hlayout1 = qt.QHBoxLayout(vlayout1)
        self.relYLabel = qt.QLabel("Y Move:", self.calibFrame)
        hlayout1.addWidget(self.relYLabel)
        self.relYText = qt.QLineEdit("0.1", self.calibFrame)
        hlayout1.addWidget(self.relYText)

        hlayout2 = qt.QHBoxLayout(vlayout1)
        self.relZLabel = qt.QLabel("Z Move:", self.calibFrame)
        hlayout2.addWidget(self.relZLabel)
        self.relZText = qt.QLineEdit("0.1", self.calibFrame)
        hlayout2.addWidget(self.relZText)

        vlayout1.addSpacing(5)

        self.calibButton = qt.QPushButton("Start New Calibration",
                                          self.calibFrame)
        self.connect(self.calibButton, qt.SIGNAL("clicked()"),
                     self.calibrationAction)
        vlayout1.addWidget(self.calibButton)

        vlayout1.addStretch(1)

    def propertyChanged(self, prop, oldValue, newValue):
        if prop == "zoom":
            if self.hwZoom is not None:
                self.disconnect(self.hwZoom, qt.PYSIGNAL("positionReached"),
                                self.zoomChanged)
                self.disconnect(self.hwZoom, qt.PYSIGNAL("noPosition"),
                                self.zoomChanged)

            self.hwZoom = self.getHardwareObject(newValue)

            if self.hwZoom is not None:
                self.connect(self.hwZoom, qt.PYSIGNAL("positionReached"),
                             self.zoomChanged)
                self.connect(self.hwZoom, qt.PYSIGNAL("noPosition"),
                             self.zoomChanged)

        if prop == "vertical motor":
            self.vmot = self.getHardwareObject(newValue)
            mne = self.vmot.getMotorMnemonic()
            self.relZLabel.setText("Delta on \"%s\" "%mne)
            self.vmotUnit = self.vmot.getProperty("unit")
            if self.vmotUnit is None:
                self.vmotUnit = 1e-3

        if prop == "horizontal motor":
            self.hmot = self.getHardwareObject(newValue)
            mne = self.hmot.getMotorMnemonic()
            self.relYLabel.setText("Delta on \"%s\" "%mne)
            self.hmotUnit = self.hmot.getProperty("unit")
            if self.hmotUnit is  None:
                self.hmotUnit = 1e-3

        if not self.firstTime:
            self.initInterface()
            self.zoomChanged()

    def run(self):
        if self.firstTime:
            self.initInterface()
            self.zoomChanged()

            """
            get view
            """
            view = {}
            self.emit(qt.PYSIGNAL("getView"), (view,))
            try:
                self.drawing = view["drawing"]

                cvs = self.drawing.canvas()
                matrix = self.drawing.matrix()
                drawingobject = QubCanvasTarget(cvs)
                color = self.drawing.foregroundColor()

                self.drawingMgr = QubPointDrawingMgr(cvs, matrix)
                self.drawingMgr.setDrawingEvent(QubMoveNPressed1Point)
                self.drawingMgr.setAutoDisconnectEvent(True)
                self.drawingMgr.addDrawingObject(drawingobject)
                self.drawingMgr.setEndDrawCallBack(self.pointSelected)
                qt.QWidget.connect(self.drawing,
                                   qt.PYSIGNAL("ForegroundColorChanged"),
                                   self.setColor)

                self.drawing.addDrawingMgr(self.drawingMgr)
            except:
                print("No View")

        self.firstTime = False

    def setColor(self, color):
        if self.drawingMgr is not None:
            self.drawingMgr.setColor(color)

    def initInterface(self):
        if self.hwZoom is not None:
            pos = self.hwZoom.positionsIndex
            self.table.setNumRows(len(pos))
            for i in range(len(pos)):
                aux = self.hwZoom.getPositionKeyValue(pos[i], "resox")
                if aux is None:
                    aux = "1"
                resoy = float(aux)
                aux = self.hwZoom.getPositionKeyValue(pos[i], "resoy")
                if aux is None:
                    aux = "1"
                resoz = float(aux)
                self.table.setText(i, 0, pos[i])
                """
                resolution are displayed in nanometer and saved in merter
                """
                if resoy is not None:
                    self.table.setText(i, 1, str(int(resoy * 1e9)))
                else:
                    self.table.setText(i, 1, "Not Defined")
                if resoz is not None:
                    self.table.setText(i, 2, str(int(resoz * 1e9)))
                else:
                    self.table.setText(i, 2, "Not Defined")
            self.table.adjustColumn(0)
            self.table.adjustColumn(1)
            self.table.adjustColumn(2)

    def getZoomIndex(self, position):
        if self.hwZoom is not None:
            positions = self.hwZoom.positionsIndex
            for i in range(len(positions)):
                if position == positions[i]:
                    return(i)
            return(-1)

    def zoomChanged(self):
        if self.hwZoom is not None:
            currentPos = self.hwZoom.getPosition()
            self.currIdx = self.getZoomIndex(currentPos)
            if self.table.numSelections() != -1:
                self.table.clearSelection(True)
            if self.currIdx != -1:
                aux = self.hwZoom.getPositionKeyValue(currentPos, "resox")
                if aux is None:
                    aux = "1"
                resoy = float(aux)
                aux = self.hwZoom.getPositionKeyValue(currentPos, "resoy")
                if aux is None:
                    aux = "1"
                resoz = float(aux)
                self.YCalib = resoy
                self.ZCalib = resoz
                self.table.selectRow(self.currIdx)
                if resoy is not None:
                    self.table.setText(self.currIdx, 1, str(int(resoy * 1e9)))
                else:
                    self.table.setText(self.currIdx, 1,"Not Defined")
                if resoz is not None:
                    self.table.setText(self.currIdx, 2, str(int(resoz * 1e9)))
                else:
                    self.table.setText(self.currIdx, 2, "Not Defined")
            else:
                self.YCalib = None
                self.ZCalib = None
        else:
            self.YCalib = None
            self.ZCalib = None

        self.emit(qt.PYSIGNAL("ChangePixelCalibration"),
                  (self.YCalib, self.ZCalib))

    def saveCalibration(self):
        if self.hwZoom is not None:
            currentPos = self.hwZoom.getPosition()
            self.hwZoom.setPositionKeyValue(currentPos, "resox", str(self.YCalib))
            self.hwZoom.setPositionKeyValue(currentPos, "resoy", str(self.ZCalib))
        else:
            print("CameraCalibrationBrick--ARG--hwZoom is None")

    def calibrationAction(self):
        if self.calibration == 0:

            if self.drawingMgr is not None:
                self.calibration = 1
                self.calibButton.setText("Cancel Calibration")

                self.drawingMgr.startDrawing()

        elif self.calibration == 1:
            self.calibration = 0
            self.calibButton.setText("Start New Calibration")
            self.drawingMgr.stopDrawing()
            self.drawingMgr.hide()

        elif self.calibration == 2:
            self.disconnect(self.vmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.disconnect(self.hmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.hmot.stop()
            self.vmot.stop()
            self.calibration = 0
            self.calibButton.setText("Start New Calibration")
            self.drawingMgr.stopDrawing()
            self.drawingMgr.hide()


    def pointSelected(self, drawingMgr):
        point = drawingMgr.point()
        if self.calibration == 1:
            self.y1 = point[0]
            self.z1 = point[1]

            ymne = self.hmot.getMotorMnemonic()
            zmne = self.vmot.getMotorMnemonic()
            self.deltaY  = float(str(self.relYText.text()))
            self.deltaZ  = float(str(self.relZText.text()))

            self.calibration = 2
            self.calibButton.setText("STOP")
            self.motorArrived = 0

            self.connect(self.hmot, qt.PYSIGNAL("moveDone"), self.moveFinished)
            self.connect(self.vmot, qt.PYSIGNAL("moveDone"), self.moveFinished)

            self.hmot.moveRelative(self.deltaY)
            self.vmot.moveRelative(self.deltaZ)

        elif self.calibration == 3:
            self.y2 = point[0]
            self.z2 = point[1]

            self.calcCalib()

            self.table.setText(self.currIdx, 1, str(int(self.YCalib * 1e9)))
            self.table.setText(self.currIdx, 2, str(int(self.ZCalib * 1e9)))

            self.calibButton.setText("Start New Calibration")
            self.calibration = 0
            self.drawingMgr.hide()

    def moveFinished(self, ver, mne):
        if mne == self.hmot.getMotorMnemonic():
            self.disconnect(self.hmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.motorArrived = self.motorArrived + 1

        if mne == self.vmot.getMotorMnemonic():
            self.disconnect(self.vmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.motorArrived = self.motorArrived + 1

        if self.calibration == 2 and self.motorArrived == 2:
            self.calibration = 3
            self.calibButton.setText("Cancel Calibration")
            self.drawingMgr.startDrawing()

    def calcCalib(self):
        if (abs(self.y1 - self.y2) != 0) and \
           (abs(self.z1 - self.z2) != 0):
            self.YCalib = self.deltaY * self.hmotUnit / float(self.y1 - self.y2)
            self.ZCalib = self.deltaZ * self.vmotUnit / float(self.z1 - self.z2)
            self.emit(qt.PYSIGNAL("ChangePixelCalibration"),
                      (self.YCalib, self.ZCalib))

    """
    SLOTS
    """

    def getCalibration(self, calib):
        calib["ycalib"] = self.YCalib
        calib["zcalib"] = self.ZCalib


    def useExpertMode(self, value):
        if value:
            # print "Someone ask to enable CameraCalibrationBrick."
            self.setEnabled(True)
        else:
            # print "Someone ask to disable CameraCalibrationBrick."
            self.setEnabled(False)

