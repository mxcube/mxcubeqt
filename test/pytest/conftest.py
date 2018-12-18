import pytest
import sys
import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
HWR_XML_FILES = os.path.join(MXCUBE_ROOT, "HardwareRepository/configuration/xml-qt")
GUI_DIR = os.path.join(MXCUBE_ROOT, "BlissFramework")

sys.path.insert(0, MXCUBE_ROOT)
sys.path.insert(0, GUI_DIR)

print ("MXCuBE Qt root: %s" % MXCUBE_ROOT)
print ("Config path: %s" % HWR_XML_FILES)


@pytest.fixture(scope="session")
def mxcube_root():
    return MXCUBE_ROOT
"""
from HardwareRepository.HardwareRepository import getHardwareRepository

@pytest.fixture(scope="session")
def hwr():
    hwr = getHardwareRepository(HWR_XML_FILES)
    hwr.connect()
    return hwr

@pytest.fixture(scope="session")
def blsetup(hwr):
    return hwr.getHardwareObject("beamline-setup")
"""
