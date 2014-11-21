import os
import sys
import time
import abc
import logging
from HardwareRepository.TaskUtils import *


class AbstractEnergyScan(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.data_collect_task = None
        self.scanning = False

    @abc.abstractmethod
    @task
    def open_safety_shutter(self, timeout):
        """
        Open the safety shutter. Give a timeout [s] if needed.
        """
        pass


    @abc.abstractmethod
    @task
    def close_safety_shutter(self, timeout):
        """
        Close the safety shutter. Give a timeout [s] if needed.
        """
        pass


    @abc.abstractmethod
    @task
    def open_fast_shutter(self):
        """
        Open the fast shutter.
        """
        pass


    @abc.abstractmethod
    @task
    def close_fast_shutter(self):
        """
        Close the fast shutter.
        """

        pass

    @abc.abstractmethod
    @task
    def energy_scan_hook(self, energy_scan_parameters):
        """
        Execute actions, required before running the raw scan(like changing
        undulator gaps, move to a given energy... These are in general
        beamline specific actions.
        """ 
        pass


    @abc.abstractmethod
    @task
    def execute_energy_scan(self, energy_scan_parameters):
        """
        Execute the raw scan sequence. Here is where you pass whatever
        parameters you need to run the raw scan (e.g start/end energy,
        counting time, energy step...).
        """       
        pass

    @abc.abstractmethod
    @task
    def get_static_parameters(self, element, edge):
        """
        Get any parameters, which are known before hand. Some of them are
        known from the theory, like the peak energy, others are equipment
        specific like the lower/upper ROI limits of the fluorescence detector.
        Usually these parameters are pre-defined in a file, but can also be
        calculated.
        The function should return a distionary with at least defined
        {'edgeEnergy': peak_energy} member, where 'edgeEnergy' is a
        compulsory key.
        It is convinient to put in the same dictionary the remote energy,
        the ROI min/max values.
        There are few more reserved key names:
        'eroi_min', 'eroi_max' - min and max ROI limits if you want ot set one.
        'findattEnergy' - energy to move to if you want to choose the attenuation
        for the scan.
        """
        pass

    @abc.abstractmethod
    @task
    def set_mca_roi(self, eroi_min, eroi_max):
        """
        Configure the fluorescent detector ROI. The input is min/max energy.
        """
        pass

    @abc.abstractmethod
    @task
    def calculate_und_gaps(self, energy):
        """
        Calculate the undulator(s) gap(s), If specified, undulator is the
        name of the undulator to chose if several possibilities. Return
        a dictionary undulator:gap in the order undulator(s)should move.
        """
        pass

    @abc.abstractmethod
    @task
    def move_undulators(self, undulators):
        """
        Move the undulator(s) to gap(s), where undulators is a dictionary
        undulator:gap and should be in the order of which motor to move first.
        """
        pass

    @abc.abstractmethod
    @task
    def escan_prepare(self):
        """
        Set the nesessary equipment in position for the scan. No need to know the c=scan paramets.
        """
        pass

    @abc.abstractmethod
    @task
    def choose_attenuation(self, energy_scan_parameters):
        """
        Procedure to set the minimal attenuation in order no preserve
        the sample. Should be done at the energy after the edge.
        """
        pass

    @abc.abstractmethod
    @task
    def move_energy(self, energy):
        """
        Move the monochromator to energy - used before and after the scan.
        """
        pass

    @abc.abstractmethod
    @task
    def escan_cleanup(self):
        pass

    @abc.abstractmethod
    @task
    def escan_postscan(self):
        """
        set the nesessary equipment in position after the scan
        """
        pass
              
    @task
    #def do_energy_scan(self, energy_scan_parameters):
    def startEnergyScan(self,element,edge,directory,prefix,session_id=None,blsample_id=None):

        self.emit('energyScanStarted', ())
        STATICPARS_DICT = {}
        #Set the energy from the element and edge parameters
        STATICPARS_DICT = self.get_static_parameters(element,edge)
        
        #Calculate the MCA ROI (if needed)
        try:
            self.set_mca_roi(STATICPARS_DICT['eroi_min'], STATICPARS_DICT['eroi_max'])
        except:
            pass
        #Calculate undulator gaps (if any)
        GAPS = {}
        try:
            GAPS = self.calculate_und_gaps(STATICPARS_DICT['edgeEnergy'])
        except:
            pass

        self.energy_scan_parameters = STATICPARS_DICT
        self.energy_scan_parameters["element"] = element
        self.energy_scan_parameters["edge"] = edge
        self.energy_scan_parameters["directory"] = directory
        #create the directory if needed
        if not os.path.exists(directory):
             os.makedirs(directory)
        self.energy_scan_parameters["prefix"]=prefix
        if session_id is not None:
            self.energy_scan_parameters["sessionId"] = session_id
            self.energy_scan_parameters["blSampleId"] = blsample_id
            self.energy_scan_parameters['startTime']=time.strftime("%Y-%m-%d %H:%M:%S")

        with error_cleanup(self.escan_cleanup):

            self.escan_prepare()
            self.energy_scan_hook(self.energy_scan_parameters)
            self.open_safety_shutter(timeout=10)
            self.choose_attenuation()
            self.close_fast_shutter()
            logging.getLogger("HWR").debug("Doing the scan, please wait...")
            self.execute_energy_scan(self.energy_scan_parameters)
            self.escan_postscan()
            
        self.close_fast_shutter()
        self.close_safety_shutter(timeout=10)
        #send finish sucessfully signal to the brick
        self.emit('energyScanFinished', (self.energy_scan_parameters,))
        self.ready_event.set()
        
    @task
    def doChooch(self, elememt, edge, scanArchiveFilePrefix, scanFilePrefix):
        """
        Use chooch to calculate edge and inflection point
        The brick expects the folowing parameters to be returned:
        pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm,
        chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title)
        """
        pass

