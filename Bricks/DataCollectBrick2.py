"""
Brick to collect data: accepts the collection parameters by a slot, and calls the data collection
h.o.
Re-emits some data collect h.o. progress signals like the collectOscillationStarted/Failed/Finished.


Slots
-----
setSession(session_id<int/None/string="">,prop_code<string/None>,prop_number<int/None>,prop_id<int/None>,expiration_time<Float>)
collectOscillations(owner<string?>,oscillations_list<list>)
sampleAcceptCentring(accepted<bool>,centring_status<dict>)


Signals
-------
collectConfirm(state<None/bool>)
[emitted with None when the confirmation dialog box appears; with False if the user doesn't confirm
the collection, with True if the collection will continue]

collectUserAccept()
[emitted when the user dismisses the dialog box at the end of a data collection]

collectOscillationStarted(owner<string?>,blsampleid<int/None>,barcode<string/None>,location<tuple/None>,collect_dict<dict>,oscillation_id<int>)
[emitted when the data collection hardware object emits this same signal]

collectOscillationFinished(owner<string?>,state<None/bool=False,message<string>,col_id<int>,oscillation_id<int>)
[emitted when the data collection hardware object emits this same signal]

collectOscillationFailed(owner<string?>,state<bool=True,message<string>,col_id<int>,oscillation_id<int>)
[emitted when the data collection hardware object emits this same signal]

beamlineConfiguration(conf<dict>)
[]

collectEnableInstrumentation(state<bool>)
[emitted when the data collection starts, with state=False to disable the application instrumentation's
bricks, and with True when the data collection finished, to re-enable back the instrumention bricks]

collectEnableMinidiffCentring(state<bool>)
[emitted when the centring inside a data collection starts, with state=True to enable the application
centring instrumentation bricks, and with False when the centring finishes, to disable the application
centring instrumention bricks]

collectStartCentring()
[emitted when starting a centring inside a data collection; used to change to the Hutch tab]

collectRejectCentring()
[emitted when the data collection hardware object wants to cancel an ongoing centring (previously
started by itself) due to either a timeout or the user pressing the stop/skip oscillation]
"""



### Modules ###
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
from qt import *
from BlissFramework import Icons
import logging
import time
import os
import copy
import string
import sys
import ProgressBarBrick
import types
import inspect
import math
import DataCollectParametersBrick

### BlissFramework brick category (for the BlissFramework Builder) ###
__category__ = 'mxCuBE'



