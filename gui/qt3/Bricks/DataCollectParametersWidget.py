from qt import *
import time
import os
from BlissFramework import Icons
import logging
import string


class DirectoryInput(QWidget):
    def __init__(self, button_text, parent):
        QWidget.__init__(self, parent)
        self.lineEdit = LineEditInput(self)
        self.lineSuffix = readonlyLineEdit(self)
        self.lineSuffix.hide()
        self.button = QToolButton(self)
        self.button.setUsesTextLabel(True)
        self.button.setTextPosition(QToolButton.BesideIcon)
        self.button.setTextLabel(button_text)

        QGridLayout(self, 1, 3)
        self.layout().addWidget(self.lineEdit, 0, 0)
        self.layout().addWidget(self.lineSuffix, 0, 1)
        self.layout().addWidget(self.button, 0, 2)

        QObject.connect(
            self.lineEdit, SIGNAL("textChanged(const QString &)"), self.txtChanged
        )
        QObject.connect(self.lineEdit, SIGNAL("returnPressed()"), self.retPressed)
        QObject.connect(self.button, SIGNAL("clicked()"), self.browseDirs)

        self.proposalCode = None
        self.proposalNumber = None

    def setMultiSample(self, multi, suffix=""):
        if multi:
            self.lineSuffix.setText(suffix)
            self.lineSuffix.show()
        else:
            self.lineSuffix.hide()

    def setProposal(self, prop_code, prop_number):
        self.proposalCode = prop_code
        self.proposalNumber = prop_number

    def setPaletteBackgroundColor(self, color):
        self.lineEdit.setPaletteBackgroundColor(color)

    def setText(self, txt):
        self.lineEdit.setText(txt)

    def text(self):
        return str(self.lineEdit.text())

    def setIcons(self, browse_icon):
        self.button.setPixmap(Icons.load(browse_icon))

    def retPressed(self):
        if self.hasAcceptableInput():
            self.emit(PYSIGNAL("returnPressed"), ())

    def validateDirectory(self, directory=None):
        valid = True
        if directory is None:
            directory = self.text()
        if self.hasAcceptableInput(directory):
            if os.path.isdir(directory):
                self.setPaletteBackgroundColor(
                    DataCollectParametersWidget.PARAMETER_STATE["OK"]
                )
            else:
                self.setPaletteBackgroundColor(
                    DataCollectParametersWidget.PARAMETER_STATE["WARNING"]
                )
        else:
            valid = False
            self.setPaletteBackgroundColor(
                DataCollectParametersWidget.PARAMETER_STATE["INVALID"]
            )
        return valid

    def txtChanged(self, txt):
        txt = str(txt)
        valid = self.validateDirectory(txt)
        if valid:
            self.emit(PYSIGNAL("textChanged"), (txt,))
        self.emit(PYSIGNAL("inputValid"), (self, valid))

    # Browses the file system and saves the directory to store the images in
    # the input field
    def browseDirs(self):
        get_dir = QFileDialog(self)
        s = self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()
        d = get_dir.getExistingDirectory(
            self.lineEdit.text(), self, "", "Select a directory", True, False
        )
        if d is not None and len(d) > 0:
            self.lineEdit.setText(d)

    def hasAcceptableInput(self, text=None):
        if text is None:
            directory = self.text()
        else:
            directory = text
        if directory == "":
            return False
        if self.proposalCode is None:
            return True
        dirs = directory.split(os.path.sep)
        try:
            dirs.index("%s%s" % (self.proposalCode, self.proposalNumber))
        except ValueError:
            return False
        else:
            return True

    def setMultipleSelection(self, multiple):
        pass


