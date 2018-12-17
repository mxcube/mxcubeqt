import pytest
import sys
import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
HWR_XML_FILES = os.path.join(MXCUBE, "HardwareRepository/configuration/xml-qt")

sys.path.insert(0, MXCUBE)

print ("MXCuBE root: %s" % MXCUBE)
print ("Config path: %s" % HWR_XML_FILES)

from HardwareRepository.HardwareRepository import getHardwareRepository

@pytest.fixture(scope="session")
def hwr():
    hwr = getHardwareRepository(HWR_XML_FILES)
    hwr.connect()
    return hwr

@pytest.fixture(scope="session")
def blsetup(hwr):
    return hwr.getHardwareObject("beamline-setup")
