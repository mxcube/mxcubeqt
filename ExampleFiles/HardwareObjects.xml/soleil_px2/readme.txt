This directory contains configuration files for MXCuBE of Proxima2A, Synchrotron SOLEIL. To allow for better overview we organized them in several subdirectories, namely: 
  1. microdiff - all motors of MD2
  2. tango_motors - notable individual motors e.g. detector distance, experimental slits ...
  3. singleton_motors - contains virtual motors, typically comprised off multiple parts, typically coming with own HardwareObject class e.g. photon energy, transmission
  4. singleton_objects - complex objects, each coming with dedicated HardwareObject e.g. queue, detector, ISPyBConnection ...
  5. experimental_methods 


More detailed outline of the content of the subdirectories follows.


The goniometer directory contains configurations of all motors of goniometer of Proxima2A beamline (MD2). We split the motors into two classes: continuous and discrete. 

The following 23 motors are continuous:
    1. AlignmentX
    2. AlignmentY
    3. AlignmentZ
    4. CentringX
    5. CentringY
    6. CentringTableVertical (virtual motor combining positions of CentringX and CentringY)
    7. CentringTableFocus (virtual motor combining positions of CentringX and CentringY)
    8. Omega
    9. Kappa
   10. Phi
   11. ApertureX
   12. ApertureY
   13. CapillaryX
   14. CapillaryY
   15. BeamstopX
   16. BeamstopY
   17. BeamstopZ
   18. ScintillatorY
   19. Zoom
   20. Backlight
   21. Frontlight
   22. BacklightFactor
   23. FrontlightFactor

The following 9 motors are discrete:
   24. AperturePosition {'BEAM', 'OFF', 'PARK'}
   26. CurrentApertureDiamgeterIndex {0, 1, 2, 3, 4, 5}
   27. Capillary {'BEAM', 'OFF', 'PARK'}
   28. Scintillator {'BEAM', 'OFF', 'PARK'}
   29. BacklightIsOn {True, False}
   30. FrontlightIsOn {True, False}
   31. Phase {'DataCollection', 'BeamLocation', 'Centring', 'Transfer'}
   32. FastShutterIsOpen {True, False}
   33. CryoIsOut {True, False}
   34. FluoDetectorIsBack {True, False}
   35. CoaxialCameraZoomValue {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
   
The following configuration puts everything together
   36. diffractometer

For all MD2 motors we have three different types of configuration relying for communication either on EMBL Exporter or Tango. For tango we have two types of set up: with events or with polling.

The tango_motors directory contains configuration for the following motors:
   34. detector_distance
   35. detector_vertical
   36. detector_horizontal
   37. experimental_slits_vertical_position
   38. experimental_slits_horizontal_position
   39. experimental_slits_vertical_gap
   40. experimental_slits_horizontal_gap
   41. fast_shutter_vertical_position
   42. fast_shutter_horizontal_position
   43. undulator_gap
   44. monochromator_position
   45. x-ray_camera_position
   
The singleton_motors directory contains configuration for the following motors:
   46. photon_energy
   47. resolution
   48. transmission
   49. flux
   50. x-ray_focus
   
The detectors directory contains configurations for all detectors available on the beamline:
   51. diffraction_detector (eiger X 9M)
   52. fluorescence_detector (ketek axas-m)
   53. x-ray_camera (basler pilot 100)
   54. sample_camera (prosilica 1350c)
   55. xbpm1 (titanium foil)
   56. xbpm3 (cvd)
   57. xbpm5 (psd)
   58. xbpm6 (psd)
       calibrated_diode (125um Si PIN diode)
   59. machine_current
       
       
The singleton_objects directory contains configuration for the following objects:

   60. sample_changer
       cryostream
       zoom_manager #takes care of optimal zoom, focus, lighting and sample_camera gain
   61. safety_shutter
   62. frontend
   63. beamline_setup
   64. beam_info
       shape_history
   65. graphics_manager
   
   66. personal_safety_system
   67. ispyb_connection
   68. ldap_connection
   69. instance_connection
   70. beam_info
   71. redis_client
   72. queue
   74. queue_model

The experimental_methods directory contains the following configurations
   75. omega_scan
   76. reference_images
   77. inverse_scan
   78. helical_scan
   79. raster_scan
   80. x-ray_centring
   81. optical_scan
   82. tomography
   83. energy_scan
   84. fluorescence_spectrum
   85. burn_strategy

The maintenance directory contains the following configurations
   86. minikappa_calibration
   87. slit_scan
   88. aperture_scan
   89. capillary_scan
   90. beam_alignment
   91. undulator_tuning_curves
   92. beam_scan
   93. detector_beamcenter_calibration
   
   
    
    
