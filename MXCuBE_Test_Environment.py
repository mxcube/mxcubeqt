#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
"""

----------------
Description
----------------
The MXCuBE Test Environment allows to test individual MXCuBE modules  
without the need of having a full MXCuBE application.

This environment is meant to test HardwareObjects or Bricks to help
during developmnent. Beware that this is not an environment to run applications 
as many of the application features are missing.

Running this module as a standalone test 
--------------------------------------------
This module can be used to directly test hardware object or bricks modules
provided that the module file contains the definition for a "test_hwo(hwo)" 
or "test_brick(brick)" for HardwareObject or Brick modules respectively.

To run the standalone test for HardwareObjects the name of an existing
hardware object mnemonic has to be provided as second parameter.

For Bricks
~~~~~~~~~~
The standalone test will require only one command line parameter: the module name for the Brick. 

If there is no test_brick() function in the module the brick will be shown
with no connection to a hardware object.

The test_brick(brick) function in the module will typically assign properties 
to the brick by calling the method propertyChanged() in the Brick.
Any other method of the Brick can be also called.

Example:
  sicilia@bl13mxcube> python MXCuBE_Test_Environment.py ~/MXCuBE/Bricks/Qt4_SlitsBrick.py

* Example of test_brick() from Qt4_ALBA_MachineInfoBrick.py

def test_brick(brick):
    brick.propertyChanged("mnemonic", None, "/mach-info")

For HardwareObjects
~~~~~~~~~~~~~~~~~~~
The standalone test for HardwareObjects will require two command line parameters. The module name
of the HardwareObject should be declared first. The second parameter should be the name of a mnemonic
using this HardwareObject

The test_hwo(hwo) function in the module, if it exists, can call any of the methods for the hardware
object

* Example,
  sicilia@bl13mxcube> python MXCuBE_Test_Environment.py ~/MXCuBE/HardwareRepository/SardanaMotor.py omega

* Example of test_hwo() in SardanaMotor.py

def test_hwo(hwo):
    print("Position for %s is: %s" % (hwo.username, hwo.getPosition()))


------------------------------
Function reference
------------------------------

Configuring the environment
------------------------------

`set_institute`
   sets the institute name so to look for specific Bricks and HardwareObjects
   (no default)

`set_xml_path(xml_path, relative=True)`
   sets the path for xml files, by default the value of xml_path is relative to
   the mxcube root directory
   (default if not called:  HardwareObjects.xml)

Testing hardware objects
--------------------------
The following methods of the MXCuBE_Test_Environment class are available to
test Hardware Objects and Bricks.

hwo = `get_hwo(xml-mnemonic)`
   obtain an instance of a hardware object with that mnemoic

hwo, mod = `get_hwo_mod(filepath, xml-mnemonic)`
   obtain an instance of a hardware object and a reference to the python module
   in filepath

`test_hwo(filepath, xml-mnemonic)`
   will try to create a hardware object with that module filepath and
   will create an instance 

   if the python module contains the definition of a function called test_hwo(hwo)
   it will run that function with the mnemonic specified in this call

Testing bricks
--------------------------

brick, mod = `get_brick_mod(filename)`
   returns and instance of the brick defined in `filename` plus the reference to the
   imported module defining it.

`test_brick(filename)`
    this function will load the Brick module defined in file `filename`, it will
    create an instance of the Brick. If a function `test_brick(brick)` is defined in the
    module it will be run with an instance of the `brick` created in this way.
    It will automatically start a standalone application containing just this `brick`.

`start_app()`
    This is a convenience function to create instances of a Qt application necessary to 
    run a Brick. It also declares the necessary code to start a gevent greenlet
    in the background to update information from hardware objects.
    If this function is used, `run_brick()` (see below) should be used to run the brick
    and the application main loop after the `brick` is created with `get_brick_mod()`

`exec_app()`
    Starts the QApplication loop and the gevent synchronization

`run_brick(brick)`
    starts execution of `brick` by starting the Qt application main loop.


----------------
Examples
----------------

Hardware Object test
---------------------
The following is an example for testing a Hardware Object::

   from MXCuBE_Test_Environment import MXCuBE_Test_Environment

   test_env = MXCuBE_Test_Environment()
   test_env.set_institute("ALBA")
   test_env.set_xml_path("../HardwareObjects.xml", relative=True)
   test_env.test_hwo("HardwareObjects/ALBA/ALBA_MachineInfo.py", "/mach-info")

   (in this case the ALBA_MachineInfo.py file contains a function test_hwo(hwo) 
    that will be triggered automatically)

Brick test 
----------------

   from MXCuBE_Test_Environment import MXCuBE_Test_Environment

   test_env = MXCuBE_Test_Environment()
   test_env.set_institute("ALBA")
   test_env.set_xml_path("../HardwareObjects.xml", relative=True)

   test_env.start_qt()
   brick, mod = test_env.get_brick_mod("Bricks/ALBA/Qt4_ALBA_MachineInfoBrick.py")
   brick.propertyChanged("mnemonic",None,"mach-info")
   test_env.run_brick(brick) 

Complex Brick test
---------------------

A more complex test example where a Brick is placed in a GUI layout
together with a "Close" button.

   from MXCuBE_Test_Environment import MXCuBE_Test_Environment
   from PyQt4 import QtGui
   import sys

   test_env = MXCuBE_Test_Environment()
   test_env.set_institute("ALBA")
   test_env.set_xml_path("../HardwareObjects.xml")

   test_env.start_app()
   
   win = QtGui.QMainWindow()
   wid = QtGui.QWidget()
   layout = QtGui.QVBoxLayout()
   
   brick, mod = test_env.get_brick_mod("Bricks/ALBA/Qt4_ALBA_MachineInfoBrick.py")
   brick.propertyChanged("mnemonic",None,"mach-info")
   
   wid.setLayout(layout)
   layout.addWidget(brick)

   quit_but = QtGui.QPushButton("Close")
   quit_but.clicked.connect(sys.exit)
   layout.addWidget(quit_but)

   win.setCentralWidget(wid)
   win.show()

   test_env.exec_app()

"""

