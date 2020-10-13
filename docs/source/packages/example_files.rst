Configuration example Files
============================

Example configuration files for framework-2 hardware objects. 
These xml files can also be found in ExampleFiles/HardwareObjects.xml.

Basic configuration file structure
--------------------------------------
Configuration xml file defines hardware object behaviour. Available configuration methods are described in example:

.. code-block:: bash

   <equipment class="ExampleClassName">
     <!-- Short description 

     --> 
     <!-- Channels -->    
     <channel type="exporter" name="chanExporterchannel_name">ExporterValueName</channel>
     <channel type="spec" name="chanSpecchannel_name">SpecValueName</channel>
     <channel type="tine" name="chanTinechannel_name" tinename="SpecificTineName">TineValueName</channel>
     <channel type="tango" name="chanTangochannel_name" polling="events">ChannelValueName</channel>
     <channel type="taco" name="chanTacochannel_name" taconame="TacoName" polling="3000" compare="False">TacoValueName</channel>
     
     <!-- Command -->
     <command type="exporter" name="cmdExportercmd_name">ExporterValueName</command>
     <command type="spec" name="cmdSpeccmd_name">SpecValueName</command>
     <command type="tine" name="cmdTinecmd_name" tinename="TineName">TineValueName</command>

     <!-- Hardware objects -->
     <object href="/device-role" role="device_role"/>
     <object href="/subdir/device-role-two" role="device_role_two"/>

     <!-- Properties -->
     <propertyNameOne>0</propertyNameOne>
     <propertyNameTwo>1.23</propertyNameTwo>
     <propertyNameThree>"Demo value"</propertyNameThree>
     <propertyNameFour>True</propertyNameFour>
     <propertyNameFive>(0, 1, 2, 3)</propertyNameFive>
     <propertyNameSix>{"one": 1, "two" : 2}</propertyNameSix>
    </equipment>

Basic xml file formating guide lines:

* Xml file starts with class type (**Device**, **Equipment** or **Procedure**) and class name
* Class name should mach with hardware object file name and class name defined in this hardware object. If **class=ExampleClassName** then file **ExampleClassName.py** should contain **class ExampleClassName**

* It is recommended to organize channels and command alphabetically. 
* Channel name should have template **chanExampleName** and initialized as **chan_example_name**
* Command name should have template **cmdExampleName** and initialized as **cmd_example_name**
* Propety name should be in camelcase style. For example: propertyExampleName and initialized as self.property_example_name
* It is possible to use boolean, int, float, lists and dictionaries as property names
* Use xmllint filename.xml to verify xml

Generic and mockup configuration files
--------------------------------------

