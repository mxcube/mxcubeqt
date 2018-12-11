import os
import logging
from PyMca.QtBlissGraph import QtBlissGraph
from SpecClient_gevent import SpecScan
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import time

__category__ = 'mxCuBE'

class QSpecScan(QObject, SpecScan.SpecScanA):
    def __init__(self, specVersion):
        QObject.__init__(self)
        SpecScan.SpecScanA.__init__(self, specVersion)

        self.x = []
        self.y = []
        self.graph_data = None

    def newScan(self, scanParameters):
        self.x = []
        self.y = []
        self.graph_data = None

    def newScanPoint(self, i, x, y):
        # if x is in keV, transform into eV otherwise let it like it is
        self.x.append(x < 1000 and x*1000.0 or x)
        self.y.append(y)

    def scanFinished(self): 
        self.graph_data = zip(self.x, self.y)


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

class EnergyScanBrickPX2(BlissWidget):
    STATES = {
        'error': QWidget.red,\
        'ok': QWidget.green,\
        'progress': QWidget.yellow
    }

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.energyScan = None
        self.scanObject = None
        self.element = None

        self.sessionId=None
        self.blSampleId=None
        self.scanParameters={}
        self.archive_directory=None

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('formatString','formatString','##.####')
        self.addProperty('decimalPlaces', 'string', '4')

        self.defineSlot('setDirectory',())
        self.defineSlot('setPrefix',())
        self.defineSlot('setElement',())
        self.defineSlot('setSample',())
        self.defineSlot('setSession',())

        self.defineSignal('energyScanning',())
        self.defineSignal('energyScanConnected',())
        self.defineSignal('energyScanCanMove',())
        self.defineSignal('edgeScanEnergies',())
        self.defineSignal('addNewPoint',())
        self.defineSignal('newScan',())
        self.defineSignal('setDirectory',())
        self.defineSignal('setValues',())

        self.parametersBox = QHGroupBox("Parameters",self)
        #self.parametersBox.hide()
        self.parametersBox.setInsideMargin(4)
        self.parametersBox.setInsideSpacing(2)
        self.parametersBox.setCheckable(True)
