## How to create hardware object

- Hardware objects (hwobj) define interface to actual beamline components.
- They are configured with a xml file and instantiated by the [mxcubecore](http://github.com/mxcube/mxcubecore).
- Hardware objects are gui independent and does not contain any graphical user interface. The only exception are QtGraphicsManager and QtGraphicsLib that link hardware repository with Qt graphics.

### Example:

Hardware Object description xml file:

```
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
```

Write necessary hardware object:

- Then class must inherit from the base HardwareObject class:
- Most common types are: Equipment, AbstractActuator and Procedure
- The initialization of the class is done in two different functions:
  - def __init__(self)
    call parent class constructor
    define all internal values and give a default value
  - def init(self):
    initialize hardware object
    initialize other intern variables

```
# Available types are: Equipment, AbstractActuator and Procedure
from mxcubecore.BaseHardwareObjects import HardwareObject

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
```

**INFO** : Device type defined in xml should match the class type in the hwobj.
