How to create hardware object
#############################

* Hardware objects (hwobj) define interface to actual beamline components.
* They are configured with a :doc:`xml file<packages/example_files>` and instanciated by the `Hardware Repository <http://github.com/mxcube/HardwareRepository>`_.
* Hardware objects are gui independent and does not contain any graphical user interface. The only exception is ``Qt4_GraphicsManager`` and ``Qt4_GraphicsLib`` that link hardware repository with Qt graphics.

Example
*******

Define xml:

.. code-block:: xml

   <object class="TestHardwareObject">
     <!-- Channels. Available: exporter, spec, tine, tango, taco -->    
     <channel type="exporter" name="chanExporterchannel_name">ExporterValueName</channel>
     
     <!-- Command. Available: exporter, spec, tine, tango, taco -->
     <command type="exporter" name="cmdExportercmd_name">ExporterValueName</command>

     <!-- Hardware objects -->
     <object href="/device-role" role="device_role"/>

     <!-- Properties -->
     <propertyNameOne>0</propertyNameOne>
    </object>

Write necessary hardware object:

.. code-block:: python

   # Available types are: Object, Device, Equipment and Procedure
   from HardwareRepository.BaseHardwareObjects import HardwareObject

   class TestHardwareObject(HardwareObject)

       # use __init__ to define all internal variables
       def __init__(self, name):   
           HardwareObject.__init__(self, name)
 
           # define all internal values and assign None or default value
           self.internal_value = None
           self.internal_hwobj = None 

           self.chan_test = None
           self.cmd_test = None

       # use init to initiate hardware object
       def init(self):

           # reads the value from xml. Returns None if property not found
           self.internal_value = self.get_property("propertyNameOne")

           # initiates hwobj
           self.internal_hwobj = self.get_object_by_role("device_role")

           # initiates channel
           self.chan_test = self.getChannelObject("chanExporterchannel_name")
           # connects to the update signal of the channel
           # method chan_test_value_changed is called when channel value changes
           if self.chan_test:
               self.chan_test.connect_signal('update', self.chan_test_value_changed)

           # initiates command
           self.cmd_test = self.getCommandObject("cmdExportercmd_name")

       def chan_test_value_changed(self, channel_value):
           pass

.. note::

   Device type defined in xml should match the class type in the hwobj.

Other information
*****************

* :doc:`how_to_create_qt_brick`
* :doc:`how_to_define_qt_gui`