import os
import sys
import imp
import logging
import gevent

try:
    from PyQt4 import QtCore, QtGui
    qt_imported = True
except:
    print("Cannot import Qt4.  Testing Hardware Objects is still possible")
    qt_imported = False

from HardwareRepository import HardwareRepository

class MXCuBE_Test_Environment(object):
    hwr_server = None
    app = None
    win = None
    gevent_timer = None

    institute = None
    xml_path = None
    default_xml_path = "HardwareObjects.xml"
    default_mxcube_dir = os.path.dirname(__file__)

    def __init__(self, mxcube_dir=None, xml_path=None):

        self.hwr_directory = None

        if mxcube_dir is None:
            mxcube_dir = self.default_mxcube_dir

        if xml_path is None:
            xml_path = self.default_xml_path

        self.set_mxcube_dir(mxcube_dir)
        self.set_xml_path(xml_path)

    def set_mxcube_dir(self, mxcube_dir):
        self.mxcube_dir = mxcube_dir
        self.brick_path = os.path.join(self.mxcube_dir,"Bricks")
        sys.path.append(self.brick_path)

    def set_institute(self, institute):
        if not institute:
            return

        self.institute = institute
        inst_brick_path = os.path.join(self.brick_path, self.institute)
        sys.path.append( inst_brick_path )

    def set_xml_path(self, xml_path, relative=True):
        if not xml_path:
            return

        if relative:
            self.hwr_directory = os.path.abspath(os.path.join(self.mxcube_dir,xml_path))
        else:
            self.hwr_directory = xml_path

    def _connect_hwserver(self):
        print self.hwr_directory

        self.hwr_server = HardwareRepository.HardwareRepository(self.hwr_directory)
        self.hwr_server.connect()

        hwo_path = os.path.join(self.mxcube_dir,"HardwareObjects")
        sc_hwo_path = os.path.join(hwo_path, "sample_changer")
        if self.institute:
            inst_hwo_path = os.path.join(hwo_path, self.institute)

        HardwareRepository.addHardwareObjectsDirs([hwo_path, inst_hwo_path, sc_hwo_path])

    def _do_gevent(self):
        if QtCore.QEventLoop():
            gevent.wait(timeout=0.01)

    def start_app(self):
        if not self.app:
            self.app = QtGui.QApplication([])
            self.gevent_timer = QtCore.QTimer()
            self.gevent_timer.connect(self.gevent_timer, QtCore.SIGNAL("timeout()"), self._do_gevent)

    def run_brick(self,brick):
        self.win = QtGui.QMainWindow()
        self.win.setCentralWidget(brick)
        self.win.show()
        self.exec_app()

    def exec_app(self):
        self.gevent_timer.start(0)
        self.app.exec_()

    def get_brick_mod(self,filename):
        if not qt_imported:
            print("Cannot test bricks without Qt")
            sys.exit(0)

        mod = imp.load_source('_brick', filename)
        basename = os.path.basename(filename)
        name, ext = os.path.splitext(basename)
        brick_class = mod.__dict__[name]

        if not self.hwr_server:
            self._connect_hwserver()

        brick = brick_class() 
        return brick, mod

    def test_brick(self, filename):
        if not self.app:
            self.start_app()

        brick, mod = self.get_brick_mod(filename)

        if "test_brick" in mod.__dict__:
            mod.test_brick(brick)

        self.run_brick(brick)

    def get_hwo(self, hwo_name):
        if self.hwr_server is None:
            self._connect_hwserver()
        obj = self.hwr_server.getHardwareObject(hwo_name)
        return obj

    def get_hwo_mod(self, filename, mnemonic):
        hwo = self.get_hwo(mnemonic)
        mod = imp.load_source('_hwo', filename)
        return hwo, mod

    def test_hwo(self,filename, mnemonic):
        hwo, mod = self.get_hwo_mod(filename, mnemonic)
        if "test_hwo" in mod.__dict__:
            mod.test_hwo(hwo)

def printUsage():
    print("""Usage: %s (arguments)

""" % sys.argv[0])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_to_test = sys.argv[1]
    else:
        printUsage()

    if len(sys.argv) > 2:
        mnemonic = sys.argv[2]
    else:
        mnemonic = None

    test_env = MXCuBE_Test_Environment()

    test_env.set_institute(os.environ.get("MXCUBE_SITE",None))
    test_env.set_xml_path(os.environ.get("MXCUBE_XML_PATH", None), relative=True)

    if "Brick" in file_to_test:
        test_env.test_brick(file_to_test)
    else:
        if mnemonic is not None:
            test_env.test_hwo(file_to_test, mnemonic)
        else:
            printUsage()

