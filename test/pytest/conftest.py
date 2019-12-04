"""
import pytest
import sys
import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
HWR_XML_FILES = os.path.join(MXCUBE, "HardwareRepository/configuration/xml-qt")

sys.path.insert(0, MXCUBE)
print ("MXCuBE root: %s" % MXCUBE)
print ("Config path: %s" % HWR_XML_FILES)

from HardwareRepository import HardwareRepository as HWR

@pytest.fixture(scope="session")
def hwr():
    HWR.init_hardware_repository(HWR_XML_FILES)
    hwr = HWR.getHardwareRepository()
    hwr.connect()
    return hwr

@pytest.fixture(scope="session")
def blsetup(hwr):
    return hwr.getHardwareObject("beamline-setup")
"""
