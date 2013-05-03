"""
Brick to 
"""

### Modules ###
from qt import *
import time
import os
from BlissFramework import Icons
import logging
import string
from DataCollectBrick2 import DataCollectBrick2
from DataCollectBrick2 import LineEditInput
from DataCollectBrick2 import readonlyLineEdit
from BlissFramework.BaseComponents import BlissWidget
import copy
import time
import re

### BlissFramework brick category (for the BlissFramework Builder) ###
__category__ = 'mxCuBE'


XTAL_SPACEGROUPS = [x.strip() for x in ['', ' P1', ' P2 ', ' P21', ' C2', ' P222 ', ' P2221 ', ' P21212 ', ' P212121', ' C222 ', ' C2221', ' F222', ' I222 ', ' I212121', ' P4 ', ' P41 ', ' P42 ', ' P43 ', ' P422 ', ' P4212', ' P4122 ', ' P41212 ', ' P4222 ', ' P42212', ' P4322 ', ' P43212', ' I4 ', ' I41 ', ' I422 ', ' I4122', ' P3 ', ' P31 ', ' P32 ', ' P312 ', ' P321 ', ' P3112', ' P3121 ', ' P3212 ', ' P3221 ', ' P6 ', ' P61', ' P65 ', ' P62 ', ' P64 ', ' P63 ', ' P622', ' P6122 ', ' P6522 ', ' P6222 ', ' P6422 ', ' P6322', ' R3 ', ' R32', ' P23 ', ' P213 ', ' P432 ', ' P4232 ', ' P4332', ' P4132', ' F23 ', ' F432 ', ' F4132', ' I23 ', ' I213 ', ' I432 ', ' I4132']]

ORIG_EDNA_SPACEGROUPS = {' I4132': '214', ' P21212 ': '18', ' P432 ': '207', ' P43212': '96', ' P6222 ': '180', ' P3 ': '143', ' C2': '5', ' P6422 ': '181', ' P212121': '19', ' F432 ': '209', ' P4132': '213', ' R32': '155', ' P23 ': '195', ' I23 ': '197', ' I212121': '24', ' P3112': '151', ' P1': '1', ' P42212': '94', ' P321 ': '150', ' P63 ': '173', ' I422 ': '97', ' P41 ': '76', ' P6122 ': '178', ' P65 ': '170', ' I41 ': '80', ' P32 ': '145', ' I432 ': '211', ' C222 ': '21', ' F4132': '210', ' F23 ': '196', ' I222 ': '23', ' P42 ': '77', ' I213 ': '199', ' P2 ': '3', ' R3 ': '146', ' P213 ': '198', ' I4122': '98', ' P61': '169', ' P312 ': '149', ' I4 ': '79', ' P64 ': '172', ' P222 ': '16', ' P41212 ': '92', ' P3212 ': '153', ' P21': '4', ' P6 ': '168', ' P4322 ': '95', ' C2221': '20', ' P422 ': '89', ' F222': '22', ' P62 ': '171', ' P6322': '182', ' P4 ': '75', ' P31 ': '144', ' P3221 ': '154', ' P4122 ': '91', ' P6522 ': '179', ' P4212': '90', ' P2221 ': '17', ' P622': '177', ' P43 ': '78', ' P4222 ': '93', ' P3121 ': '152', ' P4232 ': '208', ' P4332': '212'}
EDNA_SPACEGROUPS = {}
for x, v in ORIG_EDNA_SPACEGROUPS.iteritems():
  EDNA_SPACEGROUPS[x.strip()]=v

"""
DirectoryInput
    Description: Widget for the directory of a data collection: validates it with the proposal
                 code and number and prevents special characters, also if it doesn't exist (uses
                 the colors set in DataCollectBrick2.PARAMETER_STATE). Includes a Browse button.
                 Has a special mode when multiple samples are selected: a readonly suffix specifying
                 that the sample's acronym and name, or barcode, will be appended to the directory.
    Type       : class (qt.QWidget)
    API        : setMultiSample
                 setIcons
                 setText
                 text
                 validateDirectory
"""
class DirectoryInput(QWidget):
    INVALID_CHARS="*<>[]{},?'`~!@#$%^&=+|\\\""
    def __init__(self, button_text, parent):
        QWidget.__init__(self, parent)
        hbox = QHBox(self) 
        self.lineEdit=LineEditInput(hbox)
        self.lineSuffix=readonlyLineEdit(hbox)
        self.lineSuffix.hide()
        self.button=QToolButton(hbox)
        self.button.setUsesTextLabel(True)
        self.button.setTextPosition(QToolButton.BesideIcon)
        self.button.setTextLabel(button_text)
        self.processDirLabel = QLabel(self, "<i>Processing files directory:</i>")	
        self.processDir = ""

        QVBoxLayout(self)
        self.layout().addWidget(hbox)
        self.layout().addWidget(self.processDirLabel)

        QObject.connect(self.lineEdit, SIGNAL('textChanged(const QString &)'), self.txtChanged)
        QObject.connect(self.lineEdit, SIGNAL('returnPressed()'), self.retPressed)
        QObject.connect(self.button, SIGNAL('clicked()'), self.browseDirs)

        self.proposalCode=None
        self.proposalNumber=None 
        self.directory_check_regexp = ""

    def setMultiSample(self,multi,suffix=""):
        if multi:
            self.lineSuffix.setText(suffix)
            self.lineSuffix.show()
        else:
            self.lineSuffix.hide()

    def setPaletteBackgroundColor(self,color):
        self.lineEdit.setPaletteBackgroundColor(color)

    def setText(self,txt):
        self.lineEdit.setText(txt)

    def text(self):
        return str(self.lineEdit.text())

    def setIcons(self,browse_icon):
        self.button.setPixmap(Icons.load(browse_icon))

    def retPressed(self):
        if self.hasAcceptableInput():
            self.emit(PYSIGNAL("returnPressed"),())

    def validateDirectory(self,directory=None):
        valid=True
        if directory is None:
            directory=self.text()
        if directory.find(" ")!=-1:
            cur_pos=self.lineEdit.cursorPosition()
            directory=directory.replace(" ","_")
            self.setText(directory)
            self.lineEdit.setCursorPosition(cur_pos)
        if self.hasAcceptableInput(directory):
            QToolTip.remove(self)
            if os.path.isdir(directory):
                self.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["OK"])
            else:
                self.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["WARNING"])
        else:
            valid=False
            self.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["INVALID"])
            QToolTip.add(self, "Directory doesn't follow mxCuBE convention: should start like /data/[visitor|inhouse]/your mx number/beamline/session start date/RAW_DATA/...")
        return valid

    def txtChanged(self,txt):
        valid=self.validateDirectory(str(txt)) 
        txt=str(self.text())
        if valid: # is this necessary? why not emit always?
            self.emit(PYSIGNAL("textChanged"),(txt,))
            dirs = txt.split(os.path.sep)
            i = dirs.index('RAW_DATA')
            dirs[i]='PROCESSED_DATA'
            self.processDir = os.path.sep.join(dirs)
            self.processDirLabel.setText("<i>Processing files directory: %s</i>" % self.processDir)
        else:
            self.processDirLabel.setText("<i>Processing files directory: ?</i>")
        self.emit(PYSIGNAL("inputValid"),(self,valid,))
        self.emit(PYSIGNAL("widgetSynchronize"),((txt,),))

    def browseDirs(self):
        get_dir=QFileDialog(self)
        s=self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()

        directory_split = str(self.lineEdit.text()).split(os.path.sep)
        lsplit=len(directory_split)
        D=''
        for i in range(lsplit):
          D=os.path.sep.join(directory_split[0:lsplit-i])
          if os.path.isdir(D):
            break

        d=get_dir.getExistingDirectory(D,self,"",\
            "Select a directory",True,False)

        if d is not None and len(d)>0:
            self.lineEdit.setText(d)

    def hasAcceptableInput(self,text=None):
        if text is None:
            directory=str(self.text())
        else:
            directory=text
        if directory=="":
            return False
        for c in DirectoryInput.INVALID_CHARS:
            if directory.find(c)!=-1:
                return False
        if not directory.endswith(os.path.sep):
          directory += os.path.sep
        if not self.directory_check_regexp:
          return False
        directory_check = re.compile(self.directory_check_regexp)
        if not directory_check.match(directory):
          return False
        return True

    def widgetSynchronize(self,state):
        self.setText(str(state[0]))

