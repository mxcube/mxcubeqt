#$Log: XfeSpectrumBrick.py,v $
#Revision 1.1  2007/06/06 14:26:54  beteva
#Initial revision
#
"""
[Name] XfeSpectrumBrick

[Description]
The XfeSpectrumBrick starts an xfe spectrum acquisition with the acquisition
time and datafile directory/name as parameters, gets the mca data and if
present the calibration factors and fit configuration parameters, than
passes the data and the parameters (via the xfeSpectrumDone signal) to the
McaSpectrumBrick.

[Properties]

-------------------------------------------------
|  name    |  type  | description 
-------------------------------------------------
| mnemonic | string | xfespectrum Hardware Object
-------------------------------------------------

[Signals]

-----------------------------------------------------------------
| name                 | arguments  | description
-----------------------------------------------------------------
| xfeSpectrumDone      | mca_data   | mca data (x,y)
|                      | calib      | calibration factors (a,b,c)
|                      | config     | configuration parameters
| xfeSpectrumConnected | True/False | is SPEC connected

[Slots]

[HardwareObjects]

doSpectrum - spec command to be executed when start spectrum button is clicked
spectrumStatusMsg - status message during the execution of the procedure
spectrum_args - array with ["directory"] and ["prefix"] - datafile parameters
config_data - array with ["min"], ["max"], ["file"] - fit configuration
parameters
mca_data - shared ulong array [nb_mca_chan][2]
calib_data - shared double array [3]

Example of a valid Hardware Object XML file:
============================================
<equipment class="XfeSpectrum">
  <specversion>lid292:exp</specversion>
  <command type="spec" name="doSpectrum">eprodc_xfespectrum</command>
  <channel type="spec" name="spectrumStatusMsg">eprodc_energy_scan_msg</channel>
  <channel type="spec" name="spectrum_args">MXCOLLECT_PARS</channel>
  <channel type="spec" name="config_data">XFE_CONFIG</channel>
  <channel type="spec" name="mca_data" dispatchMode="None">XFE_DATA</channel>
  <channel type="spec" name="calib_data" dispatchMode="None">XFE_CALIB</channel>
</equipment>

"""
import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os
import numpy
import shutil

__category__ = 'mxCuBE'

class shortLineEdit(QLineEdit):
    PARAMETER_STATE={"INVALID":QWidget.red,\
        "OK":QWidget.white,\
        "WARNING":QWidget.yellow}
    def __init__(self,parent):
        QLineEdit.__init__(self,parent)
        QObject.connect(self, SIGNAL('textChanged(const QString &)'), self.txtChanged)
        self.setValidator(QDoubleValidator(self))
        self.setPaletteBackgroundColor(shortLineEdit.PARAMETER_STATE["WARNING"])
    def sizeHint(self):
        size_hint=QLineEdit.sizeHint(self)
        size_hint.setWidth(size_hint.width()/2)
        return size_hint
    def text(self):
        return str(QLineEdit.text(self))
    def txtChanged(self,txt):
        txt=str(txt)
        if self.hasAcceptableInput():
            self.setPaletteBackgroundColor(shortLineEdit.PARAMETER_STATE["OK"])
        else:
            self.setPaletteBackgroundColor(shortLineEdit.PARAMETER_STATE["WARNING"])
        self.emit(PYSIGNAL("textChanged"),(txt,))

