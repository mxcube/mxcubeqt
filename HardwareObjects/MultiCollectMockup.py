from HardwareRepository.BaseHardwareObjects import HardwareObject
from AbstractMultiCollect import *
import logging
import time
import os
import httplib
import math


class MultiCollectMockup(AbstractMultiCollect, HardwareObject):
    def __init__(self, name):
        AbstractMultiCollect.__init__(self)
        HardwareObject.__init__(self, name)
        self._centring_status = None
        self.ready_event = None
        self.actual_frame_num = 0

    def execute_command(self, command_name, *args, **kwargs): 
        wait = kwargs.get("wait", True)
        cmd_obj = self.getCommandObject(command_name)
        return cmd_obj(*args, wait=wait)
        
    def init(self):
        self.emit("collectConnected", (True,))
        self.emit("collectReady", (True, ))

    @task
    def take_crystal_snapshots(self, number_of_snapshots):
        return

    @task
    def data_collection_hook(self, data_collect_parameters):
        return

    def do_prepare_oscillation(self, start, end, exptime, npass):
        self.actual_frame_num = 0
    
    @task
    def oscil(self, start, end, exptime, npass):
        return
    
    @task
    def set_transmission(self, transmission_percent):
        return

    def set_wavelength(self, wavelength):
        return

    def set_energy(self, energy):
        return

    @task
    def set_resolution(self, new_resolution):
        return

    @task
    def move_detector(self, detector_distance):
        return

    @task
    def data_collection_cleanup(self):
        return 

    @task
    def close_fast_shutter(self):
        return

    @task
    def open_fast_shutter(self):
        return
        
    @task
    def move_motors(self, motor_position_dict):
        return

    @task
    def open_safety_shutter(self):
        return 

    def safety_shutter_opened(self):
        return 

    @task
    def close_safety_shutter(self):
        return

    @task
    def prepare_intensity_monitors(self):
        return

    def prepare_acquisition(self, take_dark, start, osc_range, exptime, npass, number_of_images, comment=""):
        return

    def set_detector_filenames(self, frame_number, start, filename, jpeg_full_path, jpeg_thumbnail_full_path):
        return

    def prepare_oscillation(self, start, osc_range, exptime, npass):
        return (start, start+osc_range)
    
    def do_oscillation(self, start, end, exptime, npass):
        return
  
    def start_acquisition(self, exptime, npass, first_frame):
        return
      
    def write_image(self, last_frame):
        self.actual_frame_num += 1
        return

    def last_image_saved(self):
        return self.actual_frame_num

    def stop_acquisition(self):
        return 
      
    def reset_detector(self):
        return

    def prepare_input_files(self, files_directory, prefix, run_number, process_directory):
        i = 1
        while True:
          xds_input_file_dirname = "xds_%s_run%s_%d" % (prefix, run_number, i)
          xds_directory = os.path.join(process_directory, xds_input_file_dirname)

          if not os.path.exists(xds_directory):
            break

          i+=1

        mosflm_input_file_dirname = "mosflm_%s_run%s_%d" % (prefix, run_number, i)
        mosflm_directory = os.path.join(process_directory, mosflm_input_file_dirname)

        hkl2000_dirname = "hkl2000_%s_run%s_%d" % (prefix, run_number, i)
        hkl2000_directory = os.path.join(process_directory, hkl2000_dirname)

        self.raw_data_input_file_dir = os.path.join(files_directory, "process", xds_input_file_dirname)
        self.mosflm_raw_data_input_file_dir = os.path.join(files_directory, "process", mosflm_input_file_dirname)
        self.raw_hkl2000_dir = os.path.join(files_directory, "process", hkl2000_dirname)

        return xds_directory, mosflm_directory, hkl2000_directory

    @task
    def write_input_files(self, collection_id):
        return

    def get_wavelength(self):
        return

    def get_detector_distance(self):
        return
       
    def get_resolution(self):
        return self.bl_control.resolution.getPosition()


    def get_transmission(self):
        return self.bl_control.transmission.getAttFactor()

    def get_undulators_gaps(self):
        return

    def get_resolution_at_corner(self):
        return

    def get_beam_size(self):
        return 

    def get_slit_gaps(self):
        return

    def get_beam_shape(self):
        return
    
    def get_measured_intensity(self):
        return

    def get_machine_current(self):
        if self.bl_control.machine_current:
            return self.bl_control.machine_current.getCurrent()
        else:
            return 0


    def get_machine_message(self):
        if  self.bl_control.machine_current:
            return self.bl_control.machine_current.getMessage()
        else:
            return ''


    def get_machine_fill_mode(self):
        if self.bl_control.machine_current:
            return self.bl_control.machine_current.getFillMode()
        else:
            ''

    def get_cryo_temperature(self):
      return self.bl_control.cryo_stream.getTemperature()


    def getCurrentEnergy(self):
        return

    def get_beam_centre(self):
        return
    
    def getBeamlineConfiguration(self, *args):
        return self.bl_config._asdict()

    def isConnected(self):
        return True

    def isReady(self):
        return True
 
    def sampleChangerHO(self):
        return self.bl_control.sample_changer

    def diffractometer(self):
        return self.bl_control.diffractometer

    def dbServerHO(self):
        return self.bl_control.lims

    def sanityCheck(self, collect_params):
        return
    
    def setBrick(self, brick):
        return

    def directoryPrefix(self):
        return self.bl_config.directory_prefix

    def store_image_in_lims(self, frame, first_frame, last_frame):
        return True

    def get_flux(self):
        return self.bl_control.flux.getCurrentFlux()

    def getOscillation(self, oscillation_id):
        return self.oscillations_history[oscillation_id - 1]
       
    def sampleAcceptCentring(self, accepted, centring_status):
        self.sample_centring_done(accepted, centring_status)

    def setCentringStatus(self, centring_status):
        self._centring_status = centring_status

    def getOscillations(self,session_id):
        return []

    def set_helical(self, helical_on):
        return

    def set_helical_pos(self, helical_oscil_pos):
        return

    def get_archive_directory(self, directory):
        archive_dir = os.path.join(directory, '/archive/')
        return archive_dir
