import glob

from qt import *
import qttable
import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar

from DataCollectBrick2 import LineEditInput
from DataCollectParametersBrick import CheckBoxInput4
from DataCollectParametersBrick import CheckBoxInput2
from DataCollectParametersBrick import ComboBoxInput
from DataCollectParametersBrick import DirectoryInput
from DataCollectParametersBrick import PrefixInput

from XSDataMXCuBEv1_3 import XSDataMXCuBEDataSet
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataString
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataFlux
from XSDataCommon import XSDataWavelength
from XSDataCommon import XSDataLength
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataBoolean
from XSDataCommon import XSDataTime

from BlissFramework import Icons

import copy

DEBUG=0


__category__="mxCuBE"

class EDNARDBrick(BlissWidget):

    """ Data structure for input fields: variable name, text description, row,col,width, type, args
 xml tag name                           widget entry label                              row column span  widget type args """

    """ Add any parameters that are not in the data structure below because they are layed out differently. This is to be taken into account
    when passing the parameters to the next stage """
    NONGRIDPARAMETERS = ()

    OTHER_PARAMETERS = (\
("run_number",    "Run N.o",        2, 1, 0,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0), ()),\
("prefix",        "Prefix",         3, 1, 0,    PrefixInput, (), None, None, ("PYSIGNAL",)),\
("range",         "Range",          4, 1, 0,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0), ()),\
("exposure",      "Exposure",       5, 1, 0,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0), ()),\
("flux",          "Flux",           6, 1, 0,    CheckBoxInput2, ("ph/s",), QWidget.AlignRight, (QDoubleValidator,1), ()),\
)

    DIFFRACTION_PLAN_PARAMETERS = (\
("anomalous",     "Optimized SAD",      2, 4, 3,    CheckBoxInput4, (), None, None, ()),\
("dampar",        "Induce Burn Strategy",      3, 4, 3,    CheckBoxInput4, (), None, None, ()),\
("forcedSpaceGroup",                     "Force Space Group",                                      4, 4, 3,    CheckBoxInput2, ("Group",), QWidget.AlignRight, None, ()),\
("complexity",                           "Strategy Complexity",                                    5, 4, 3,    ComboBoxInput, (), None, None, ()),\
("maxExposureTimePerDataCollection","Maximum exposure time per data collection         Time(secs)",6, 4, 3,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0), ()),\
("aimedIOverSigmaAtHighestResolution",  "Aimed I over Sigma at highest Resolution",                7, 4, 3,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0.01), ()),\
("aimedResolution",                     "Define Aimed Resolution (default - highest possible)",    8, 4, 3,    CheckBoxInput2, ("Angstroms",), QWidget.AlignRight, (QDoubleValidator,0.1), ()),\
("aimedCompleteness",                   "Define Aimed Completeness (default >= 0.99 )",            9, 4, 3,    CheckBoxInput2, ("(0.0-0.99)",), QWidget.AlignRight, (QDoubleValidator,0.05), ()),\
("aimedMultiplicity",                   "Define Aimed Multiplicity (default - optimized)    ",     10, 4, 3,    CheckBoxInput2, ("",), QWidget.AlignRight, (QDoubleValidator,1), ())\
)
    SAMPLE_PARAMETERS = (\
("y",                     "Maximum vertical crystal dimension, mm",       8, 1, 0,    LineEditInput, (), QWidget.AlignRight, None, ()),\
("z",                     "Minimum vertical crystal dimension, mm",                                       9, 1, 0,    LineEditInput, (), QWidget.AlignRight, None, ()),\
("susceptibility",        "Radiation Susceptibility",                    10, 1, 0,    LineEditInput, (), QWidget.AlignRight, (QDoubleValidator,0.05), ())\
)
    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        self.chemicalComposition = None
        self.ednaHwObj=None
        self.fluxObj=None
        self.resolutionMotor=None
        self.wavelengthMotor=None
        self.currentEnergy=None
        self.currentResolution=None
        self.currentFlux=None
        self.currentWavelength=None
        self.energyMotor=None
        self.radiationDamageDict=None
        self.noRefimages = None

        self.addProperty("Wavelength motor","string","")
        self.addProperty("Energy motor","string","")
        self.addProperty("Resolution motor","string","")
        self.addProperty("EDNA config","string","")
        self.addProperty("dataCollect","string","")
        self.addProperty("photonFlux","string","")
        self.addProperty('hideInUser', 'boolean', True)
        self.addProperty('alwaysStartAt0', "boolean", False)

        self.defineSlot("userLoggedIn", ())
        self.defineSlot("setFileParameters",())
        self.defineSlot("collectOscillationFinished",())
        self.defineSlot("DataCollectParameters",())
        self.defineSlot("resolutionChanged",())
        self.defineSlot("setSample",())
        self.defineSlot("prefixChanged",())
        self.defineSlot("rangeChanged",())
        self.defineSlot("exposureChanged",())

        self.defineSignal("submitDataCollection",())
        self.defineSignal("clearQueue",())
        self.defineSignal("clearMessages",())
        self.defineSignal("characterisationDone",())
        self.defineSignal("collectOscillations", ())
        self.defineSignal("getDataCollectParameters", ())
        self.defineSignal('collectParameterRequest',())


        QVBoxLayout(self,1,1)
        self.buildGUI()

    def buildGUIParameters(self, params_desc, parent):
        grid = QWidget(parent)
        QGridLayout(grid) 

        for param in params_desc:
            param_id            =param[0]
            param_label         =param[1]
            param_row           =param[2]
            param_column        =param[3]
            param_span          =param[4]
            param_class         =param[5]
            param_class_args    =list(param[6])
            param_class_align   =param[7]
            param_class_validator=param[8]
            connect_signals     =param[9]

            if param_label:
                label=QLabel("%s:" % param_label, grid)
                grid.layout().addWidget(label,param_row,param_column)
                self.labelDict[param_id]=label

            param_class_args.append(grid)
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

            grid.layout().addMultiCellWidget(input_widget, param_row, param_row, param_column+1, param_column+1+param_span)

            self.paramDict[param_id]=input_widget
            exec("self.widget%s=input_widget" % param_id)
            exec("self.widgetLabel%s=label" % param_id)
            self.connect(input_widget,PYSIGNAL('inputValid'),self.isInputValid)
            self.connectWidget(input_widget,param_id,connect_signals)
            input_widget.show()


    def buildGUI(self):
        self.lw1=QWidget(self)
        lw1=self.lw1
        QGridLayout(lw1, 4, 2, 1, 2)
        
        self.ChHBox = QHBox(lw1)
        lbl5=QLabel("Characterise using:",self.ChHBox)
        self.methodBox=QComboBox(0,self.ChHBox)
        self.methodBox.insertItem("1 Image")
        self.methodBox.insertItem("2 Images")
        self.methodBox.insertItem("4 Images")
        self.methodBox.setCurrentItem(1)
        self.ChHBox.show()
        lw1.layout().addWidget(self.ChHBox, 0, 0)

        self.RdHBox = QHBox(lw1)
        self.rdBtn=QCheckBox("Account for Radiation Damage:",self.RdHBox)
        self.rdBtn.setChecked(True)
        QObject.connect(self.rdBtn, SIGNAL('toggled(bool)'), self.rdbtnToggled)
        self.rdBtn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.rdPars = QComboBox(0,self.RdHBox)
        self.rdPars.insertItem("of average protein Crystal")
        #self.rdPars.insertItem("User Input parameters")
        QObject.connect(self.rdPars, SIGNAL('activated(int)'), self.rdParsChanged)
        self.RdHBox.show()
        lw1.layout().addWidget(self.RdHBox, 0, 1)

        self.labelDict = {}
        self.paramDict = {}
        self.validDict = {}
        self.lastValid = True

        DCParInputs = QVGroupBox("Data Collection Parameters", lw1)
        lw1.layout().addWidget(DCParInputs, 1, 0) 
        self.buildGUIParameters(EDNARDBrick.OTHER_PARAMETERS, DCParInputs)

        SamplePlanGBox = QVGroupBox("Sample", lw1) 
        lw1.layout().addWidget(SamplePlanGBox, 2, 0)
        self.buildGUIParameters(EDNARDBrick.SAMPLE_PARAMETERS, SamplePlanGBox)
        
        DiffractionPlanGBox = QVGroupBox("Diffraction Plan",lw1)
        lw1.layout().addMultiCellWidget(DiffractionPlanGBox, 1, 2, 1, 1)
        self.buildGUIParameters(EDNARDBrick.DIFFRACTION_PLAN_PARAMETERS, DiffractionPlanGBox)       
 
        """ These 3 lines have to be added after as its not included in the above structure """
        self.paramDict["complexity"].insertItem("single subwedge")
        self.paramDict["complexity"].insertItem("few sub wedges")
        self.paramDict["complexity"].insertItem("many subwedges")

        actionsHBox = QHBox(lw1)
        actionsHBox.setSpacing(20)
        self.CCButton=QPushButton("Collect and Characterise",actionsHBox)
        QObject.connect(self.CCButton,SIGNAL("clicked()"),self.startCollectCharacterisation)
        lw1.layout().addWidget(actionsHBox,3,0)

        spacer = QSpacerItem(768, 0)
        lw1.layout().addMultiCell(spacer, 0, 3, 2, 2)


        self.layout().addWidget(lw1)
        lw1.show()
 
        QObject.connect(self.widgetprefix,SIGNAL('textChanged(const QString &)'),self.resetRunNumber)
        QObject.connect(self.widgetrange,SIGNAL('textChanged(const QString &)'),self.rangeChanged)
        QObject.connect(self.widgetexposure,SIGNAL('textChanged(const QString &)'),self.exposureChanged)

        QObject.connect(self.widgetflux.checkBox, SIGNAL('toggled(bool)'), self.fluxCheckToggled)

    def resetGUI(self):
        """Reset GUI to default values"""
        self.layout().deleteAllItems()
        self.buildGUI()
        self.getEDNADefaultConfigParameters()

    def userLoggedIn(self, logged_in):
        if not logged_in:
          self.resetGUI()
          self.run()
 
    def run(self):
        paramDict = {}
        self.emit(PYSIGNAL("getDataCollectParameters"),(paramDict,))
        try:
            self.widgetprefix.setText(str(paramDict['prefix']))
            self.widgetrange.setText(str(paramDict['osc_range']))
            self.widgetexposure.setText(str(paramDict['exposure_time']))
            self.widgetrun_number.setText(str(paramDict['run_number']))
        except Exception,msg:
            logging.getLogger().warning("There seems to be no values for prefix, range, exposure time or run, maybe the connection editor does not contain the links to the parameters brick (%s)" % msg)

    def startCollectCharacterisation(self):
        baseCollectDict={}
        logging.getLogger().info("Getting default parameters")
        self.emit(PYSIGNAL("getDataCollectParameters"),(baseCollectDict,))
        baseCollectDict['run_number'] = self.widgetrun_number.text()
        baseCollectDict['prefix'] = self.widgetprefix.text()
        baseCollectDict['osc_range'] = self.widgetrange.text()
        baseCollectDict['exposure_time'] = self.widgetexposure.text()
        #self.recharacteriseDirectoryInput.setText(baseCollectDict["directory"])
        #self.recharacteriseTemplateInput.setText("ref-%s_%s_" % (baseCollectDict["prefix"],baseCollectDict['run_number']))
        extra_parameters={}
        self.emit(PYSIGNAL("collectParameterRequest"), (extra_parameters,))
        """ Energy/wavelength is already dealt with by EDNA brick, perhaps it should be changed to this method?
        try:
            wanted_energy=extra_parameters['energy']
        except KeyError:
            pass
        else:
            baseCollectDict['energy']=wanted_energy
        try:
            wanted_wavelength=extra_parameters['wavelength']
        except KeyError:
            pass
        else:
            baseCollectDict['wavelength']=wanted_wavelength
        """
        try:
            wanted_transmission=extra_parameters['transmission']
        except KeyError:
            pass
        else:
            baseCollectDict['transmission']=wanted_transmission
        try:
            wanted_resolution=extra_parameters['resolution']
        except KeyError:
            pass
        else:
            baseCollectDict['resolution']=wanted_resolution
        try:
            wanted_detdistance=extra_parameters['detdistance']
        except KeyError:
            pass
        else:
            baseCollectDict['detdistance']=wanted_detdistance
        try:
            baseCollectDict['kappaStart']=extra_parameters["kappaStart"]
        except KeyError:
            baseCollectDict['kappaStart']=-9999
        try:
            baseCollectDict['phiStart']=extra_parameters["phiStart"]
        except KeyError:
            baseCollectDict['phiStart']=-9999

        self.CollectReferenceImages(baseCollectDict)

    def CollectReferenceImages(self,paramDict):
        """ Pass the user choice of characterise method as an index
        The images to collect and their angles are defined in the hardware object """
        methodIndex=self.methodBox.currentItem()
        self.sampleCharacteriseIndex = 0

        self.thisCollectWavelength = self.currentWavelength
        logging.getLogger().info("Wavelength used for reference images will be %6.3f, (equivalent to energy of %6.2f keV)" %(self.thisCollectWavelength,self.currentEnergy))
        if self.currentResolution is None or self.currentWavelength is None:
            logging.getLogger().error("Resolution or Wavelength are not defined. Is spec running? Is the configuration correct?")
            return
        else:
            """ Build the dictionary to collect the reference images """
            self.collectSeqList=self.ednaHwObj.buildEdnaCollectRefImagesDictList(\
                str(paramDict['directory']),\
                str(paramDict['process_directory']),\
                str(paramDict['run_number']),\
                str(paramDict['prefix']),\
                float(paramDict['exposure_time']),\
                0 if self["alwaysStartAt0"] else float("%3.2f" % paramDict['current_osc_start']),\
                float(paramDict['osc_range']),\
                self.thisCollectWavelength,\
                self.currentResolution,\
                paramDict["detector_mode"],\
                methodIndex)

            if self.collectSeqList:
                # To make the code simpler to read!
                self.collectSeqListLen = len(self.collectSeqList)
                self.emit(PYSIGNAL("collectOscillations"),("EDNA",self.collectSeqList,False))
            else:
                logging.getLogger().error("Error building collect dict for EDNA, contact software support")
                return

    def collectOscillationFinished(self,owner,state,message,col_id, _, data_collect_parameters, *args):
        if owner=="EDNA":
            runnb = int(self.widgetrun_number.text())
            self.widgetrun_number.setText(str(runnb+1))
            # xml object should already be built
            self.characterise(data_collect_parameters=data_collect_parameters)
            self.sampleCharacteriseIndex += 1

    #def recharacterise(self):
    #    self.characterise(recharacterise=True)

    def characterise(self,recharacterise=False,data_collect_parameters=None):
        """ re-initialise the parameters list based on the input xml"""
        self.ednaHwObj.initialiseEDNAdefaults()
        """ Update the edna xml default input , taking account of any user changes made in the gui """
        self.setEDNACurrentConfigParameters()

        """ Only need to clear the queue if there is no list of samples or its the first sample of a list """
        if self.sampleCharacteriseIndex == 0: 
            self.emit(PYSIGNAL("clearMessages"),())
            self.emit(PYSIGNAL("clearQueue"),(0,))

        beamsize_x = data_collect_parameters.get("beamSizeAtSampleX", 5.0E-2)
        beamsize_y = data_collect_parameters.get("beamSizeAtSampleY", 5.0E-2)
        self.ednaHwObj.characteriseWithXmlInput(data_collect_parameters["collection_id"],
                                                self.sampleCharacteriseIndex,
                                                beamsize=(beamsize_x, beamsize_y))

    """ This function is designed to get all available data out of the default xml file and put it in the gui """
    def getEDNADefaultConfigParameters(self):
        if self.ednaHwObj is not None:
            self.ednaHwObj.initialiseEDNAdefaults()
            for guiPar in EDNARDBrick.DIFFRACTION_PLAN_PARAMETERS:
                if guiPar[5] == CheckBoxInput2 or guiPar[5] == LineEditInput:
                    try:
                        lookupValue = "value = self.ednaHwObj.ednaInput.getDiffractionPlan().get%s%s().getValue()" % (guiPar[0][0].capitalize(),guiPar[0][1:])
                        exec(lookupValue)
                        if lookupValue is not None:
                            if guiPar[5] == CheckBoxInput2:
                                cmd = ("self.widget%s.setInputText('%s')" % (guiPar[0],str(value)))
                            else:
                                cmd = ("self.widget%s.setText('%s')" % (guiPar[0],str(value)))
                            exec(cmd)
                    except Exception,msg:
                        logging.getLogger().warning("Could not establish default value from edna configuration for %s." % guiPar[0])
                        logging.getLogger().debug("EDNARDBrick:getEDNACurrentConfigParameters: %s (%s)" % (guiPar[0],msg))

            for guiPar in EDNARDBrick.SAMPLE_PARAMETERS:
                if guiPar[5] == CheckBoxInput2 or guiPar[5] == LineEditInput:
                    try:
                        if guiPar[0]=='x' or guiPar[0]=='y' or guiPar[0]=='z':
                            lookupValue = "value = self.ednaHwObj.ednaInput.getSample().getSize().get%s().getValue()" % (guiPar[0][0].capitalize())
                        else:
                            lookupValue = "value = self.ednaHwObj.ednaInput.getSample().get%s%s().getValue()" % (guiPar[0][0].capitalize(),guiPar[0][1:])
                        exec(lookupValue)
                        if guiPar[5] == CheckBoxInput2:
                            cmd = ("self.widget%s.setInputText('%s')" % (guiPar[0],str(value)))
                        else:
                            cmd = ("self.widget%s.setText('%s')" % (guiPar[0],str(value)))
                        exec(cmd)
                    except:
                        logging.getLogger().warning("Could not establish default value from edna configuration for %s." % guiPar[0])
                        raise

            for guiPar in EDNARDBrick.OTHER_PARAMETERS:
                if guiPar[0] == 'flux':
                    exec("value = self.ednaHwObj.ednaInput.getExperimentalCondition().getBeam().getFlux().getValue()")
                    self.widgetflux.setInputText("%g" % value)
	    """
	    Example bit of code from hamburg (commented out)
        self.widgetaimedResolution.setInputText('5.0')
            #
	    ResPos=float(tine.pysendrecvEx("/TEST/DataCollection2/Simulation","axis_position","NAME32",1,"INTEGER",1,["Resolution"])[0])
	    print "ResPos", ResPos
	    self.widgetaimedResolution.setInputText(str(ResPos))
	    """

    def setEDNACurrentConfigParameters(self):
        # Setting EXPERIMENTAL CONDITION (incl. FLUX) AND SAMPLE
        #
        # Flux=None disables RD calcs in EDNA 
        # Beam object must be present in any case, irrespective of wether the RD Account is on or off.
        # If "off", it still carries the minExposureTimePerImage and Transmission
        #	    
        BeamObj = self.ednaHwObj.ednaInput.getExperimentalCondition().getBeam()
        BeamObj.setTransmission(XSDataDouble(self.collectObj.get_transmission()))
        BeamObj.setWavelength(XSDataWavelength(self.currentWavelength))
 
        if self.rdBtn.isChecked():
            self.defaultFluxValue = BeamObj.getFlux().getValue()

            if self.widgetflux.isChecked(0):
                FluxValue = float(self.widgetflux.text()[1])         
            else:     
                FluxValue = None
                try:
                    if self.ednaHwObj.fluxSource == 'lastImage':
                        last_intensity=self.collectObj.get_measured_intensity()
                        if last_intensity is not None:
                            FluxValue = last_intensity
                        else:
                            logging.getLogger().warning("The last image intensity is unavailable for this characterisation, taking the edna_defaults.xml value")
                            FluxValue = self.defaultFluxValue
                    elif self.ednaHwObj.fluxSource == 'currentFlux':
                        try:
                            FluxValue = float(self.currentFlux) + 0.0
                        except Exception,msg:
                            logging.getLogger().warning("Exception reading the current Flux value (%r), %s",FluxValue,msg)
                            FluxValue = 0
                        if FluxValue == 0 or FluxValue is None:
                            logging.getLogger().warning("Unable to read the current Flux value, taking the edna_defaults.xml value")
                            FluxValue = self.defaultFluxValue
                    else:
                            FluxValue = self.defaultFluxValue
                        
                            
                except Exception,msg:
                    logging.getLogger().warning("There was a problem obtaining the image intensity for this data (%s). Therefore the EDNA results may not be accurate" % msg)
                self.widgetflux.setInputText("%g" % FluxValue)
            
            BeamObj.setFlux(XSDataFlux(FluxValue))
            """
            Could dynamically switch off the radiation damage calculation if the flux value cannot be determined with reasonable defaults
            if FluxValue > 1.0e7 and FluxValue < 1.0e15:
                BeamObj.setFlux(XSDataFloat(FluxValue))
            else:
                logging.getLogger().warning("The flux is not a reasonable value (1.0e7 < flux < 1.0e15)" )
                self.rdBtn.setChecked(False)
            """
            # GB  - If Flux is there, then Sample object MUST be present
            # with SizeY, SizeX, Susceptibiliy
            #
            # Size X  - along the spindle, irrelevant
            # Size Y  - across spindle
            SizeYValue=float(self.widgety.text())
            self.ednaHwObj.ednaInput.getSample().getSize().setY(XSDataLength(SizeYValue))
            #
            # Size Z  - also across spindle
            SizeZValue=float(self.widgetz.text())
            self.ednaHwObj.ednaInput.getSample().getSize().setZ(XSDataLength(SizeZValue))
            #
            # Susceptibility
            SusceptibilityValue=float(self.widgetsusceptibility.text())
            self.ednaHwObj.ednaInput.getSample().setSusceptibility(XSDataDouble(SusceptibilityValue))
            #
            # currently the chemical composition widget is not interpreted!!!
            #if (average protein crystal) :
            self.ednaHwObj.ednaInput.getSample().setChemicalComposition(None)
            #else : if 
            #   .... here chemical composition will have to come in
            #
        else:
            # RD is disabled, so we need no beam flux, no beam size, no sample object
            self.ednaHwObj.ednaInput.getExperimentalCondition().getBeam().setFlux(None)
            self.ednaHwObj.ednaInput.getExperimentalCondition().getBeam().setSize(None)
            self.ednaHwObj.ednaInput.setSample(None) 
        #
        # Set Diffraction Plan
        
        if self.widgetdampar.isChecked(0) is True:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setStrategyOption(XSDataString("-DamPar"))
            self.ednaHwObj.do_inducedraddam = True 
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setStrategyOption(None)
            self.ednaHwObj.do_inducedraddam = False        
 
        if self.widgetanomalous.isChecked(0) is True:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAnomalousData(XSDataBoolean(True))
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAnomalousData(None)
        
        #
        # forcedSpaceGroup :: watch out - has check button, type String
        checkedValue = self.widgetforcedSpaceGroup.text()
        if checkedValue[0]:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setForcedSpaceGroup(XSDataString(checkedValue[1])) 
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setForcedSpaceGroup(None)
        #  
        #complexity    :: popup , type Sting
        userChoice = self.paramDict["complexity"].text()
        userChoiceIndex = ["single subwedge","few sub wedges","many subwedges"].index(userChoice)
        userChoice = ['none','min','full'][userChoiceIndex]
        self.ednaHwObj.ednaInput.getDiffractionPlan().setComplexity(XSDataString(userChoice))
        #
        #Maximum exposure time per data collection : no check button, Float
        value = float(self.widgetmaxExposureTimePerDataCollection.text())
        self.ednaHwObj.ednaInput.getDiffractionPlan().setMaxExposureTimePerDataCollection(XSDataTime(value))
        #
        #Aimed I over SIgma at highest resolution : no check button, Float
        value = float(self.widgetaimedIOverSigmaAtHighestResolution.text())
        self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedIOverSigmaAtHighestResolution(XSDataDouble(value))
        #
        # Aimed resolution : has check button, type Float
        checkedValue = self.widgetaimedResolution.text()
        if checkedValue[0]:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedResolution(XSDataDouble(float(checkedValue[1]))) 
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedResolution(None)
        #
        # Aimed Completeness : has check button, type Float
        checkedValue = self.widgetaimedCompleteness.text()
        if checkedValue[0]:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedCompleteness(XSDataDouble(float(checkedValue[1]))) 
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedCompleteness(None)
        #
        # Aimed Multiplicity : has check button, type Float
        checkedValue = self.widgetaimedMultiplicity.text()
        if checkedValue[0]:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedMultiplicity(XSDataDouble(float(checkedValue[1]))) 
        else:
            self.ednaHwObj.ednaInput.getDiffractionPlan().setAimedMultiplicity(None)
            
    def createStrategyDict(self, strategy_dict_list):
        collect_dict=copy.deepcopy(strategy_dict_list)
        self.emit(PYSIGNAL("clearQueue"),(0,))
        self.emit(PYSIGNAL("submitDataCollection"),(strategy_dict_list,))

    def setSample(self,samples_list):
        """ Deal with multiple samples
        If this is working then setSample can be suppressed"""
        sampleDbInfoList = []
        sampleGUIInfoList = []
        
        if len(samples_list) > 0:
            for item in samples_list:
                sample = item
                blsample_id=sample[0]
                sampleGUIInfo=sample[1]
                try:
                    sample_id=int(blsample_id)
                except (TypeError,ValueError):
                    try:
                        sample_id=sampleGUIInfo['code']
                    except KeyError:
                        sample_id=None
                if sample_id is None:
                    logging.getLogger().warning("EDNARDBrick: unknown sample!")
                if blsample_id is "":
                    logging.getLogger().warning("Warning, selected sample in list (%r) is not recognised in the database" % sample_id)
    
                """ This bit of sample info mapping is copied in 3 places, the other 2 in the DataCollectBrick !
                Maybe this could be refactored. Now it is working I should check which is the needed format between dbInfo and GUIInfo
                If I could suppress the asignments to DbInfo here that would be good."""
                sampleDbInfo={}
                blsampleid=sample[0]
                sampleGUIInfo=sample[1]
    
                if blsampleid is not None and blsampleid!="":
                    sampleDbInfo['blSampleId']=blsampleid
    
                try:
                    barcode=sampleGUIInfo['code']
                except (KeyError,TypeError):
                    barcode=None
                else:
                    sampleDbInfo['code']=barcode
                try:
                    sampleDbInfo['container_reference']=sampleGUIInfo['basket']
                except (KeyError,TypeError):
                    pass
                try:
                    sampleDbInfo['sample_location']=sampleGUIInfo['vial']
                except (KeyError,TypeError):
                    pass
                try:
                    sampleDbInfo['holderLength']=sampleGUIInfo['holder_length']
                except (KeyError,TypeError):
                    pass

                sampleDbInfoList.append(sampleDbInfo)
                sampleGUIInfoList.append(sampleGUIInfo)

            self.ednaHwObj.selectedSample = (sampleDbInfoList,sampleGUIInfoList)
        else:
            self.ednaHwObj.selectedSample = None

    def oldsetSample(self,samples_list):
        """ Only deal with one sample here , the first one selected"""
        if len(samples_list) > 0:
            sample = samples_list[0]
            blsample_id=sample[0]
            sampleGUIInfo=sample[1]
            try:
                sample_id=int(blsample_id)
            except (TypeError,ValueError):
                try:
                    sample_id=sampleGUIInfo['code']
                except KeyError:
                    sample_id=None
            if sample_id is None:
                logging.getLogger().warning("EDNARDBrick: unknown sample!")
            if blsample_id is "":
                logging.getLogger().warning("Warning, selected sample in list (%r) is not recognised in the database" % sample_id)

            """ This bit of sample info mapping is copied in 3 places, the other 2 in the DataCollectBrick !
            Maybe this could be refactored. Now it is working I should check which is the needed format between dbInfo and GUIInfo
            If I could suppress the asignments to DbInfo here that would be good."""
            sampleDbInfo={}
            blsampleid=sample[0]
            sampleGUIInfo=sample[1]

            if blsampleid is not None and blsampleid!="":
                sampleDbInfo['blSampleId']=blsampleid

            try:
                barcode=sampleGUIInfo['code']
            except (KeyError,TypeError):
                barcode=None
            else:
                sampleDbInfo['code']=barcode
            try:
                sampleDbInfo['container_reference']=sampleGUIInfo['basket']
            except (KeyError,TypeError):
                pass
            try:
                sampleDbInfo['sample_location']=sampleGUIInfo['vial']
            except (KeyError,TypeError):
                pass
            try:
                sampleDbInfo['holderLength']=sampleGUIInfo['holder_length']
            except (KeyError,TypeError):
                pass

            self.ednaHwObj.selectedSample = (sampleDbInfo,sampleGUIInfo)

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

    def isInputValid(self,input_widget,valid):
        self.validDict[input_widget]=valid
        current_valid=True
        for wid in self.validDict:
            if not self.validDict[wid]:
                current_valid=False
        if current_valid!=self.lastValid:
            self.lastValid=current_valid
            self.emit(PYSIGNAL("parametersValid"),(current_valid,))

    def popupRadiationDamageDialog(self):

        changedParameters=self.rdDialog.exec_loop()
        if changedParameters==self.rdDialog.Accepted:
            diffractParsDict =  self.rdDialog.getChemicalComposition()
            self.rdBtn.setChecked(True)
        else:
            """ If cancel pressed, restore only the chemical composition parameters """
            """ This should be implemented when the data structure for the chemical composition exists """
            self.rdBtn.setChecked(False)
            
    def rdbtnToggled(self):
        if self.rdBtn.isChecked():
            ##self.widgetflux.lineEdit.setEnabled(True)
            self.widgetflux.checkToggled(False)
            self.widgetflux.setChecked(False)
            self.widgetflux.checkBox.setEnabled(True)
            self.widgetsusceptibility.setEnabled(True)
            self.widgety.setEnabled(True)
            self.widgetz.setEnabled(True)
            self.widgetflux.setEnabled(True)
        else:
            self.widgetflux.checkToggled(False)
            self.widgetflux.lineEdit.setEnabled(False)
            self.widgetflux.setChecked(False)
            self.widgetflux.checkBox.setEnabled(False)
    
            #self.widgetsusceptibility.setChecked(False)
            self.widgetsusceptibility.setEnabled(False)
            self.widgety.setEnabled(False)
            self.widgetz.setEnabled(False)
            self.widgetflux.setEnabled(False)
            
    def propertyChanged(self, propertyName, oldValue, newValue):

        if propertyName == "Energy motor":
            if self.energyMotor is not None:
                self.disconnect(self.energyMotor,PYSIGNAL('positionChanged'),self.energyChanged)
            self.energyMotor=self.getHardwareObject(newValue)
            if self.energyMotor is not None:
                self.connect(self.energyMotor,PYSIGNAL('positionChanged'),self.energyChanged)

        if propertyName == "Wavelength motor":
            if self.wavelengthMotor is not None:
                self.disconnect(self.wavelengthMotor,PYSIGNAL('positionChanged'),self.wavelengthChanged)
            self.wavelengthMotor=self.getHardwareObject(newValue)
            if self.wavelengthMotor is not None:
                self.connect(self.wavelengthMotor,PYSIGNAL('positionChanged'),self.wavelengthChanged)

        if propertyName == "Resolution motor":
            if self.resolutionMotor is not None:
                self.disconnect(self.resolutionMotor,PYSIGNAL('positionChanged'),self.resolutionChanged)
            self.resolutionMotor=self.getHardwareObject(newValue)
            if self.resolutionMotor is not None:
                self.connect(self.resolutionMotor,PYSIGNAL('positionChanged'),self.resolutionChanged)
                try:
                    self.currentResolution = self.resolutionMotor.currentResolution
                except:
                    pass

        if propertyName == "dataCollect":
            self.collectObj=self.getHardwareObject(newValue)
            self.connect(self.collectObj, 'collectOscillationFinished', self.collectOscillationFinished)

        if propertyName == "photonFlux":
            if self.fluxObj is not None:
                self.disconnect(self.fluxObj,PYSIGNAL('valueChanged'),self.fluxChanged)
            self.fluxObj=self.getHardwareObject(newValue)
            if self.fluxObj is not None:
                self.connect(self.fluxObj,PYSIGNAL('valueChanged'),self.fluxChanged)
                try:
                    self.currentFlux = self.fluxObj.currentFlux
                except:
                    pass

        if propertyName == "EDNA config":
            if self.ednaHwObj is not None:
                self.disconnect(self.ednaHwObj,PYSIGNAL("newEDNAStrategyCreated"),self.createStrategyDict)
            self.ednaHwObj=self.getHardwareObject(newValue)
            if self.ednaHwObj is not None:
                self.connect(self.ednaHwObj,PYSIGNAL("newEDNAStrategyCreated"),self.createStrategyDict)
            """ Now that the reference to the hardware object is known,
            we can create the dialog and intisalise the parameters.
            We can also set the default difraction parameters which can be accessed from the edna default xml file """
            self.getEDNADefaultConfigParameters()
            self.rdDialog = RadiationDamageDialog(self.ednaHwObj)
       
    def rdParsChanged(self,idx):
        if idx == 1:
            self.popupRadiationDamageDialog()
            self.rdParsDefined = True
        else:
            self.rdParsDefined = False
            
    def resolutionChanged(self,resolution):
        self.currentResolution = resolution

    def fluxChanged(self,flux):
        if self.widgetflux.checkBox.isChecked():
            return
        try:
            thisFlux = float(flux)
        except:
            thisFlux = -1
        if thisFlux > 0:
            self.currentFlux = thisFlux
            self.widgetflux.setInputText("%g" % thisFlux)
        else:
            self.widgetflux.setInputText("shutter is closed ; flux will be determined automatically when doing 'Collect and Characterise'")

    def fluxCheckToggled(self, checked):
        if checked:
            if self.widgetflux.text()[1].startswith("shutter"):
              self.widgetflux.setInputText('')

    def energyChanged(self,energy):
        self.currentEnergy = energy
        self.currentWavelength = 12.398424122/self.currentEnergy

    def wavelengthChanged(self,wavelength):
        self.currentWavelength = wavelength
        self.currentEnergy = 12.398424122/wavelength

    def rangeChanged(self,txt):
        self.widgetrange.setText(txt)

    def exposureChanged(self,txt):
        self.widgetexposure.setText(txt)

    def prefixChanged(self,txt):
        self.widgetprefix.setText(txt)

    def resetRunNumber(self, _):
        self.widgetrun_number.setText('1')

    def setExpertMode(self,mode):
        #print "MotorSpinBoxBrick.setExpertMode",mode,self['hideInUser']
        self.inExpert=mode
        if not self.inExpert:
          self.widgetdampar.setChecked(False)
        if self['hideInUser']:
            if mode:
                self.widgetmaxExposureTimePerDataCollection.setEnabled(True)
                self.widgetLabelmaxExposureTimePerDataCollection.setEnabled(True)
                self.widgetdampar.setEnabled(True)
                self.widgetLabeldampar.setEnabled(True)
            else:
                self.widgetmaxExposureTimePerDataCollection.setEnabled(False)
                self.widgetLabelmaxExposureTimePerDataCollection.setEnabled(False)
                self.widgetdampar.setEnabled(False)
                self.widgetLabeldampar.setEnabled(False)


