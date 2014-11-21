import os
import sys
import types
import logging
import time
import errno
import abc
import collections
import gevent
import autoprocessing
import gevent
from HardwareRepository.TaskUtils import *

BeamlineControl = collections.namedtuple('BeamlineControl',
                                         ['diffractometer',
                                          'sample_changer',
                                          'lims',
                                          'safety_shutter',
                                          'machine_current',
                                          'cryo_stream',
                                          'energy',
                                          'resolution',
                                          'detector_distance',
                                          'transmission',
                                          'undulators',
                                          'flux',
                                          'detector',
                                          'beam_info'])

BeamlineConfig = collections.namedtuple('BeamlineConfig',
                                        ['directory_prefix',
                                         'default_exposure_time',
                                         'minimum_exposure_time',
                                         'detector_fileext',
                                         'detector_type',
                                         'detector_mode',
                                         'detector_manufacturer',
                                         'detector_model',
                                         'detector_px',
                                         'detector_py',
                                         'undulators',
                                         'focusing_optic', 
                                         'monochromator_type', 
                                         'beam_divergence_vertical',
                                         'beam_divergence_horizontal',
                                         'polarisation',
                                         'input_files_server'])


class AbstractMultiCollect(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.bl_control = BeamlineControl(*[None]*14)
        self.bl_config = BeamlineConfig(*[None]*17)
        self.data_collect_task = None
        self.oscillations_history = []
        self.current_lims_sample = None
        self.__safety_shutter_close_task = None


    def setControlObjects(self, **control_objects):
      self.bl_control = BeamlineControl(**control_objects)
  

    def setBeamlineConfiguration(self, **configuration_parameters):
      self.bl_config = BeamlineConfig(**configuration_parameters)


    @abc.abstractmethod
    @task
    def data_collection_hook(self, data_collect_parameters):
      pass


    @abc.abstractmethod
    @task
    def set_transmission(self, transmission_percent):
        pass


    @abc.abstractmethod
    @task
    def set_wavelength(self, wavelength):
        pass


    @abc.abstractmethod
    @task
    def set_resolution(self, new_resolution):
      pass


    @abc.abstractmethod
    @task
    def set_energy(self, energy):
      pass   


    @abc.abstractmethod
    @task
    def close_fast_shutter(self):
        pass


    @abc.abstractmethod
    @task
    def move_detector(self, distance):
        pass


    @abc.abstractmethod
    @task
    def move_motors(self, motor_position_dict):
        return


    @abc.abstractmethod
    @task
    def open_safety_shutter(self):
        pass

   
    def safety_shutter_opened(self):
        return False


    @abc.abstractmethod
    @task
    def close_safety_shutter(self):
        pass


    @abc.abstractmethod
    @task
    def prepare_intensity_monitors(self):
        pass


    @abc.abstractmethod
    @task
    def prepare_oscillation(self, start, osc_range, exptime, npass):
        """Should return osc_start and osc_end positions -
        gonio should be ready for data collection after this ;
        Remember to check for still image if range is too small !
        """
        pass


    @abc.abstractmethod
    @task
    def do_oscillation(self, start, end, exptime, npass):
        pass


    @abc.abstractmethod
    @task
    def set_detector_filenames(self, frame_number, start, filename, jpeg_full_path, jpeg_thumbnail_full_path):
      pass

    @abc.abstractmethod
    def last_image_saved(self):
      pass

    @abc.abstractmethod
    @task
    def prepare_acquisition(self, take_dark, start, osc_range, exptime, npass, number_of_images, comment):
        pass
      

    @abc.abstractmethod
    @task
    def start_acquisition(self, exptime, npass, first_frame):
        pass


    @abc.abstractmethod
    @task
    def stop_acquisition(self):
      # detector's readout
      pass


    @abc.abstractmethod
    @task
    def write_image(self, last_frame):
        pass


    @abc.abstractmethod
    @task
    def reset_detector(self):
        pass


    @abc.abstractmethod
    @task
    def data_collection_cleanup(self):
        pass


    @abc.abstractmethod
    def get_wavelength(self):
      pass


    @abc.abstractmethod
    def get_detector_distance(self):
      pass


    @abc.abstractmethod
    def get_resolution(self):
      pass


    @abc.abstractmethod
    def get_transmission(self):
      pass


    @abc.abstractmethod
    def get_undulators_gaps(self):
      pass


    @abc.abstractmethod
    def get_resolution_at_corner(self):
      pass


    @abc.abstractmethod
    def get_beam_size(self):
      pass


    @abc.abstractmethod
    def get_slit_gaps(self):
      pass


    @abc.abstractmethod
    def get_beam_shape(self):
      pass

    @abc.abstractmethod
    def get_beam_centre(self):
      pass

    @abc.abstractmethod
    def get_measured_intensity(self):
      pass


    @abc.abstractmethod
    def get_machine_current(self):
      pass

    @abc.abstractmethod
    def get_machine_fill_mode(self):
      pass

    
    @abc.abstractmethod
    def get_machine_message(self):
      pass


    @abc.abstractmethod
    def get_cryo_temperature(self):
      pass


    @abc.abstractmethod
    def get_flux(self):
      """Return flux in photons/second"""
      pass


    @abc.abstractmethod
    def store_image_in_lims(self, frame, first_frame, last_frame):
      pass
    

    def get_sample_info_from_parameters(self, parameters):
        """Returns sample_id, sample_location and sample_code from data collection parameters"""
        sample_info = parameters.get("sample_reference")
        
        try:
            sample_id = int(sample_info["blSampleId"])
        except:
            sample_id = None
        
        try:
            sample_code = sample_info["code"]
        except:
            sample_code = None

        sample_location = None
        
        try:
            sample_container_number = int(sample_info['container_reference'])
        except:
            pass
        else:
            try:
                vial_number = int(sample_info["sample_location"])
            except:
                pass
            else:
                sample_location = (sample_container_number, vial_number)
            
        return sample_id, sample_location, sample_code


    def create_directories(self, *args):
        for directory in args:
            try:
                os.makedirs(directory)
            except os.error, e:
                if e.errno != errno.EEXIST:
                    raise
     

    def _take_crystal_snapshots(self, number_of_snapshots):
      if isinstance(number_of_snapshots, bool):
        # backward compatibility, if number_of_snapshots is True|False
        if number_of_snapshots:
          return self.take_crystal_snapshots(4)
        else:
          return
      return self.take_crystal_snapshots(number_of_snapshots)


    @abc.abstractmethod
    @task
    def take_crystal_snapshots(self, number_of_snapshots):
      pass

       
    @abc.abstractmethod
    def set_helical(self, helical_on):
      pass


    @abc.abstractmethod
    def set_helical_pos(self, helical_pos):
      pass

 
    def prepare_wedges_to_collect(self, start, nframes, osc_range, subwedge_size=1, overlap=0):
        if overlap == 0:
          wedge_sizes_list = [nframes//subwedge_size]*subwedge_size
        else:
          wedge_sizes_list = [subwedge_size]*(nframes//subwedge_size)
        remaining_frames = nframes % subwedge_size
        if remaining_frames:
            wedge_sizes_list.append(remaining_frames)
        
        wedges_to_collect = []

        for wedge_size in wedge_sizes_list:
            orig_start = start
            
            wedges_to_collect.append((start, wedge_size))
            start += wedge_size*osc_range - overlap

        return wedges_to_collect

    def update_oscillations_history(self, data_collect_parameters):
      sample_id, sample_code, sample_location = self.get_sample_info_from_parameters(data_collect_parameters)
      self.oscillations_history.append((sample_id, sample_code, sample_location, data_collect_parameters))
      return len(self.oscillations_history), sample_id, sample_code, sample_location


    @abc.abstractmethod
    def get_archive_directory(self, directory):
      pass


    @abc.abstractmethod
    def prepare_input_files(self, files_directory, prefix, run_number, process_directory):
        """Return XDS input file directory"""
        pass


    @abc.abstractmethod
    @task
    def write_input_files(self, collection_id):
        pass

    @task
    def do_collect(self, owner, data_collect_parameters):
        if self.__safety_shutter_close_task is not None:
            self.__safety_shutter_close_task.kill()

        # reset collection id on each data collect
        self.collection_id = None

        # Preparing directory path for images and processing files
        # creating image file template and jpegs files templates
        file_parameters = data_collect_parameters["fileinfo"]

        file_parameters["suffix"] = self.bl_config.detector_fileext
        image_file_template = "%(prefix)s_%(run_number)s_%%04d.%(suffix)s" % file_parameters
        file_parameters["template"] = image_file_template

        archive_directory = self.get_archive_directory(file_parameters["directory"])
        data_collect_parameters["archive_dir"] = archive_directory

        if archive_directory:
          jpeg_filename="%s.jpeg" % os.path.splitext(image_file_template)[0]
          thumb_filename="%s.thumb.jpeg" % os.path.splitext(image_file_template)[0]
          jpeg_file_template = os.path.join(archive_directory, jpeg_filename)
          jpeg_thumbnail_file_template = os.path.join(archive_directory, thumb_filename)
        else:
          jpeg_file_template = None
          jpeg_thumbnail_file_template = None
         
        # database filling
        if self.bl_control.lims:
            data_collect_parameters["collection_start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            if self.bl_control.machine_current is not None:
                data_collect_parameters["synchrotronMode"] = self.get_machine_fill_mode()
            data_collect_parameters["status"] = "failed"

            (self.collection_id, detector_id) = \
                                 self.bl_control.lims.store_data_collection(data_collect_parameters, self.bl_config)
              
            data_collect_parameters['collection_id'] = self.collection_id

            if detector_id:
                data_collect_parameters['detector_id'] = detector_id
              
        # Creating the directory for images and processing information
        self.create_directories(file_parameters['directory'],  file_parameters['process_directory'])
        self.xds_directory, self.mosflm_directory, self.hkl2000_directory = self.prepare_input_files(file_parameters["directory"], file_parameters["prefix"], file_parameters["run_number"], file_parameters['process_directory'])
        data_collect_parameters['xds_dir'] = self.xds_directory

	sample_id, sample_location, sample_code = self.get_sample_info_from_parameters(data_collect_parameters)
        data_collect_parameters['blSampleId'] = sample_id

        if self.bl_control.sample_changer is not None:
            try:
                data_collect_parameters["actualSampleBarcode"] = \
                    self.bl_control.sample_changer.getLoadedSample().getID()
                data_collect_parameters["actualContainerBarcode"] = \
                    self.bl_control.sample_changer.getLoadedSample().getContainer().getID()

                basket, vial = self.bl_control.sample_changer.getLoadedSample().getCoords()

                data_collect_parameters["actualSampleSlotInContainer"] = vial
                data_collect_parameters["actualContainerSlotInSC"] = basket
            except:
                data_collect_parameters["actualSampleBarcode"] = None
                data_collect_parameters["actualContainerBarcode"] = None
        else:
            data_collect_parameters["actualSampleBarcode"] = None
            data_collect_parameters["actualContainerBarcode"] = None

        self._take_crystal_snapshots(data_collect_parameters.get("take_snapshots", False))

        centring_info = {}
        try:
            centring_status = self.diffractometer().getCentringStatus()
        except:
            pass
        else:
            centring_info = dict(centring_status)

        #Save sample centring positions
        motors = centring_info.get("motors", {})
        extra_motors = centring_info.get("extraMotors", {})

        positions_str = ""

        motors_to_move_before_collect = data_collect_parameters.setdefault("motors", {})
        
        for motor, pos in motors.iteritems():
          if pos is None:
              positions_str = "%s %s=None" % (positions_str, motor)
          else:
              positions_str = "%s %s=%f" % (positions_str, motor, pos)
              # update 'motors' field, so diffractometer will move to centring pos.
              motors_to_move_before_collect.update({motor: pos})
        for motor, pos in extra_motors.iteritems():
          if pos is None:
              positions_str = "%s %s=None" % (positions_str, motor)
          else:
              positions_str = "%s %s=%f" % (positions_str, motor, pos)
              motors_to_move_before_collect.update({motor: pos})
          
        data_collect_parameters['actualCenteringPosition'] = positions_str

        if self.bl_control.lims:
          try:
            if self.current_lims_sample:
              self.current_lims_sample['lastKnownCentringPosition'] = positions_str
              self.bl_control.lims.update_bl_sample(self.current_lims_sample)
          except:
            logging.getLogger("HWR").exception("Could not update sample infromation in LIMS")

        if centring_info.get('images'):
          # Save snapshots
          snapshot_directory = self.get_archive_directory(file_parameters["directory"])
          logging.getLogger("HWR").debug("Snapshot directory is %s" % snapshot_directory)

          try:
            self.create_directories(snapshot_directory)
          except:
              logging.getLogger("HWR").exception("Error creating snapshot directory")
          else:
              snapshot_i = 1
              snapshots = []
              for img in centring_info["images"]:
                img_phi_pos = img[0]
                img_data = img[1]
                snapshot_filename = "%s_%s_%s.snapshot.jpeg" % (file_parameters["prefix"],
                                                                file_parameters["run_number"],
                                                                snapshot_i)
                full_snapshot = os.path.join(snapshot_directory,
                                             snapshot_filename)

                try:
                  f = open(full_snapshot, "w")
                  f.write(img_data)
                except:
                  logging.getLogger("HWR").exception("Could not save snapshot!")
                  try:
                    f.close()
                  except:
                    pass

                data_collect_parameters['xtalSnapshotFullPath%i' % snapshot_i] = full_snapshot

                snapshots.append(full_snapshot)
                snapshot_i+=1

          try:
            data_collect_parameters["centeringMethod"] = centring_info['method']
          except:
            data_collect_parameters["centeringMethod"] = None

        if self.bl_control.lims:
            try:
                self.bl_control.lims.update_data_collection(data_collect_parameters)
            except:
                logging.getLogger("HWR").exception("Could not update data collection in LIMS")

        oscillation_parameters = data_collect_parameters["oscillation_sequence"][0]
        sample_id = data_collect_parameters['blSampleId']
        subwedge_size = oscillation_parameters.get("reference_interval", 1)
        wedges_to_collect = self.prepare_wedges_to_collect(oscillation_parameters["start"],
                                                           oscillation_parameters["number_of_images"],
                                                           oscillation_parameters["range"],
                                                           subwedge_size,
                                                           oscillation_parameters["overlap"])
        nframes = sum([wedge_size for _, wedge_size in wedges_to_collect])

        self.emit("collectNumberOfFrames", nframes) 

        start_image_number = oscillation_parameters["start_image_number"]    
        last_frame = start_image_number + nframes - 1
        if data_collect_parameters["skip_images"]:
            for start, wedge_size in wedges_to_collect[:]:
              filename = image_file_template % start_image_number
              file_location = file_parameters["directory"]
              file_path  = os.path.join(file_location, filename)
              if os.path.isfile(file_path):
                logging.info("Skipping existing image %s", file_path)
                del wedges_to_collect[0]
                start_image_number += wedge_size
                nframes -= wedge_size
              else:
                # images have to be consecutive
                break

        if nframes == 0:
            return

	# data collection
        self.data_collection_hook(data_collect_parameters)

        if 'transmission' in data_collect_parameters:
          self.set_transmission(data_collect_parameters["transmission"])

        if 'wavelength' in data_collect_parameters:
          self.set_wavelength(data_collect_parameters["wavelength"])
        elif 'energy' in data_collect_parameters:
          self.set_energy(data_collect_parameters["energy"])

        if 'resolution' in data_collect_parameters:
          resolution = data_collect_parameters["resolution"]["upper"]
          self.set_resolution(resolution)
        elif 'detdistance' in oscillation_parameters:
          self.move_detector(oscillation_parameters["detdistance"])

        self.close_fast_shutter()

        self.move_motors(motors_to_move_before_collect)

        with cleanup(self.data_collection_cleanup):
            if not self.safety_shutter_opened():
                self.open_safety_shutter(timeout=10)

            self.prepare_intensity_monitors()

            frame = start_image_number
            osc_range = oscillation_parameters["range"]
            exptime = oscillation_parameters["exposure_time"]
            npass = oscillation_parameters["number_of_passes"]

            # update LIMS
            if self.bl_control.lims:
                  try:
                    data_collect_parameters["flux"] = self.get_flux()
                    data_collect_parameters["flux_end"] = data_collect_parameters["flux"]
                    data_collect_parameters["wavelength"]= self.get_wavelength()
                    data_collect_parameters["detectorDistance"] =  self.get_detector_distance()
                    data_collect_parameters["resolution"] = self.get_resolution()
                    data_collect_parameters["transmission"] = self.get_transmission()
                    beam_centre_x, beam_centre_y = self.get_beam_centre()
                    data_collect_parameters["xBeam"] = beam_centre_x
                    data_collect_parameters["yBeam"] = beam_centre_y

                    und = self.get_undulators_gaps()
                    for i, key in enumerate(und):
                        if i>=2:
                          break
                        self.bl_config.undulators[i].type = key
                        data_collect_parameters["undulatorGap%d" % (i+1)] = und[key]  

                    data_collect_parameters["resolutionAtCorner"] = self.get_resolution_at_corner()
                    beam_size_x, beam_size_y = self.get_beam_size()
                    data_collect_parameters["beamSizeAtSampleX"] = beam_size_x
                    data_collect_parameters["beamSizeAtSampleY"] = beam_size_y
                    data_collect_parameters["beamShape"] = self.get_beam_shape()
                    hor_gap, vert_gap = self.get_slit_gaps()
                    data_collect_parameters["slitGapHorizontal"] = hor_gap
                    data_collect_parameters["slitGapVertical"] = vert_gap

                    logging.info("Updating data collection in ISPyB")

                    self.bl_control.lims.update_data_collection(data_collect_parameters, wait=True)
                    logging.info("Done")
                  except:
                    logging.getLogger("HWR").exception("Could not store data collection into LIMS")

            if self.bl_control.lims and self.bl_config.input_files_server:
                self.write_input_files(self.collection_id, wait=False) 

            # at this point input files should have been written           
            if data_collect_parameters.get("processing", False)=="True":
                self.trigger_auto_processing("before",
                                       self.xds_directory,
                                       data_collect_parameters["EDNA_files_dir"],
                                       data_collect_parameters["anomalous"],
                                       data_collect_parameters["residues"],
                                       data_collect_parameters["do_inducedraddam"],
                                       data_collect_parameters.get("sample_reference", {}).get("spacegroup", ""),
                                       data_collect_parameters.get("sample_reference", {}).get("cell", ""))
 
            for start, wedge_size in wedges_to_collect:
                self.prepare_acquisition(1 if data_collect_parameters.get("dark", 0) else 0,
                                         start,
                                         osc_range,
                                         exptime,
                                         npass,
                                         wedge_size,
                                         data_collect_parameters["comment"])
                data_collect_parameters["dark"] = 0

                i = 0
                j = wedge_size
                while j > 0: 
                  frame_start = start+i*osc_range
                  i+=1

                  filename = image_file_template % frame
                  try:
                    jpeg_full_path = jpeg_file_template % frame
                    jpeg_thumbnail_full_path = jpeg_thumbnail_file_template % frame
                  except:
                    jpeg_full_path = None
                    jpeg_thumbnail_full_path = None
                  file_location = file_parameters["directory"]
                  file_path  = os.path.join(file_location, filename)

                  self.set_detector_filenames(frame, frame_start, file_path, jpeg_full_path, jpeg_thumbnail_full_path)
                  osc_start, osc_end = self.prepare_oscillation(frame_start, osc_range, exptime, npass)

                  with error_cleanup(self.reset_detector):
                      self.start_acquisition(exptime, npass, j == wedge_size)
                      self.do_oscillation(osc_start, osc_end, exptime, npass)
                      self.stop_acquisition()
                      self.write_image(j == 1)
                                     
                      # Store image in lims
                      if self.bl_control.lims:
                        if self.store_image_in_lims(frame, j == wedge_size, j == 1):
                          lims_image={'dataCollectionId': self.collection_id,
                                      'fileName': filename,
                                      'fileLocation': file_location,
                                      'imageNumber': frame,
                                      'measuredIntensity': self.get_measured_intensity(),
                                      'synchrotronCurrent': self.get_machine_current(),
                                      'machineMessage': self.get_machine_message(),
                                      'temperature': self.get_cryo_temperature()}

                          if archive_directory:
                            lims_image['jpegFileFullPath'] = jpeg_full_path
                            lims_image['jpegThumbnailFileFullPath'] = jpeg_thumbnail_full_path

                          try:
                            self.bl_control.lims.store_image(lims_image)
                          except:
                            logging.getLogger("HWR").exception("Could not store store image in LIMS")
                
                      if data_collect_parameters.get("processing", False)=="True":
                        self.trigger_auto_processing("image",
                                                     self.xds_directory, 
                                                     data_collect_parameters["EDNA_files_dir"],
                                                     data_collect_parameters["anomalous"],
                                                     data_collect_parameters["residues"],
                                                     data_collect_parameters["do_inducedraddam"],
                                                     data_collect_parameters.get("sample_reference", {}).get("spacegroup", ""),
                                                     data_collect_parameters.get("sample_reference", {}).get("cell", ""))

                      if data_collect_parameters.get("shutterless"):
			  while self.last_image_saved() == 0:
                            time.sleep(exptime)
                          
                          time.sleep(exptime*wedge_size/100.0)
                          last_image_saved = self.last_image_saved()
                          frame = max(start_image_number+1, start_image_number+last_image_saved-1)
                          self.emit("collectImageTaken", frame)
                          logging.info("J=%d", j)
                          j = wedge_size - last_image_saved
                      else:
                          j -= 1
                          self.emit("collectImageTaken", frame)
                          frame += 1
                          if j == 0:
                            break

                
    @task
    def loop(self, owner, data_collect_parameters_list):
        failed_msg = "Data collection failed!"
        failed = True
        collections_analyse_params = []

        try:
            self.emit("collectReady", (False, ))
            self.emit("collectStarted", (owner, 1))
            for data_collect_parameters in data_collect_parameters_list:
                logging.debug("collect parameters = %r", data_collect_parameters)
                failed = False
                try:
                  # emit signals to make bricks happy
                  osc_id, sample_id, sample_code, sample_location = self.update_oscillations_history(data_collect_parameters)
                  self.emit('collectOscillationStarted', (owner, sample_id, sample_code, sample_location, data_collect_parameters, osc_id))
                  data_collect_parameters["status"]='Running'
                  
                  # now really start collect sequence
                  self.do_collect(owner, data_collect_parameters)
                except:
                  failed = True
                  exc_type, exc_value, exc_tb = sys.exc_info()
                  logging.exception("Data collection failed")
                  data_collect_parameters["status"] = 'Data collection failed!' #Message to be stored in LIMS
                  failed_msg = 'Data collection failed!\n%s' % exc_value
                  self.emit("collectOscillationFailed", (owner, False, failed_msg, self.collection_id, osc_id))
                else:
                  data_collect_parameters["status"]='Data collection successful'

                try:
                  if data_collect_parameters.get("processing", False)=="True":
                    self.trigger_auto_processing("after",
                                                 self.xds_directory,
                                                 data_collect_parameters["EDNA_files_dir"],
                                                 data_collect_parameters["anomalous"],
                                                 data_collect_parameters["residues"],
                                                 "reference_interval" in data_collect_parameters["oscillation_sequence"][0],
                                                 data_collect_parameters["do_inducedraddam"],
                                                 data_collect_parameters.get("sample_reference", {}).get("spacegroup", ""),
                                                 data_collect_parameters.get("sample_reference", {}).get("cell", ""))
                except:
                  pass
                else:
                   collections_analyse_params.append((self.collection_id,
                                                      self.xds_directory, 
                                                      data_collect_parameters["EDNA_files_dir"],
                                                      data_collect_parameters["anomalous"],
                                                      data_collect_parameters["residues"],
                                                      "reference_interval" in data_collect_parameters["oscillation_sequence"][0],
                                                      data_collect_parameters["do_inducedraddam"]))
  
                if self.bl_control.lims:    
                  data_collect_parameters["flux_end"]=self.get_flux()
                  try:
                    self.bl_control.lims.update_data_collection(data_collect_parameters)
                  except:
                    logging.getLogger("HWR").exception("Could not store data collection into LIMS")
                                  
                if failed:
                  # if one dc fails, stop the whole loop
                  break
                else:
                  self.emit("collectOscillationFinished", (owner, True, data_collect_parameters["status"], self.collection_id, osc_id, data_collect_parameters))

            try:
              self.__safety_shutter_close_task = gevent.spawn_later(10*60, self.close_safety_shutter, timeout=10)
            except:
              logging.exception("Could not close safety shutter")

            #if callable(finished_callback):
            #   try:
            #     finished_callback()
            #   except:
            #     logging.getLogger("HWR").exception("Exception while calling finished callback")
        finally:
           self.emit("collectEnded", owner, not failed, failed_msg if failed else "Data collection successful")
           self.emit("collectReady", (True, ))


    def collect(self, owner, data_collect_parameters_list): #, finished_callback=None):
        self.data_collect_task = self.loop(owner, data_collect_parameters_list, wait = False)
        return self.data_collect_task


    #TODO: rename to stop_collect
    def stopCollect(self, owner):
        if self.data_collect_task is not None:
            self.data_collect_task.kill(block = False)


    """
    processDataScripts
        Description    : executes a script after the data collection has finished
        Type           : method
    """
    def trigger_auto_processing(self, process_event, xds_dir, EDNA_files_dir=None, anomalous=None, residues=200, do_inducedraddam=False, spacegroup=None, cell=None):
      # quick fix for anomalous, do_inducedraddam... passed as a string!!!
      # (comes from the queue)
      if type(anomalous) == types.StringType:
        anomalous = anomalous == "True"      
      if type(do_inducedraddam) == types.StringType:
        do_inducedraddam = do_inducedraddam == "True" 
      if type(residues) == types.StringType:
        try:
          residues = int(residues)
        except:
          residues = 200

      # residues = zero should be interpreted as if no value was provided
      # use default of 200
      if residues == 0:
          residues = 200

      processAnalyseParams = {}
      processAnalyseParams['EDNA_files_dir'] = EDNA_files_dir

      try:
        if type(xds_dir) == types.ListType:
            processAnalyseParams["collections_params"] = xds_dir
        else:
            processAnalyseParams['datacollect_id'] = self.collection_id
            processAnalyseParams['xds_dir'] = xds_dir
        processAnalyseParams['anomalous'] = anomalous
        processAnalyseParams['residues'] = residues
        processAnalyseParams["spacegroup"]=spacegroup
        processAnalyseParams["cell"]=cell
      except Exception,msg:
        logging.getLogger().exception("DataCollect:processing: %r" % msg)
      else:
        #logging.info("AUTO PROCESSING: %s, %s, %s, %s, %s, %s, %r, %r", process_event, EDNA_files_dir, anomalous, residues, do_inducedraddam, spacegroup, cell)
            
        try: 
            autoprocessing.start(self["auto_processing"], process_event, processAnalyseParams)
        except:
            logging.getLogger().exception("Error starting processing")
          
        if process_event=="after" and do_inducedraddam:
            try:
              autoprocessing.startInducedRadDam(processAnalyseParams)
            except:
              logging.exception("Error starting induced rad.dam")
               