.. hlist::
   :columns: 4

   * :download:`beam-info.xml <../../../ExampleFiles/HardwareObjects.xml/beam-info.xml>`
   * :download:`beamline-setup.xml <../../../ExampleFiles/HardwareObjects.xml/beamline-setup.xml>`
   * :download:`beamline-test.xml <../../../ExampleFiles/HardwareObjects.xml/beamline-test.xml>`
   * :download:`camera.xml <../../../ExampleFiles/HardwareObjects.xml/camera.xml>`
   * :download:`cats.xml <../../../ExampleFiles/HardwareObjects.xml/cats.xml>`
   * :download:`catsmaint.xml <../../../ExampleFiles/HardwareObjects.xml/catsmaint.xml>`
   * :download:`centring-math.xml <../../../ExampleFiles/HardwareObjects.xml/centring-math.xml>`
   * :download:`collect-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/collect-mockup.xml>`
   * :download:`data-analysis.xml <../../../ExampleFiles/HardwareObjects.xml/data-analysis.xml>`
   * :download:`detector-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/detector-mockup.xml>`
   * :download:`diff-kappa-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/diff-kappa-mockup.xml>`
   * :download:`diff-kappaphi-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/diff-kappaphi-mockup.xml>`
   * :download:`diff-omega-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/diff-omega-mockup.xml>`
   * :download:`diff-phiz.xml <../../../ExampleFiles/HardwareObjects.xml/diff-phiz.xml>`
   * :download:`diffractometer-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/diffractometer-mockup.xml>`
   * :download:`edna_defaults.xml <../../../ExampleFiles/HardwareObjects.xml/edna_defaults.xml>`
   * :download:`energy-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/energy-mockup.xml>`
   * :download:`energyscan-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/energyscan-mockup.xml>`
   * :download:`instanceconnection.xml <../../../ExampleFiles/HardwareObjects.xml/instanceconnection.xml>`
   * :download:`ldapconnection-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/ldapconnection-mockup.xml>`
   * :download:`lims-client-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/lims-client-mockup.xml>`
   * :download:`locallogin.xml <../../../ExampleFiles/HardwareObjects.xml/locallogin.xml>`
   * :download:`minikappa-correction.xml <../../../ExampleFiles/HardwareObjects.xml/minikappa-correction.xml>`
   * :download:`mockup_camera.xml <../../../ExampleFiles/HardwareObjects.xml/mockup_camera.xml>`
   * :download:`queue_model.xml <../../../ExampleFiles/HardwareObjects.xml/queue-model.xml>`
   * :download:`queue.xml <../../../ExampleFiles/HardwareObjects.xml/queue.xml>`
   * :download:`resolution-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/resolution-mockup.xml>`
   * :download:`sc-generic.xml <../../../ExampleFiles/HardwareObjects.xml/sc-generic.xml>`
   * :download:`sc-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/sc-mockup.xml>`
   * :download:`session.xml <../../../ExampleFiles/HardwareObjects.xml/session.xml>`
   * :download:`shape-history.xml <../../../ExampleFiles/HardwareObjects.xml/shape-history.xml>`
   * :download:`transmission-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/transmission-mockup.xml>`
   * :download:`xml-rpc-server.xml <../../../ExampleFiles/HardwareObjects.xml/xml-rpc-server.xml>`
   * :download:`xrf-spectrum-mockup.xml <../../../ExampleFiles/HardwareObjects.xml/xrf-spectrum-mockup.xml>`

ESRF ID23_1
-------------------------------------

ESRF ID29
------------------------------------

EMBL Hamburg P13
------------------------------------