class XfeSpectrumBrick(BlissWidget):
    STATES = {
        'error': QWidget.red,\
        'ok': QWidget.green,\
        'progress': QWidget.yellow
    }

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.xfeSpectrum = None

        self.sessionId=None
        self.blSampleId=None
        self.archive_directory=None

        self.spectrumParameters={}

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('formatString','formatString','##.####')
        self.addProperty('decimalPlaces', 'string', '4')

        self.defineSlot('setDirectory',())
        self.defineSlot('setPrefix',())
        self.defineSlot('setSample',())
        self.defineSlot('setSession',())

        self.defineSignal('xfeSpectrumRun',())
        self.defineSignal('xfeSpectrumConnected',())
        self.defineSignal('xfeSpectrumCanMove',())
        self.defineSignal('edgeSpectrumEnergies',())
        self.defineSignal('xfeSpectrumDone', ())

        self.parametersBox = QHGroupBox("XRF spectrum Parameters",self)
        self.parametersBox.setInsideMargin(4)
        self.parametersBox.setInsideSpacing(2)
        self.parametersBox.setCheckable(True)
        self.parametersBox.setChecked(False)
        QObject.connect(self.parametersBox, SIGNAL("toggled(bool)"), self.parametersBoxToggled)

        QLabel("Count time (in seconds) :", self.parametersBox)
        self.countTimeInput=QSpinBox(1, 600, 5, self.parametersBox)
        self.countTimeInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed) 
        QLabel("Prefix:",self.parametersBox)
        self.prefixInput=QLineEdit(self.parametersBox)
        self.prefixInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        QLabel("Directory:",self.parametersBox)
        self.directoryInput=QLineEdit(self.parametersBox)
        self.directoryInput.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

        self.browseButton=QToolButton(self.parametersBox)
        self.browseButton.setTextLabel("Browse")
        self.browseButton.setUsesTextLabel(True)
        self.browseButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.browseButton,SIGNAL("clicked()"),self.browseButtonClicked)

        self.spectrumBox=QHGroupBox("XRF spectrum",self)
        self.spectrumBox.setInsideMargin(4)
        self.spectrumBox.setInsideSpacing(2)
        self.startSpectrumButton=MenuButton(self.spectrumBox,"Start spectrum")
        self.connect(self.startSpectrumButton,PYSIGNAL('executeCommand'),self.startXfeSpectrum)
        self.connect(self.startSpectrumButton,PYSIGNAL('cancelCommand'),self.cancelXfeSpectrum)

        self.statusBox=QHGroupBox("XRF spectrum status",self.spectrumBox)
        #self.statusBox.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.MinimumExpanding)
        self.statusBox.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.statusBox.setAlignment(QGroupBox.AlignCenter)
        self.spectrumStatus=QLabel(self.statusBox)
        self.spectrumStatus.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.MinimumExpanding)
        self.spectrumStatus.setAlignment(QLabel.AlignCenter)

        self.parametersBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.spectrumBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        QVBoxLayout(self)
        self.layout().addWidget(self.parametersBox)
        self.layout().addWidget(self.spectrumBox)

        self.setEnabled(False)

    def parametersBoxToggled(self, on):
        self.clearEnergies()

    def setIcons(self,icons):
        icons_list=icons.split()
        try:
            self.startSpectrumButton.setIcons(icons_list[0],icons_list[1])
        except IndexError:
            pass
        try:
            self.browseButton.setPixmap(Icons.load(icons_list[2]))
        except IndexError:
            pass

    def browseButtonClicked(self):
        get_dir=QFileDialog(self)
        s=self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()
        d=get_dir.getExistingDirectory(self.directoryInput.text(),self,"",\
            "Select a directory",True,False)
        if d is not None and len(d)>0:
            self.setDirectory(d)

    def setSample(self,samples_list):
        #print "XfeSpectrumBrick.setSample",samples_list
        if len(samples_list)==0:
            self.blSampleId=None
        else:
            if len(samples_list)>1:
                logging.getLogger().warning("XfeSpectrumBrick: multiple samples selected (attaching spectrum to the first sample only)!")
            for sample in samples_list:
                try:
                    blsample_id=int(sample[0])
                except:
                    pass
                else:
                    self.blSampleId=blsample_id
                    break

    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        self.sessionId=session_id
        if prop_code is None or prop_number is None:
          pass
        else:
          self.archive_directory=str(prop_code)+str(prop_number)

    def setDirectory(self,spectrum_dir):
        self.directoryInput.setText(spectrum_dir)
    
    def setPrefix(self,spectrum_prefix):
        self.prefixInput.setText(spectrum_prefix)

    def resetEnergies(self):
        confirm_dialog=QMessageBox("Confirm reset",\
            "This will also clear your energies in the Collect tab. Press OK to reset the energies.",\
            QMessageBox.Warning,QMessageBox.Ok,QMessageBox.Cancel,\
            QMessageBox.NoButton,self)

        s=self.font().pointSize()
        f = confirm_dialog.font()
        f.setPointSize(s)
        confirm_dialog.setFont(f)
        confirm_dialog.updateGeometry()
        
        if confirm_dialog.exec_loop()==QMessageBox.Ok:
            self.emit(PYSIGNAL('edgeSpectrumEnergies'), ({},))

    def acceptEnergies(self):
        self.emit(PYSIGNAL('edgeSpectrumEnergies'), (energies,))

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.xfeSpectrum is not None:
                self.disconnect(self.xfeSpectrum, 'xfeSpectrumStarted', self.spectrumStarted)
                self.disconnect(self.xfeSpectrum, 'xfeSpectrumFinished', self.spectrumFinished)
                self.disconnect(self.xfeSpectrum, 'xfeSpectrumFailed', self.spectrumFailed)
                self.disconnect(self.xfeSpectrum, 'spectrumStatusChanged', self.spectrumStatusChanged)
                self.disconnect(self.xfeSpectrum, 'xfeSpectrumReady', self.spectrumReady)
                self.disconnect(self.xfeSpectrum, 'connected', self.connected)
                self.disconnect(self.xfeSpectrum, 'disconnected', self.disconnected)
            self.clearEnergies()
            self.xfeSpectrum = self.getHardwareObject(newValue)
            if self.xfeSpectrum is not None:
                self.connect(self.xfeSpectrum, 'xfeSpectrumStarted', self.spectrumStarted)
                self.connect(self.xfeSpectrum, 'xfeSpectrumFinished', self.spectrumFinished)
                self.connect(self.xfeSpectrum, 'xfeSpectrumFailed', self.spectrumFailed)
                self.connect(self.xfeSpectrum, 'spectrumStatusChanged', self.spectrumStatusChanged)
                self.connect(self.xfeSpectrum, 'xfeSpectrumReady', self.spectrumReady)
                self.connect(self.xfeSpectrum, 'connected', self.connected)
                self.connect(self.xfeSpectrum, 'disconnected', self.disconnected)

                if self.xfeSpectrum.isConnected():
                    self.connected()
                else:
                    self.disconnected()

            else:
                self.disconnected()

        elif propertyName == 'icons':
            self.setIcons(newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def run(self):
        if self.xfeSpectrum is not None:
            if self.xfeSpectrum.isConnected():
                self.connected()
            else:
                self.disconnected()
        else:
            self.disconnected()

    def connected(self):
        can_spectrum=self.xfeSpectrum.canSpectrum()
        self.setEnabled(can_spectrum)
        self.emit(PYSIGNAL('xfeSpectrumConnected'), (True,can_spectrum))
        self.emit(PYSIGNAL('xfeSpectrumCanMove'), (can_spectrum,))

    def disconnected(self):
        self.setEnabled(False)
        self.emit(PYSIGNAL('xfeSpectrumConnected'), (False,))
        self.emit(PYSIGNAL('xfeSpectrumCanMove'), (False,))

    def spectrumReady(self,state):
        self.startSpectrumButton.setEnabled(state)
        self.statusBox.setEnabled(state)

    def spectrumStatusChanged(self,msg=None):
        if msg is None:
            msg=""
            color=self.spectrumBox.paletteBackgroundColor()
        else:
            color=XfeSpectrumBrick.STATES['progress']
        self.spectrumStatus.setText(str(msg))
        self.spectrumStatus.setPaletteBackgroundColor(QColor(color))

    def startXfeSpectrum(self):
        self.spectrumParameters={}
        self.spectrumStatus.setText(str(""))
        go_on=True
        if self.sessionId is None or self.sessionId=="":
            res=QMessageBox.question(self,'XRF Spectrum',"You are not properly logged, therefore your spectrum won't be stored in ISPyB.\nContinue?","Yes","No")
            if res!=0:
                go_on=False
        if not go_on:
            self.startSpectrumButton.commandFailed()
            return

        if self.sessionId is not None and self.sessionId!="":
            self.spectrumParameters["sessionId"] = self.sessionId
            self.spectrumParameters["exposureTime"] = self.countTimeInput
            #self.spectrumParameters["edgeEnergy"] = self.??????
            self.spectrumParameters["startTime"] = time.strftime("%Y-%m-%d %H:%M:%S")

        self.statusBox.setTitle("starting Xfe spectrum...")
        spectrum_result=self.xfeSpectrum.startXfeSpectrum(str(self.countTimeInput.text()),
            str(self.directoryInput.text()),\
            str(self.prefixInput.text()), self.sessionId, self.blSampleId)

        if not spectrum_result:
            self.spectrumFailed()

    def cancelXfeSpectrum(self):
        self.xfeSpectrum.cancelXfeSpectrum()

    def spectrumStarted(self):
        self.startSpectrumButton.commandStarted()
        self.emit(PYSIGNAL("xfeSpectrumRun"),(True,))
        self.parametersBox.setEnabled(False)

    def spectrumFailed(self):
        color=XfeSpectrumBrick.STATES['error']
        self.spectrumStatus.setPaletteBackgroundColor(QColor(color))
        self.startSpectrumButton.commandFailed()
        self.emit(PYSIGNAL("xfeSpectrumRun"),(False,))
        self.parametersBox.setEnabled(True)

    def spectrumFinished(self, mca_data,calib,config):

        a = str(self.directoryInput.text()).split(os.path.sep)
        suffix_path=os.path.join(*a[4:])
        if 'inhouse' in a :
            a_dir = os.path.join('/data/pyarch/', a[2], suffix_path)
        else:
            a_dir = os.path.join('/data/pyarch/',a[4],a[3],*a[5:])
        if a_dir[-1]!=os.path.sep:
            a_dir+=os.path.sep
        print "a_dir --------------------------->", a_dir
        
        if not os.path.exists(os.path.dirname(a_dir)):
            os.makedirs(os.path.dirname(a_dir))
        
        filename_pattern = os.path.join(str(self.directoryInput.text()), "%s_%s_%%02d" % (str(self.prefixInput.text()),time.strftime("%d_%b_%Y")) )
        filename_pattern = os.path.extsep.join((filename_pattern, "png"))
        filename = filename_pattern % 1

        i = 2
        while os.path.isfile(filename):
            filename = filename_pattern % i
            i=i+1
        try:
            a=float(calib[0])
            b=float(calib[1])
            c=float(calib[2])
        except:
            a=0
            b=1
            c=0
        calibrated_data=[]
        for line in mca_data:
            channel=line[0]
            counts=line[1]
            energy=a + b*channel + c*channel*channel
            calibrated_line=[energy,counts]
            calibrated_data.append(calibrated_line)
        calibrated_array=numpy.array(calibrated_data)

        fig=Figure(figsize=(15, 11))
        ax=fig.add_subplot(111)
        ax.set_title(filename)
        ax.grid(True)
        #ax.plot(*(zip(*mca_data)), **{"color":'black'})
        ax.plot(*(zip(*calibrated_array)), **{"color":'black'})
        #ax.set_xlabel("MCA channel")
        #ax.set_ylabel("MCA counts")
        ax.set_xlabel("Energy")
        ax.set_ylabel("Counts")
        canvas=FigureCanvasAgg(fig)
        logging.getLogger().info("Rendering spectrum to PNG file : %s", filename)
        canvas.print_figure(filename, dpi=80)
        logging.getLogger().debug("Copying PNG file to: %s", a_dir)
        shutil.copy (filename, a_dir)
        logging.getLogger().debug("Copying .fit file to: %s", a_dir)
        #tmpname=filename.split(".")
        

        color=XfeSpectrumBrick.STATES['ok']
        self.statusBox.setTitle("Xfe spectrum status")

        config['max']=config['max_user']
        config['htmldir'] = a_dir
        try:
            self.emit(PYSIGNAL("xfeSpectrumDone"), (mca_data,calib,config))
        except:
            logging.getLogger().exception("XfeSpectrumBrick: problem updating embedded PyMCA")
        self.spectrumStatus.setPaletteBackgroundColor(QColor(color))

        self.startSpectrumButton.commandDone()
        self.emit(PYSIGNAL("xfeSpectrumRun"),(False,))
        self.parametersBox.setEnabled(True)

    def clearEnergies(self):
        self.statusBox.setTitle("XRF spectrum status")
        msg=""
        self.spectrumStatus.setText(str(msg))
        color=XfeSpectrumBrick.STATES['progress']
        self.spectrumStatus.setPaletteBackgroundColor(QColor(color))
        

class MenuButton(QToolButton):
    def __init__(self, parent, caption):
        QToolButton.__init__(self,parent)

        self.executing=None
        self.runIcon=None
        self.stopIcon=None

        self.setUsesTextLabel(True)
        self.setTextLabel(caption)

        QObject.connect(self, SIGNAL('clicked()'), self.buttonClicked)

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

    def setIcons(self,icon_run,icon_stop):
        self.runIcon=Icons.load(icon_run)
        self.stopIcon=Icons.load(icon_stop)

        if self.executing:
            self.setPixmap(self.stopIcon)
        else:
            self.setPixmap(self.runIcon)

    def buttonClicked(self):
        if self.executing:
            self.setEnabled(False)
            self.emit(PYSIGNAL('cancelCommand'), ())
        else:
            self.setEnabled(False)
            self.emit(PYSIGNAL('executeCommand'), ())

    def commandStarted(self):
        self.executing=True
        if self.stopIcon is not None:
            self.setPixmap(self.stopIcon)
        label=str(self.textLabel())
        self.setTextLabel(label.replace("Start","Stop"))
        self.setEnabled(True)

    def commandDone(self):
        self.executing=False
        if self.runIcon is not None:
            self.setPixmap(self.runIcon)
        label=str(self.textLabel())
        self.setTextLabel(label.replace("Stop","Start"))
        self.setEnabled(True)

    def commandFailed(self):
        self.commandDone()

class MenuButton2(QToolButton):
    def __init__(self, parent, caption):
        QToolButton.__init__(self,parent)
        self.setUsesTextLabel(True)
        self.setTextLabel(caption)
        self.setTextPosition(QToolButton.BesideIcon)
