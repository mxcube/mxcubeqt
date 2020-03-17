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
"""

import os
import sys
import unittest
from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import HardwareObject


__credits__ = ["MXCuBE colaboration"]

cwd = os.getcwd()
hwr_server = cwd +  "/HardwareRepository/configuration/xml-qt"

print "==============================================================="
print "MXCuBE home directory: %s" % cwd
print "Hardware repository: %s" % hwr_server
HardwareRepository.setHardwareRepositoryServer(hwr_server)
hardware_repository = HardwareRepository.HardwareRepository()
hardware_repository.connect()
unittest_hwobj = hardware_repository.getHardwareObject("unittest")
if unittest_hwobj is not None:
    print "UnitTest hardware object loaded"
else:
    print "Unable to load UnitTest hardware object!"
    print "Check if unittest.xml is in %s" % hwr_server
print "==============================================================="

class TestException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TestMethods(unittest.TestCase):

    def test_get_value(self):
        self.assertIn(type(unittest_hwobj.energy_hwobj.getCurrentEnergy()),
                      (float, int),
                      "Energy hwobj | getCurrentEnergy() returns float")
        self.assertIn(type(unittest_hwobj.transmission_hwobj.getAttFactor()),
                      (float, int),
                      "Transmission hwobj | getAttFactor() returns float")

    def test_get_limits(self):
        self.assertIsInstance(unittest_hwobj.energy_hwobj.get_limits(),
                              list,
                              "Energy hwobj | get_energy_limits() returns list with two floats")

    def test_get_state(self):
        self.assertIsInstance(unittest_hwobj.transmission_hwobj.getAttState(),
                              int,
                              "Transmission hwobj | getAttState() returns int")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMethods)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
    testResult.wasSuccessful
    testResult.errors
    testResult.failures
    testResult.skipped
