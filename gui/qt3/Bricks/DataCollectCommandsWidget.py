from qt import *
from BlissFramework import Icons
import logging
import ProgressBarBrick


class DataCollectCommandsWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        box1 = QHBox(self)
        self.stopButton = QToolButton(box1)
        self.stopButton.setTextPosition(QToolButton.BesideIcon)
        self.stopButton.setUsesTextLabel(True)
        self.stopButton.setTextLabel("Stop collection")
        self.stopButton.setPaletteBackgroundColor(QWidget.yellow)
        QObject.connect(self.stopButton, SIGNAL("clicked()"), self.stopCollect)

        spacer1 = HorizontalSpacer3(box1)

        self.skipButton = QToolButton(box1)
        self.skipButton.setTextPosition(QToolButton.BesideIcon)
        self.skipButton.setUsesTextLabel(True)
        self.skipButton.setTextLabel("Skip oscillation")
        QObject.connect(self.skipButton, SIGNAL("clicked()"), self.skipOscillation)

        self.progressBar = ProgressBarBrick.ProgressBarBrick(self)

        self.abortButton = QToolButton(self)
        self.abortButton.setTextPosition(QToolButton.BesideIcon)
        self.abortButton.setUsesTextLabel(True)
        self.abortButton.setTextLabel("Abort!")
        self.abortButton.setPaletteBackgroundColor(QWidget.red)
        QObject.connect(self.abortButton, SIGNAL("clicked()"), self.abortCollect)

        QGridLayout(self, 1, 3, 0, 0)
        self.layout().addWidget(box1, 0, 0)
        self.layout().addWidget(self.progressBar, 0, 1)
        self.layout().addWidget(self.abortButton, 0, 2)
        self.layout().setSpacing(4)

    def setIcons(self, stop_icon, abort_icon, skip_icon):
        self.abortButton.setPixmap(Icons.load(abort_icon))
        self.stopButton.setPixmap(Icons.load(stop_icon))
        self.skipButton.setPixmap(Icons.load(skip_icon))

    def stopCollect(self):
        stop_dialog = QMessageBox(
            "Stop collection",
            "Are you sure you want to stop the current data collection?",
            QMessageBox.Question,
            QMessageBox.Yes,
            QMessageBox.No,
            QMessageBox.NoButton,
            self,
        )

        s = self.font().pointSize()
        f = stop_dialog.font()
        f.setPointSize(s)
        stop_dialog.setFont(f)
        stop_dialog.updateGeometry()
        if stop_dialog.exec_loop() == QMessageBox.Yes:
            self.emit(PYSIGNAL("stopCollect"), ())

    def abortCollect(self):
        self.emit(PYSIGNAL("abortCollect"), ())

    def skipOscillation(self):
        self.emit(PYSIGNAL("skipOscillation"), ())

    def collectStarted(self, num_oscillations):
        self.stopButton.setEnabled(True)
        if num_oscillations > 1:
            self.skipButton.setEnabled(True)
        self.abortButton.setEnabled(True)

    def collectDone(self):
        self.stopButton.setEnabled(False)
        self.skipButton.setEnabled(False)
        self.abortButton.setEnabled(False)

    def collectFailed(self):
        self.stopButton.setEnabled(False)
        self.skipButton.setEnabled(False)
        self.abortButton.setEnabled(False)

        # def cancelStop(self):
        #    pass

        """
        QToolTip.add(self.prefixLabel,"Prefix for the image's filename")
        QToolTip.add(self.prefixInput,"Prefix for the image's filename")
        QToolTip.add(self.runNumberLabel,"The data collection number")
        QToolTip.add(self.runNumberInput,"The data collection number")
        QToolTip.add(self.templateLabel,"Current template of the image's filename")
        QToolTip.add(self.templateInput,"Current template of the image's filename")
        QToolTip.add(self.firstImageLabel,"The number to use as the first image")
        QToolTip.add(self.firstImageInput,"The number to use as the first image")
        QToolTip.add(self.oscStartLabel,"Starting degree of the oscillation")
        QToolTip.add(self.oscStartInput,"Starting degree of the oscillation")
        QToolTip.add(self.oscRangeLabel,"Degree range of the oscillation")
        QToolTip.add(self.oscRangeInput,"Degree range of the oscillation")
        QToolTip.add(self.oscOverlapLabel,"Degree overlap of the oscillation")
        QToolTip.add(self.oscOverlapInput,"Degree overlap of the oscillation")
        QToolTip.add(self.noImagesLabel,"Number of images to collect")
        QToolTip.add(self.noImagesInput,"Number of images to collect")
        QToolTip.add(self.exposureModeLabel,"The type of experiment to perform")
        QToolTip.add(self.exposureMode,"The type of experiment to perform")
        QToolTip.add(self.energiesLabel,"The beam energy(ies) to use (in keV)")
        QToolTip.add(self.defaultEnergyDisplay,"The current beam energy")
        QToolTip.add(self.currentEnergy,"Finds the current beam energy")
        QToolTip.add(self.energyInput,"Sets the beam energy for this data collection")
        QToolTip.add(self.madEnergiesInput,"The MAD energies to use in this data collection")
        QToolTip.add(self.madEnergiesButton,"Selects which MAD energies to use")
        QToolTip.add(self.detectorModeLabel,"Sets the detector mode")
        QToolTip.add(self.detectorMode,"Sets the detector mode")
        QToolTip.add(self.transmissionLabel,"The transmission percentage to use in this data collection")
        QToolTip.add(self.currentTransmission,"Finds the current transmission")
        QToolTip.add(self.transmissionInput,"The transmission percentage to use in this data collection")
        QToolTip.add(self.detectorResLabel,"The detector resolution (in Angstrom)")
        QToolTip.add(self.currentResolution,"Finds the current resolution (according to the current detector distance)")
        QToolTip.add(self.detectorResInput,"The detector resolution (in Angstrom)")
        QToolTip.add(self.exposureTimeLabel,"Exposure time for each image (in seconds)")
        QToolTip.add(self.exposureTimeInput,"Exposure time for each image (in seconds)")
        QToolTip.add(self.noPassesLabel,"Number of passes per image")
        QToolTip.add(self.noPassesInput,"Number of passes per image")
        QToolTip.add(self.directoryLabel,"Which directory to store the images")
        QToolTip.add(self.directoryInput,"Which directory to store the images")
        QToolTip.add(self.browseDirectory,"Browses the filesystem to select a directory")
        QToolTip.add(self.commentsLabel,"Comments for this data collection")
        QToolTip.add(self.commentsInput,"Comments for this data collection")
        QToolTip.add(self.collectButton,"Starts the data collection")
        """


class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class HorizontalSpacer3(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def sizeHint(self):
        return QSize(4, 0)
