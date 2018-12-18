import pytest
import sys
import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
HWR_XML_FILES = os.path.join(MXCUBE_ROOT, "HardwareRepository/configuration/xml-qt")

sys.path.insert(0, MXCUBE_ROOT)

print ("MXCuBE Qt root: %s" % MXCUBE_ROOT)
print ("Config path: %s" % HWR_XML_FILES)


@pytest.fixture(scope="session")
def mxcube_root():
    return MXCUBE_ROOT
