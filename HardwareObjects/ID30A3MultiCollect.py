from ESRFMultiCollect import *
from detectors.TacoMar import Mar225
import gevent
import shutil
import logging
import os

class ID30A3MultiCollect(ESRFMultiCollect):
    def __init__(self, name):
        ESRFMultiCollect.__init__(self, name, CcdDetector(Mar225), FixedEnergy(0.965, 12.8))

        self.helical = False

    @task
    def data_collection_hook(self, data_collect_parameters):
      oscillation_parameters = data_collect_parameters["oscillation_sequence"][0]
 
      file_info = data_collect_parameters["fileinfo"]
      diagfile = os.path.join(file_info["directory"], file_info["prefix"])+"_%d_diag.dat" % file_info["run_number"]
      self.getObjectByRole("diffractometer").controller.set_diagfile(diagfile)

    @task
    def take_crystal_snapshots(self, number_of_snapshots):
        self.bl_control.diffractometer.takeSnapshots(number_of_snapshots, wait=True)

    @task
    def get_beam_size(self):
        return self.bl_control.beam_info.get_beam_size()
 
    @task
    def get_slit_gaps(self):
        return (0.1, 0.1)

    def get_measured_intensity(self):
        return 0

    @task
    def get_beam_shape(self):
        return self.bl_control.beam_info.get_beam_shape()

    @task
    def move_detector(self, detector_distance):
        det_distance = self.getObjectByRole("distance")
        det_distance.move(detector_distance)
        while det_distance.motorIsMoving():
          time.sleep(0.1)

    @task
    def set_resolution(self, new_resolution):
        self.bl_control.resolution.move(new_resolution)
        while self.bl_control.resolution.motorIsMoving():
          time.sleep(0.1)

    def get_resolution_at_corner(self):
        return self.bl_control.resolution.get_value_at_corner()

    def get_detector_distance(self):
        det_distance = self.getObjectByRole("distance")
        return det_distance.getPosition()

    @task
    def move_motors(self, motors_to_move_dict):
        motion = ESRFMultiCollect.move_motors(self,motors_to_move_dict,wait=False)

        #cover_task = self.getObjectByRole("eh_controller").detcover.set_out(wait=False, timeout=15)
        self.getObjectByRole("beamstop").moveToPosition("in")
        self.getObjectByRole("light").wagoOut()

        motion.get()
        #cover_task.get()

    @task
    def do_prepare_oscillation(self, *args, **kwargs):
        return

    @task
    def oscil(self, start, end, exptime, npass):
        save_diagnostic = True
        operate_shutter = True
        if self.helical: 
          self.getObjectByRole("diffractometer").helical_oscil(start, end, self.helical_pos, exptime, npass, save_diagnostic, operate_shutter)
        else:
          self.getObjectByRole("diffractometer").oscil(start, end, exptime, npass, save_diagnostic, operate_shutter)

    def open_fast_shutter(self):
        self.getObjectByRole("diffractometer").controller.fshut.open()

    def close_fast_shutter(self):
        self.getObjectByRole("diffractometer").controller.fshut.close()

    def set_helical(self, helical_on):
        self.helical = helical_on

    def set_helical_pos(self, helical_oscil_pos):
        self.helical_pos = helical_oscil_pos

    def get_flux(self):
        return 1E12

    def set_transmission(self, transmission):
    	self.getObjectByRole("transmission").set_value(transmission)

    def get_transmission(self):
        return self.getObjectByRole("transmission").get_value()

    def get_cryo_temperature(self):
        return 0

    @task
    def prepare_intensity_monitors(self):
        return

    def get_beam_centre(self):
        return self.bl_control.resolution.get_beam_centre()

