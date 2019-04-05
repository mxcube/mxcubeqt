import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import os

__category__ = "mxCuBE"


class SnapshotBrick(BlissWidget):
    OUTPUT_FORMATS = ("bmp", "png", "jpeg", "tiff")

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.prefix = "snapshot"
        self.directory = "/tmp"
        self.fileIndex = 1
        self.formatType = "jpeg"

        self.settingsDialog = None

        self.addProperty("icons", "string", "")
        self.addProperty("defaultFormat", "combo", SnapshotBrick.OUTPUT_FORMATS, "jpeg")
        self.defineSlot("setDirectory", ())
        self.defineSlot("setPrefix", ())
        self.defineSignal("takeSnapshot", ())

        self.topBox = QVGroupBox("Sample snapshot", self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.snapshotButton = QToolButton(self.topBox)
        self.snapshotButton.setTextLabel("Take snapshot")
        self.snapshotButton.setUsesTextLabel(True)
        QObject.connect(self.snapshotButton, SIGNAL("clicked()"), self.takeSnapshot)

        self.settingsButton = QToolButton(self.topBox)
        self.settingsButton.setTextLabel("File settings")
        self.settingsButton.setUsesTextLabel(True)
        self.settingsButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(
            self.settingsButton, SIGNAL("clicked()"), self.openSettingsDialog
        )

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def setDirectory(self, directory):
        self.directory = directory

    def setPrefix(self, prefix):
        self.prefix = prefix

    def takeSnapshot(self):
        if not os.path.isdir(self.directory):
            try:
                os.makedirs(self.directory)
            except OSError as diag:
                logging.getLogger().error(
                    "SnapshotBrick: error trying to create the directory %s (%s)"
                    % (self.directory, str(diag))
                )
                return
            else:
                logging.getLogger().info(
                    "SnapshotBrick: created the directory %s" % self.directory
                )

        path = os.path.join(self.directory, self.prefix)
        filename = path + "_%d%s%s" % (self.fileIndex, os.path.extsep, self.formatType)
        self.emit(PYSIGNAL("takeSnapshot"), (filename,))
        self.fileIndex += 1

    def openSettingsDialog(self):
        if self.isRunning():
            if self.settingsDialog is None:
                self.settingsDialog = SettingsDialog(self, "Take snapshot")
                icons_list = self["icons"].split()
                try:
                    self.settingsDialog.setIcons(
                        icons_list[2], icons_list[3], icons_list[4], icons_list[5]
                    )
                except IndexError:
                    pass

            self.settingsDialog.setParameters(
                self.prefix, self.directory, self.fileIndex, self.formatType
            )

            s = self.font().pointSize()
            f = self.settingsDialog.font()
            f.setPointSize(s)
            self.settingsDialog.setFont(f)
            self.settingsDialog.updateGeometry()
            if self.settingsDialog.exec_loop():
                params = self.settingsDialog.getParameters()
                self.prefix = params[0]
                self.directory = params[1]
                self.fileIndex = params[2]
                self.formatType = params[3]

    def setIcons(self, icons):
        icons_list = icons.split()
        try:
            self.snapshotButton.setPixmap(Icons.load(icons_list[0]))
        except IndexError:
            pass
        try:
            self.settingsButton.setPixmap(Icons.load(icons_list[1]))
        except IndexError:
            pass

    def propertyChanged(self, property, oldValue, newValue):
        if property == "icons":
            self.setIcons(newValue)
        elif property == "defaultFormat":
            self.formatType = newValue
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)


###
# Dialog box to change the snapshot file settings
###


class SettingsDialog(QDialog):
    def __init__(self, parent, caption):
        QDialog.__init__(self, parent, "", False)

        self.setCaption(caption)

        box1 = QHGroupBox("Snapshot settings", self)
        box2 = QHBox(self)

        grid1 = QWidget(box1)
        QGridLayout(grid1, 4, 3, 0, 2)

        label1 = QLabel("File prefix:", grid1)
        grid1.layout().addWidget(label1, 0, 0)
        self.filePrefix = QLineEdit(grid1)
        grid1.layout().addMultiCellWidget(self.filePrefix, 0, 0, 1, 2)

        label2 = QLabel("Directory:", grid1)
        grid1.layout().addWidget(label2, 1, 0)
        self.fileDirectory = QLineEdit(grid1)
        grid1.layout().addWidget(self.fileDirectory, 1, 1)

        self.browseButton = QToolButton(grid1)
        self.browseButton.setTextLabel("Browse")
        self.browseButton.setUsesTextLabel(True)
        self.browseButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(
            self.browseButton, SIGNAL("clicked()"), self.browseButtonClicked
        )
        grid1.layout().addWidget(self.browseButton, 1, 2)

        label3 = QLabel("File index:", grid1)
        grid1.layout().addWidget(label3, 2, 0)
        self.fileIndex = myLineEdit(grid1)
        grid1.layout().addWidget(self.fileIndex, 2, 1)

        self.resetButton = QToolButton(grid1)
        self.resetButton.setTextLabel("Reset")
        self.resetButton.setUsesTextLabel(True)
        self.resetButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.resetButton, SIGNAL("clicked()"), self.resetButtonClicked)
        grid1.layout().addWidget(self.resetButton, 2, 2)

        label4 = QLabel("Format:", grid1)
        grid1.layout().addWidget(label4, 3, 0)
        self.imageFormat = QComboBox(grid1)
        grid1.layout().addMultiCellWidget(self.imageFormat, 3, 3, 1, 2)
        for t in SnapshotBrick.OUTPUT_FORMATS:
            self.imageFormat.insertItem(t)

        self.applyButton = QToolButton(box2)
        self.applyButton.setTextLabel("Accept")
        self.applyButton.setUsesTextLabel(True)
        self.applyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.applyButton, SIGNAL("clicked()"), self.accept)
        HorizontalSpacer(box2)

        self.cancelButton = QToolButton(box2)
        self.cancelButton.setTextLabel("Cancel")
        self.cancelButton.setUsesTextLabel(True)
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)

        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(box1)
        self.layout().addWidget(box2)

    def resetButtonClicked(self):
        self.fileIndex.setText("1")

    def setIcons(self, apply_icon, cancel_icon, browse_icon, reset_icon):
        self.browseButton.setPixmap(Icons.load(browse_icon))
        self.resetButton.setPixmap(Icons.load(reset_icon))
        self.applyButton.setPixmap(Icons.load(apply_icon))
        self.cancelButton.setPixmap(Icons.load(cancel_icon))

    def setParameters(self, prefix, directory, index, format):
        self.filePrefix.setText(prefix)
        self.fileDirectory.setText(directory)
        self.fileIndex.setText(str(index))
        index = list(SnapshotBrick.OUTPUT_FORMATS).index(format)
        self.imageFormat.setCurrentItem(index)

    def getParameters(self):
        return (
            str(self.filePrefix.text()),
            str(self.fileDirectory.text()),
            int(str(self.fileIndex.text())),
            str(self.imageFormat.currentText()),
        )

    def browseButtonClicked(self):
        get_dir = QFileDialog(self)
        s = self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()
        d = get_dir.getExistingDirectory(
            self.fileDirectory.text(), self, "", "Select a directory", True, False
        )
        if d is not None and len(d) > 0:
            self.fileDirectory.setText(d)


class myLineEdit(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        palette = self.palette()
        self.disabledCG = QColorGroup(palette.disabled())
        self.disabledCG.setColor(QColorGroup.Text, QWidget.black)
        self.setEnabled(False)
        palette.setDisabled(self.disabledCG)


class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