.. hlist::
   :columns: 4

   * :download:`embl_hh_p13/attenuators.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/attenuators.xml>`
   * :download:`embl_hh_p13/auto-processing.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/auto-processing.xml>`
   * :download:`embl_hh_p13/beam-info.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/beam-info.xml>`
   * :download:`embl_hh_p13/beam-test.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/beam-test.xml>`
   * :download:`embl_hh_p13/beamcmds.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/beamcmds.xml>`
   * :download:`embl_hh_p13/beamline-setup.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/beamline-setup.xml>`
   * :download:`embl_hh_p13/centring-math.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/centring-math.xml>`
   * :download:`embl_hh_p13/data-analysis.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/data-analysis.xml>`
   * :download:`embl_hh_p13/dbconnection.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/dbconnection.xml>`
   * :download:`embl_hh_p13/detector-distance.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/detector-distance.xml>`
   * :download:`embl_hh_p13/detector.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/detector.xml>`
   * :download:`embl_hh_p13/door-interlock.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/door-interlock.xml>`
   * :download:`embl_hh_p13/edna-defaults.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/edna-defaults.xml>`
   * :download:`embl_hh_p13/energy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/energy.xml>`
   * :download:`embl_hh_p13/energy-motor.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/energy-motor.xml>`
   * :download:`embl_hh_p13/energyscan.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/energyscan.xml>`
   * :download:`embl_hh_p13/image-tracking.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/image-tracking.xml>`
   * :download:`embl_hh_p13/instanceconnection.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/instanceconnection.xml>`
   * :download:`embl_hh_p13/ldapconnection.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/ldapconnection.xml>`
   * :download:`embl_hh_p13/locallogin.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/locallogin.xml>`
   * :download:`embl_hh_p13/minikappa-correction.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/minikappa-correction.xml>`
   * :download:`embl_hh_p13/mxcollect.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/mxcollect.xml>`
   * :download:`embl_hh_p13/ppu-control.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/ppu-control.xml>`
   * :download:`embl_hh_p13/queue_model.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/queue-model.xml>`
   * :download:`embl_hh_p13/queue.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/queue.xml>`
   * :download:`embl_hh_p13/eh1/resolution.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/resolution.xml>`
   * :download:`embl_hh_p13/safshut.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/safshut.xml>`
   * :download:`embl_hh_p13/sc-generic.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/sc-generic.xml>`
   * :download:`embl_hh_p13/session.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/session.xml>`
   * :download:`embl_hh_p13/shape-history.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/shape-history.xml>`
   * :download:`embl_hh_p13/xml-rpc-server.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/xml-rpc-server.xml>`
   * :download:`embl_hh_p13/xrf-spectrum.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/xrf-spectrum.xml>`
   * :download:`embl_hh_p13/ccd/limavideo.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/ccd/limavideo.xml>`
   * :download:`embl_hh_p13/eh1/detector-distance.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/detector-distance.xml>`
   * :download:`embl_hh_p13/eh1/detector.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/detector.xml>`
   * :download:`embl_hh_p13/eh1/diff-aperture.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-aperture.xml>`
   * :download:`embl_hh_p13/eh1/diff-backLight.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-backLight.xml>`
   * :download:`embl_hh_p13/eh1/diff-beamstop.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-beamstop.xml>`
   * :download:`embl_hh_p13/eh1/diff-centring-vert.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-centring-vert.xml>`
   * :download:`embl_hh_p13/eh1/diff-focus.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-focus.xml>`
   * :download:`embl_hh_p13/eh1/diff-frontLight.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-frontLight.xml>`
   * :download:`embl_hh_p13/eh1/diff-holder-length.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-holder-length.xml>`
   * :download:`embl_hh_p13/eh1/diff-kappa.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-kappa.xml>`
   * :download:`embl_hh_p13/eh1/diff-kappaphi.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-kappaphi.xml>`
   * :download:`embl_hh_p13/eh1/diff-omega.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-omega.xml>`
   * :download:`embl_hh_p13/eh1/diff-phiy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-phiy.xml>`
   * :download:`embl_hh_p13/eh1/diff-phiz.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-phiz.xml>`
   * :download:`embl_hh_p13/eh1/diff-sampx.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-sampx.xml>`
   * :download:`embl_hh_p13/eh1/diff-sampy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-sampy.xml>`
   * :download:`embl_hh_p13/eh1/diff-zoom.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/diff-zoom.xml>`
   * :download:`embl_hh_p13/eh1/resolution.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p13/eh1/resolution.xml>` 
   

EMBL Hamburg P14
------------------------------------

