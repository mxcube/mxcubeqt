import gevent
import time
import subprocess
import os
import math
from HardwareRepository.TaskUtils import task, cleanup, error_cleanup

class Pilatus:

  def init(self, config, collect_obj):
      self.config = config
      self.collect_obj = collect_obj
      self.header = dict()

      lima_device = config.getProperty("lima_device")
      pilatus_device = config.getProperty("pilatus_device")

      for channel_name in ("acq_status", "acq_trigger_mode", "saving_mode", "acq_nb_frames",
                           "acq_expo_time", "saving_directory", "saving_prefix",
                           "saving_suffix", "saving_next_number", "saving_index_format",
                           "saving_format", "saving_overwrite_policy",
                           "saving_header_delimiter", "last_image_saved"):
          self.addChannel({"type":"tango", "name": channel_name, "tangoname": lima_device },
                           channel_name)

      for channel_name in ("fill_mode", "working_energy", "threshold"):
          self.addChannel({"type":"tango", "name": channel_name, "tangoname": pilatus_device },
                          channel_name)

      self.addCommand({ "type": "tango",
                        "name": "prepare_acq",
                        "tangoname": lima_device }, "prepareAcq")
      self.addCommand({ "type": "tango",
                        "name": "start_acq",
                        "tangoname": lima_device }, "startAcq")
      self.addCommand({ "type": "tango",
                        "name": "stop_acq",
                        "tangoname": lima_device }, "stopAcq")
      self.addCommand({ "type": "tango",
                        "name": "reset",
                        "tangoname": lima_device }, "reset")
      self.addCommand({ "type": "tango",
                        "name": "set_image_header",
                        "tangoname": lima_device }, "SetImageHeader")

  def wait_ready(self):
      acq_status_chan = self.getChannelObject("acq_status")
      with gevent.Timeout(10, RuntimeError("Detector not ready")):
          while acq_status_chan.getValue() != "Ready":
              time.sleep(1)

  def last_image_saved(self):
      return self.getChannelObject("last_image_saved").getValue() + 1

  def get_deadtime(self):
      return float(self.config.getProperty("deadtime"))

  @task
  def prepare_acquisition(self, take_dark, start, osc_range, exptime, npass, number_of_images, comment, energy, still):
      diffractometer_positions = self.collect_obj.bl_control.diffractometer.getPositions()
      self.start_angles = list()
      for i in range(number_of_images):
        self.start_angles.append("%0.4f deg." % (start+osc_range*i))
      self.header["file_comments"]=comment
      self.header["N_oscillations"]=number_of_images
      self.header["Oscillation_axis"]="omega"
      self.header["Chi"]="0.0000 deg."
      self.header["Phi"]="%0.4f deg." % diffractometer_positions.get("kappa_phi", -9999)
      self.header["Kappa"]="%0.4f deg." % diffractometer_positions.get("kappa", -9999)
      self.header["Alpha"]="0.0000 deg."
      self.header["Polarization"]=self.collect_obj.bl_config.polarisation
      self.header["Detector_2theta"]="0.0000 deg."
      self.header["Angle_increment"]="%0.4f deg." % osc_range
      #self.header["Start_angle"]="%0.4f deg." % start
      self.header["Transmission"]=self.collect_obj.get_transmission()
      self.header["Flux"]=self.collect_obj.get_flux()
      self.header["Beam_xy"]="(%.2f, %.2f) pixels" % tuple([value/0.172 for value in self.collect_obj.get_beam_centre()])
      self.header["Detector_Voffset"]="0.0000 m"
      self.header["Energy_range"]="(0, 0) eV"
      self.header["Detector_distance"]="%f m" % (self.collect_obj.get_detector_distance()/1000.0)
      self.header["Wavelength"]="%f A" % self.collect_obj.get_wavelength()
      self.header["Trim_directory:"]="(nil)"
      self.header["Flat_field:"]="(nil)"
      self.header["Excluded_pixels:"]=" badpix_mask.tif"
      self.header["N_excluded_pixels:"]="= 321"
      self.header["Threshold_setting"]="%d eV" % self.getChannelObject("threshold").getValue()
      self.header["Count_cutoff"]="1048500"
      self.header["Tau"]="= 0 s"
      self.header["Exposure_period"]="%f s" % (exptime+self.get_deadtime())
      self.header["Exposure_time"]="%f s" % exptime

      self.stop()
      self.wait_ready()

      self.set_energy_threshold(energy)

      if still:
          self.getChannelObject("acq_trigger_mode").setValue("INTERNAL_TRIGGER")
      else:
          self.getChannelObject("acq_trigger_mode").setValue("EXTERNAL_TRIGGER")

      self.getChannelObject("saving_mode").setValue("AUTO_FRAME")
      self.getChannelObject("acq_nb_frames").setValue(number_of_images)
      self.getChannelObject("acq_expo_time").setValue(exptime)
      self.getChannelObject("saving_overwrite_policy").setValue("OVERWRITE")

  def set_energy_threshold(self, energy):  
      minE = self.config.getProperty("minE")
      if energy < minE:
        energy = minE
      
      working_energy_chan = self.getChannelObject("working_energy")
      working_energy = working_energy_chan.getValue()
      if math.fabs(working_energy - energy) > 0.1:
        working_energy_chan.setValue(energy)
        
        while math.fabs(working_energy_chan.getValue() - energy) > 0.1:
          time.sleep(1)    
      
      self.getChannelObject("fill_mode").setValue("ON")
     
  @task 
  def set_detector_filenames(self, frame_number, start, filename, jpeg_full_path, jpeg_thumbnail_full_path):
      prefix, suffix = os.path.splitext(os.path.basename(filename))
      prefix = "_".join(prefix.split("_")[:-1])+"_"
      dirname = os.path.dirname(filename)
      if dirname.startswith(os.path.sep):
        dirname = dirname[len(os.path.sep):]
      
      saving_directory = os.path.join(self.config.getProperty("buffer"), dirname)
      subprocess.Popen("ssh %s@%s mkdir --parents %s" % (os.environ["USER"],
                                                         self.config.getProperty("control"),
                                                         saving_directory),
                                                         shell=True, stdin=None, 
                                                         stdout=None, stderr=None, 
                                                         close_fds=True).wait()
      
      self.wait_ready()  
   
      self.getChannelObject("saving_directory").setValue(saving_directory) 
      self.getChannelObject("saving_prefix").setValue(prefix)
      self.getChannelObject("saving_suffix").setValue(suffix)
      self.getChannelObject("saving_next_number").setValue(frame_number)
      self.getChannelObject("saving_index_format").setValue("%04d")
      self.getChannelObject("saving_format").setValue("CBF")
      self.getChannelObject("saving_header_delimiter").setValue(["|", ";", ":"])

      headers = list()
      for i, start_angle in enumerate(self.start_angles):
          header = "\n%s\n" % self.config.getProperty("serial")
          header += "# %s\n" % time.strftime("%Y/%b/%d %T")
          header += "# Pixel_size 172e-6 m x 172e-6 m\n"
          header += "# Silicon sensor, thickness 0.000320 m\n"  
          self.header["Start_angle"]=start_angle
          for key, value in self.header.iteritems():
              header += "# %s %s\n" % (key, value)
          headers.append("%d : array_data/header_contents|%s;" % (i, header))    
      
      self.getCommandObject("set_image_header")(headers)
       
  @task 
  def start_acquisition(self):
      self.getCommandObject("prepare_acq")()
      return self.getCommandObject("start_acq")()

  def stop(self):
      try:
          self.getCommandObject("stop_acq")()
      except:
          pass
      time.sleep(1)
      self.getCommandObject("reset")()