#        self.parametersBox.setChecked(False)
        self.parametersBox.setChecked(True)

        QLabel("Prefix:",self.parametersBox)
        self.prefixInput=QLineEdit(self.parametersBox)
        self.prefixInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        QObject.connect(self.prefixInput,SIGNAL('textChanged(const QString &)'),self.prefixChanged)
        QLabel("Directory:",self.parametersBox)
        self.directoryInput=QLineEdit(self.parametersBox)
        self.directoryInput.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        QObject.connect(self.directoryInput,SIGNAL('textChanged(const QString &)'),self.directoryChanged)

        self.browseButton=QToolButton(self.parametersBox)
        self.browseButton.setTextLabel("Browse")
        self.browseButton.setUsesTextLabel(True)
        self.browseButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.browseButton,SIGNAL("clicked()"),self.browseButtonClicked)

        self.scanBox=QHGroupBox("Energy scan",self)
        self.scanBox.setInsideMargin(4)
        self.scanBox.setInsideSpacing(2)
        #self.scanBox.hide()
        self.startScanButton=MenuButton(self.scanBox,"Start scan")
        #self.startScanButton.hide()
        self.connect(self.startScanButton,PYSIGNAL('executeCommand'),self.startEnergyScan)
        self.connect(self.startScanButton,PYSIGNAL('cancelCommand'),self.cancelEnergyScan)

        self.statusBox=QHGroupBox("(no element)",self.scanBox)
        #self.statusBox.hide()
        #self.statusBox.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.MinimumExpanding)
        self.statusBox.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.statusBox.setAlignment(QGroupBox.AlignCenter)
        self.scanStatus=QLabel(self.statusBox)
        self.scanStatus.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.MinimumExpanding)
        self.scanStatus.setAlignment(QLabel.AlignCenter)

        box4=QVBox(self.scanBox)
        peakLabel=QLabel("Peak:",box4)
        peakLabel.setAlignment(QLabel.AlignHCenter | QLabel.AlignBottom)
        kev1Label=QLabel("(keV)",box4)
        kev1Label.setAlignment(QLabel.AlignHCenter | QLabel.AlignTop)
        #kev2Label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.peakInput=shortLineEdit(self.scanBox)
        self.peakInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.peakInput.setValidator(QDoubleValidator(self))

        box5=QVBox(self.scanBox)
        inflectionLabel=QLabel("Inflection:",box5)
        inflectionLabel.setAlignment(QLabel.AlignHCenter | QLabel.AlignBottom)
        kev2Label=QLabel("(keV)",box5)
        kev2Label.setAlignment(QLabel.AlignHCenter | QLabel.AlignTop)
        #kev1Label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.inflectionInput=shortLineEdit(self.scanBox)
        self.inflectionInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.inflectionInput.setValidator(QDoubleValidator(self))

        box6=QVBox(self.scanBox)
        remoteLabel=QLabel("Remote:",box6)
        remoteLabel.setAlignment(QLabel.AlignHCenter | QLabel.AlignBottom)
        kev3Label=QLabel("(keV)",box6)
        kev3Label.setAlignment(QLabel.AlignHCenter | QLabel.AlignTop)
        #kev3Label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.remoteInput=shortLineEdit(self.scanBox)
        self.remoteInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.remoteInput.setValidator(QDoubleValidator(self))

        box7=QVBox(self.scanBox)
        remoteLabel=QLabel("2nd Remote:",box7)
        remoteLabel.setAlignment(QLabel.AlignHCenter | QLabel.AlignBottom)
        kev4Label=QLabel("(keV)",box7)
        kev4Label.setAlignment(QLabel.AlignHCenter | QLabel.AlignTop)
        #kev4Label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.remote2Input=shortLineEdit(self.scanBox)
        self.remote2Input.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.remote2Input.setValidator(QDoubleValidator(self))

        self.acceptBox=QVBox(self.scanBox)
        self.acceptBox.setSpacing(2)
        self.acceptButton=MenuButton2(self.acceptBox,"Accept")
        self.resetButton=MenuButton2(self.acceptBox,"Reset")
        #self.acceptBox.hide()
        QObject.connect(self.resetButton,SIGNAL('clicked()'),self.resetEnergies)
        QObject.connect(self.acceptButton,SIGNAL('clicked()'),self.acceptEnergies)

        self.parametersBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.scanBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        self.instanceSynchronize("parametersBox","prefixInput","directoryInput","peakInput","inflectionInput","remoteInput","remote2Input")

        self.choochGraphs = QtBlissGraph(self)
        self.choochGraphs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        QVBoxLayout(self)
        self.layout().addWidget(self.parametersBox)
        self.layout().addWidget(self.scanBox)
        self.layout().addWidget(self.choochGraphs)

        self.setEnabled(True)

    def setIcons(self,icons):
        icons_list=icons.split()
        try:
            self.startScanButton.setIcons(icons_list[0],icons_list[1])
        except IndexError:
            pass
        try:
            self.acceptButton.setPixmap(Icons.load(icons_list[2]))
        except IndexError:
            pass
        try:
            self.resetButton.setPixmap(Icons.load(icons_list[3]))
        except IndexError:
            pass
        try:
            self.browseButton.setPixmap(Icons.load(icons_list[4]))
        except IndexError:
            pass

    def prefixChanged(self,txt):
        txt=str(txt).replace(" ","_")
        self.prefixInput.setText(txt)

    def directoryChanged(self,txt):
        txt=str(txt).replace(" ","_")
        self.directoryInput.setText(txt)

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
        #print "EnergyScanBrick.setSample",samples_list
        if len(samples_list)==0:
            self.blSampleId=None
        else:
            if len(samples_list)>1:
                logging.getLogger().warning("EnergyScanBrick: multiple samples selected (attaching scan only to first sample)!")
            for sample in samples_list:
                try:
                    blsample_id=int(sample[0])
                except:
                    pass
                else:
                    self.blSampleId=blsample_id
                    break

    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        #print "EnergyScanBrick.setSession",session_id
        self.sessionId=session_id
        if prop_code is None or prop_number is None:
          pass
        else:
          self.archive_directory=str(prop_code)+str(prop_number)

    def setDirectory(self,scan_dir):
        self.directoryInput.setText(scan_dir)
    
    def setPrefix(self,scan_prefix):
        self.prefixInput.setText(scan_prefix)

    def setElement(self,symbol,edge):
        logging.getLogger().info("ENERGYSCANBRICK.setElement %s, %s" %(symbol, edge))
        if symbol is None:
            self.clearEnergies()
            self.setEnabled(False)
            self.element=None
        else:
            if self.energyScan is not None and self.energyScan.canScanEnergy():
                self.setEnabled(True)
            self.element=(symbol,edge)
            self.statusBox.setTitle("%s - %s" % (self.element[0],self.element[1]))
            
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
            self.inflectionInput.setText("")
            self.peakInput.setText("")
            self.remoteInput.setText("")
            self.remote2Input.setText("")
            self.emit(PYSIGNAL('edgeScanEnergies'), ({},))

    def acceptEnergies(self):
        if self.peakInput.hasAcceptableInput():
            pk=float(self.peakInput.text())
        else:
            pk=None
        if self.inflectionInput.hasAcceptableInput():
            ip=float(self.inflectionInput.text())
        else:
            ip=None
        if self.remoteInput.hasAcceptableInput():
            rm=float(self.remoteInput.text())
        else:
            rm=None
        if self.remote2Input.hasAcceptableInput():
            rm2=float(self.remote2Input.text())
        else:
            rm2=None
        energies={"pk":pk, "ip":ip, "rm":rm, "rm2":rm2}
        self.emit(PYSIGNAL('edgeScanEnergies'), (energies,))

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.energyScan is not None:
                self.disconnect(self.energyScan, 'energyScanStarted', self.scanStarted)
                self.disconnect(self.energyScan, 'energyScanFinished2', self.scanFinished)
                self.disconnect(self.energyScan, 'energyScanFailed', self.scanFailed)
                self.disconnect(self.energyScan, 'scanStatusChanged', self.scanStatusChanged)
                self.disconnect(self.energyScan, 'energyScanReady', self.scanReady)
                self.disconnect(self.energyScan, 'connected', self.connected)
                self.disconnect(self.energyScan, 'disconnected', self.disconnected)
                self.disconnect(self.energyScan, 'addNewPoint', self.addNewPoint)
                self.disconnect(self.energyScan, 'newScan', self.newScan)
                self.disconnect(self.energyScan, 'setElement', self.setElement)
                self.disconnect(self.energyScan, 'setDirectory', self.setDirectory)

            self.clearEnergies()
            self.energyScan = self.getHardwareObject(newValue)
            if self.energyScan is not None:
                self.scanObject = None
                #try:
                #  specversion = self.energyScan.getCommandObject("doEnergyScan").specVersion
                #except:
                #  logging.getLogger().exception("%s: could not get spec version from Energy Scan Hardware Object", self.name())
                #else:
                #  self.scanObject = QSpecScan(specversion)

                self.connect(self.energyScan, 'energyScanStarted', self.scanStarted)
                self.connect(self.energyScan, 'energyScanFinished2', self.scanFinished)
                self.connect(self.energyScan, 'energyScanFailed', self.scanFailed)
                self.connect(self.energyScan, 'scanStatusChanged', self.scanStatusChanged)
                self.connect(self.energyScan, 'energyScanReady', self.scanReady)
                self.connect(self.energyScan, 'connected', self.connected)
                self.connect(self.energyScan, 'disconnected', self.disconnected)
                self.connect(self.energyScan, 'chooch_finished', self.chooch_finished)
                self.connect(self.energyScan, 'addNewPoint', self.addNewPoint)
                self.connect(self.energyScan, 'newScan', self.newScan)
                self.connect(self.energyScan, 'setElement', self.setElement)
                self.connect(self.energyScan, 'setDirectory', self.setDirectory)

                if self.energyScan.isConnected():
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
        logging.getLogger().info("Anonmalous Scattering Factors determination based on Chooch 5.0.6 by Gwyndaf Evans\nCopyright (C) 1994--2007\ngwyndaf@gwyndafevans.co.uk\nG. Evans & R. F. Pettifer (2001)\nJ. Appl. Cryst. 34, 82-86.")

        if self.energyScan is not None:
            if self.energyScan.isConnected():
                self.connected()
            else:
                self.disconnected()
        else:
            self.disconnected()

    def connected(self):
        can_scan=self.energyScan.canScanEnergy()
        if self.element is not None:
            self.setEnabled(can_scan)
        else:
            self.setEnabled(False)
        self.emit(PYSIGNAL('energyScanConnected'), (True,can_scan))
        self.emit(PYSIGNAL('energyScanCanMove'), (can_scan,))

    def disconnected(self):
        self.setEnabled(False)
        self.emit(PYSIGNAL('energyScanConnected'), (False,))
        self.emit(PYSIGNAL('energyScanCanMove'), (False,))

    def scanReady(self,state):
        self.startScanButton.setEnabled(state)
        self.statusBox.setEnabled(state)

    def scanStatusChanged(self,msg=None):
        if msg is None:
            msg=""
            color=self.scanBox.paletteBackgroundColor()
        else:
            color=self.STATES['progress']
        self.scanStatus.setText(str(msg))
        self.scanStatus.setPaletteBackgroundColor(QColor(color))

    def startEnergyScan(self):
        self.scanParameters={}
        go_on=True
        if self.sessionId is None or self.sessionId=="":
            res=QMessageBox.question(self,'Energy scan',"You are not properly logged, therefore your scan won't be stored in ISPyB.\nProceed with the energy scan?","Proceed","Cancel")
            if res!=0:
                go_on=False
        if not go_on:
            self.startScanButton.commandFailed()
            return

        if self.sessionId is not None and self.sessionId!="":
            self.scanParameters["sessionId"] = self.sessionId
            self.scanParameters["element"] = self.element[0]
            self.scanParameters["edgeEnergy"] = self.element[1]
            self.scanParameters["startTime"] = time.strftime("%Y-%m-%d %H:%M:%S")

        self.statusBox.setTitle("%s - %s" % (self.element[0],self.element[1]))
        self.inflectionInput.setText("")
        self.peakInput.setText("")
        self.remoteInput.setText("")
        self.remote2Input.setText("")

        scan_result=self.energyScan.startEnergyScan(self.element[0],self.element[1],\
            str(self.directoryInput.text()),\
            str(self.prefixInput.text()),\
            self.sessionId,self.blSampleId)
        if not scan_result:
            self.scanFailed()

    def cancelEnergyScan(self):
        self.energyScan.cancelEnergyScan()

    def scanStarted(self):
        self.choochGraphs.newcurve("spline", [],[])
        self.choochGraphs.newcurve("fp", [], [])
        self.choochGraphs.replot()

        self.startScanButton.commandStarted()
        self.emit(PYSIGNAL("energyScanning"),(True,))
        self.parametersBox.setEnabled(False)
        self.acceptBox.setEnabled(False)
        self.inflectionInput.setEnabled(False)
        self.peakInput.setEnabled(False)
        self.remoteInput.setEnabled(False)
        self.remote2Input.setEnabled(False)

    def scanFailed(self):
        color=self.STATES['error']
        self.scanStatus.setPaletteBackgroundColor(QColor(color))
        self.startScanButton.commandFailed()
        self.emit(PYSIGNAL("energyScanning"),(False,))
        self.parametersBox.setEnabled(True)
        self.acceptBox.setEnabled(True)
        self.inflectionInput.setEnabled(True)
        self.peakInput.setEnabled(True)
        self.remoteInput.setEnabled(True)
        self.remote2Input.setEnabled(True)

    def chooch_finished(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl,
                        rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        # display Chooch graphs
        self.choochGraphs.setTitle(title) 
        self.choochGraphs.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.choochGraphs.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.choochGraphs.replot()

#    def scanFinished(self, *args):
    def scanFinished(self, scanData):
        print "EnergyScanBrick : scanCommandFinished scanData = " , scanData
        color=self.STATES['ok']
        self.scanStatusChanged("scan finished")

        scanDesc = scanData
        #print 'self.scanObject', self.scanObject
        pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
        chooch_graph_x, chooch_graph_y1, chooch_graph_y2, \
        title = self.energyScan.choochResults
        #self.energyScan.doChooch(scanData['element'], scanData['edgeEnergy'], scanArchiveFilePrefix='/927bis/ccd/Database', scanFilePrefix='Archive2')
        #self.energyScan.doChooch(self.scanObject, scanDesc)
                                     
                                 #self.element[0], 
                                 #self.element[1])
                                 #, 
                                 #scanArchiveFilePrefix = 'scanArchiveFilePrefix' , 
                                 #scanFilePrefix = 'scanFilePrefix')

        # display Chooch graphs
        self.choochGraphs.setTitle(title) 
        self.choochGraphs.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.choochGraphs.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.choochGraphs.replot()

        # display Chooch results
        energy_str=self['formatString'] % pk
        self.peakInput.setText(energy_str)
        energy_str=self['formatString'] % ip
        self.inflectionInput.setText(energy_str)
        energy_str=self['formatString'] % rm
        self.remoteInput.setText(energy_str)

        self.scanStatus.setPaletteBackgroundColor(QColor(color))

        self.startScanButton.commandDone()
        self.emit(PYSIGNAL("energyScanning"),(False,))
        self.parametersBox.setEnabled(True)
        self.acceptBox.setEnabled(True)
        self.inflectionInput.setEnabled(True)
        self.peakInput.setEnabled(True)
        self.remoteInput.setEnabled(True)
        self.remote2Input.setEnabled(True)


    def addNewPoint(self,x,y):
        self.emit(PYSIGNAL('addNewPoint'), (x,y))
    
    def newScan(self,scanParameters):
        self.emit(PYSIGNAL('newScan'), (scanParameters,))

    def clearEnergies(self):
        self.inflectionInput.setText("")
        self.peakInput.setText("")
        self.remoteInput.setText("")
        self.remote2Input.setText("")
        self.statusBox.setTitle("(no element)")

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