"""
PrefixInput
    Description: Widget for the prefix of the filename of a data collection: validates it with special
                 characters (uses the colors set in DataCollectBrick2.PARAMETER_STATE).
    Type       : class (LineEditInput)
"""
class PrefixInput(LineEditInput):
    INVALID_CHARS="*<>[]{},?'`~!@#$%^&=+|\\\"/"
    def txtChanged(self,txt):
        txt=str(txt)
        if txt.find(" ")!=-1:
            cur_pos=self.cursorPosition()
            txt=txt.replace(" ","_")
            self.setText(txt)
            self.setCursorPosition(cur_pos)
        if self.hasAcceptableInput():
            valid=True
            self.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["OK"])
        else:
            valid=False
            self.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["INVALID"])
        #self.emit(PYSIGNAL("textChanged"),(txt,))
        self.emit(PYSIGNAL("inputValid"),(self,valid,))
    def hasAcceptableInput(self,text=None):
        if text is None:
            txt=self.text()
        else:
            txt=text
        if txt=="":
            return False
        if not self.isReadOnly():
            for c in PrefixInput.INVALID_CHARS:
                if txt.find(c)!=-1:
                    return False
        return True

"""
InvBeamInput
    Description: Widget for the 
    Type       : class (qt.QWidget)
    API        : setLabelText
                 setChecked
                 isChecked
                 setInputText
                 text
"""
class InvBeamInput(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.checkBox=QCheckBox(self)
        self.label=readonlyLineEdit(self)
        self.lineEdit=LineEditInput(self)

        QGridLayout(self,1,3)
        self.layout().addWidget(self.checkBox,0,0)
        self.layout().addWidget(self.label,0,1)
        self.layout().addWidget(self.lineEdit,0,2)

        QObject.connect(self.checkBox, SIGNAL('toggled(bool)'), self.checkToggled)
        self.label.setEnabled(False)
        self.lineEdit.setEnabled(False)
        QObject.connect(self.label, SIGNAL('textChanged(const QString &)'), self.labelTxtChanged)
        QObject.connect(self.lineEdit, SIGNAL('textChanged(const QString &)'), self.txtChanged)

        self.setEnabled(False)

        self.label.setAlignment(QWidget.AlignRight)

    def checkToggled(self,state):
        self.label.setEnabled(state)
        self.lineEdit.setEnabled(state)
        self.emit(PYSIGNAL("toggled"),(state,))
        self.emitWidgedSynchronize()

    def setLabelText(self,txt):
        self.label.setText(txt)
        if txt!="":
            self.setEnabled(True)
        else:
            self.setEnabled(False)
            self.checkBox.setChecked(False)

    def setChecked(self,state):
        self.checkBox.setChecked(state)

    def isChecked(self,state):
        return self.checkBox.isChecked()

    def setInputText(self,txt):
        self.lineEdit.setText(txt)

    def text(self):
        return (self.checkBox.isChecked(),self.label.text(),self.lineEdit.text())

    def hasAcceptableInput(self):
        if self.checkBox.isChecked():
            return self.lineEdit.hasAcceptableInput()
        return True

    def txtChanged(self,txt):
        self.emitWidgedSynchronize()

    def labelTxtChanged(self,txt):
        self.emitWidgedSynchronize()

    def emitWidgedSynchronize(self):
        self.emit(PYSIGNAL("widgetSynchronize"),(self.text(),))

    def widgetSynchronize(self,state):
        self.setChecked(state[0])
        self.setLabelText(str(state[1]))
        self.setInputText(str(state[2]))

"""
CheckBoxInput2
    Description: Widget for the 
    Type       : class (qt.QWidget)
    API        : setLabelText
                 setChecked
                 isChecked
                 setInputText
                 setAlignment
                 setValidator
                 text
"""
class CheckBoxInput2(QWidget):
    def __init__(self, text, parent):
        QWidget.__init__(self, parent)
        self.checkBox=QCheckBox(self)
        self.label=QLabel(text,self)
        self.lineEdit=LineEditInput(self)
        QGridLayout(self,1,3)
        self.layout().addWidget(self.checkBox,0,0)
        self.layout().addWidget(self.label,0,1)
        self.layout().addWidget(self.lineEdit,0,2)

        QObject.connect(self.checkBox, SIGNAL('toggled(bool)'), self.checkToggled)
        self.label.setEnabled(False)
        self.lineEdit.setEnabled(False)
        QObject.connect(self.lineEdit, SIGNAL('textChanged(const QString &)'), self.txtChanged)

    def setAlignment(self,alignment):
        self.lineEdit.setAlignment(alignment)

    def isChecked(self,state):
        return self.checkBox.isChecked()

    def setChecked(self,state):
        self.checkBox.setChecked(state)

    def checkToggled(self,state):
        self.label.setEnabled(state)
        self.lineEdit.setEnabled(state)
        self.emitWidgedSynchronize()

    def setLabelText(self,txt):
        self.checkBox.setText(txt)

    def setInputText(self,txt):
        self.lineEdit.setText(txt)

    def setValidator(self,validator):
        self.lineEdit.setValidator(validator)

    def text(self):
        return (self.checkBox.isChecked(),self.lineEdit.text())

    def hasAcceptableInput(self):
        if self.checkBox.isChecked():
            return self.lineEdit.hasAcceptableInput()
        return True

    def txtChanged(self,txt):
        txt=str(txt)
        valid=None
        if self.hasAcceptableInput():
            valid=True
            self.lineEdit.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["OK"])
        else:
            valid=False
            self.lineEdit.setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE["INVALID"])
        self.emit(PYSIGNAL("textChanged"),(txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"),(self,valid,))
        self.emitWidgedSynchronize()

    def emitWidgedSynchronize(self):
        self.emit(PYSIGNAL("widgetSynchronize"),(self.text(),))

    def widgetSynchronize(self,state):
        self.setChecked(state[0])
        self.setInputText(str(state[1]))

"""
CheckBoxInput3
    Description: Widget for the 
    Type       : class (qt.QWidget)
    API        : setChecked
                 isChecked
                 setInputText
                 setAlignment
                 setValidator
                 text
"""
class CheckBoxInput3(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.checkBox=QCheckBox(self)
        self.lineEdit=LineEditInput(self)
        self.checkBox.setChecked(True)
        QGridLayout(self,1,2)
        self.layout().addWidget(self.checkBox,0,0)
        self.layout().addWidget(self.lineEdit,0,1)
        QObject.connect(self.checkBox, SIGNAL('toggled(bool)'), self.checkToggled)
        QObject.connect(self.lineEdit, SIGNAL('textChanged(const QString &)'), self.txtChanged)
    def text(self):
        return (self.checkBox.isChecked(),self.lineEdit.text())
    def hasAcceptableInput(self):
        return self.lineEdit.hasAcceptableInput()
    def isChecked(self,state):
        return self.checkBox.isChecked()
    def setChecked(self,state):
        self.checkBox.setChecked(state)
    def setAlignment(self,alignment):
        self.lineEdit.setAlignment(alignment)
    def setValidator(self,validator):
        self.lineEdit.setValidator(validator)
    def setInputText(self,txt):
        self.lineEdit.setText(txt)
    def checkToggled(self,state):
        self.lineEdit.setEnabled(state)
        self.emit(PYSIGNAL("toggled"),(state,))
        self.emitWidgedSynchronize()
    def txtChanged(self,txt):
        txt=str(txt)
        self.emit(PYSIGNAL("textChanged"),(txt,))
        self.emitWidgedSynchronize()
    def emitWidgedSynchronize(self):
        self.emit(PYSIGNAL("widgetSynchronize"),(self.text(),))
    def widgetSynchronize(self,state):
        self.setChecked(state[0])
        self.setInputText(str(state[1]))

"""
CheckBoxInput4
    Description: Simple checkbox Widget which has the methods to fit in to existing infrastructure!
    Type       : 
"""

class CheckBoxInput4(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.checkBox=QCheckBox(self)
        QGridLayout(self,1,2)
        self.layout().addWidget(self.checkBox,0,0)
        QObject.connect(self.checkBox, SIGNAL('toggled(bool)'), self.checkToggled)

    def setAlignment(self,alignment):
        pass
    
    def setValidator(self,validator):
        pass

    def isChecked(self,state):
        return self.checkBox.isChecked()
    
    def setChecked(self,state):
        self.checkBox.setChecked(state)

    def checkToggled(self,state):
        self.emit(PYSIGNAL("toggled"),(state,))
        #self.emitWidgedSynchronize()

    def hasAcceptableInput(self):
        return True

    def emitWidgedSynchronize(self):
        pass
        #self.emit(PYSIGNAL("widgetSynchronize"),('',))

    def text(self):
        return (str(self.isChecked(True)))

"""
ComboBoxInput
    Description: Widget for the 
    Type       : class (qt.QComboBox)
"""
class ComboBoxInput(QComboBox):
    def text(self):
        return str(self.currentText())
    def hasAcceptableInput(self):
        return True

"""
HorizontalSpacer
    Description: Widget that expands itself horizontally.
    Type       : class (qt.QWidget)
"""
class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

"""
VerticalSpacer
    Description: Widget that expands itself vertically.
    Type       : class (qt.QWidget)
"""
class VerticalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)

"""
DataCollectParametersBrick
    Type       : class (BlissWidget)
    (please see file and method headers for details)
"""
class DataCollectParametersBrick(BlissWidget):
    OTHERPARAMETERS = (("processing",),("residues",),("anomalous",))
    PARAMETERS = (
        ("directory","Raw data directory",      0, 0, 2, DirectoryInput, ("Browse",), None, None, ("PYSIGNAL","PYSIGNAL")),\
        ("prefix","Prefix",                     1, 0, 0, PrefixInput, (), None, None, ("SIGNAL",)),\
        ("run_number","Run number",             2, 0, 0, LineEditInput, (), QWidget.AlignRight, (QIntValidator,0), ("PYSIGNAL",)),\
        ("template","Template",                 3, 0, 0, readonlyLineEdit, (), None, None, ()),\
        ("first_image","First image #",         4, 0, 0, LineEditInput, (), QWidget.AlignRight, (QIntValidator,0), ("PYSIGNAL",)),\
        ("number_images","Number of images",    5, 0, 0, LineEditInput, (), QWidget.AlignRight, (QIntValidator,1), ("PYSIGNAL",)),\
        ("comments","Comments",                 6, 0, 2, LineEditInput, (), None, None, ()),\
        ("osc_start","Oscillation start (deg)", 1, 2, 0, CheckBoxInput3, (), QWidget.AlignRight, (QDoubleValidator,), (None, None, None, "PYSIGNAL")),\
        ("osc_range","Oscillation range (deg)", 2, 2, 0, LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,), ("PYSIGNAL",)),\
        ("overlap","Overlap (deg)",             3, 2, 0, LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,), ()),\
        ("exposure_time","Exposure time (s)",   4, 2, 0, LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0.0), ("PYSIGNAL",)),\
        ("number_passes","Number of passes",    5, 2, 0, LineEditInput, (), QWidget.AlignRight, (QIntValidator,1), ()),\
        ("mad_energies","MAD energies",         0, 4, 0, ComboBoxInput, (), None, None, (None, None, "SIGNAL")),\
        ("mad_1_energy","",                     1, 4, 0, InvBeamInput, (), None, None, (None, None, None, "PYSIGNAL")),\
        ("mad_2_energy","",                     2, 4, 0, InvBeamInput, (), None, None, (None, None, None, "PYSIGNAL")),\
        ("mad_3_energy","",                     3, 4, 0, InvBeamInput, (), None, None, (None, None, None, "PYSIGNAL")),\
        ("mad_4_energy","",                     4, 4, 0, InvBeamInput, (), None, None, (None, None, None, "PYSIGNAL")),\
        ("inverse_beam","Inverse beam",         5, 4, 0, CheckBoxInput2, ("interval:",), QWidget.AlignRight, (QIntValidator,1), ()),\
        ("detector_mode","Detector mode",       6, 4, 0, ComboBoxInput, (), None, None, ()), \
        ("sum_images","Sum images",            7, 0, 0, CheckBoxInput2, ("Nb of frames to sum:",), QWidget.AlignRight, (QIntValidator, 2), ())
    )

    """
    __init__
        Description : Initializes the brick: defines the BlissFramework properties, signals and
                      slots; sets internal attribute to None; creates the brick's widgets and
                      layout.
        Type        : instance constructor
        Arguments   : *args (not used; just passed to the super class)
    """
    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        self.addProperty('dataCollect','string')
        self.addProperty("oscillationAxisMotor", "string")
        self.addProperty("dbConnection", "string")
        self.addProperty('icons','string','')
        self.addProperty('degFormatString','formatString','+###.##')
        self.addProperty('secFormatString','formatString','###.#')
        self.addProperty('disableDetectorMode','boolean',False)
        self.addProperty('hideQueueButton','boolean',False)
        self.addProperty('overrideSession','boolean',False)

        self.defineSlot('setBeamlineConfiguration',())
        self.defineSlot('setSession',())
        self.defineSlot('setSample',())
        self.defineSlot('collectReady',())
        self.defineSlot('setEnergyScanConnected',())
        self.defineSlot('setMADEnergies',())
        self.defineSlot('scanningMADEnergies',())
        self.defineSlot('getDataCollectParameters',())

        self.defineSignal('collectOscillations',())
        self.defineSignal('addToQueue',())
        self.defineSignal('directoryChanged',())
        self.defineSignal('prefixChanged',())
        self.defineSignal('rangeChanged',())
        self.defineSignal('exposureChanged',())
        self.defineSignal('runNumberChanged',())
        self.defineSignal('collectParameterRequest',())
        self.defineSignal('DataCollectParameters',())

        self.collectObj = None
        self.axisMotorObj = None

        QGridLayout(self, 9, 9, 1, 2)

        self.labelDict = {}
        self.paramDict = {}
        self.validDict = {}
        self.lastValid = True

        self.lastReady = False
        self.beamlineConfiguration = {}

        self.imageFileSuffix=None

        self.proposalCode=None
        self.proposalNumber=None
        self.sessionId=None

        self.selectedSamples=[]

        self.madEnergies={}
        self.madEnergiesCheck={}

        widgets=[]
        for param in DataCollectParametersBrick.PARAMETERS:
            param_id=param[0]
            param_label=param[1]
            param_row=param[2]
            param_column=param[3]
            param_span=param[4]
            param_class=param[5]
            param_class_args=list(param[6])
            param_class_align=param[7]
            param_class_validator=param[8]
            connect_signals=param[9]

            if param_label:
                label=QLabel("%s:" % param_label, self)
                self.layout().addWidget(label, param_row, param_column)
                self.labelDict[param_id]=label
            param_class_args.append(self)
            input_widget=param_class(*param_class_args)
            if param_class_align is not None:
                input_widget.setAlignment(param_class_align)
            if param_class_validator is not None:
                class_validator=param_class_validator[0]
                validator=class_validator(input_widget)
                try:
                    validator_bottom=param_class_validator[1]
                except IndexError:
                    pass
                else:
                    validator.setBottom(validator_bottom)
                input_widget.setValidator(validator)
            self.layout().addMultiCellWidget(input_widget, param_row, param_row, param_column+1, param_column+1+param_span)
            self.paramDict[param_id]=input_widget

            exec("self.widget%s=input_widget" % param_id)
            widgets.append("widget%s" % param_id)
            self.connect(input_widget,PYSIGNAL('inputValid'),self.isInputValid)
            self.connectWidget(input_widget,param_id,connect_signals)

        QObject.connect(self.paramDict["inverse_beam"].checkBox, SIGNAL("toggled(bool)"), self.inverse_beam_toggled)
        for w_name in ("mad_1_energy", "mad_2_energy", "mad_3_energy", "mad_4_energy"):
          QObject.connect(self.paramDict[w_name].checkBox, SIGNAL("toggled(bool)"), self.mad_checkbox_toggled)

        """ Make the special processing widget and put it in the grid.  I was unable to lay it out with the other widgets otherwise """
        procHBox = QHBox(self)
        procHBox.setSpacing(5)
        HorizontalSpacer(procHBox)
        input_widget = self.widgetprocessing = CheckBoxInput4(procHBox)
        self.widgetprocessing.checkBox.setText("Process && Analyse Data")
        widgets.append("widgetprocessing")
        self.paramDict["processing"]=input_widget
        self.connect(input_widget,PYSIGNAL('inputValid'),self.isInputValid)
        self.connectWidget(input_widget,"processing",("PYSIGNAL,"))

        QLabel(": N.o Residues",procHBox)
        input_widget = self.widgetresidues = LineEditInput(procHBox)
        self.widgetresidues.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.paramDict["residues"]=self.widgetresidues
        
        QLabel("Crystal space group:", procHBox) #spaceGroupBox)
        self.lstSpaceGroup = QComboBox(procHBox) #spaceGroupBox)
        self.lstSpaceGroup.insertStrList(XTAL_SPACEGROUPS)
        celldimbox = QVBox(procHBox)
        celldimbox.setMargin(0); celldimbox.setSpacing(0)
        QLabel("Cell dim. (a b c alpha beta gamma):", celldimbox)
        self.txtCellDimension = QLineEdit(celldimbox)
 
        QLabel("Anomalous",procHBox)
        input_widget = self.widgetanomalous = CheckBoxInput4(procHBox)
        self.paramDict["anomalous"]=self.widgetanomalous
        
        self.layout().addMultiCellWidget(procHBox, 7, 7, 3, 8) #procHBox,7,7,4,8)
        
        self.instanceSynchronize(*widgets)

        self.labelDict["detector_mode"].setDisabled(True)
        self.paramDict["detector_mode"].setDisabled(True)

        self.setEnergyScanConnected(None)

        self.buttonsContainer=QHBox(self)
        self.buttonsContainer.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.collectButton=QToolButton(self.buttonsContainer)
        self.collectButton.setUsesTextLabel(True)
        self.collectButton.setTextLabel("Collect data")
        self.collectButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        QObject.connect(self.collectButton,SIGNAL('clicked()'), self.collectThisClicked)
        HorizontalSpacer(self.buttonsContainer)
        box2=QVBox(self.buttonsContainer)
        VerticalSpacer(box2)
        self.addButton=QToolButton(box2)
        self.addButton.setUsesTextLabel(True)
        self.addButton.setTextPosition(QToolButton.BesideIcon)
        self.addButton.setTextLabel("Add to queue")
        self.addButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)        
        QObject.connect(self.addButton,SIGNAL('clicked()'), self.addToQueueClicked)

        #self.layout().addMultiCellWidget(VerticalSpacer(self), 7, 7, 0, 11)
        self.layout().addMultiCellWidget(self.buttonsContainer, 8, 8, 0, 11)


    def inverse_beam_toggled(self, checked):
        self.enableCollectButton() 

    def mad_checkbox_toggled(self, checked):
        self.enableCollectButton()

    def enableCollectButton(self): 
        enable = self.lastReady and self.lastValid and not self.paramDict["inverse_beam"].checkBox.isChecked() and not any([self.paramDict[w_name].checkBox.isChecked() for w_name in ("mad_1_energy", "mad_2_energy", "mad_3_energy", "mad_4_energy")])
        self.collectButton.setEnabled(enable)

    def connectWidget(self,input_widget,param_id,connect_signals):
        try:
            connect_on_changed=connect_signals[0]
        except IndexError:
            connect_on_changed=None
        if connect_on_changed=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('textChanged(const QString &)'), self.%sChanged)" % param_id)
        elif connect_on_changed=="PYSIGNAL":
            exec("self.connect(input_widget, PYSIGNAL('textChanged'), self.%sChanged)" % param_id)
        try:
            connect_on_return=connect_signals[1]
        except IndexError:
            connect_on_return=None
        if connect_on_return=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('returnPressed()'), self.%sPressed)" % param_id)
        elif connect_on_return=="PYSIGNAL":
            exec("self.connect(input_widget, PYSIGNAL('returnPressed'), self.%sPressed)" % param_id)
        try:
            connect_on_activated=connect_signals[2]
        except IndexError:
            connect_on_activated=None
        if connect_on_activated=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('activated(int)'), self.%sActivated)" % param_id)
        elif connect_on_activated=="PYSIGNAL":
            exec("self.connect(input_widget, PYSIGNAL('activated'), self.%sActivated)" % param_id)
        try:
            connect_on_toggled=connect_signals[3]
        except IndexError:
            connect_on_toggled=None
        if connect_on_toggled=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('toggled(bool)'), self.%sToggled)" % param_id)
        elif connect_on_toggled=="PYSIGNAL":
            exec("self.connect(input_widget, PYSIGNAL('toggled'), self.%sToggled)" % param_id)


    """
    propertyChanged
        Description: BlissFramework callback, when a property is set during initialization time
                     (or in edit mode).
        Type       : callback
        Arguments  : propertyName (string; property name)
                     oldValue     (?/defined in addProperty; previous property value)
                     newValue     (?/defined in addProperty; new property value)
        Returns    : nothing
    """
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'oscillationAxisMotor':
            if self.axisMotorObj is not None:
              self.disconnect(self.axisMotorObj, PYSIGNAL("motorPositionChanged"), self.phiMoved)
            self.axisMotorObj = self.getHardwareObject(newValue)
            if self.axisMotorObj is not None:
              self.connect(self.axisMotorObj, PYSIGNAL("motorPositionChanged"), self.phiMoved)
        elif propertyName == "dbConnection":
            self.dbServer = self.getHardwareObject(newValue)
        elif propertyName == 'dataCollect':
            if self.collectObj is not None:
                self.disconnect(self.collectObj, PYSIGNAL('collectConnected'), self.collectConnected)
                self.disconnect(self.collectObj, PYSIGNAL('collectDisconnected'), self.collectDisconnected)
                self.disconnect(self.collectObj, PYSIGNAL('collectReady'), self.collectReady)
                self.disconnect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.collectOscillationFinished)
            self.collectObj=self.getHardwareObject(newValue)
            if self.collectObj is not None:
                self.connect(self.collectObj, PYSIGNAL('collectConnected'), self.collectConnected)
                self.connect(self.collectObj, PYSIGNAL('collectDisconnected'), self.collectDisconnected)
                self.connect(self.collectObj, PYSIGNAL('collectReady'), self.collectReady)
                self.connect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.collectOscillationFinished)

            self.updateGUI()

        elif propertyName == 'icons':
            icons_list=newValue.split()

            try:
                self.collectButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass

            try:
                self.addButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass

            try:
                self.setIcons("directory",icons_list[2])
            except IndexError:
                pass

        elif propertyName == 'hideQueueButton':
            if newValue:
                self.addButton.hide()
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    """
    isCollectOk
        Description: 
        Type       : method
        Arguments  : none
        Returns    : 
    """
    def isCollectOk(self):
        if self['overrideSession'] or self.sessionId=="":
            return True
        return (self.sessionId is not None)

    """
    collectConnected
        Description: 
        Type       : slot (h.o.)
        Arguments  : none
        Returns    : nothing
    """
    def collectConnected(self):
        self.setEnabled(True and self.isCollectOk())

    """
    collectDisconnected
        Description: 
        Type       : slot (h.o.)
        Arguments  : none
        Returns    : nothing
    """
    def collectDisconnected(self):
        self.setEnabled(False)

    """
    collectReady
        Description: 
        Type       : slot (h.o.)
        Arguments  : state (bool; )
        Returns    : nothing
    """
    def collectReady(self,state):
        self.lastReady = state
        if self.isEnabled():
            self.enableCollectButton() #state and self.lastValid)

    """
    setEnergyScanConnected
        Description: Sets the beamline energy-moving capabilities.
        Type       : slot (brick)
        Arguments  : state (bool; )
                     scan  (bool/None; )
        Returns    : nothing
    """
    def setEnergyScanConnected(self,state,scan=None):
        if scan:
            self.showMADEnergies()
        else:
            self.hideMADEnergies()

    """
    setSample
        Description: 
        Type       : slot (brick)
        Arguments  : samples_list (list; )
        Returns    : nothing
    """
    def setSample(self,samples_list):
        self.selectedSamples=[]
        for sample in samples_list:
            blsample_id=sample[0]
            sample_info=sample[1]
            try:
                sample_id=int(blsample_id)
            except (TypeError,ValueError):
                try:
                    sample_id=sample_info['code']
                except KeyError:
                    sample_id=None
            if sample_id is None:
                logging.getLogger().warning("DataCollectParametersBrick: unknown sample!")
                continue

            self.selectedSamples.append(sample)

        if len(samples_list)==0:
            self.setSingleSample(None,None)
        elif len(samples_list)==1:
            if blsample_id is "":
                # Sample selected but unknown
                logging.getLogger().warning("Warning, selected sample in list (%r) is not recognised in the database" % sample_id)
                self.setSingleSample(None,None)
            else:
                # Known sample selected
                self.setSingleSample(sample_info['protein_acronym'],sample_info['name'], sample_info.get("crystal_space_group"), sample_info.get('cell'))
        else:
            #logging.info("@@@@@ %r", sample_info)
            self.setSingleSample(None, None, None)  #this is just to set spacegroup
            if sample_info.has_key('name'):
                if sample_info['name']:
                    self.setMultiSample('use sample name')
                else:
                    self.setMultiSample('use barcode')
            elif sample_info.has_key('code'):
                self.setMultiSample('use barcode')
            else:
                logging.getLogger().warning("Sample (%r) seems to have no name or barcode" % sample_info)
                self.setMultiSample('generic')


    """
    isInputValid
        Description: 
        Type       : slot (widget)
        Arguments  : input_widget
                     valid
        Returns    : nothing
        Signals    : parametersValid(current_valid<bool>)
    """
    def isInputValid(self,input_widget,valid):
        self.validDict[input_widget]=valid
        current_valid=True
        for wid in self.validDict:
            if not self.validDict[wid]:
                current_valid=False
        if current_valid!=self.lastValid:
            self.lastValid=current_valid
            self.enableCollectButton() #self.lastReady and self.lastValid)
            self.addButton.setEnabled(current_valid)
            self.emit(PYSIGNAL("parametersValid"),(current_valid,))

    """
    increaseRunNumber
        Description: 
        Type       : method
        Arguments  : count (int,=1; )
        Returns    : nothing
    """
    def increaseRunNumber(self,count=1):
        if self.paramDict["run_number"].hasAcceptableInput():
            run_number=int(self.paramDict["run_number"].text())
            run_number+=count
            inv_beam=self.paramDict["inverse_beam"].text()
            if inv_beam[0]:
                run_number+=1
            self.setRunNumber(run_number)

    """
    addToQueueClicked
        Description: 
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothing
        Signals    : collectParameterRequest(extra_parameters<dict={}>), addToQueue(collect_list<list>)
    """
    def addToQueueClicked(self):
        params_dict=self.getParamDict()
        #try:
        #    if params_dict['inverse_beam'][0] is True:
        #        params_dict['inv_interval'] = params_dict['inverse_beam'][1]
        #except Exception,msg:
        #    logging.getLogger().error("Something went wrong trying to set the inverse beam, %s" % msg)
                     
   
        try:
            centring_status=self.collectObj.diffractometer().getCentringStatus()
        except:
            pass
        else:
            if centring_status["valid"]: # Check if valid
                try:
                    centring_accepted=centring_status['accepted']
                except:
                    centring_accepted=False
                if centring_accepted: # Check if accepted:
                    # Create a new dictionary instance
                    params_dict["centring_status"]=dict(centring_status)

        extra_parameters={}
        self.emit(PYSIGNAL("collectParameterRequest"), (extra_parameters,))

        try:
            fixed_energy=extra_parameters["fixed_energy"]
        except:
            try:
                wanted_energy=extra_parameters['energy']
            except KeyError:
                try:
                    current_energy=extra_parameters['current_energy']
                except KeyError:
                    pass
                else:
                    params_dict['energy']=current_energy
            else:
                params_dict['energy']=wanted_energy
        else:
            params_dict['fixed_energy']=fixed_energy

        try:
            wanted_transmission=extra_parameters['transmission']
        except KeyError:
            try:
                current_transmission=extra_parameters['current_transmission']
            except KeyError:
                params_dict['fixed_transmission']=100
            else:
                params_dict['transmission']=current_transmission
        else:
            params_dict['transmission']=wanted_transmission

        try:
            wanted_resolution=extra_parameters['resolution']
        except KeyError:
            try:
                current_resolution=extra_parameters['current_resolution']
            except KeyError:
                pass
            else:
                params_dict['resolution']=current_resolution
        else:
            params_dict['resolution']=wanted_resolution
        try:
            params_dict['kappaStart']=extra_parameters["kappaStart"]
        except KeyError:
            params_dict['kappaStart']=-9999
        try:
            params_dict['phiStart']=extra_parameters["phiStart"]
        except KeyError:
            params_dict['phiStart']=-9999

        mad_1=params_dict['mad_1_energy']
        mad_2=params_dict['mad_2_energy']
        mad_3=params_dict['mad_3_energy']
        mad_4=params_dict['mad_4_energy']
        if mad_1[0] or mad_2[0] or mad_3[0] or mad_4[0]:
            params_list=[]

            mad_energy_order=map(string.strip,params_dict['mad_energies'].split("-"))
            energies=(mad_1,mad_2,mad_3,mad_4)
            collect_list=[]
            for energy in energies:
                if energy[0]:
                    en=float(energy[1])
                    temp_dict=copy.deepcopy(params_dict)
                    temp_dict['energy']=en
                    temp_dict['experiment_type']='MAD'
                    mad_dir=temp_dict['directory']
                    temp_dict['directory']=os.path.join(mad_dir,energy[2].strip(os.path.sep))
                    temp_dict["prefix"]+="-%s" % energy[2].strip(os.path.sep)
                    params_list.append(temp_dict)
        else:
            params_list=[params_dict]

        if len(self.selectedSamples):
            collect_list=[]

            """
            The following logic is complicated because it is prepared for doing a batch collection from a multiple selection of the samples.
            This means that the data collection parameters have to be correctly filled in, including the naming which follows a naming convention
            using the protein acronym and sample name.
            """
            for sample in self.selectedSamples:
                blsampleid=sample[0]
                sample_info=sample[1]

                for params in params_list:
                    params2=copy.deepcopy(params)
                    params2["sample_info"]=sample
                    try:
                       params2["sample_info"][1].update(params["sample_info"][1])
                    except:
                       pass

                    if len(self.selectedSamples)>1:
                        if blsampleid is not None and blsampleid!="":
                            params2['prefix']="%s-%s" % (sample_info['protein_acronym'],sample_info['name'])
                            params2['directory']=os.path.join(params2['directory'],sample_info['protein_acronym'],sample_info['name'])
                        else:
                            try:
                                prefix=str(sample_info['code'])
                            except (KeyError,TypeError):
                                prefix=None
                            if prefix=="" or prefix==str(None) or prefix is None:
                                try:
                                    basket=int(sample_info["basket"])
                                except KeyError:
                                    prefix="yourprefix"
                                else:
                                    try:
                                        vial=int(sample_info["vial"])
                                    except KeyError:
                                        prefix="yourprefix"
                                    else:
                                        prefix="b%ds%02d" % (basket,vial)

                            params2['prefix']=prefix
                            params2['directory']=os.path.join(params2['directory'],prefix)

                    collect_list.append(params2)
        else:
            collect_list=params_list

        if params_dict['inverse_beam'][0] is True:
          reference_interval = int(params_dict['inverse_beam'][1])
          wedges_list = []
          for params_dict in collect_list:
              osc_start = float(params_dict['osc_start'])
              osc_range = float(params_dict['osc_range'])
              number_images = int(params_dict['number_images'])
              overlap = float(params_dict['overlap'])
              wedges_to_collect = self.collectObj.prepare_wedges_to_collect(osc_start, number_images, osc_range, reference_interval, True, overlap)
              run_number = int(params_dict["run_number"])
              wedge_no = 0
              j = 0
              first_image_number = int(params_dict["first_image"])
              current_wedge = []
              wedges_list.append(current_wedge)
              for osc_start, wedge_size in wedges_to_collect:
                if j>=wedge_size:
                  j=0
                  wedge_no+=1
                if j == 0:
                  inv_beam_wedge = wedge_no%2
                  current_wedge.append(params_dict.copy())
                  current_wedge[-1]["osc_start"]=osc_start
                  current_wedge[-1]["run_number"]=run_number+inv_beam_wedge
                  current_wedge[-1]["number_images"]=wedge_size
                  current_wedge[-1]["first_image"]=first_image_number
                  if inv_beam_wedge:
                    first_image_number+=wedge_size
                j+=1
          collect_list = []
          for wedge in wedges_list:
            collect_list.extend(wedge)

        self.emit(PYSIGNAL("addToQueue"),(collect_list,))
        self.increaseRunNumber(len(params_list))

    """
    collectThisClicked
        Description: 
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothing
        Signals    : collectParameterRequest(extra_parameters<dict={}>),
                     collectOscillations(owner<string>,collect_list<list>)
    """
    def collectThisClicked(self):
        params_dict=self.getParamDict()

        try:
            centring_status=self.collectObj.diffractometer().getCentringStatus()
        except:
            pass
        else:
            if centring_status["valid"]: # Check if valid
                try:
                    centring_accepted=centring_status['accepted']
                except:
                    centring_accepted=False
                if centring_accepted: # Check if accepted:
                    # Create a new dictionary instance
                    params_dict["centring_status"]=dict(centring_status)

        extra_parameters={}
        self.emit(PYSIGNAL("collectParameterRequest"), (extra_parameters,))
        try:
            wanted_energy=extra_parameters['energy']
        except KeyError:
            pass
        else:
            params_dict['energy']=wanted_energy
        try:
            wanted_wavelength=extra_parameters['wavelength']
        except KeyError:
            pass
        else:
            params_dict['wavelength']=wanted_wavelength
        try:
            wanted_transmission=extra_parameters['transmission']
        except KeyError:
            pass
        else:
            params_dict['transmission']=wanted_transmission
        try:
            wanted_resolution=extra_parameters['resolution']
        except KeyError:
            pass
        else:
            params_dict['resolution']=wanted_resolution
        try:
            wanted_detdistance=extra_parameters['detdistance']
        except KeyError:
            pass
        else:
            params_dict['detdistance']=wanted_detdistance
        try:
            params_dict['kappaStart']=extra_parameters["kappaStart"]
        except KeyError:
            params_dict['kappaStart']=-9999
        try:
            params_dict['phiStart']=extra_parameters["phiStart"]
        except KeyError:
            params_dict['phiStart']=-9999

        mad_1=params_dict['mad_1_energy']
        mad_2=params_dict['mad_2_energy']
        mad_3=params_dict['mad_3_energy']
        mad_4=params_dict['mad_4_energy']
        if mad_1[0] or mad_2[0] or mad_3[0] or mad_4[0]:
            params_list=[]

            mad_energy_order=map(string.strip,params_dict['mad_energies'].split("-"))
            energies=(mad_1,mad_2,mad_3,mad_4)
            collect_list=[]
            for energy in energies:
                if energy[0]:
                    en=float(energy[1])
                    temp_dict=copy.deepcopy(params_dict)
                    temp_dict['energy']=en
                    temp_dict['experiment_type']='MAD'
                    mad_dir=temp_dict['directory']
                    temp_dict['directory']=os.path.join(mad_dir,energy[2].strip(os.path.sep))
                    params_list.append(temp_dict)
        else:
            params_list=[params_dict]

        if len(self.selectedSamples):
            collect_list=[]
            for sample in self.selectedSamples:
                blsampleid=sample[0]
                sample_info=sample[1]
                for params in params_list:
                    params2=copy.deepcopy(params)
                    params2["sample_info"]=sample

                    if len(self.selectedSamples)>1:
                        if blsampleid is not None and blsampleid!="":
                            params2['prefix']="%s-%s" % (sample_info['protein_acronym'],sample_info['name'])
                            params2['directory']=os.path.join(params2['directory'],sample_info['protein_acronym'],sample_info['name'])
                            params2['process_directory']=os.path.join(params2['process_directory'], sample_info['protein_acronym'], sample_info['name'])
                        else:
                            try:
                                prefix=str(sample_info['code'])
                            except (KeyError,TypeError):
                                prefix=None
                            if prefix=="" or prefix==str(None) or prefix is None:
                                try:
                                    basket=int(sample_info["basket"])
                                except KeyError:
                                    prefix="yourprefix"
                                else:
                                    try:
                                        vial=int(sample_info["vial"])
                                    except KeyError:
                                        prefix="yourprefix"
                                    else:
                                        prefix="b%ds%02d" % (basket,vial)

                            params2['prefix']=prefix
                            params2['directory']=os.path.join(params2['directory'],prefix)
                            params2['process_directory']=os.path.join(params2['process_directory'], prefix)

                    collect_list.append(params2)
        else:
            collect_list=params_list

        self.emit(PYSIGNAL("collectOscillations"),(str(DataCollectParametersBrick),collect_list))

    """
    getParam
        Description: 
        Type       : method
        Arguments  : param_id
        Returns    : 
    """
    def getParam(self,param_id):
        try:
            param=self.paramDict[param_id]
        except KeyError:
            param=None
        return param

    """
    run
        Description: Called when the brick is set to run mode. Sets default values in the input parameters.
        Type       : callback (BlissFramework)
        Arguments  : none
        Returns    : nothing
    """
    def run(self):
        self.setDefaultValues()

    """
    setDefaultValues
        Description: Sets default values in the input parameters.
        Type       : method
        Arguments  : prefix
                     prop_code
                     prop_number
        Returns    : nothing
    """
    def setDefaultValues(self,prefix=None,prop_code=None,prop_number=None,start_date=None):
        self.fillMadEnergiesOrder()

        self.paramDict["osc_start"].setInputText(self['degFormatString'] %  0.0)
        self.paramDict["osc_range"].setText(self['degFormatString'] %  1.0)
        self.paramDict["overlap"].setText(self['degFormatString'] %  0.0)
        self.paramDict["exposure_time"].setText(self['secFormatString'] %  1.0)
        self.paramDict["number_passes"].setText("1")
        self.paramDict["number_images"].setText("1")
        self.paramDict["run_number"].setText("1")
        self.paramDict["first_image"].setText("1")
        self.paramDict["comments"].setText("")
        self.paramDict["inverse_beam"].setInputText("1")
        self.setMADEnergies({})
        self.paramDict["inverse_beam"].setChecked(False)
        self.paramDict["inverse_beam"].setInputText("1")
        self.paramDict["processing"].setChecked(True)

        directory_prefix=self.getDirectoryPrefix()

        if start_date is None:
          start_date=time.strftime("%Y%m%d")
        
        if prop_code is not None and prop_code!="" :
            is_inhouse=self.dbServer.isInhouseUser(prop_code,prop_number)
            if is_inhouse:
                inhouse="%s%s" % (prop_code,prop_number)
                self.widgetdirectory.directory_check_regexp = ".+/inhouse/%s/%s/RAW_DATA/.*" % (inhouse, start_date)
                self.setDirectory(os.path.join('/data',directory_prefix,'inhouse',inhouse,start_date, "RAW_DATA"))
            else:
                """ External ESRF user """
                prop=prop_code+prop_number
                self.widgetdirectory.directory_check_regexp = ".+/%s/.+/%s/RAW_DATA/.*" % (prop, start_date)
                self.setDirectory(os.path.join('/data','visitor',prop,directory_prefix,start_date, "RAW_DATA"))
        else:
            self.widgetdirectory.directory_check_regexp = ".+/%s/RAW_DATA/.*" % start_date
            self.setDirectory(os.path.join('/data',directory_prefix,start_date,"RAW_DATA"))
        
        self.setPrefix(prefix)

        self.beamlineConfigurationRefresh()

    """
    scanningMADEnergies
        Description: 
        Type       : slot (brick)
        Arguments  : scanning (bool; )
        Returns    : nothing
    """
    def scanningMADEnergies(self,scanning):
        if scanning:
            self.paramDict["mad_1_energy"].setChecked(False)
            self.paramDict["mad_2_energy"].setChecked(False)
            self.paramDict["mad_3_energy"].setChecked(False)
            self.paramDict["mad_4_energy"].setChecked(False)

    """
    setMADEnergies
        Description: 
        Type       : slot (brick)
        Arguments  : energies (dict; )
        Returns    : nothing
    """
    def setMADEnergies(self,energies):
        if not self.labelDict["mad_energies"].isShown():
            return

        mad_energy_order=map(string.strip,self.paramDict["mad_energies"].text().split("-"))
        mad_pk_order="mad_%s_energy" % (mad_energy_order.index("pk")+1)
        mad_ip_order="mad_%s_energy" % (mad_energy_order.index("ip")+1)
        mad_rm_order="mad_%s_energy" % (mad_energy_order.index("rm")+1)
        mad_rm2_order="mad_%s_energy" % (mad_energy_order.index("rm2")+1)

        if energies is not None:
            self.madEnergies=energies

        try:
            pk=self.madEnergies["pk"]
        except KeyError:
            pk=None
        try:
            ip=self.madEnergies["ip"]
        except KeyError:
            ip=None
        try:
            rm=self.madEnergies["rm"]
        except KeyError:
            rm=None
        try:
            rm2=self.madEnergies["rm2"]
        except KeyError:
            rm2=None
        
        if pk is not None:
            self.paramDict[mad_pk_order].setLabelText(str(pk))
            self.paramDict[mad_pk_order].setInputText("/pk")
            if energies is not None:
                self.paramDict[mad_pk_order].setChecked(True)
            else:
                try:
                    pk_checked=self.madEnergiesCheck["pk"]
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
                    ip_checked=self.madEnergiesCheck["ip"]
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
                    rm_checked=self.madEnergiesCheck["rm"]
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
                    rm2_checked=self.madEnergiesCheck["rm2"]
                except KeyError:
                    pass
                else:
                    self.paramDict[mad_rm2_order].setChecked(rm2_checked)
            self.paramDict[mad_rm2_order].setEnabled(True)
        else:
            self.paramDict[mad_rm2_order].setEnabled(False)
            self.paramDict[mad_rm2_order].setLabelText("")
            self.paramDict[mad_rm2_order].setInputText("")

    """
    setPrefix
        Description: 
        Type       : method
        Arguments  : prefix
        Returns    : nothing
    """
    def setPrefix(self,prefix=None):
        if prefix is None:
            prefix="prefix"
        self.paramDict["prefix"].setText(prefix)

    """
    setDirectory
        Description: 
        Type       : method
        Arguments  : directory
        Returns    : nothing
    """
    def setDirectory(self,directory):
        self.paramDict["directory"].setText(str(directory))

    """
    setRunNumber
        Description: 
        Type       : method
        Arguments  : run_number
        Returns    : nothing
    """
    def setRunNumber(self,run_number):
        self.paramDict["run_number"].setText(str(run_number))

    """
    buildFileTemplate
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def buildFileTemplate(self):
        image_number_format="####"
        try:
            first_image=int(str(self.paramDict['first_image'].text()))
            number_images=int(str(self.paramDict['number_images'].text()))
            run_number=int(str(self.paramDict['run_number'].text()))
        except Exception,diag:
            template=""
        else:
            template="%s_%d_%s" % (self.paramDict['prefix'].text(),run_number,image_number_format)
            if self.imageFileSuffix is not None:
                template+=".%s" % self.imageFileSuffix

        self.paramDict['template'].setText(template)

    """
    getDirectoryPrefix
        Description: 
        Type       : method
        Arguments  : none
        Returns    : 
    """
    def getDirectoryPrefix(self):
        if self.collectObj is not None:
            return self.collectObj.directoryPrefix()
        
        return "/"

    """
    buildDirectoryTemplate
        Description: 
        Type       : method
        Arguments  : protein_acronym
                     sample_name
        Returns    : nothing
    """
    def buildDirectoryTemplate(self,protein_acronym,sample_name):
        dir_prefix=self.getDirectoryPrefix()
        curr_date_str=time.strftime("%Y%m%d")
        dir_str=None

        if self.proposalCode is not None:
            prop_str="%s%s" % (self.proposalCode,self.proposalNumber)

            if self.dbServer.isInhouseUser(self.proposalCode,self.proposalNumber):
                dir_prop="inhouse"
            else:
                dir_prop="visitor"
            
            if protein_acronym is None:
                if dir_prop == "inhouse":
                    dir_str=os.path.join('/data',dir_prefix,dir_prop,prop_str,curr_date_str,"RAW_DATA")
                else:
                    dir_str=os.path.join('/data',dir_prop,prop_str,dir_prefix,curr_date_str,"RAW_DATA")                    
            else:
                curr_sample=os.path.join(protein_acronym,sample_name)
                if dir_prop == "inhouse":
                    dir_str=os.path.join('/data',dir_prefix,dir_prop,prop_str,curr_date_str,"RAW_DATA",curr_sample)
                else:
                    dir_str=os.path.join('/data',dir_prop,prop_str,dir_prefix,curr_date_str,"RAW_DATA",curr_sample)

        else:
            dir_str=os.path.join(dir_prefix,curr_date_str, "RAW_DATA")

        if dir_str is not None:
            self.setDirectory(dir_str)

    """
    setBeamlineConfiguration
        Description: Stores the detector image extension and the default number of passes. Emits a
                     signal with the given beamline configuration.
        Type       : slot (brick)
        Arguments  : beamline_conf (dict; beamline configuration, from the data collect h.o.)
        Returns    : nothing
    """
    def setBeamlineConfiguration(self,beamline_conf):
        self.beamlineConfiguration=beamline_conf

        try:
            self.imageFileSuffix=self.beamlineConfiguration["detector_extension"]
        except:
            pass

        try:
            detector_type=self.beamlineConfiguration["detector_type"]
        except (KeyError,ValueError,TypeError):
            pass
        else:
            try:
                detector_mode=int(self.beamlineConfiguration["detector_mode"])
            except (KeyError,ValueError,TypeError):
                detector_mode=None
            self.setDetectorType(detector_type,detector_mode)

        self.beamlineConfigurationRefresh()

    """
    beamlineConfigurationRefresh
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def beamlineConfigurationRefresh(self):
        self.buildFileTemplate()

        try:
            number_of_passes=int(self.beamlineConfiguration["default_number_of_passes"])
        except (KeyError,ValueError,TypeError):
            pass
        else:
            self.paramDict["number_passes"].setText(str(number_of_passes))

        try:
            exposure_time=float(self.beamlineConfiguration["default_exposure_time"])
        except (KeyError,ValueError,TypeError):
            pass
        else:
            self.paramDict["exposure_time"].setText(str(exposure_time))

        if self.axisMotorObj is not None:
            phi_pos=self.axisMotorObj.getPosition()
            if phi_pos is not None:
                manual_phi=self.paramDict["osc_start"].text()[0]
                if not manual_phi:
                    self.paramDict["osc_start"].setInputText(self['degFormatString'] %  phi_pos)

    """
    phiMoved
        Description: Updates the start angle according to the current phi axis position.
        Type       : slot (brick)
        Arguments  : session_id      (float; the current position of the phi axis)
        Returns    : nothing
    """
    def phiMoved(self,pos):
        manual_phi=self.paramDict["osc_start"].text()[0]
        if not manual_phi:
            self.paramDict["osc_start"].setInputText(self['degFormatString'] %  pos)

    """
    setSession
        Description: Sets whoever is logged (or not logged...) in the application: proposal
                     code, number, etc.
        Type       : slot (brick)
        Arguments  : session_id      (int/None/string; None if nobody is logged, if logged and
                                      using the database, int for the session id, empty string
                                      if logged but not using the database: local user)
                     prop_code       (string; proposal code, empty "" for the local user)
                     prop_number     (int/string; proposal number, empty string "" for the local
                                      user, not used)
                     prop_id         (int; proposal database id, not currently used)
                     start_date	     (string)
        Returns    : nothing
    """
    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,start_date="-"):
        if self.collectObj is None:
            logging.getLogger().warning('DataCollectParametersBrick: disabled (no data collection hardware object)')
            return

        if prop_code is None or prop_number is None or prop_code=='' or prop_number=='':
            prefix=None
        else:
            prefix=prop_code+prop_number

        self.proposalCode=prop_code
        self.proposalNumber=prop_number
        self.sessionId=session_id

        self.setDefaultValues(prefix=prefix,prop_code=prop_code,prop_number=prop_number,start_date=start_date.split()[0].replace("-", ""))
        self.updateGUI()

    """
    updateGUI
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def updateGUI(self):
        if self.collectObj is not None and self.collectObj.isConnected():
            self.collectConnected()
            self.collectReady(self.collectObj.isReady())
        else:
            self.collectDisconnected()

    """
    setDetectorType
        Description: 
        Type       : method
        Arguments  : detector_type
                     detector_mode
        Returns    : nothing
    """
    def setDetectorType(self,detector_type,detector_mode):
        self.paramDict["detector_mode"].clear()
        self.paramDict["detector_mode"].insertItem("Software binned")
        self.paramDict["detector_mode"].insertItem("Unbinned")
        self.paramDict["detector_mode"].insertItem("Hardware binned")

        if detector_type=='adsc':
            state=self['disableDetectorMode']
            self.labelDict["detector_mode"].setDisabled(state)
            self.paramDict["detector_mode"].setDisabled(state)
            if detector_mode is not None:
                self.paramDict["detector_mode"].setCurrentItem(detector_mode)
            else:
                logging.getLogger().warning('DataCollectParametersBrick: unknown adsc default detector mode')
            self.labelDict["sum_images"].hide()
            self.paramDict["sum_images"].hide()
        elif detector_type=='marccd':
            self.paramDict["detector_mode"].setCurrentItem(detector_mode)
            self.labelDict["detector_mode"].setEnabled(False)
            self.paramDict["detector_mode"].setEnabled(False)
            self.labelDict["sum_images"].hide()
            self.paramDict["sum_images"].hide()
        elif detector_type=='pilatus':
            self.paramDict["detector_mode"].setCurrentItem(detector_mode)
            self.labelDict["detector_mode"].setEnabled(False)
            self.paramDict["detector_mode"].setEnabled(False)
            self.paramDict["sum_images"].setChecked(False)
            self.paramDict["sum_images"].setInputText("10")


    """
    fillMadEnergiesOrder
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def fillMadEnergiesOrder(self):
        self.paramDict["mad_energies"].clear()
        self.paramDict["mad_energies"].insertItem("pk - ip - rm - rm2")
        self.paramDict["mad_energies"].insertItem("ip - pk - rm - rm2")
        self.paramDict["mad_energies"].insertItem("pk - rm - ip - rm2")
        self.paramDict["mad_energies"].insertItem("ip - rm - pk - rm2")
        self.paramDict["mad_energies"].insertItem("rm - pk - ip - rm2")
        self.paramDict["mad_energies"].insertItem("rm - ip - pk - rm2")

    """
    setMultiSample
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def setMultiSample(self,prefix_type="acronym-name|barcode"):
        self.paramDict["prefix"].setReadOnly(True)
        self.setPrefix(prefix_type)
        self.paramDict["directory"].setMultiSample(True,prefix_type)
        self.paramDict["prefix"].setReadOnly(True)

        self.buildDirectoryTemplate(None,None)

    """
    setSingleSample
        Description: 
        Type       : method
        Arguments  : protein_acronym
                     sample_name
        Returns    : nothing
    """
    def setSingleSample(self,protein_acronym,sample_name,spacegroup=None,cell=None):
        if protein_acronym is None:
            if self.paramDict["prefix"].isReadOnly():
                self.setParamState("prefix","WARNING")
                if self.proposalCode is None:
                    self.setPrefix()
                    self.buildDirectoryTemplate(protein_acronym,sample_name)
                else:
                    self.setPrefix("%s%s" % (self.proposalCode,self.proposalNumber))
                    self.buildDirectoryTemplate(protein_acronym,sample_name)
        else:
            self.setParamState("prefix","OK")
            self.setPrefix("%s-%s" % (protein_acronym,sample_name))
            self.buildDirectoryTemplate(protein_acronym,sample_name)

        self.paramDict["prefix"].setReadOnly(False)
        self.paramDict["directory"].setMultiSample(False)
        
        if spacegroup is not None:
            try:
                self.lstSpaceGroup.setCurrentItem(XTAL_SPACEGROUPS.index(spacegroup))
            except:
                self.lstSpaceGroup.setCurrentItem(0)
        else:
            self.lstSpaceGroup.setCurrentItem(0)

        if cell: 
            try:
                cell_dimensions_str = cell
            except:
                cell_dimensions_str = ""
            self.txtCellDimension.setText(cell_dimensions_str) 
        else:
            self.txtCellDimension.setText("")

    """
    hideMADEnergies
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def hideMADEnergies(self):
        self.labelDict["mad_energies"].hide()
        self.paramDict["mad_energies"].hide()
        self.paramDict["mad_1_energy"].hide()
        self.paramDict["mad_2_energy"].hide()
        self.paramDict["mad_3_energy"].hide()
        self.paramDict["mad_4_energy"].hide()

    """
    showMADEnergies
        Description: 
        Type       : method
        Arguments  : none
        Returns    : nothing
    """
    def showMADEnergies(self):
        self.labelDict["mad_energies"].show()
        self.paramDict["mad_energies"].show()
        self.paramDict["mad_1_energy"].show()
        self.paramDict["mad_2_energy"].show()
        self.paramDict["mad_3_energy"].show()
        self.paramDict["mad_4_energy"].show()

    def setParamState(self,param_id,state):
        self.paramDict[param_id].setPaletteBackgroundColor(DataCollectBrick2.PARAMETER_STATE[state])

    """
    setIcons
        Description: 
        Type       : method
        Arguments  : param_id
                     icons
        Returns    : nothing
    """
    def setIcons(self,param_id,icons):
        self.paramDict[param_id].setIcons(icons)

    """
    mad_energiesActivated
        Description: 
        Type       : slot (widget)
        Arguments  : order
        Returns    : nothing
    """
    def mad_energiesActivated(self,order):
        self.setMADEnergies(None)

    """
    mad_1_energyToggled
        Description: 
        Type       : slot (widget)
        Arguments  : state
        Returns    : nothing
    """
    def mad_1_energyToggled(self,state):
        mad_energy_order=map(string.strip,self.paramDict["mad_energies"].text().split("-"))
        self.madEnergiesCheck[mad_energy_order[0]]=state

    """
    mad_2_energyToggled
        Description: 
        Type       : slot (widget)
        Arguments  : state
        Returns    : nothing
    """
    def mad_2_energyToggled(self,state):
        mad_energy_order=map(string.strip,self.paramDict["mad_energies"].text().split("-"))
        self.madEnergiesCheck[mad_energy_order[1]]=state

    """
    mad_3_energyToggled
        Description: 
        Type       : slot (widget)
        Arguments  : state
        Returns    : nothing
    """
    def mad_3_energyToggled(self,state):
        mad_energy_order=map(string.strip,self.paramDict["mad_energies"].text().split("-"))
        self.madEnergiesCheck[mad_energy_order[2]]=state

    """
    mad_4_energyToggled
        Description: 
        Type       : slot (widget)
        Arguments  : state
        Returns    : nothing
    """
    def mad_4_energyToggled(self,state):
        mad_energy_order=map(string.strip,self.paramDict["mad_energies"].text().split("-"))
        self.madEnergiesCheck[mad_energy_order[3]]=state

    """
    osc_startToggled
        Description: 
        Type       : slot (widget)
        Arguments  : state
        Returns    : nothing
    """
    def osc_startToggled(self,state):
        if not state:
            phi_pos=self.axisMotorObj.getPosition()
            if phi_pos is not None:
                self.paramDict["osc_start"].setInputText(self['degFormatString'] %  phi_pos)

    """
    prefixChanged
        Description: 
        Type       : slot (widget)
        Arguments  : text
        Returns    : nothing
        Signals    : prefixChanged
    """
    def prefixChanged(self,text):
        self.setRunNumber(1)
        self.buildFileTemplate()
        self.emit(PYSIGNAL("prefixChanged"),(text,))
    def osc_rangeChanged(self,text):
        self.emit(PYSIGNAL("rangeChanged"),(text,))
    def exposure_timeChanged(self,text):
        self.emit(PYSIGNAL("exposureChanged"),(text,))

    """
    directoryChanged
        Description: 
        Type       : slot (widget)
        Arguments  : text
        Returns    : nothing
        Signals    : directoryChanged
    """
    def directoryChanged(self,text):
        self.emit(PYSIGNAL("directoryChanged"),(text,))

    """
    directoryPressed
        Description: 
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothing
    """
    def directoryPressed(self):
        directory=self.paramDict["directory"].text()
        
        if directory!="" and not os.path.isdir(directory):
            create_directory_dialog=QMessageBox("Directory not found",\
                "Press OK to create the directory.",\
                QMessageBox.Question,QMessageBox.Ok,QMessageBox.Cancel,\
                QMessageBox.NoButton,self)
            s=self.font().pointSize()
            f=create_directory_dialog.font()
            f.setPointSize(s)
            create_directory_dialog.setFont(f)
            create_directory_dialog.updateGeometry()

            if create_directory_dialog.exec_loop()==QMessageBox.Ok:
                try:
                    os.makedirs(directory)
                except OSError,diag:
                    logging.getLogger().error("DataCollectBrick: error trying to create the directory %s (%s)" % (directory,str(diag)))
                self.paramDict["directory"].validateDirectory(directory)
                
                try:
                    os.makedirs(self.widgetdirectory.processDir)
                except OSError,diag:
                    logging.getLogger().error("DataCollectBrick: error trying to create the directory %s (%s)" % (self.widgetdirectory.processDir,str(diag)))


    """
    first_imageChanged
        Description: 
        Type       : slot (widget)
        Arguments  : text
        Returns    : nothing
    """
    def first_imageChanged(self,text):
        self.buildFileTemplate()

    """
    run_numberChanged
        Description: 
        Type       : slot (widget)
        Arguments  : text
        Returns    : nothing
        Signals    : runNumberChanged
    """
    def run_numberChanged(self,text):
        self.buildFileTemplate()
        self.emit(PYSIGNAL("runNumberChanged"),(text,))

    """
    number_imagesChanged
        Description: 
        Type       : slot (widget)
        Arguments  : text
        Returns    : nothing
    """
    def number_imagesChanged(self,text):
        self.buildFileTemplate()

    """
    getParamDict
        Description: 
        Type       : method
        Arguments  : none
        Returns    : 
    """
    def getParamDict(self):
        params={}

        for param in DataCollectParametersBrick.PARAMETERS + DataCollectParametersBrick.OTHERPARAMETERS:
            param_id=param[0]
            if self.paramDict[param_id].hasAcceptableInput():
                text=self.paramDict[param_id].text()
                if param_id=="osc_start":
                    text=text[1]
            else:
                text=None
            params[param_id]=text

        params["current_osc_start"]=self.axisMotorObj.getPosition()
        params["process_directory"]=self.widgetdirectory.processDir
        params.setdefault("sample_info", (None,{}))[1]["crystal_space_group"]=str(self.lstSpaceGroup.currentText())
        params["sample_info"][1]["cell"] = str(self.txtCellDimension.text())

        return params
    
    def getDataCollectParameters(self,paramDict={}):
        paramDict.update(self.getParamDict())
       
        self.emit(PYSIGNAL("collectParameterRequest"), (paramDict,))
 
        return paramDict


    """
    collectOscillationFinished
        Description: Called when the data collect h.o. finishes an oscillation. Increases the run number.
        Type       : slot (h.o.)
        Arguments  : owner          (string?; the owner of the finished data collection)
                     state          (None/bool; the finished state, should always be True)
                     msg            (successful message)
                     col_id         (int; entry id in the Collection database table)
                     oscillation_id (int; the oscillation id internal to the data collect h.o.)
        Returns    : nothing
    """
    def collectOscillationFinished(self,owner,state,message,col_id,oscillation_id,*args):
        if owner==str(DataCollectParametersBrick) or owner == 'EDNA':
            self.increaseRunNumber()