class CheckBoxInput(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.checkBox = QCheckBox(self)
        self.label = readonlyLineEdit(self)
        self.lineEdit = LineEditInput(self)

        QGridLayout(self, 1, 3)
        self.layout().addWidget(self.checkBox, 0, 0)
        self.layout().addWidget(self.label, 0, 1)
        self.layout().addWidget(self.lineEdit, 0, 2)

        QObject.connect(self.checkBox, SIGNAL("toggled(bool)"), self.checkToggled)
        self.label.setEnabled(False)
        self.lineEdit.setEnabled(False)

        self.setEnabled(False)

        self.label.setAlignment(QWidget.AlignRight)

    def checkToggled(self, state):
        self.label.setEnabled(state)
        self.lineEdit.setEnabled(state)
        self.emit(PYSIGNAL("toggled"), (state,))

    def setLabelText(self, txt):
        self.label.setText(txt)
        if txt != "":
            self.setEnabled(True)
        else:
            self.setEnabled(False)
            self.checkBox.setChecked(False)

    def setChecked(self, state):
        self.checkBox.setChecked(state)

    def isChecked(self, state):
        return self.checkBox.isChecked()

    def setInputText(self, txt):
        self.lineEdit.setText(txt)

    def text(self):
        return (self.checkBox.isChecked(), self.label.text(), self.lineEdit.text())

    def hasAcceptableInput(self):
        if self.checkBox.isChecked():
            return self.lineEdit.hasAcceptableInput()
        return True


class CheckBoxInput2(QWidget):
    def __init__(self, text, parent):
        QWidget.__init__(self, parent)
        self.checkBox = QCheckBox(self)
        self.label = QLabel(text, self)
        self.lineEdit = LineEditInput(self)
        QGridLayout(self, 1, 3)
        self.layout().addWidget(self.checkBox, 0, 0)
        self.layout().addWidget(self.label, 0, 1)
        self.layout().addWidget(self.lineEdit, 0, 2)

        QObject.connect(self.checkBox, SIGNAL("toggled(bool)"), self.checkToggled)
        self.label.setEnabled(False)
        self.lineEdit.setEnabled(False)
        QObject.connect(
            self.lineEdit, SIGNAL("textChanged(const QString &)"), self.txtChanged
        )

    def setAlignment(self, alignment):
        self.lineEdit.setAlignment(alignment)

    def isChecked(self, state):
        return self.checkBox.isChecked()

    def setChecked(self, state):
        self.checkBox.setChecked(state)

    def checkToggled(self, state):
        self.label.setEnabled(state)
        self.lineEdit.setEnabled(state)

    def setLabelText(self, txt):
        self.checkBox.setText(txt)

    def setInputText(self, txt):
        self.lineEdit.setText(txt)

    def setValidator(self, validator):
        self.lineEdit.setValidator(validator)

    def text(self):
        return (self.checkBox.isChecked(), self.lineEdit.text())

    def hasAcceptableInput(self):
        if self.checkBox.isChecked():
            return self.lineEdit.hasAcceptableInput()
        return True

    def txtChanged(self, txt):
        txt = str(txt)
        valid = None
        if self.hasAcceptableInput():
            valid = True
            self.lineEdit.setPaletteBackgroundColor(
                DataCollectParametersWidget.PARAMETER_STATE["OK"]
            )
        else:
            valid = False
            self.lineEdit.setPaletteBackgroundColor(
                DataCollectParametersWidget.PARAMETER_STATE["INVALID"]
            )
        self.emit(PYSIGNAL("textChanged"), (txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"), (self, valid))


class CheckBoxInput3(QWidget):
    def __init__(self, text, parent):
        QWidget.__init__(self, parent)
        self.checkBox = QCheckBox(self)
        self.label = QLabel(text, self)
        spacer1 = HorizontalSpacer(self)
        QGridLayout(self, 1, 2)
        self.layout().addWidget(self.checkBox, 0, 0)
        self.layout().addWidget(self.label, 0, 1)
        self.layout().addWidget(spacer1, 0, 2)

    def text(self):
        return self.checkBox.isChecked()

    def hasAcceptableInput(self):
        return True

    def isChecked(self, state):
        return self.checkBox.isChecked()

    def setChecked(self, state):
        self.checkBox.setChecked(state)


class ComboBoxInput(QComboBox):
    def text(self):
        return str(self.currentText())

    def hasAcceptableInput(self):
        return True


class LineEditInput(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        QObject.connect(self, SIGNAL("textChanged(const QString &)"), self.txtChanged)
        QObject.connect(self, SIGNAL("returnPressed()"), self.retPressed)

        self.origPalette = QPalette(self.palette())
        self.palette2 = QPalette(self.origPalette)
        self.palette2.setColor(
            QPalette.Active, QColorGroup.Base, self.origPalette.disabled().background()
        )
        self.palette2.setColor(
            QPalette.Inactive,
            QColorGroup.Base,
            self.origPalette.disabled().background(),
        )
        self.palette2.setColor(
            QPalette.Disabled,
            QColorGroup.Base,
            self.origPalette.disabled().background(),
        )

    def retPressed(self):
        if self.validator() is not None:
            if self.hasAcceptableInput():
                self.emit(PYSIGNAL("returnPressed"), ())
        else:
            self.emit(PYSIGNAL("returnPressed"), ())

    def text(self):
        return str(QLineEdit.text(self))

    def txtChanged(self, txt):
        txt = str(txt)
        valid = None
        if self.validator() is not None:
            if self.hasAcceptableInput():
                valid = True
                self.setPaletteBackgroundColor(
                    DataCollectParametersWidget.PARAMETER_STATE["OK"]
                )
            else:
                valid = False
                self.setPaletteBackgroundColor(
                    DataCollectParametersWidget.PARAMETER_STATE["INVALID"]
                )
        self.emit(PYSIGNAL("textChanged"), (txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"), (self, valid))

    def sizeHint(self):
        size_hint = QLineEdit.sizeHint(self)
        size_hint.setWidth(size_hint.width() / 3)
        return size_hint

    def setReadOnly(self, readonly):
        if readonly:
            self.setPalette(self.palette2)
        else:
            self.setPalette(self.origPalette)
        QLineEdit.setReadOnly(self, readonly)


class readonlyLineEdit(LineEditInput):
    def __init__(self, parent):
        LineEditInput.__init__(self, parent)
        self.setReadOnly(True)


class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)


class DataCollectParametersWidget(QWidget):
    PARAMETER_STATE = {
        "INVALID": QWidget.red,
        "OK": QWidget.white,
        "WARNING": QWidget.yellow,
    }

    PARAMETERS = (
        (
            "directory",
            "Directory",
            0,
            0,
            2,
            DirectoryInput,
            ("Browse",),
            None,
            None,
            ("PYSIGNAL", "PYSIGNAL"),
        ),
        ("prefix", "Prefix", 1, 0, 0, LineEditInput, (), None, None, ("PYSIGNAL",)),
        (
            "run_number",
            "Run number",
            2,
            0,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QIntValidator, 0),
            ("PYSIGNAL",),
        ),
        ("template", "Template", 3, 0, 0, readonlyLineEdit, (), None, None, ()),
        (
            "first_image",
            "First image #",
            4,
            0,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QIntValidator, 0),
            ("PYSIGNAL",),
        ),
        (
            "number_images",
            "Number of images",
            5,
            0,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QIntValidator, 1),
            ("PYSIGNAL",),
        ),
        ("comments", "Comments", 6, 0, 2, LineEditInput, (), None, None, ()),
        (
            "osc_start",
            "Oscillation start (deg)",
            1,
            2,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QDoubleValidator,),
            (),
        ),
        (
            "osc_range",
            "Oscillation range (deg)",
            2,
            2,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QDoubleValidator,),
            (),
        ),
        (
            "overlap",
            "Overlap (deg)",
            3,
            2,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QDoubleValidator,),
            (),
        ),
        (
            "exposure_time",
            "Exposure time (s)",
            4,
            2,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QDoubleValidator, 0.0),
            (),
        ),
        (
            "number_passes",
            "Number of passes",
            5,
            2,
            0,
            LineEditInput,
            (),
            QWidget.AlignRight,
            (QIntValidator, 1),
            (),
        ),
        ("detector_mode", "Detector mode", 6, 4, 0, ComboBoxInput, (), None, None, ()),
        (
            "mad_energies",
            "MAD energies",
            0,
            4,
            0,
            ComboBoxInput,
            (),
            None,
            None,
            (None, None, "SIGNAL"),
        ),
        (
            "mad_1_energy",
            "",
            1,
            4,
            0,
            CheckBoxInput,
            (),
            None,
            None,
            (None, None, None, "PYSIGNAL"),
        ),
        (
            "mad_2_energy",
            "",
            2,
            4,
            0,
            CheckBoxInput,
            (),
            None,
            None,
            (None, None, None, "PYSIGNAL"),
        ),
        (
            "mad_3_energy",
            "",
            3,
            4,
            0,
            CheckBoxInput,
            (),
            None,
            None,
            (None, None, None, "PYSIGNAL"),
        ),
        (
            "mad_4_energy",
            "",
            4,
            4,
            0,
            CheckBoxInput,
            (),
            None,
            None,
            (None, None, None, "PYSIGNAL"),
        ),
        (
            "inverse_beam",
            "Inverse beam",
            5,
            4,
            0,
            CheckBoxInput2,
            ("interval:",),
            QWidget.AlignRight,
            (QIntValidator, 1),
            (),
        ),
    )
    #    "maintain_res":("", 4, 4, 0, CheckBoxInput3, ("Maintain resolution",), None, None, ()),\
    #    "inverse_beam":("Inverse beam", 5, 4, 0, CheckBoxInput2, ("interval:",), QWidget.AlignRight, (QIntValidator,1), ()),\
    #    "dose_mode":("Dose mode", 6, 4, 0, CheckBoxInput3, (), None, None, ()),\
    #    "dna_screening":("DNA screening", 6, 4, 0, CheckBoxInput3, (), None, None, ()),\
    #    "dose_mode":("Dose mode", 5, 4, 0, CheckBoxInput3, ("",), None, None, ()),\
    #    "start_phi_curr_pos":("Phi start", 6, 4, 0, CheckBoxInput3, ("from current position",), None, None, ())

    def __init__(self, parent, brick):
        QWidget.__init__(self, parent)

        self.Brick = brick

        self.paramsBox = QWidget(parent)
        QGridLayout(self.paramsBox, 1, 1, 1, 2)

        self.labelDict = {}
        self.paramDict = {}
        self.validDict = {}
        self.lastValid = True
        self.lastSpecReady = False

        self.imageFileSuffix = None
        self.proposalCode = None
        self.proposalNumber = None
        self.madEnergies = {}
        self.madEnergiesCheck = {}

        for param in DataCollectParametersWidget.PARAMETERS:
            param_id = param[0]
            param_label = param[1]
            param_row = param[2]
            param_column = param[3]
            param_span = param[4]
            param_class = param[5]
            param_class_args = list(param[6])
            param_class_align = param[7]
            param_class_validator = param[8]
            connect_signals = param[9]

            if param_label:
                label = QLabel("%s:" % param_label, self.paramsBox)
                self.paramsBox.layout().addWidget(label, param_row, param_column)
                self.labelDict[param_id] = label
            param_class_args.append(self.paramsBox)
            input_widget = param_class(*param_class_args)
            if param_class_align is not None:
                input_widget.setAlignment(param_class_align)
            if param_class_validator is not None:
                class_validator = param_class_validator[0]
                validator = class_validator(input_widget)
                try:
                    validator_bottom = param_class_validator[1]
                except IndexError:
                    pass
                else:
                    validator.setBottom(validator_bottom)
                input_widget.setValidator(validator)
            self.paramsBox.layout().addMultiCellWidget(
                input_widget,
                param_row,
                param_row,
                param_column + 1,
                param_column + 1 + param_span,
            )
            self.paramDict[param_id] = input_widget

            QObject.connect(input_widget, PYSIGNAL("inputValid"), self.isInputValid)

            try:
                connect_on_changed = connect_signals[0]
            except IndexError:
                connect_on_changed = None
            if connect_on_changed == "SIGNAL":
                exec(
                    "QObject.connect(input_widget, SIGNAL('textChanged(const QString &)'), self.%sChanged)"
                    % param_id
                )
            elif connect_on_changed == "PYSIGNAL":
                exec(
                    "QObject.connect(input_widget, PYSIGNAL('textChanged'), self.%sChanged)"
                    % param_id
                )
            try:
                connect_on_return = connect_signals[1]
            except IndexError:
                connect_on_return = None
            if connect_on_return == "SIGNAL":
                exec(
                    "QObject.connect(input_widget, SIGNAL('returnPressed()'), self.%sPressed)"
                    % param_id
                )
            elif connect_on_return == "PYSIGNAL":
                exec(
                    "QObject.connect(input_widget, PYSIGNAL('returnPressed'), self.%sPressed)"
                    % param_id
                )
            try:
                connect_on_activated = connect_signals[2]
            except IndexError:
                connect_on_activated = None
            if connect_on_activated == "SIGNAL":
                exec(
                    "QObject.connect(input_widget, SIGNAL('activated(int)'), self.%sActivated)"
                    % param_id
                )
            elif connect_on_activated == "PYSIGNAL":
                exec(
                    "QObject.connect(input_widget, PYSIGNAL('activated'), self.%sActivated)"
                    % param_id
                )
            try:
                connect_on_toggled = connect_signals[3]
            except IndexError:
                connect_on_toggled = None
            if connect_on_toggled == "SIGNAL":
                exec(
                    "QObject.connect(input_widget, SIGNAL('toggled(bool)'), self.%sToggled)"
                    % param_id
                )
            elif connect_on_toggled == "PYSIGNAL":
                exec(
                    "QObject.connect(input_widget, PYSIGNAL('toggled'), self.%sToggled)"
                    % param_id
                )

        self.buttonsContainer = QHBox(self.paramsBox)
        self.buttonsContainer.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed
        )
        self.thisButton = QToolButton(self.buttonsContainer)
        self.thisButton.setUsesTextLabel(True)
        self.thisButton.setTextLabel("Collect data")
        self.thisButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.thisButton, SIGNAL("clicked()"), self.collectThisClicked)
        HorizontalSpacer(self.buttonsContainer)
        box2 = QVBox(self.buttonsContainer)
        VerticalSpacer(box2)
        self.addButton = QToolButton(box2)
        self.addButton.setUsesTextLabel(True)
        self.addButton.setTextPosition(QToolButton.BesideIcon)
        self.addButton.setTextLabel("Add to queue")
        self.addButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.addButton, SIGNAL("clicked()"), self.addToQueueClicked)
        self.paramsBox.layout().addMultiCellWidget(
            VerticalSpacer(self.paramsBox), 7, 7, 0, 5
        )
        self.paramsBox.layout().addMultiCellWidget(self.buttonsContainer, 8, 8, 0, 5)

    def isInputValid(self, input_widget, valid):
        self.validDict[input_widget] = valid
        current_valid = True
        for wid in self.validDict:
            if not self.validDict[wid]:
                current_valid = False
        if current_valid != self.lastValid:
            self.lastValid = current_valid
            self.thisButton.setEnabled(self.lastSpecReady and self.lastValid)
            self.addButton.setEnabled(current_valid)

            self.emit(PYSIGNAL("parametersValid"), (current_valid,))

    def addToQueueClicked(self):
        params_dict = self.getParamDict()
        self.emit(PYSIGNAL("addToQueue"), (params_dict,))

    def collectThisClicked(self):
        params_dict = self.getParamDict()
        self.emit(PYSIGNAL("collectThis"), (params_dict,))

    def setSpecReady(self, is_spec_ready):
        self.lastSpecReady = is_spec_ready
        self.thisButton.setEnabled(self.lastSpecReady and self.lastValid)

    def getParam(self, param_id):
        try:
            param = self.paramDict[param_id]
        except KeyError:
            param = None
        return param

    def setDefaultValues(self, prefix=None, prop_code=None, prop_number=None):
        self.proposalCode = prop_code
        self.proposalNumber = prop_number

        self.fillMadEnergiesOrder()

        self.paramDict["directory"].setProposal(prop_code, prop_number)
        self.paramDict["osc_start"].setText(self.Brick["degFormatString"] % 0.0)
        self.paramDict["osc_range"].setText(self.Brick["degFormatString"] % 1.0)
        self.paramDict["overlap"].setText(self.Brick["degFormatString"] % 0.0)
        self.paramDict["exposure_time"].setText(self.Brick["secFormatString"] % 1.0)
        self.paramDict["number_passes"].setText("1")
        self.paramDict["number_images"].setText("1")
        self.paramDict["run_number"].setText("1")
        self.paramDict["first_image"].setText("1")
        self.paramDict["comments"].setText("")
        self.paramDict["inverse_beam"].setInputText("1")
        self.setMADEnergies({})
        self.paramDict["inverse_beam"].setChecked(False)
        self.paramDict["inverse_beam"].setInputText("1")

        directory_prefix = self.Brick.getDirectoryPrefix()

        curr_date_str = time.strftime("%Y%m%d")
        if prop_code is not None and prop_code != "":
            inhouse = self.Brick["inhouseUsers"].split()
            try:
                inhouse.index(prop_code)
            except ValueError:
                prop = prop_code + prop_number
                self.setDirectory(
                    os.path.join(
                        "/data", "visitor", directory_prefix, prop, curr_date_str
                    )
                )
            else:
                inhouse = "%s%s" % (prop_code, prop_number)
                self.setDirectory(
                    os.path.join(
                        "/data", directory_prefix, "inhouse", inhouse, curr_date_str
                    )
                )
        else:
            self.setDirectory(os.path.join(directory_prefix, curr_date_str))
        self.setPrefix(prefix)

    def uncheckMADEnergies(self):
        self.paramDict["mad_1_energy"].setChecked(False)
        self.paramDict["mad_2_energy"].setChecked(False)
        self.paramDict["mad_3_energy"].setChecked(False)
        self.paramDict["mad_4_energy"].setChecked(False)

    def setMADEnergies(self, energies):
        if not self.labelDict["mad_energies"].isShown():
            return

        mad_energy_order = map(
            string.strip, self.paramDict["mad_energies"].text().split("-")
        )
        # print "MAD ENERGY ORDER",mad_energy_order
        mad_pk_order = "mad_%s_energy" % (mad_energy_order.index("pk") + 1)
        mad_ip_order = "mad_%s_energy" % (mad_energy_order.index("ip") + 1)
        mad_rm_order = "mad_%s_energy" % (mad_energy_order.index("rm") + 1)
        mad_rm2_order = "mad_%s_energy" % (mad_energy_order.index("rm2") + 1)

        if energies is not None:
            self.madEnergies = energies

        try:
            pk = self.madEnergies["pk"]
        except KeyError:
            pk = None
        try:
            ip = self.madEnergies["ip"]
        except KeyError:
            ip = None
        try:
            rm = self.madEnergies["rm"]
        except KeyError:
            rm = None
        try:
            rm2 = self.madEnergies["rm2"]
        except KeyError:
            rm2 = None

        if pk is not None:
            self.paramDict[mad_pk_order].setLabelText(str(pk))
            self.paramDict[mad_pk_order].setInputText("/pk")
            if energies is not None:
                self.paramDict[mad_pk_order].setChecked(True)
            else:
                try:
                    pk_checked = self.madEnergiesCheck["pk"]
                except KeyError:
                    pass
                else:
                    self.paramDict[mad_pk_order].setChecked(pk_checked)
            self.paramDict[mad_pk_order].setEnabled(True)
        else:
            self.paramDict[mad_pk_order].setEnabled(False)
            self.paramDict[mad_pk_order].setLabelText("")
            self.paramDict[mad_pk_order].setInputText("")

        if ip is not None:
            self.paramDict[mad_ip_order].setLabelText(str(ip))
            self.paramDict[mad_ip_order].setInputText("/ip")
            if energies is not None:
                self.paramDict[mad_ip_order].setChecked(True)
            else:
                try:
                    ip_checked = self.madEnergiesCheck["ip"]
                except KeyError:
                    pass
                else:
                    self.paramDict[mad_ip_order].setChecked(ip_checked)
            self.paramDict[mad_ip_order].setEnabled(True)
        else:
            self.paramDict[mad_ip_order].setEnabled(False)
            self.paramDict[mad_ip_order].setLabelText("")
            self.paramDict[mad_ip_order].setInputText("")

        if rm is not None:
            self.paramDict[mad_rm_order].setLabelText(str(rm))
            self.paramDict[mad_rm_order].setInputText("/rm")
            if energies is not None:
                self.paramDict[mad_rm_order].setChecked(False)
            else:
                try:
                    rm_checked = self.madEnergiesCheck["rm"]
                except KeyError:
                    pass
                else:
                    self.paramDict[mad_rm_order].setChecked(rm_checked)
            self.paramDict[mad_rm_order].setEnabled(True)
        else:
            self.paramDict[mad_rm_order].setEnabled(False)
            self.paramDict[mad_rm_order].setLabelText("")
            self.paramDict[mad_rm_order].setInputText("")

        if rm2 is not None:
            self.paramDict[mad_rm2_order].setLabelText(str(rm2))
            self.paramDict[mad_rm2_order].setInputText("/rm2")
            if energies is not None:
                self.paramDict[mad_rm2_order].setChecked(False)
            else:
                try:
                    rm2_checked = self.madEnergiesCheck["rm2"]
                except KeyError:
                    pass
                else:
                    self.paramDict[mad_rm2_order].setChecked(rm2_checked)
            self.paramDict[mad_rm2_order].setEnabled(True)
        else:
            self.paramDict[mad_rm2_order].setEnabled(False)
            self.paramDict[mad_rm2_order].setLabelText("")
            self.paramDict[mad_rm2_order].setInputText("")

    def setPrefix(self, prefix=None):
        if prefix is None:
            prefix = "prefix"
        self.paramDict["prefix"].setText(prefix)

    def getPrefix(self):
        return self.paramDict["prefix"].text()

    def setDirectory(self, directory):
        self.paramDict["directory"].setText(str(directory))

    def getDirectory(self):
        return self.paramDict["directory"].text()

    def setDirectoryIcon(self, browse_icon):
        self.paramDict["directory"].setIcons(browse_icon)

    def setAddQueueIcon(self, add_icon):
        self.addButton.setPixmap(Icons.load(add_icon))

    def setCollectThisIcon(self, this_icon):
        self.thisButton.setPixmap(Icons.load(this_icon))

    def getRunNumber(self):
        if self.paramDict["run_number"].hasAcceptableInput():
            return int(self.paramDict["run_number"].text())
        return None

    def setRunNumber(self, run_number):
        self.paramDict["run_number"].setText(str(run_number))

    def setNumberPasses(self, number_of_passes):
        self.paramDict["number_passes"].setText(str(number_of_passes))

    def setExposureTime(self, exposure_time):
        self.paramDict["exposure_time"].setText(str(exposure_time))

    def isInverseBeam(self):
        inv_beam = self.paramDict["inverse_beam"].text()
        return inv_beam[0]

    def buildFileTemplate(self):
        image_number_format = "###"
        try:
            first_image = int(str(self.paramDict["first_image"].text()))
            number_images = int(str(self.paramDict["number_images"].text()))
            run_number = int(str(self.paramDict["run_number"].text()))
        except Exception as diag:
            template = ""
        else:
            if (first_image + number_images - 1) > 999:
                image_number_format = "####"

            template = "%s_%d_%s" % (
                self.paramDict["prefix"].text(),
                run_number,
                image_number_format,
            )
            if self.imageFileSuffix is not None:
                template += ".%s" % self.imageFileSuffix

        self.paramDict["template"].setText(template)

    def buildDirectoryTemplate(self, protein_acronym, sample_name):
        inhouse_users = self.Brick["inhouseUsers"].split()
        """
        Now just the beamline prefix, to be added in the right order.
        For example /data/id14eh4/inhouse/xxx or /data/visitor/id14eh4/mx999
        """
        dir_prefix = self.Brick.getDirectoryPrefix()
        curr_date_str = time.strftime("%Y%m%d")
        dir_str = None

        if self.proposalCode is not None:
            prop_str = "%s%s" % (self.proposalCode, self.proposalNumber)

            try:
                inhouse_users.index(self.proposalCode)
            except ValueError:
                dir_prop = "visitor"
            else:
                dir_prop = "inhouse"

            if protein_acronym is None:
                if dir_prop == "inhouse":
                    dir_str = os.path.join(
                        "/data", dir_prefix, dir_prop, prop_str, curr_date_str
                    )
                else:
                    dir_str = os.path.join(
                        "/data", dir_prop, dir_prefix, prop_str, curr_date_str
                    )
            else:
                curr_sample = os.path.join(protein_acronym, sample_name)
                if dir_prop == "inhouse":
                    dir_str = os.path.join(
                        "/data",
                        dir_prefix,
                        dir_prop,
                        prop_str,
                        curr_date_str,
                        curr_sample,
                    )
                else:
                    dir_str = os.path.join(
                        "/data",
                        dir_prop,
                        dir_prefix,
                        prop_str,
                        curr_date_str,
                        curr_sample,
                    )
        else:
            dir_str = os.path.join(dir_prefix, curr_date_str)

        if dir_str is not None:
            self.setDirectory(dir_str)

    def setFileSuffix(self, suffix):
        if self.imageFileSuffix != suffix:
            self.imageFileSuffix = suffix
            self.buildFileTemplate()

    def setDetectorMode(self, mode_index):
        if self.paramDict["detector_mode"].count() > mode_index:
            self.paramDict["detector_mode"].setCurrentItem(mode_index)

    def setDetectorType(self, detector_type):
        self.paramDict["detector_mode"].clear()
        if detector_type == "adsc":
            self.paramDict["detector_mode"].insertItem("Software binned")
            self.paramDict["detector_mode"].insertItem("Unbinned")
            self.paramDict["detector_mode"].insertItem("Hardware binned")
        elif detector_type == "marccd":
            self.labelDict["detector_mode"].setEnabled(False)
            self.paramDict["detector_mode"].setEnabled(False)

    def fillMadEnergiesOrder(self):
        self.paramDict["mad_energies"].clear()
        self.paramDict["mad_energies"].insertItem("pk - ip - rm - rm2")
        self.paramDict["mad_energies"].insertItem("ip - pk - rm - rm2")

    def setMultiSample(self):
        self.paramDict["prefix"].setReadOnly(True)
        self.setPrefix("acronym-name|barcode")
        self.paramDict["directory"].setMultiSample(True, "/acronym/name|/barcode")
        self.buildDirectoryTemplate(None, None)

    def setSample(self, protein_acronym, sample_name):
        self.paramDict["prefix"].setReadOnly(False)
        if protein_acronym is None:
            self.setParamState("prefix", "WARNING")
            if self.proposalCode is None:
                self.setPrefix()
            else:
                self.setPrefix("%s%s" % (self.proposalCode, self.proposalNumber))
        else:
            self.setParamState("prefix", "OK")
            self.setPrefix("%s-%s" % (protein_acronym, sample_name))

        self.paramDict["directory"].setMultiSample(False)
        self.buildDirectoryTemplate(protein_acronym, sample_name)

    def hideMADEnergies(self):
        self.labelDict["mad_energies"].hide()
        self.paramDict["mad_energies"].hide()
        self.paramDict["mad_1_energy"].hide()
        self.paramDict["mad_2_energy"].hide()
        self.paramDict["mad_3_energy"].hide()
        self.paramDict["mad_4_energy"].hide()

    def showMADEnergies(self):
        self.labelDict["mad_energies"].show()
        self.paramDict["mad_energies"].show()
        self.paramDict["mad_1_energy"].show()
        self.paramDict["mad_2_energy"].show()
        self.paramDict["mad_3_energy"].show()
        self.paramDict["mad_4_energy"].show()

    def hideInverseBeam(self):
        self.labelDict["inverse_beam"].hide()
        self.paramDict["inverse_beam"].hide()

    def hideDoseMode(self):
        pass
        # self.labelDict["dose_mode"].hide()
        # self.paramDict["dose_mode"].hide()

    def hideComments(self):
        self.labelDict["comments"].hide()
        self.paramDict["comments"].hide()

    def disableDetectorMode(self):
        self.labelDict["detector_mode"].setDisabled(True)
        self.paramDict["detector_mode"].setDisabled(True)

    def disableDoseMode(self):
        pass
        # self.labelDict["dose_mode"].setDisabled(True)
        # self.paramDict["dose_mode"].setDisabled(True)

    def disableInverseBeam(self):
        self.labelDict["inverse_beam"].setDisabled(True)
        self.paramDict["inverse_beam"].setDisabled(True)

    def enableMADEnergies(self, state):
        self.labelDict["mad_energies"].setEnabled(state)

    def sanityCheck(self):
        return (True,)

    def setParamState(self, param_id, state):
        self.paramDict[param_id].setPaletteBackgroundColor(
            DataCollectParametersWidget.PARAMETER_STATE[state]
        )

    def setIcons(self, param_id, icons):
        self.paramDict[param_id].setIcons(icons)

    def mad_energiesActivated(self, order):
        self.setMADEnergies(None)

    def mad_1_energyToggled(self, state):
        mad_energy_order = map(
            string.strip, self.paramDict["mad_energies"].text().split("-")
        )
        self.madEnergiesCheck[mad_energy_order[0]] = state

    def mad_2_energyToggled(self, state):
        mad_energy_order = map(
            string.strip, self.paramDict["mad_energies"].text().split("-")
        )
        self.madEnergiesCheck[mad_energy_order[1]] = state

    def mad_3_energyToggled(self, state):
        mad_energy_order = map(
            string.strip, self.paramDict["mad_energies"].text().split("-")
        )
        self.madEnergiesCheck[mad_energy_order[2]] = state

    def mad_4_energyToggled(self, state):
        mad_energy_order = map(
            string.strip, self.paramDict["mad_energies"].text().split("-")
        )
        self.madEnergiesCheck[mad_energy_order[3]] = state

    def prefixChanged(self, text):
        self.setRunNumber(1)
        self.buildFileTemplate()
        self.emit(PYSIGNAL("prefixChanged"), (text,))

    def directoryChanged(self, text):
        self.emit(PYSIGNAL("directoryChanged"), (text,))

    def directoryPressed(self):
        directory = self.paramDict["directory"].text()
        if directory != "" and not os.path.isdir(directory):
            create_directory_dialog = QMessageBox(
                "Directory not found",
                "Press OK to create the directory.",
                QMessageBox.Question,
                QMessageBox.Ok,
                QMessageBox.Cancel,
                QMessageBox.NoButton,
                self,
            )
            s = self.font().pointSize()
            f = create_directory_dialog.font()
            f.setPointSize(s)
            create_directory_dialog.setFont(f)
            create_directory_dialog.updateGeometry()

            if create_directory_dialog.exec_loop() == QMessageBox.Ok:
                try:
                    os.makedirs(directory)
                except OSError as diag:
                    logging.getLogger().error(
                        "DataCollectBrick: error trying to create the directory %s (%s)"
                        % (directory, str(diag))
                    )
                self.paramDict["directory"].validateDirectory(directory)

    def first_imageChanged(self, text):
        self.buildFileTemplate()

    def run_numberChanged(self, text):
        self.buildFileTemplate()

    def number_imagesChanged(self, text):
        self.buildFileTemplate()

    def getParamDict(self):
        params = {}
        for param in DataCollectParametersWidget.PARAMETERS:
            param_id = param[0]
            if self.paramDict[param_id].hasAcceptableInput():
                text = self.paramDict[param_id].text()
            else:
                text = None
            params[param_id] = text
        return params

    def getValidationDict(self):
        params = {}
        for param in DataCollectParametersWidget.PARAMETERS:
            param_id = param[0]
            if self.paramDict[param_id].hasAcceptableInput():
                valid = True
            else:
                valid = False
            params[param_id] = valid
        return params
