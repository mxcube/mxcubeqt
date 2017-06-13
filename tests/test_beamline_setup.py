import pytest

def test_hardware_objects(hwr):
  blsetup = hwr.getHardwareObject("beamline-setup")

  diffractometer = blsetup.diffractometer_hwobj

  assert diffractometer is not None

  default_path_template = blsetup.get_default_path_template()