.. hlist::
   :columns: 4
   
   * :download:`embl_hh_p14/attenuators.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/attenuators.xml>`
   * :download:`embl_hh_p14/auto-processing.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/auto-processing.xml>`
   * :download:`embl_hh_p14/beam-info.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/beam-info.xml>`
   * :download:`embl_hh_p14/beam-test.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/beam-test.xml>`
   * :download:`embl_hh_p14/beamcmds.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/beamcmds.xml>`
   * :download:`embl_hh_p14/beamline-setup.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/beamline-setup.xml>`
   * :download:`embl_hh_p14/centring-math.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/centring-math.xml>`
   * :download:`embl_hh_p14/data-analysis.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/data-analysis.xml>`
   * :download:`embl_hh_p14/dbconnection.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/dbconnection.xml>`
   * :download:`embl_hh_p14/door-interlock.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/door-interlock.xml>`
   * :download:`embl_hh_p14/edna-defaults.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/edna-defaults.xml>`
   * :download:`embl_hh_p14/energyscan.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/energyscan.xml>`
   * :download:`embl_hh_p14/image-tracking.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/image-tracking.xml>`
   * :download:`embl_hh_p14/instanceconnection.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/instanceconnection.xml>`
   * :download:`embl_hh_p14/locallogin.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/locallogin.xml>`
   * :download:`embl_hh_p14/minikappa-correction.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/minikappa-correction.xml>`
   * :download:`embl_hh_p14/mxcollect.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/mxcollect.xml>`
   * :download:`embl_hh_p14/ppu-control.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/ppu-control.xml>`
   * :download:`embl_hh_p14/queue_model.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/queue-model.xml>`
   * :download:`embl_hh_p14/queue.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/queue.xml>`
   * :download:`embl_hh_p14/safshut.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/safshut.xml>`
   * :download:`embl_hh_p14/sc-generic.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/sc-generic.xml>`
   * :download:`embl_hh_p14/session.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/session.xml>`
   * :download:`embl_hh_p14/shape-history.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/shape-history.xml>`
   * :download:`embl_hh_p14/xml-rpc-server.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/xml-rpc-server.xml>`
   * :download:`embl_hh_p14/xrf-spectrum.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/xrf-spectrum.xml>`
   * :download:`embl_hh_p14/ccd/limavideo.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/ccd/limavideo.xml>`
   * :download:`embl_hh_p14/eh1/beamAttocube.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamAttocube.xml>`
   * :download:`embl_hh_p14/eh1/beamFocusing.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamFocusing.xml>`
   * :download:`embl_hh_p14/eh1/detector-distance.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/detector-distance.xml>`
   * :download:`embl_hh_p14/eh1/detector.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/detector.xml>`
   * :download:`embl_hh_p14/eh1/diff-aperture.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-aperture.xml>`
   * :download:`embl_hh_p14/eh1/diff-beamstop.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-beamstop.xml>`
   * :download:`embl_hh_p14/eh1/diff-focus.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-focus.xml>`
   * :download:`embl_hh_p14/eh1/diff-frontLight.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-frontLight.xml>`
   * :download:`embl_hh_p14/eh1/diff-holder-length.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-holder-length.xml>`
   * :download:`embl_hh_p14/eh1/diff-kappa.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-kappa.xml>`
   * :download:`embl_hh_p14/eh1/diff-kappaphi.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-kappaphi.xml>`
   * :download:`embl_hh_p14/eh1/diff-light.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-light.xml>`
   * :download:`embl_hh_p14/eh1/diff-omega.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-omega.xml>`
   * :download:`embl_hh_p14/eh1/diff-phiy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-phiy.xml>`
   * :download:`embl_hh_p14/eh1/diff-phiz.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-phiz.xml>`
   * :download:`embl_hh_p14/eh1/diff-sampx.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-sampx.xml>`
   * :download:`embl_hh_p14/eh1/diff-sampy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-sampy.xml>`
   * :download:`embl_hh_p14/eh1/diff-zoom.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/diff-zoom.xml>`
   * :download:`embl_hh_p14/eh1/energy.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/energy.xml>`
   * :download:`embl_hh_p14/eh1/resolution.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/resolution.xml>`
   * :download:`embl_hh_p14/eh1/attocubeMotors/attoGroup.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/attocubeMotors/attoGroup.xml>`
   * :download:`embl_hh_p14/eh1/beamFocusingMotors/P14BCU.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamFocusingMotors/P14BCU.xml>`
   * :download:`embl_hh_p14/eh1/beamFocusingMotors/P14DetTrans.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamFocusingMotors/P14DetTrans.xml>`
   * :download:`embl_hh_p14/eh1/beamFocusingMotors/P14ExpTbl.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamFocusingMotors/P14ExpTbl.xml>`
   * :download:`embl_hh_p14/eh1/beamFocusingMotors/P14KB.xml <../../../ExampleFiles/HardwareObjects.xml/embl_hh_p14/eh1/beamFocusingMotors/P14KB.xml>`




