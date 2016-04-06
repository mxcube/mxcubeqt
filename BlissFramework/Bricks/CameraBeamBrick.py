"""
Camera Beam Brick

[Description]

This brick displays and save for different zoom value a beam position.

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save beam position for each of them

[Signals]

ChangeBeamPosition - (xpos,ypos) - emitted when beam position change for a
                                   given zoom value.
                                   The client must get the zoom hardware
                                   object to know the current zoom position.

[Slots]

getBeamPosition - position["ybeam"] - When a client want to know the current
                  position["zbeam"]   beam position, it can connect a signal
                                      to this slot. At return of its emit call
                                      the dictionnary passed as argument will
                                      be filled with the current beam position

beamPositionChanged - ybeam, zbeam - slot which should be connected to all
                                     client able to change beam position.
                                     Display numerically and save the new
                                     beam positions.

setBrickEnabled - isEnabled - slot to call to disable the brick (expert mode for example).

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
class CameraBeamBrick(BlissWidget):
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        """
        variables
        """
        self.YBeam  = None
        self.ZBeam  = None

        """
        property
        """
        self.addProperty("zoom", "string", "")
        self.hwZoom = None

        """
        signals
        """
        self.defineSignal("ChangeBeamPosition", ())

        """
        slots
        """
        self.defineSlot("getBeamPosition", ())
        self.defineSlot("beamPositionChanged", ())
        self.defineSlot("setBrickEnabled", ())

        self.buildInterface()

    def buildInterface(self):
        vlayout = qt.QVBoxLayout(self)

        title = qt.QLabel("<B>Beam Position<B>", self)
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
        header.setLabel(1, "Y Beam (pix.)")
        header.setLabel(2, "Z Beam (pix.)")

        self.table.clearSelection(True)

        vlayout1.addWidget(self.table)

        vlayout1.addSpacing(10)
        f1 = qt.QFrame(self.calibFrame)
        f1.setFrameShape(qt.QFrame.HLine)
        f1.setFrameShadow(qt.QFrame.Sunken)
        vlayout1.addWidget(f1)
        vlayout1.addSpacing(10)

        self.saveButton = qt.QPushButton("Save Current Beam Pos.",
                                         self.calibFrame)
        self.connect(self.saveButton, qt.SIGNAL("clicked()"),
                     self.saveCalibration)
        vlayout1.addWidget(self.saveButton)

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

                self.initInterface()
                self.zoomChanged()

    def run(self):
        self.zoomChanged()

    def initInterface(self):
        if self.hwZoom is not None:
            pos = self.hwZoom.positionsIndex
            self.table.setNumRows(len(pos))
            for i in range(len(pos)):
                aux = self.hwZoom.getPositionKeyValue(pos[i], "beamx")
                if aux is None:
                    aux = "0"
                beamy = float(aux)
                aux = self.hwZoom.getPositionKeyValue(pos[i], "beamy")
                if aux is None:
                    aux = "0"
                beamz = float(aux)
                self.table.setText(i, 0, pos[i])
                if beamy is not None:
                    self.table.setText(i, 1, str(beamy))
                else:
                    self.table.setText(i, 1, "Not Defined")
                if beamz is not None:
                    self.table.setText(i, 2, str(beamz))
                else:
                    self.table.setText(i, 2, "Not Defined")
            self.table.adjustColumn(0)
            self.table.adjustColumn(1)
            self.table.adjustColumn(2)

    def getZoomIndex(self, position):
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
                aux = self.hwZoom.getPositionKeyValue(currentPos,"beamx")
                if aux is None:
                    aux = "0"
                beamy = float(aux)
                aux = self.hwZoom.getPositionKeyValue(currentPos,"beamy")
                if aux is None:
                    aux = "0"
                beamz = float(aux)
                self.YBeam = beamy
                self.ZBeam = beamz
                self.table.selectRow(self.currIdx)
                if beamy is not None:
                    self.table.setText(self.currIdx, 1, str(beamy))
                else:
                    self.table.setText(self.currIdx, 1, "Not Defined")
                if beamz is not None:
                    self.table.setText(self.currIdx, 2, str(beamz))
                else:
                    self.table.setText(self.currIdx, 2, "Not Defined")
            else:
                # self.YBeam = None
                # self.ZBeam = None
                print("CameraBeamBrick.py--zoomChanged--zerouillage")
                self.YBeam = 0
                self.ZBeam = 0
        else:
            # self.YBeam = None
            # self.ZBeam = None
            print("CameraBeamBrick.py--zoomChanged--zerouying")
            self.YBeam = 0
            self.ZBeam = 0

        self.emit(qt.PYSIGNAL("ChangeBeamPosition"),
                      (self.YBeam, self.ZBeam))

    def saveCalibration(self):
        currentPos = self.hwZoom.getPosition()
        self.hwZoom.setPositionKeyValue(currentPos, "beamx", str(self.YBeam))
        self.hwZoom.setPositionKeyValue(currentPos, "beamy", str(self.ZBeam))

    """
    SLOTS
    """
    def getBeamPosition(self, position):
        position["ybeam"] = self.YBeam
        position["zbeam"] = self.ZBeam

    def beamPositionChanged(self, beamy, beamz):
        self.YBeam = beamy
        self.ZBeam = beamz
        self.table.setText(self.currIdx, 1, str(beamy))
        self.table.setText(self.currIdx, 2, str(beamz))

    def setBrickEnabled(self, value):
        if value:
            # print "Someone ask to enable CameraBeamBrick."
            self.setEnabled(True)
        else:
            # print "Someone ask to disable CameraBeamBrick."
            self.setEnabled(False)

