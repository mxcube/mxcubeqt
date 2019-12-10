from qt import *
import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from MotorSpinBoxBrick import MotorSpinBoxBrick

import copy

__category__ = "mxCuBE"

DEBUG = 0


class EDNACharacteriseBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.ednaObj = None

        self.addProperty("Wavelength_motor", "string", "")
        self.addProperty("EDNA_conf", "string", "")

        self.defineSlot("setFileParameters", ())
        self.defineSlot("collectOscillationFinished", ())

        self.defineSignal("submitDataCollection", ())
        self.defineSignal("characterisationDone", ())
        self.defineSignal("collectOscillations", ())

        self.dataGroupBox = QGroupBox(self)
        QHBoxLayout(self.dataGroupBox)
        lbl1 = QLabel("Directory", self.dataGroupBox)
        self.dataDirEdit = QLineEdit(self.dataGroupBox)
        lbl2 = QLabel("Prefix", self.dataGroupBox)
        self.prefixEdit = QLineEdit(self.dataGroupBox)
        self.dataGroupBox.layout().addWidget(lbl1)
        self.dataGroupBox.layout().addWidget(self.dataDirEdit)
        self.dataGroupBox.layout().addWidget(lbl2)
        self.dataGroupBox.layout().addWidget(self.prefixEdit)

        lw1 = QWidget(self)
        QHBoxLayout(lw1, 2, 50)
        vbox1 = QVBox(lw1)
        hbox1 = QHBox(vbox1)
        lbl5 = QLabel("Characterise using:", hbox1)
        self.methodBox = QComboBox(0, hbox1)
        self.methodBox.insertItem("1 Image")
        self.methodBox.insertItem("2 Images")
        self.methodBox.insertItem("4 Images")
        self.startButton = QPushButton("Start", vbox1)
        QObject.connect(
            self.startButton, SIGNAL("clicked()"), self.startCharacterisation
        )
        lw2 = QWidget(lw1)
        QGridLayout(lw2, 2, 4, 2, 2)
        lbl3 = QLabel("Exposure time (s)", lw2)
        self.exposureEdit = QLineEdit(lw2)
        lbl4 = QLabel("Resolution (%s)" % chr(197), lw2)
        self.resolutionEdit = QLineEdit(lw2)
        self.wavelengthEdit = MotorSpinBoxBrick(lw2)
        self.wavelengthEdit.stopButton.hide()
        self.wavelengthEdit.stepButton.hide()
        self.wavelengthEdit.moveLeftButton.hide()
        self.wavelengthEdit.moveRightButton.hide()
        self.wavelengthEdit.stepList.hide()
        self.enableMADCheckBox = QCheckBox("enable MAD", lw2)
        lw2.layout().addWidget(lbl3, 0, 0)
        lw2.layout().addWidget(self.exposureEdit, 0, 1)
        lw2.layout().addWidget(lbl4, 0, 2)
        lw2.layout().addWidget(self.resolutionEdit, 0, 3)
        lw2.layout().addMultiCellWidget(self.wavelengthEdit, 1, 1, 0, 1)
        lw2.layout().addMultiCellWidget(self.enableMADCheckBox, 1, 1, 2, 3)
        lw1.layout().addWidget(vbox1)
        lw1.layout().addWidget(lw2)

        QVBoxLayout(self, 2, 2)
        self.layout().addWidget(self.dataGroupBox)
        self.layout().addWidget(lw1)

    def propertyChanged(self, propertyName, oldValue, newValue):

        if propertyName == "Wavelength_motor":
            self.wavelengthEdit.setMotor(None, newValue)
        if propertyName == "EDNA_conf":
            if self.ednaObj is not None:
                self.disconnect(
                    self.ednaObj,
                    PYSIGNAL("strategyDictCreated"),
                    self.createStrategyDict,
                )
            self.ednaObj = self.getHardwareObject(newValue)
            if self.ednaObj is not None:
                self.connect(
                    self.ednaObj,
                    PYSIGNAL("strategyDictCreated"),
                    self.createStrategyDict,
                )
                self.setExposure(self.ednaObj.default_exposure)
                self.setResolution(self.ednaObj.default_resolution)

    def setExposure(self, exp):
        self.exposureEdit.setText(str(exp))

    def setResolution(self, res):
        self.resolutionEdit.setText(str(res))

    def setFileParameters(self, directory, prefix):
        self.dataDirEdit.setText(directory)
        self.prefixEdit(prefix)

    def startCharacterisation(self):
        method = self.methodBox.currentItem()
        dataDir = str(self.dataDirEdit.text())
        prefix = str(self.prefixEdit.text())
        exposure = float(str(self.exposureEdit.text()))
        resolution = float(str(self.resolutionEdit.text()))
        if DEBUG:
            wavelength = 1.0
        else:
            wavelength = self.wavelengthEdit.motor.getPosition()
        self.collectSeq = self.ednaObj.buildEdnaCollectRefImagesDict(
            dataDir, prefix, exposure, resolution, wavelength, method
        )
        if self.collectSeq:
            """
            First collect reference images, then collectOscillationFinished will be called to start the characterisation
            """
            self.emit(PYSIGNAL("collectOscillations"), ("EDNA", self.collectSeq, 1))
        else:
            logging.getlogger().error("Error building collect dict")
            return

    def collectOscillationFinished(self, owner, state, message, col_id, *args):
        if owner == "EDNA":
            self.ednaObj.characterise(self.collectSeq)

    def createStrategyDict(self, strategy_dict):
        collect_dict = copy.deepcopy(strategy_dict)

        if not DEBUG:
            collect_dict["wavelength"] = self.wavelengthEdit.motor.getPosition()

        self.emit(PYSIGNAL("submitDataCollection"), ([collect_dict],))
