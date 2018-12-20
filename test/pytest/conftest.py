import pytest
import sys
import os
import gevent
import QtImport

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, MXCUBE_ROOT)

print("MXCuBE Qt root: %s" % MXCUBE_ROOT)

@pytest.fixture(scope="session")
def mxcube_root():
    return MXCUBE_ROOT