"""
DataCollectBrick2
    Type       : class (BlissWidget)
    (please see file and method headers for details)
"""
class DataCollectBrick2(BlissWidget):
    # String description of the detector binning modes
    DETECTOR_MODES=["Software binned","Unbinned","Hardware binned"]

    # Validattion colors for the parameter input fields
    PARAMETER_STATE={"INVALID":QWidget.red,\
        "OK":QWidget.white,\
        "WARNING":QWidget.yellow}

    """
    __init__
        Description : Initializes the brick: defines the BlissFramework properties, signals and
                      slots; sets internal attribute to None; creates the brick's widgets and
                      layout.
        Type        : instance constructor
        Arguments   : *args (not used; just passed to the super class)
    """
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.collectObj=None
        self.minidiff=None
        self.fileSuffix=None
        self.defaultNumberOfPasses=1
        self.lastCollectOwner=None
        self.data_collection_task = None

        self.threadRefs={}

        self.addProperty('dataCollect','string')
        self.addProperty('overrideSession','boolean',False)
        self.addProperty('icons','string','')
        self.addProperty('checkDarkCurrent','boolean',True)

        self.defineSignal('collectConfirm',())
        self.defineSignal('collectUserAccept',())
        self.defineSignal('collectOscillationStarted',())
        self.defineSignal('collectOscillationFinished',())
        self.defineSignal('collectOscillationFailed',())
        self.defineSignal('beamlineConfiguration',())
        self.defineSignal('collectEnableInstrumentation',())
        self.defineSignal('collectEnableMinidiffCentring',())
        self.defineSignal('collectStartCentring',())
        self.defineSignal('collectRejectCentring',())

        self.defineSlot('setSession',())
        self.defineSlot('collectOscillations',())
        self.defineSlot('sampleAcceptCentring',())

        self.sessionId=None
        self.proposalInfo=None
        self.expirationTime=0

        self.stopButton = QToolButton(self)
        self.stopButton.setTextPosition(QToolButton.BesideIcon)
        self.stopButton.setUsesTextLabel(True)
        self.stopButton.setTextLabel("Stop collection")
        self.stopButton.setPaletteBackgroundColor(QWidget.yellow)
        QObject.connect(self.stopButton, SIGNAL('clicked()'), self.stopCollect)

        self.skipButton = QToolButton(self)
        self.skipButton.setTextPosition(QToolButton.BesideIcon)
        self.skipButton.setUsesTextLabel(True)
        self.skipButton.setTextLabel("Skip oscillation")
        QObject.connect(self.skipButton, SIGNAL('clicked()'), self.skipOscillation)

        self.progressBar=ProgressBarBrick.ProgressBarBrick(self)
        self.progressBar['appearance']='normal'

        """
        self.abortButton = QToolButton(self)
        self.abortButton.setTextPosition(QToolButton.BesideIcon)
        self.abortButton.setUsesTextLabel(True)
        self.abortButton.setTextLabel("Abort!")
        self.abortButton.setPaletteBackgroundColor(QWidget.red)
        QObject.connect(self.abortButton, SIGNAL('clicked()'), self.abortCollect)
        """
        
        self.stopButton.setEnabled(False)
        self.skipButton.setEnabled(False)
        #self.abortButton.setEnabled(False)

        QHBoxLayout(self)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.layout().setSpacing(4)
        self.layout().addWidget(self.stopButton)
        self.layout().addWidget(self.skipButton)
        self.layout().addWidget(self.progressBar)
        #self.layout().addWidget(self.abortButton)

        self.confirmDialog=ConfirmDialog()

        self.instanceSynchronize("progressBar")

    """
    run
        Description: Called when the brick is set to run mode. Gets and stores the beamline configuration.
        Type       : callback (BlissFramework)
        Arguments  : none
        Returns    : nothing
    """
    def run(self):
        if self.collectObj is not None:
            self.setBeamlineConfiguration(self.collectObj.getBeamlineConfiguration(None))

    """
    setBeamlineConfiguration
        Description: Stores the detector image extension and the default number of passes. Emits a
                     signal with the given beamline configuration.
        Type       : method
        Arguments  : beamline_conf (dict; beamline configuration, from the data collect h.o.)
        Returns    : nothing
        Signals    : beamlineConfiguration(beamline_conf<dict>)
    """
    def setBeamlineConfiguration(self,beamline_conf):
        try:
            self.fileSuffix=beamline_conf['detector_fileext']
        except KeyError:
            self.fileSuffix=None
        try:
            self.defaultNumberOfPasses=int(beamline_conf["default_number_of_passes"])
        except:
            self.defaultNumberOfPasses=1
        self.emit(PYSIGNAL("beamlineConfiguration"),(beamline_conf,))

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
                                      user)
                     prop_id         (int; proposal database id, not currently used)
                     expiration_time (float; not currently used)
        Returns    : nothing
    """
    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        #print "DataCollectBrick session=%s code=%s number=%s" % (session_id,prop_code,prop_number)
    
        if self.collectObj is None:
            logging.getLogger().warning('DataCollectBrick2: disabled (no data collection hardware object)')
            return

        self.sessionId=session_id
        #self.expirationTime=expiration_time
        prefix=None
        if prop_code is None or prop_number is None or prop_code=='' or prop_number=='':
            self.proposalInfo=None
        else:
            prefix=prop_code+prop_number
            self.proposalInfo=(prop_code,prop_number)

    """
    showCollectResult
        Description: Displays a popup dialog box with an icon and a message, corresponding to the result
                     of a data collection.
        Type       : method
        Arguments  : stat (None/bool; the finished state, None for warning, False for error, True for
                           ok)
                     msg  (result message)
                     show (bool,=True; True for really display the dialog box)
        Returns    : tuple(stat,msg) (returns the parameters given as arguments)
    """
    def showCollectResult(self,stat,msg,show=True):
        #print "CMDCOLLECTRESULT",stat,msg,show
        if show:
            if stat is None:
                icon=QMessageBox.Warning
            elif stat is False:
                icon=QMessageBox.Critical
            else:
                icon=QMessageBox.Information

            msg=msg.strip("\n")
            msg_dialog=QMessageBox("Data collection",\
                msg,\
                icon,QMessageBox.Ok,QMessageBox.NoButton,\
                QMessageBox.NoButton,self)
            s=self.font().pointSize()
            f = msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.exec_loop()

        return (stat,msg)

    """
    callbackValidateResult
        Description: Called when the parameters validation thread finishes. If the validation result is False
                     then it just displays the error and exits, otherwise it continues with the collection by
                     displaying a confirmation dialog box with eventually warning messages, a preview of files,
                     and some final minor options.
        Type       : callback
        Arguments  : validate_result (bool; False=with errors, None=with warnings, True=everything ok)
                     owner           (string?; who is demanding the data collection)
                     collect_list    (list; a list of dictionaries, XSD-style, each with all required parameters
                                      to perform an oscillation: angles, sample information, etc.)
                     load_using_sc   (bool; if a sample inside the sample changer should be mounted by default)
        Returns    : tuple; [0]=collect code, [1]=collect message
    """
    def callbackValidateCollect(self,validate_result,owner,collect_list,load_using_sc):
        #print "VERIFY COLLECT RESULT IS",validate_result,collect_list

        # Cleanup the data collection and release resources
        #def cleanup(stat,msg,show=True):
        #    return self.showCollectResult(stat,msg,show)

        #validate_messages=None
        #if not validate_result["code"]:
        #    
        #    if validate_result["code"]==False:
        #        validate_messages=string.join(validate_result["messages"],"\n")
        #        return cleanup(False,validate_messages)
        #    else:
        #        pass
        pass 

    """
    collect
        Description: Displays a confirmation dialog box with warning messages and a preview of the
                     diffracted images. Gives some options to the user: force a dark current, take
                     snapshots, mount the selected sample, etc..
        Type       : method
        Arguments  : owner            (string?; who is demanding the data collection)
                     collect_list     (list; a list of dictionaries, XSD-style, each with all required parameters
                                       to perform an oscillation: angles, sample information, etc.)
                     validated        (tuple/None; the result of the parameters validation)
                     sc_mount_default (bool/None: if inside a parameters dictionary there's a sample changer
                                       location, should the Mount sample checkbox in the confirmation dialog
                                       box be checked by default on not)
        Returns    : None/tuple; depending on the data collection hardware object and validation, can be either
                                 None or a tuple with [0]=collect code, [1]=collect message
    """
    def collect(self,owner,collect_list,validated=None,sc_mount_default=None):
        #print "DataCollec(Brick.cmdCollect",validated,load_using_sc,collect_owner
        try:
          collect_list[0]['helical'] = int(self.helical.getValue())
        except:
          collect_list[0]['helical'] = 0

        val = 0
        try:
            val = int(self.scan4d.getValue())
        except:
            collect_list[0]['scan4d'] = 0
        try:
            if collect_list[0]['scan4d'] == 1 :
                self.scan4dm.setValue(0)
            else:
                collect_list[0]['scan4d'] = int(self.scan4d.getValue())
        except:
            collect_list[0]['scan4d'] = val
            try:
                self.scan4dm.setValue(1)
            except:
                pass
        
        # Cleanup the data collection and release resources
        def cleanup(stat,msg,show=True):
            return self.showCollectResult(stat,msg,show)

        if BlissWidget.isInstanceModeSlave():
            return cleanup(False,"Lost control meanwhile...",False)

        if len(self.collectObj.oscillations_history) == 0:
            self.confirmDialog.forceDarkImage.setChecked(True)
        else:
            self.confirmDialog.forceDarkImage.setChecked(False)

        # The expousure time changed, take dark.
        if len(self.collectObj.oscillations_history) > 0:
            try:
                previous_osc = self.collectObj.oscillations_history[-1][3]
                current_osc = collect_list[0]

                previous_exp_t = \
                    previous_osc['oscillation_sequence'][0]['exposure_time']

                current_exp_t = \
                    current_osc['oscillation_sequence'][0]['exposure_time']  
            except:
                pass
            else:
                if previous_exp_t != current_exp_t:
                    self.confirmDialog.forceDarkImage.setChecked(True)
                    

        if self['checkDarkCurrent'] == 0:
            self.confirmDialog.forceDarkImage.hide()
            
        if hasattr(self.collectObj._detector, "shutterless"):
            self.confirmDialog.forceDarkImage.hide()
            self.confirmDialog.shutterlessDatacollection.show()
            self.confirmDialog.useHelicalModeCheckbox.hide()
            self.confirmDialog.useScan4dModeCheckbox.show()
            for abcd in collect_list[0]['oscillation_sequence']:
              if abcd['overlap']==0:
                self.confirmDialog.shutterlessDatacollection.setEnabled(True)
                self.confirmDialog.shutterlessDatacollection.setChecked(True)
                self.confirmDialog.useScan4dModeCheckbox.setChecked(True)
                self.confirmDialog.useScan4dModeCheckbox.setEnabled(True)
	      else:
                self.confirmDialog.shutterlessDatacollection.hide()
                self.confirmDialog.shutterlessDatacollection.setChecked(False)
                self.confirmDialog.shutterlessDatacollection.setEnabled(False)
                self.confirmDialog.useScan4dModeCheckbox.hide()
                self.confirmDialog.useScan4dModeCheckbox.setChecked(False)
                self.confirmDialog.useScan4dModeCheckbox.setEnabled(False)
                collect_list[0]['scan4d'] = 0
        else:
            self.confirmDialog.useScan4dModeCheckbox.hide()
        s=self.font().pointSize()
        f = self.confirmDialog.font()
        f.setPointSize(s)
        self.confirmDialog.setFont(f)
        self.confirmDialog.updateGeometry()

        locations=[]
        sc_ho=self.collectObj.sampleChangerHO()
        prev_dict = collect_list[0]
        for collect_dict in collect_list:
            
            try:
                sample_reference=collect_dict['sample_reference']
            except KeyError:
                pass
            else:
                try:
                    basket=int(sample_reference['container_reference'])
                    vial=int(sample_reference['sample_location'])
                except:
                    pass
                else:
                    location=(basket,vial)
                    if sc_ho is not None:
                        sc_can_load=sc_ho.canLoadSample(None,location)
                        if sc_can_load[0] and not sc_can_load[1]:
                            try:
                                locations.index(location)
                            except ValueError:
                                locations.append(location)
                                
            try:
                oscillation_parameters = \
                    collect_dict["oscillation_sequence"][0]
            except KeyError:
                oscillation_parameters = {}

            if oscillation_parameters['number_of_images'] > 4:
                self.confirmDialog.forceDarkImage.setChecked(True)


            # Queue collection, the expousure time changed between
            # two queue elements, take dark.
            if len(collect_list) > 1:

                if collect_dict != prev_dict:
                    try:
                        previous_osc = prev_dict
                        current_osc = collect_dict

                        previous_exp_t = \
                            previous_osc['oscillation_sequence'][0]['exposure_time']

                        current_exp_t = \
                            current_osc['oscillation_sequence'][0]['exposure_time']  
                    except:
                        pass
                    else:
                        if previous_exp_t != current_exp_t:
                            self.confirmDialog.forceDarkImage.setChecked(True)

                    prev_dict = collect_dict
                        

        if len(locations)==0:
            use_sc=False
            mount_sc=False
        elif len(locations)==1:
            use_sc=True
            if sc_mount_default is None:
                mount_sc=True
            else:
                mount_sc=sc_mount_default
        else:
            use_sc=False
            mount_sc=True

        warnings=None
        #enable_snapshots = True
        set_check_snapshots = False
        is_microdiff=None
        if sc_ho is not None:
            is_microdiff = sc_ho.isMicrodiff()


##  Marcus Oscarsson 2012-06-05
##  This code does not seem to do anything usefull,
##  validated is alwaus set to {code: True} before collect is called.
##  I added the more general code below, which in my understanding
##  does the same thing.
##
##         if not is_microdiff and validated is not None:
##             if not validated["code"]:
##                 warnings=validated["messages"]
##                 try:
##                     centring_valid=validated["centring_valid"]
##                 except:
##                     centring_valid_False
##                 if centring_valid:
##                     try:
##                         enable_snapshots=not validated["centring_accepted"]
##                     except:
##                         pass

        diffractometer = self.collectObj.diffractometer()

        try:
            centring_status = diffractometer.getCentringStatus()
        except:
            centring_status = {} 

        try:
            centring_valid=centring_status['valid']
        except:
            centring_valid=False

        if centring_valid:
            try:
                centring_accepted = centring_status['accepted']
                set_check_snapshots = False
            except:
                centring_accepted = False
        else:
            centring_accepted = False

        self.confirmDialog.setCollectionParameters(collect_list,
                                                   self.fileSuffix,warnings,use_sc,mount_sc,
                                                   True, owner,
                                                   set_checked_snapshots = set_check_snapshots)
       
        if owner != "external":
          self.emit(PYSIGNAL("collectConfirm"), (None,))
          confirm_result = self.confirmDialog.exec_loop()
          #confirm_result=QDialog.Accepted
          if confirm_result!=QDialog.Accepted:
              self.emit(PYSIGNAL("collectConfirm"), (False,))
              return cleanup(False,"User didn't confirm the data collection.",False)
        self.emit(PYSIGNAL("collectConfirm"), (True,))

        # Skip already collected images?
        skip=0
        if self.confirmDialog.skipImages():
            skip=1
        for collect_dict in collect_list:
            collect_dict["skip_images"]=skip

        # Force a dark current?
        collect_list[0]['dark'] = self.confirmDialog.forceDarkCurrent()

        # Generate input files?
        for collect_dict in collect_list:
            collect_dict["input_files"]=self.confirmDialog.writeInputFiles() and 1 or 0

        #Do shutterless datacollection
        if self.confirmDialog.doShutterlessDatacollect():
            for collect_dict in collect_list:
                collect_dict["shutterless"]=1
        else:
            for collect_dict in collect_list:
                collect_dict["shutterless"]=0
        
        # Do helical oscilation ?
        if self.confirmDialog.useHelicalMode():
            for collect_dict in collect_list:
                collect_dict["helical"] = 1
        else:
           for collect_dict in collect_list:
                collect_dict["helical"] = 0

        # Do scan4d oscilation ?
        if self.confirmDialog.useScan4dMode():
            for collect_dict in collect_list:
                collect_dict["scan4d"] = 1
        else:
           for collect_dict in collect_list:
                collect_dict["scan4d"] = 0

        # Use sample changer?
        if not self.confirmDialog.mountSample():
            for collect_dict in collect_list:
                try:
                    sample_ref=collect_dict['sample_reference']
                except KeyError:
                    pass
                else:
                    try:
                        sample_ref.pop('code')
                    except KeyError:
                        pass
                    try:
                        sample_ref.pop('container_reference')
                    except KeyError:
                        pass
                    try:
                        sample_ref.pop('sample_location')
                    except KeyError:
                        pass
                    try:
                        sample_ref.pop('holderLength')
                    except KeyError:
                        pass

            collect_list[0]["take_snapshots"]=self.confirmDialog.take4Snapshots()
        else:
            for collect_dict in collect_list:
                collect_dict["keep_sample_loaded"]=True

        if owner is None:
            owner=str(DataCollectBrick2)

        #logging.info("CALLING COLLECT FROM BRICK")
        self.collectObj.collect(owner,collect_list)
        

    """
    buildOscillationFromParameters
        Description: Transforms the interface-style dictionary into the DataCollect h.o. XSD-style dictionary.
        Type       : method
        Arguments  : parameters_list (list; a list of dictionaries, interface-style, each with all required
                                      parameters to perform an oscillation: angles, sample information, etc.)
        Returns    : list; a valid list for the DataCollect h.o.
    """
    def buildOscillationFromParameters(self,parameters_list,mapFromGUIParameters=True):
        multiple_collect_list=[]
        for params_dict in parameters_list:
            fileinfo_dict={}
            sequence_dict={}
            collect_dict={}
            sample_ref={}
            
            collect_dict['EDNA_files_dir']=params_dict.get('EDNA_files_dir','')
            collect_dict['do_inducedraddam']=params_dict.get('do_inducedraddam', False)
            collect_dict['motors']=params_dict.get("motors", {})

            try:
                collect_dict['scan4d'] = int(params_dict['scan4d'])
            except:
                pass
            try:
                collect_dict['phiy_s'] = params_dict['phiy_s']
                collect_dict['phiz_s'] = params_dict['phiz_s']
                collect_dict['sampx_s'] = params_dict['sampx_s']
                collect_dict['sampy_s'] = params_dict['sampy_s']
                collect_dict['phiy_e'] = params_dict['phiy_e']
                collect_dict['phiz_e'] = params_dict['phiz_e']
                collect_dict['sampx_e'] = params_dict['sampx_e']
                collect_dict['sampy_e'] = params_dict['sampy_e']
            except:
                pass

            if mapFromGUIParameters is True:
                fileinfo_dict['directory']          =       params_dict['directory']
                fileinfo_dict['prefix']             =       params_dict['prefix']
                fileinfo_dict['process_directory']  =       params_dict['process_directory']
                fileinfo_dict['run_number']         =int(   params_dict['run_number'])
                sequence_dict['start']              =float( params_dict['osc_start'])
                sequence_dict['range']              =float( params_dict['osc_range'])
                sequence_dict['number_of_images']   =int(   params_dict['number_images'])
                sequence_dict['overlap']            =float( params_dict['overlap'])
                sequence_dict['exposure_time']      =float( params_dict['exposure_time'])
                sequence_dict['kappaStart']         =float( params_dict.get('kappaStart', -9999))
                sequence_dict['phiStart']           =float( params_dict.get('phiStart', -9999))
                sequence_dict['start_image_number'] =int(   params_dict['first_image'])
                collect_dict['comment']             =       params_dict['comments']
                try:
                    sequence_dict['number_of_passes']=int(params_dict['number_passes'])
                except:
                    sequence_dict['number_of_passes']=self.defaultNumberOfPasses
                
            else:
                fileinfo_dict = params_dict['fileinfo']
                """ This code does not handle multiple collection sequences so I can only use the first one """
                if len(sequence_dict) > 1:
                    logging.getLogger().warning('DataCollectBrick2:buildOscillationFromParameters only handles single oscillation sequences. Code needs restructuring (QueueBrick is for multiple)')
                sequence_dict = params_dict['oscillation_sequence'][0]
                if not 'kappaStart' in sequence_dict or not 'phiStart' in sequence_dict:
                  logging.getLogger().warning("kappaStart and/or kappa phiStart not taken into account within sequence parameters")
                  sequence_dict['kappaStart']=-9999
                  sequence_dict['phiStart']=-9999

                collect_dict['comment']=params_dict['comment']

            try:
                collect_dict['experiment_type']=params_dict['experiment_type']
            except:
                collect_dict['experiment_type']='SAD'
            collect_dict['fileinfo']=fileinfo_dict
            collect_dict['oscillation_sequence']=[sequence_dict]
            if (self.sessionId is not None) and (self.sessionId!="") and not self['overrideSession']:
                collect_dict['sessionId']=self.sessionId

            try:
                detector_mode=params_dict['detector_mode']
            except KeyError:
                pass
            else:
                try:
                    det_mode_index=DataCollectBrick2.DETECTOR_MODES.index(detector_mode)
                except ValueError:
                    pass
                else:
                    collect_dict['detector_mode']=det_mode_index

            try:
                collect_dict['transmission']=float(params_dict['transmission'])
            except (TypeError,ValueError,KeyError):
                pass

            try:
                collect_dict['energy']=float(params_dict['energy'])
            except (TypeError,ValueError,KeyError):
                try:
                    collect_dict['wavelength']=float(params_dict['wavelength'])
                except (TypeError,ValueError,KeyError):
                    pass

            try:
                res_dict={'upper':float(params_dict['resolution'])}
            except (TypeError,ValueError,KeyError):
                try:
                    collect_dict['detdistance']=float(params_dict['detdistance'])
                except (TypeError,ValueError,KeyError):
                    pass
            else:
                collect_dict['resolution']=res_dict
            try:
                use_inverse_beam=params_dict['inverse_beam']
            except:
                pass
            else:
                ref_interval=1
                # inverse beam as set in queue brick
                if use_inverse_beam[0] == 'True':
                    if params_dict.has_key('inv_interval'):
                        if params_dict['inv_interval'] != '':
                            ref_interval = int(params_dict['inv_interval'])
                    collect_dict['experiment_type']="%s - Inverse Beam" % collect_dict['experiment_type']
                    sequence_dict['reference_interval']=ref_interval


                # inverse beam as set in parameters brick
                elif use_inverse_beam[0] is True:
                    collect_dict['experiment_type']="%s - Inverse Beam" % collect_dict['experiment_type']
                    try:
                        ref_interval=int(use_inverse_beam[1])
                    except:
                        logging.getLogger().warning("Inverse beam interval was not set, defaulting to 1")
                    sequence_dict['reference_interval']=ref_interval

            try:
                sum_images = params_dict['sum_images']
            except:
                pass
            else:
                collect_dict['nb_sum_images'] = 0
                if sum_images[0] == True:
                    collect_dict['nb_sum_images'] = int(sum_images[1])

            try:
                sample_info=params_dict['sample_info']
            except KeyError:
                pass
            else:
                sample_ref["spacegroup"]=DataCollectParametersBrick.EDNA_SPACEGROUPS.get(sample_info[1].get("crystal_space_group",""), "")
                sample_ref["cell"] = sample_info[1].get("cell", "")

                try:
                    blsampleid=sample_info[0]
                    sample_info_dict=sample_info[1]
                except (KeyError,TypeError):
                    pass
                else:
                    if blsampleid is not None and blsampleid!="":
                        sample_ref['blSampleId']=blsampleid

                    try:
                        sample_ref['code']=sample_info_dict['code']
                    except KeyError:
                        pass
                    try:
                        sample_ref['container_reference']=sample_info_dict['basket']
                    except (KeyError,TypeError):
                        pass
                    try:
                        sample_ref['sample_location']=sample_info_dict['vial']
                    except (KeyError,TypeError):
                        pass
                    try:
                        sample_ref['holderLength']=sample_info_dict['holder_length']
                    except (KeyError,TypeError):
                        pass
                     
            collect_dict['sample_reference']=sample_ref

            try:
                centring_status=params_dict['centring_status']
            except KeyError:
                pass
            else:
                collect_dict['centring_status']=centring_status
                
            """ processing/anomalous parameter can be passed as a tuple (queue- boolItem) or simply as a value (parameters brick) """
            if params_dict.has_key('processing'):
                if type(params_dict['processing']) is types.TupleType:
                    params_dict['processing'] = params_dict['processing'][0]
                try:
                    collect_dict['processing']=params_dict['processing']
                except Exception,msg:
                    logging.getLogger().debug("No data processing will be performed %r" % msg)
                    collect_dict['processing']='False'
            else:
                collect_dict['processing']='False'

            if params_dict.has_key('processing'):
                try:
                    collect_dict['residues']=params_dict['residues']
                except Exception,msg:
                    logging.getLogger().debug("No number of residues found %r" % msg)
                    collect_dict['residues']=None
            else:
                collect_dict['residues']=False

            if params_dict.has_key('anomalous'):
                if type(params_dict['anomalous']) is types.TupleType:
                    params_dict['anomalous'] = params_dict['processing'][0]
                try:
                    collect_dict['anomalous']=params_dict['anomalous']
                except Exception,msg:
                    logging.getLogger().debug("No anomalous flag found %r" % msg)
                    collect_dict['anomalous']=False
            else:
                collect_dict['anomalous']=False

            collect_dict['in_queue']=params_dict.get('in_queue', 0)

            multiple_collect_list.append(collect_dict)

        return multiple_collect_list

    """
    collectOscillations
        Description: Entry point to perform a data collection, available to all bricks by being a slot.
                     Calls an internal method to transform the interface-style dictionary into the DataCollect
                     h.o. XSD-style dictionary. Starts a thread (required because there's a call to spec) to
                     validate the parameters giving the callback to continue the data collection after the
                     thread finishes.
        Type       : slot (brick)
        Arguments  : owner             (string?; who wants to start a data collection)
                     oscillations_list (list; a list of dictionaries, each with all required parameters to
                                        perform an oscillation: angles, sample information, etc.)
        Returns    : nothing
        Notes      : Starts a thread to validate the parameters and returns immediatly. When the validation
                     thread finishes a callback is executed that pops up a confirmation dialog box.
    """
    def collectOscillations(self,owner,oscillations_list,mapFromGUIParameters=True):
        multiple_collect_list=self.buildOscillationFromParameters(oscillations_list,mapFromGUIParameters)
        
        current_energy = self.collectObj.getCurrentEnergy()
        for oscillation in multiple_collect_list:
          if owner != "external":
            if math.fabs(float(current_energy)-float(oscillation.get("energy", current_energy)))>3E-4:
              if QMessageBox.question(self, 'Warning',"Collecting queued oscillations will trigger an energy change ; are you sure to continue ?","Yes","No")!=0:
                return
              else:
                break
              
        mount_using_sc=False
        #self.threadRefs["validateParamsThread"]=validateParamsThread(self.collectObj,\
        #    self.callbackValidateCollect,owner,multiple_collect_list,mount_using_sc,self.expirationTime)
        #self.threadRefs["validateParamsThread"].start()
        self.callbackValidateCollect({},owner,multiple_collect_list,mount_using_sc)
        return self.collect(owner,multiple_collect_list,{"code":True},mount_using_sc)
        

    """
    collectStarted
        Description: Called when the data collect h.o. starts a data collection. Resets the progress bar
                     and enables the buttons.
        Type       : slot (h.o.)
        Arguments  : owner            (string?; who started a data collection)
                     num_oscillations (number of oscillations inside the data collection, usually just 1)
        Returns    : nothing
        Signals    : collectEnableInstrumentation(False)
    """
    def collectStarted(self,owner,num_oscillations):
        self.progressBar.barReset()
        self.stopButton.setEnabled(True)
        if num_oscillations>1:
            self.skipButton.setEnabled(True)
        #self.abortButton.setEnabled(True)

        self.emit(PYSIGNAL('collectEnableInstrumentation'),(False,))

    """
    collectOscillationStarted
        Description: Called when the data collect h.o. starts an oscillation.
        Type       : slot (h.o.)
        Arguments  : owner          (string?; who started a data collection)
                     blsampleid     (None/int; the sample id in the database)
                     barcode        (None/string; the sample barcode inside the sample changer)
                     location       (None/tuple; the sample location inside the sample changer)
                     collect_dict   (dict; the given collection parameters)
                     oscillation_id (int; the oscillation id internal to the data collect h.o.)
        Returns    : nothing
        Signals    : collectOscillationStarted(owner<string?>,blsampleid<int/None>,barcode<string/None>,location<tuple/None>,collect_dict<dict>,oscillation_id<int>)
    """
    def collectOscillationStarted(self,owner,blsampleid,barcode,location,collect_dict,oscillation_id,*args):

        scan4d = collect_dict['scan4d']
        try:
            self.scan4d.setValue(int(scan4d))
        except:
            pass
        
        helic = collect_dict['helical']
        try:
            self.helical.setValue(int(helic))
        except:
            pass

        self.emit(PYSIGNAL("collectOscillationStarted"), (owner,blsampleid,barcode,location,collect_dict,oscillation_id))

    """
    collectOscillationFinished
        Description: Called when the data collect h.o. finishes an oscillation.
        Type       : slot (h.o.)
        Arguments  : owner          (string?; the owner of the finished data collection)
                     state          (None/bool; the finished state, should always be True)
                     msg            (successful message)
                     col_id         (int; entry id in the Collection database table)
                     oscillation_id (int; the oscillation id internal to the data collect h.o.)
        Returns    : nothing
        Signals    : collectOscillationFinished(owner<string?>,state<None/bool=False,message<string>,col_id<int>,oscillation_id<int>)
    """
    def collectOscillationFinished(self,owner,state,message,col_id,oscillation_id,data_collect_parameters,*args):
        self.emit(PYSIGNAL("collectOscillationFinished"), (owner,state,message,col_id,oscillation_id,data_collect_parameters))

    """
    collectOscillationFailed
        Description: Called when the data collect h.o. failed to do an oscillation.
        Type       : slot (h.o.)
        Arguments  : owner          (string?; the owner of the failed data collection)
                     state          (None/bool; the failed state: None for stopped, False for aborted)
                     msg            (stopped/aborted/error message)
                     col_id         (int; entry id in the Collection database table)
                     oscillation_id (int; the oscillation id internal to the data collect h.o.)
        Returns    : nothing
        Signals    : collectOscillationFailed(owner<string >,state<bool=True,message<string>,col_id<int>,oscillation_id<int>)
    """
    def collectOscillationFailed(self,owner,state,message,col_id,oscillation_id,*args):
        self.emit(PYSIGNAL("collectOscillationFailed"), (owner,state,message,col_id,oscillation_id))

    """
    collectNumberOfFrames
        Description: Called when the oscillation starts. Initializes the progress bar.
        Type       : slot (h.o.)
        Arguments  : status (bool; True is macro started ok)
                     number_of_images (int; total number of images in the just started collection)
        Returns    : nothing
    """
    def collectNumberOfFrames(self,number_of_images=0):
        self.progressBar.barTotalSteps(number_of_images)
        self.progressBar.barStart()

    """
    instanceModeChanged
        Description: Called when the remote access application mode changes. Closes the data
                     collection confirmation dialog box if the user loses control.
        Type       : callback (BlissFramework)
        Arguments  : mode (int)
        Returns    : nothing
    """
    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.confirmDialog.reject()

    """
    abortCollect
        Description: Called when the user wants to abort the current oscillation.
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothing
    """
    def abortCollect(self):
        self.collectObj.abortCollect(self.lastCollectOwner)
        #self.collectFailed("Brick'>","Failed","User Hit Abort")
        

    """
    stopCollect
        Description: Called when the user wants to stop the current oscillation. Pops up a
                     confirmation dialog box.
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothing
    """
    def stopCollect(self):
        ## stop_dialog=QMessageBox("Stop collection",\
##             "Are you sure you want to stop the current data collection?",\
##             QMessageBox.Question,QMessageBox.Yes,QMessageBox.No,\
##             QMessageBox.NoButton,self)

##         s=self.font().pointSize()
##         f = stop_dialog.font()
##         f.setPointSize(s)
##         stop_dialog.setFont(f)
##         stop_dialog.updateGeometry()
##         if stop_dialog.exec_loop()==QMessageBox.Yes:
##             self.collectObj.stopCollect(self.lastCollectOwner)
        self.collectObj.stopCollect(self.lastCollectOwner)


    """
    skipOscillation
        Description: Called when the user wants to skip the current oscillation
        Type       : slot (widget)
        Arguments  : none
        Returns    : nothinggrep "Image " *
    """
    def skipOscillation(self):
        self.collectObj.skipOscillation(self)

    """
    collectImageTaken
        Description: Called when the data collect h.o. exposes an image. Updates the progress
                     bar.
        Type       : slot (h.o.)
        Arguments  : image_number (int; index of the diffracted image starting at 1)
        Returns    : nothing
    """
    def collectImageTaken(self,image_number, stored_dict={"saved_number":1}):
## Marcus Oscarsson 2012-06-12
##    
##         if self.progressBar.progressBar.progress() < 0:
##           stored_dict["saved_number"] = 1
##         else:
##           stored_dict["saved_number"] += 1
        self.progressBar.barProgress(image_number)

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
        if propertyName == 'dataCollect':
            self.minidiff=None
            if self.collectObj is not None:
                self.disconnect(self.collectObj, PYSIGNAL('collectStarted'), self.collectStarted)
                self.disconnect(self.collectObj, PYSIGNAL('collectOscillationStarted'), self.collectOscillationStarted)
                self.disconnect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.collectOscillationFinished)
                self.disconnect(self.collectObj, PYSIGNAL('collectOscillationFailed'), self.collectOscillationFailed)
                self.disconnect(self.collectObj, PYSIGNAL('collectNumberOfFrames'), self.collectNumberOfFrames)
                self.disconnect(self.collectObj, PYSIGNAL('collectImageTaken'), self.collectImageTaken)
                self.disconnect(self.collectObj, PYSIGNAL('collectEnded'), self.collectEnded)
                self.disconnect(self.collectObj, PYSIGNAL('collectFailed'), self.collectFailed)
                self.disconnect(self.collectObj, PYSIGNAL('collectValidateCentring'), self.collectValidateCentring)
                self.disconnect(self.collectObj, PYSIGNAL('collectRejectCentring'), self.collectRejectCentring)

            self.collectObj=self.getHardwareObject(newValue)
            
            if self.collectObj is not None:
                self.minidiff = self.collectObj.diffractometer()
                try:
                    self.helical  = self.collectObj.getChannelObject('helical')
                except:
                    pass
                
                try:
                    self.scan4d = self.collectObj.getChannelObject('scan4d')
                    self.scan4dm = self.collectObj.getChannelObject('scan4dm')
                except:
                    pass
                
                self.connect(self.collectObj, PYSIGNAL('collectStarted'), self.collectStarted)
                self.connect(self.collectObj, PYSIGNAL('collectOscillationStarted'), self.collectOscillationStarted)
                self.connect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.collectOscillationFinished)
                self.connect(self.collectObj, PYSIGNAL('collectOscillationFailed'), self.collectOscillationFailed)
                self.connect(self.collectObj, PYSIGNAL('collectNumberOfFrames'), self.collectNumberOfFrames)
                self.connect(self.collectObj, PYSIGNAL('collectImageTaken'), self.collectImageTaken)
                self.connect(self.collectObj, PYSIGNAL('collectEnded'), self.collectEnded)
                self.connect(self.collectObj, PYSIGNAL('collectFailed'), self.collectFailed)
                self.connect(self.collectObj, PYSIGNAL('collectValidateCentring'), self.collectValidateCentring)
                self.connect(self.collectObj, PYSIGNAL('collectRejectCentring'), self.collectRejectCentring)

        elif propertyName == 'icons':
            icons_list=newValue.split()

            try:
                self.stopButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass

            try:
                self.skipButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass

            #try:
            #    self.abortButton.setPixmap(Icons.load(icons_list[2]))
            #except IndexError:
            #    pass
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    """
    collectValidateCentring
        Description: Re-emits the data collect h.o. signal to start a centring, while initializing
                     a data collection. First it emits a signal to re-enable the centring bricks
                     or application tab.
        Type       : slot (h.o.)
        Arguments  : sample_was_loaded (bool; should always be True)
                     fileinfo          (dict; "fileinfo" key of the current collection parameters)
        Returns    : nothing
        Signals    : collectEnableMinidiffCentring(True),collectStartCentring()
    """
    def collectValidateCentring(self,sample_was_loaded,snapshot_fileinfo):
        self.emit(PYSIGNAL("collectEnableMinidiffCentring"),(True,))
        self.emit(PYSIGNAL("collectStartCentring"),())

    """
    collectRejectCentring
        Description: Re-emits the data collect h.o. signal to stop the ongoing centring
        Type       : slot (h.o.)
        Arguments  : none
        Returns    : nothing
        Signals    : collectRejectCentring()
    """
    def collectRejectCentring(self):
        self.emit(PYSIGNAL("collectRejectCentring"),())

    """
    sampleAcceptCentring
        Description: Called by an external brick to continue or cancel the ongoing data collection.
        Type       : slot (brick)
        Arguments  : accepted        (bool; if the centring was successful or not)
                     centring_status (dict; motor positions, snapshots, etc.)
        Returns    : nothing
        Signals    : collectEnableMinidiffCentring(False)
    """
    def sampleAcceptCentring(self,accepted,centring_status):
        self.emit(PYSIGNAL("collectEnableMinidiffCentring"),(False,))
        self.collectObj.sampleAcceptCentring(accepted,centring_status)

    """
    collectEnded
        Description: Called when the data collect h.o. ends a data collection. Disables the
                     buttons, enables the intrumentation bricks, and if the owner ends with
                     "Brick'>" then pops up a dialog box.
        Type       : slot (h.o.)
        Arguments  : owner (string?; the owner of the finished data collection)
                     state (None/bool; the finished state, should always be True)
                     msg   (successful message)
        Returns    : nothing
        Signals    : collectEnableInstrumentation(True),collectUserAccept()
    """
    def collectEnded(self,owner,state,msg):
        self.stopButton.setEnabled(False)
        self.skipButton.setEnabled(False)
        #self.abortButton.setEnabled(False)

        self.progressBar.barStop()
        self.emit(PYSIGNAL("collectEnableInstrumentation"),(True,))

        try:
            if owner.endswith("Brick'>"):
                try:
                    msg=msg.replace('DataCollect: ','')
                    msg=msg[0].upper()+msg[1:]+'.'
                except IndexError:
                    msg='Generic failed message.'
                self.showCollectResult(state,msg,True)
                self.emit(PYSIGNAL("collectUserAccept"),())
        except AttributeError:
            pass

    """
    collectFailed
        Description: Called when the data collect h.o. fails a data collection. Disables the
                     buttons, enables the intrumentation bricks, and if the owner ends with
                     "Brick'>" then pops up a dialog box.
        Type       : slot (h.o.)
        Arguments  : owner (string?; the owner of the failed data collection)
                     state (None/bool; the failed state: None for stopped, False for aborted)
                     msg   (stopped/aborted/error message)
        Returns    : nothing
        Signals    : collectEnableInstrumentation(True),collectUserAccept()
    """
    def collectFailed(self,owner,state,msg):
        self.stopButton.setEnabled(False)
        self.skipButton.setEnabled(False)
        #self.abortButton.setEnabled(False)

        self.progressBar.barStop()
        self.emit(PYSIGNAL("collectEnableInstrumentation"),(True,))

        try:
            if owner.endswith("Brick'>"):
                try:
                    msg=msg.replace('DataCollect: ','')
                    msg=msg[0].upper()+msg[1:]+'.'
                except IndexError:
                    msg='Generic failed message.'
                self.showCollectResult(state,msg,True)
                self.emit(PYSIGNAL("collectUserAccept"),())
        except AttributeError:
            pass



"""
LineEditInput
    Description: Single-line input field. Changes color depending on the validity of the input:
                 red for invalid (or whatever DataCollectBrick2.PARAMETER_STATE["INVALID"] has)
                 and white for valid (or whatever DataCollectBrick2.PARAMETER_STATE["OK"]).
    Type       : class (qt.QLineEdit)
    API        : setReadOnly(readonly<bool>)
                 <string> text()
    Signals    : returnPressed(), inputValid(valid<bool>), textChanged(txt<string>)
    Notes      : Returns 1/3 of the width in the sizeHint from QLineEdit
"""
class LineEditInput(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        QObject.connect(self, SIGNAL('textChanged(const QString &)'), self.txtChanged)
        QObject.connect(self, SIGNAL('returnPressed()'), self.retPressed)
        self.colorDefault=None
        self.origPalette=QPalette(self.palette())
        self.palette2=QPalette(self.origPalette)
        self.palette2.setColor(QPalette.Active,QColorGroup.Base,self.origPalette.disabled().background())
        self.palette2.setColor(QPalette.Inactive,QColorGroup.Base,self.origPalette.disabled().background())
        self.palette2.setColor(QPalette.Disabled,QColorGroup.Base,self.origPalette.disabled().background())

    def retPressed(self):
        if self.validator() is not None:
            if self.hasAcceptableInput():
                self.emit(PYSIGNAL("returnPressed"),())
        else:
            self.emit(PYSIGNAL("returnPressed"),())

    def text(self):
        return str(QLineEdit.text(self))

    def txtChanged(self,txt):
        txt=str(txt)
        valid=None
        if self.validator() is not None:
            if self.hasAcceptableInput():
                valid=True
                if txt=="":
                    if self.colorDefault is None:
                        color=DataCollectBrick2.PARAMETER_STATE["OK"]
                    else:
                        color=self.colorDefault
                else:
                    color=DataCollectBrick2.PARAMETER_STATE["OK"]
            else:
                if txt=="":
                    if self.colorDefault is None:
                        valid=False
                        color=DataCollectBrick2.PARAMETER_STATE["INVALID"]
                    else:
                        color=self.colorDefault
                else:
                    valid=False
                    color=DataCollectBrick2.PARAMETER_STATE["INVALID"]
            self.setPaletteBackgroundColor(color)
        else:
            if txt=="":
                if self.colorDefault is None:
                    if self.isReadOnly():
                        color=self.origBackgroundColor()
                    else:
                        color=DataCollectBrick2.PARAMETER_STATE["OK"]
                else:
                    color=self.colorDefault
            else:
                #color=DataCollectBrick2.PARAMETER_STATE["OK"]
                if self.isReadOnly():
                    color=self.origBackgroundColor()
                else:
                    color=DataCollectBrick2.PARAMETER_STATE["OK"]
            self.setPaletteBackgroundColor(color)
        self.emit(PYSIGNAL("textChanged"),(txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"),(self,valid,))

    def sizeHint(self):
        size_hint=QLineEdit.sizeHint(self)
        size_hint.setWidth(size_hint.width()/3)
        return size_hint
                
    def setReadOnly(self,readonly):
        if readonly:
            self.setPalette(self.palette2)
        else:
            self.setPalette(self.origPalette)
        QLineEdit.setReadOnly(self,readonly)
        
    def origBackgroundColor(self):
        return self.origPalette.disabled().background()

    def setDefaultColor(self,color=None):
        self.colorDefault=color
        self.txtChanged(self.text())

"""
readonlyLineEdit
    Description: Read-only single-line input field
    Type       : class (LineEditInput)
    Notes      : Returns the original sizeHint from QLineEdit and not from the super class
                 LineEditInput
"""
class readonlyLineEdit(LineEditInput):
    def __init__(self, parent):
        LineEditInput.__init__.im_func(self, parent)
        self.setReadOnly(True)
    def sizeHint(self):
        size_hint=QLineEdit.sizeHint(self)
        return size_hint



"""
VerticalSpacer2
    Description: Widget that expands itself vertically.
    Type       : class (qt.QWidget)
"""
class VerticalSpacer2(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)

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
HorizontalSpacer3
    Description: Widget that occupies 4 pixels horizontally.
    Type       : class (qt.QWidget)
"""
class HorizontalSpacer3(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
    def sizeHint(self):
        return QSize(4,0)



"""
ConfirmDialog
    Description: Dialog box for the confirmation of the data collection: tries to estimate the
                 total time, previews the diffraction files and corresponding angles, allows the
                 user to select some options, like forcing a dark current and mounting the current
                 selected sample if inside the sample changer, or taking 4 snapshots if the centring
                 has finished but wasn't accepted.
    Type       : class (qt.QDialog)
    API        : setCollectionParameters(<list>collect_list,<string>file_suffix,
                                         <list/None>warnings=None,
                                         <bool>enable_samplechanger=True,
                                         <bool>check_samplechanger=True,
                                         <bool>enable_snapshots=False,
                                         <string>owner=None)
                 <bool> shutterlessDatacollection()
                 <bool> forceDarkCurrent()
                 <bool> mountSample()
                 <bool> skipImages()
                 <bool> take4Snapshots()
                 <bool> useHelicalMode()
                 <bool> useScan4dMode()
    
"""
class ConfirmDialog(QDialog):
    #TIME_PER_IMAGE = 1.5
    #TIME_PER_OSCILLATION = 15
    TIME_SAMPLE_CHANGER = 180
    TIME_PER_IMAGE = 1
    TIME_PER_OSCILLATION = 1

    def __init__(self):
        QDialog.__init__(self,None)
        self.setCaption('Collect data')

        self.messageBox=QVGroupBox("Confirm",self)

        self.message1=QLabel("Doing ? oscillation over ? sample, totaling ??? images.",self.messageBox)
        self.message2=QLabel("Estimated time is ??? minutes.",self.messageBox)

        self.warningsBox=QHGroupBox("Warnings",self)
        self.warningsIcon=QLabel(self.warningsBox)
        self.warningsIcon.setPixmap(QMessageBox.standardIcon(QMessageBox.Warning))
        self.warningsIcon.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.warningsLabel=QLabel(self.warningsBox)

        self.optionsBox=QVGroupBox("Options",self)
        self.shutterlessDatacollection=QCheckBox('Do shutterless datacollection',self.optionsBox)
        self.forceDarkImage=QCheckBox('Force a dark current at start of collection',self.optionsBox)
        self.generateInputFiles=QCheckBox("Generate processing input files", self.optionsBox)
        self.generateInputFiles.hide()
        self.useSampleChanger=QCheckBox('Mount the sample using the sample changer',self.optionsBox)
        self.useHelicalModeCheckbox=QCheckBox('Use helical oscillation',self.optionsBox)
        self.useScan4dModeCheckbox=QCheckBox('Use scan4d oscillation',self.optionsBox)
        QObject.connect(self.useSampleChanger, SIGNAL('toggled(bool)'), self.sampleChangerToggled)
        self.skipCollectedImages=QCheckBox('Skip images already collected',self.optionsBox)
        self.takeSnapshots=QCheckBox('Take 4 snapshots of the sample before collecting',self.optionsBox)

        self.filesBox=QVGroupBox("Files",self)
        self.filesList=QListView(self.filesBox)
        self.filesList.setAllColumnsShowFocus(True)
        self.filesList.setSelectionMode(QListView.NoSelection)
        self.filesList.setSorting(-1)
        self.filesList.setFocusPolicy(QWidget.NoFocus)
        self.filesList.header().setResizeEnabled(True)
        self.filesList.header().setClickEnabled(False)
        self.filesList.addColumn("Phi start")
        self.filesList.addColumn("Phi end")
        self.filesList.addColumn("Filename")
        self.filesList.addColumn("Directory")

        self.enableTakeSnapshots=False

        buttonsBox=DialogButtonsBar(self,"Continue","Cancel",None,self.buttonClicked,0,DialogButtonsBar.DEFAULT_SPACING)

        QVBoxLayout(self,DialogButtonsBar.DEFAULT_MARGIN,DialogButtonsBar.DEFAULT_SPACING)
        self.layout().addWidget(self.messageBox)
        self.layout().addWidget(self.warningsBox)
        self.layout().addWidget(self.optionsBox)
        self.layout().addWidget(self.filesBox)
        self.layout().addWidget(VerticalSpacer2(self))
        self.layout().addWidget(buttonsBox)

        self.messageBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.optionsBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        self.estimatedTime=None
        self.numberOfSamples=None
        self.shutterlessDatacollection.hide()
        self.shutterlessDatacollection.setChecked(False)

    def buttonClicked(self,action):
        if action=="Continue":
            self.accept()
        elif action=="Cancel":
            self.reject()

    def sampleChangerToggled(self,state):
        if self.estimatedTime is not None:
            total_time=self.estimatedTime
            if state:
                total_time+=self.numberOfSamples*ConfirmDialog.TIME_SAMPLE_CHANGER
            total_time=int(total_time/60)
            if total_time % 60>0:
                total_time+=1
            if total_time==0:
                total_time=1

            self.setEstimatedTimeText(total_time)

            if state:
                self.takeSnapshots.setEnabled(False)
                self.takeSnapshots.setChecked(True)
            else:
                self.takeSnapshots.setEnabled(self.enableTakeSnapshots)
                self.takeSnapshots.setChecked(False)

    def setCollectionParameters(self,collect_list,file_suffix,warnings=None,\
        enable_samplechanger=True,check_samplechanger=True,enable_snapshots=False,owner=None, set_checked_snapshots = False):

        samples=[]
        for collect_dict in collect_list:
            try:
                sample_reference_dict=collect_dict['sample_reference']
            except KeyError:
                sample_id=None
            else:
                try:
                    basket=sample_reference_dict['container_reference']
                except KeyError:
                    sample_id=None
                else:
                    try:
                        vial=sample_reference_dict['sample_location']
                    except KeyError:
                        sample_id=None
                    else:
                        sample_id=(basket,vial)
            try:
                samples.index(sample_id)
            except ValueError:
                samples.append(sample_id)
            try:
		helical = collect_dict['helical']
                if helical == 1:
                   self.useHelicalModeCheckbox.setChecked(True)
                else:
                   self.useHelicalModeCheckbox.setChecked(False)
	    except:
		self.useHelicalModeCheckbox.setChecked(False)
            try:
		scan4d = collect_dict['scan4d']
                if scan4d == 1:
                   self.useScan4dModeCheckbox.setChecked(True)
                else:
                   self.useScan4dModeCheckbox.setChecked(False)
	    except:
		self.useScan4dModeCheckbox.setChecked(False)
        self.numberOfSamples=len(samples)

        #self.forceDarkImage.setChecked(False)
        if owner == 'EDNA':
          self.forceDarkImage.setChecked(True)
          #self.generateInputFiles.setChecked(False)
        else:
          #self.generateInputFiles.setChecked(True)
          pass
 
        self.useSampleChanger.setEnabled(enable_samplechanger)
        self.useSampleChanger.setChecked(check_samplechanger)
        self.takeSnapshots.setChecked(set_checked_snapshots)
        self.takeSnapshots.setEnabled(enable_snapshots)
        self.enableTakeSnapshots=enable_snapshots
        if check_samplechanger:
            self.takeSnapshots.setChecked(True)

        collect_dict=collect_list[0]
        sequence_dict=collect_dict['oscillation_sequence'][0]
        exposure_time=sequence_dict['exposure_time']

        number_of_images=0
        self.filesList.clear()
        file_list=getFileList(collect_list,file_suffix)
        last_item=None
        file_ex = 0
        for f_list in file_list:
            number_of_images+=len(f_list)
            for files in f_list:
                phi_start=str(files[0])
                phi_end=str(files[1])
                filename=files[2]
                directory=files[3]
                if last_item is None:
                    item=myListViewItem(self.filesList,phi_start,phi_end,filename,directory)
                else:
                    item=myListViewItem(self.filesList,last_item)
                    item.setText(0,phi_start)
                    item.setText(1,phi_end)
                    item.setText(2,filename)
                    item.setText(3,directory)

                full_filename=os.path.join(directory,filename)
                state = os.path.isfile(full_filename)
                item.imageExists(state)
                if state == True:
                    #file_ex = filename
                    file_ex += 1

                last_item=item

        
        collect_dict['file_exists'] = file_ex

        total_time=number_of_images*(exposure_time+ConfirmDialog.TIME_PER_IMAGE)
        total_time+=len(collect_dict['oscillation_sequence'])*ConfirmDialog.TIME_PER_OSCILLATION
        self.estimatedTime=total_time
        if check_samplechanger:
            total_time+=self.numberOfSamples*ConfirmDialog.TIME_SAMPLE_CHANGER
        total_time=int(total_time/60)
        if total_time % 60>0:
            total_time+=1
        if total_time==0:
            total_time=1
   
        self.setLabelsText(len(collect_list),self.numberOfSamples,number_of_images)
        self.setEstimatedTimeText(total_time)

        if warnings is not None:
            self.warningsBox.show()
            warnings_txt="<font color='red'><b><u>%s</u></b>" % string.join(warnings,"<br/>")
            self.warningsLabel.setText(warnings_txt)
        else:
            self.warningsBox.hide()

    def setLabelsText(self,n_collections,n_samples,n_images):
        c_suffix=""
        if n_collections>1:
            c_suffix="s"
        s_suffix=""
        if n_samples>1:
            s_suffix="s"
        i_suffix=""
        if n_images>1:
            i_suffix="s"
        self.message1.setText("Doing %d oscillation%s over %d sample%s, totaling %d image%s." % (n_collections,c_suffix,n_samples,s_suffix,n_images,i_suffix))

    def setEstimatedTimeText(self,n_minutes):
        m_suffix=""
        if n_minutes>1:
            m_suffix="s"
        self.message2.setText("Estimated time is %d minute%s." % (n_minutes,m_suffix))

    def forceDarkCurrent(self):
        return self.forceDarkImage.isChecked()

    def writeInputFiles(self):
        return True #self.generateInputFiles.isChecked()

    def doShutterlessDatacollect(self):
        return self.shutterlessDatacollection.isChecked()

    def useHelicalMode(self):
        return self.useHelicalModeCheckbox.isChecked()
    
    def useScan4dMode(self):
        return self.useScan4dModeCheckbox.isChecked()
    
    def mountSample(self):
        return self.useSampleChanger.isChecked()

    def skipImages(self):
        return self.skipCollectedImages.isChecked()

    def take4Snapshots(self):
        return self.takeSnapshots.isChecked()

"""
myListViewItem
    Description: List item for the collection-confirmation dialog box. Displays the 2nd column
                 (the filename) in red if the file already exists.
    Type       : class (qt.QListViewItem)
    API        : imageExists(state<bool>; True if the file already exists, so it should be displayed in red)
"""
class myListViewItem(QListViewItem):
    def imageExists(self,state):
        self.imageFileExists=state
    def paintCell(self,painter,colors,column,width,align):
        if column==2:
            try:
                if self.imageFileExists:
                    try:
                        colors=self.redColorGroup
                    except AttributeError:
                        colors=QColorGroup(colors)
                        colors.setColor(QColorGroup.Text,QWidget.red)
                        self.redColorGroup=colors
            except AttributeError:
                pass        
        QListViewItem.paintCell(self,painter,colors,column,width,align)



"""
validateParamsThread
    Description: Validates the data collection parameters: calls the sanityCheck of the data
                 collect h.o., verifies the centring status from the minidiff h.o., and the
                 session expiration time. Calls a callback (by posting an event through the
                 data collect h.o.) when finished.
    Type       : class (qt.QThread)
    API        : run
"""
class validateParamsThread(QThread):
    def __init__(self,collect_obj,finished_callback,owner,collect_list,mount_using_sc,session_expiration_time):
        QThread.__init__(self)
        self.collectObj=collect_obj
        self.finishedCallback=finished_callback
        self.collectList=collect_list
        self.mountUsingSC=mount_using_sc
        self.owner=owner
        self.sessionExpirationTime=session_expiration_time

    def run(self):
        if self.sessionExpirationTime is not None and self.sessionExpirationTime!=0:
            if self.sessionExpirationTime<time.time():
                session_check={'code':False,'messages':('Your session has expired. Please logout.',)}
                #self.collectObj.collectEvent(self.finishedCallback,(session_check,self.owner,self.collectList,self.mountUsingSC))
                self.finishedCallback(session_check,self.owner,self.collectList,self.mountUsingSC)
                return

        sanity_check=self.collectObj.sanityCheck(self.collectList)
        
        minidiff_ho=self.collectObj.diffractometer()
        centring_status=minidiff_ho.getCentringStatus()

        try:
            centring_valid=centring_status['valid']
        except:
            centring_valid=False
        if not centring_valid:
            sanity_check['messages'].append("The centring isn't valid!")
            if sanity_check['code']!=False:
                sanity_check['code']=None

        if centring_valid:
            try:
                centring_accepted=centring_status['accepted']
            except:
                centring_accepted=False
            if not centring_accepted:
                sanity_check['messages'].append("No crystal snapshots (hint: press the Accept button)!")
                if sanity_check['code']!=False:
                    sanity_check['code']=None
        else:
            centring_accepted=False

        sanity_check["centring_accepted"]=centring_accepted        
        sanity_check["centring_valid"]=centring_valid

        #self.collectObj.collectEvent(self.finishedCallback,(sanity_check,self.owner,self.collectList,self.mountUsingSC))
        self.finishedCallback(sanity_check,self.owner,self.collectList,self.mountUsingSC)


"""
getFileList
    Description: Previews the collection images: filenames with corresponding start and end
                 angles.
    Type       : method
    Arguments  : collect_list (list; )
                 file_suffix  (string; )
    Returns    : list; elements are tuples (oscillation_angle_start,oscillation_angle_end,
                                            filename,directory)
"""
def getFileList(collect_list,file_suffix):
    final_list=[]

    phi=0
    for collect_dict in collect_list:
        file_list=[]

        fileinfo_dict=collect_dict['fileinfo']
        run_number=fileinfo_dict['run_number']
        prefix=fileinfo_dict['prefix']
        directory=fileinfo_dict['directory']

        sequence_dict=collect_dict['oscillation_sequence'][0]
        tot_images=sequence_dict['number_of_images']
        start_image_number=sequence_dict['start_image_number']
        try:
            collect_dict['experiment_type'].index(" - Inverse Beam")
        except (KeyError,ValueError):
            inverse_beam=False
        else:
            inverse_beam=True
            reference_interval=sequence_dict['reference_interval']
            ref_int=reference_interval

        image_number_format="%04d"

        osc_start=float(sequence_dict['start'])
        osc_range=float(sequence_dict['range'])
        osc_overlap=float(sequence_dict['overlap'])
        osc_start_inv=osc_start+180

        i=0
        while i<tot_images:
            image_number=i+start_image_number
            image_number_str=image_number_format % image_number
            filename="%s_%s_%s.%s" % (prefix,run_number,image_number_str,file_suffix)
            file_list.append((osc_start,osc_start+osc_range,filename,directory))
            i+=1

            if inverse_beam:
                ref_int-=1
                if i==tot_images and ref_int>0:
                    reference_interval-=ref_int
                    ref_int=0

                if ref_int==0:
                    i2=0
                    image_number2=image_number+1-reference_interval
                    while i2<reference_interval:
                        image_number_str2=image_number_format % image_number2
                        filename2="%s_%s_%s.%s" % (prefix,run_number+1,image_number_str2,file_suffix)
                        file_list.append((osc_start_inv,osc_start_inv+osc_range,filename2,directory))
                        image_number2+=1
                        i2+=1
                        osc_start_inv=osc_start_inv+osc_range-osc_overlap

                    ref_int=reference_interval

            osc_start=osc_start+osc_range-osc_overlap

        final_list.append(file_list)

    return final_list
