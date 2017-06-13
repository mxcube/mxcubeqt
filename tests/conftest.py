# -*- coding: utf-8 -*-

import pytest
import sys
import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
MXCUBE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HWR_OBJECTS = os.path.join(MXCUBE, "HardwareObjects")
HWR_XML_FILES = os.path.join(TESTS_DIR, "HardwareObjects.xml")
sys.path.insert(0, MXCUBE)

from HardwareRepository import HardwareRepository
HardwareRepository.addHardwareObjectsDirs([HWR_OBJECTS])

@pytest.fixture(scope="session")
def hwr():
    hwr = HardwareRepository.HardwareRepository(HWR_XML_FILES)  
    hwr.connect()
    return hwr

@pytest.fixture(scope="session")
def blsetup(hwr):
    return hwr.getHardwareObject("beamline-setup")

    