class RadiationDamageDialog(QDialog):

    def __init__(self,ho):
        QDialog.__init__(self,None)
        self.setCaption('Chemical Composition')
        self.ednaHwObj=ho


        self.labelDict = {}
        self.paramDict = {}
        self.validDict = {}
        self.lastValid = True
        widgets=[]

        QGridLayout(self, 6, 6, 1, 2)
        """ Sample description part """

        """ related to solvent definition """
        self.solventGroup = QVGroupBox("Solvent",self)
        self.solventTable=qttable.QTable(0, 2, self.solventGroup)
        self.solventTable.horizontalHeader().setLabel(0,'Atom')
        self.solventTable.horizontalHeader().setLabel(1,'Conc. (mmol)')
        self.solventTableAddHeavyAtom = QPushButton("Add Heavy atom",self.solventGroup)
        QObject.connect(self.solventTableAddHeavyAtom,SIGNAL("clicked()"),self.addHeavyAtom0)

        """ Overall Structure Definition """
        self.structure = QVGroupBox("Structure",self)
        self.sCopiesBox = QHBox(self.structure)
        self.sCopiesLbl = QLabel("Number of Copies in the Asymetric Unit",self.sCopiesBox)
        self.sCopies = LineEditInput(self.sCopiesBox)
        self.sCopies.setText('1')

        """ Chains definition """
        self.chainligandBox = QHBox(self.structure)
        self.chainStuff = QVGroupBox("Chain",self.chainligandBox)

        self.chainCopyBox0 = QHBox(self.chainStuff)
        QLabel("Number of Copies",self.chainCopyBox0)
        w = LineEditInput(self.chainCopyBox0)
        w.setText('1')
        self.chainCopyBox1 = QHBox(self.chainStuff)
        QLabel("Number of Residues (Nucleotides) in chain",self.chainCopyBox1)
        w= LineEditInput(self.chainCopyBox1)
        w.setText('1')
        QLabel("Enter below no. and type of Heavy Atoms (S,Se) in this chain",self.chainStuff)

        self.chainTable = qttable.QTable(0, 2, self.chainStuff)
        self.chainTable.horizontalHeader().setLabel(0,'Atom')
        self.chainTable.horizontalHeader().setLabel(1,'Number')
        self.chainTableAddHeavyAtom = QPushButton("Add Heavy atom",self.chainStuff)
        self.chainTableAddHeavyAtom.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        QObject.connect(self.chainTableAddHeavyAtom,SIGNAL("clicked()"),self.addHeavyAtom1)


        """ Ligand definition """
        self.ligandStuff = QVGroupBox("Ligand",self.chainligandBox)

        self.ligandCopyBox0 = QHBox(self.ligandStuff)
        QLabel("Number of Copies",self.ligandCopyBox0)
        ligandCopies = LineEditInput(self.ligandCopyBox0)
        ligandCopies.setText('1')
        self.ligandCopyBox1 = QHBox(self.ligandStuff)
        QLabel("Number of light atoms (O,C,N)",self.ligandCopyBox1)
        LineEditInput(self.ligandCopyBox1)
        QLabel("Enter below no. and type of Heavy Atoms in this ligand",self.ligandStuff)        
        
        self.ligandTable = qttable.QTable(0, 2, self.ligandStuff)
        self.ligandTable.horizontalHeader().setLabel(0,'Atom')
        self.ligandTable.horizontalHeader().setLabel(1,'Number')
        self.ligandTableAddHeavyAtom = QPushButton("Add Heavy atom",self.ligandStuff)
        self.ligandTableAddHeavyAtom.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        QObject.connect(self.ligandTableAddHeavyAtom,SIGNAL("clicked()"),self.addHeavyAtom2)

        self.layout().addMultiCellWidget(self.solventGroup,0,6,0,1)
        self.layout().addMultiCellWidget(self.structure, 0,6,2,3)
        
        self.buttonsContainer=QHBox(self)
        self.buttonsContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        
        self.buttonsBox=DialogButtonsBar(self.buttonsContainer,"Confirm","Cancel",None,self.buttonClicked,0,DialogButtonsBar.DEFAULT_SPACING)

        self.layout().addMultiCellWidget(self.buttonsContainer, 9, 9, 0, 9)
        
    """ This function should return what the user changed in the gui
    ideally in a format to easily go back into the xml edna input file """
    def getChemicalComposition(self):
        pass
    
    def addHeavyAtom0(self):
        row=self.solventTable.numRows()
        self.solventTable.insertRows(row)
        
    def addHeavyAtom1(self):
        row=self.chainTable.numRows()
        self.chainTable.insertRows(row)
        
    def addHeavyAtom2(self):
        row=self.ligandTable.numRows()
        self.ligandTable.insertRows(row)
        
    def buttonClicked(self,action):
        if action=="Confirm":
            self.accept()
        elif action=="Cancel":
            self.reject()

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
            self.emit(PYSIGNAL("parametersValid"),(current_valid,))
            
"""
InputHeavyAtomBoxes
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
class InputHeavyAtomBoxes(QWidget):
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
        self.label.seDnabled(False)
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

        
