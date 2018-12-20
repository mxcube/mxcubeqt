import os
import sys
import pytest

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, MXCUBE_ROOT)

@pytest.fixture(scope="session")
def mxcube_root():
    return MXCUBE_ROOT
