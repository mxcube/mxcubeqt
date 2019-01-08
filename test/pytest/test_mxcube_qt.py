import sys
import os
import pytest
import QtImport

def test_mxcube_qt(mxcube_root):
    sys.path.insert(0, mxcube_root)
    gui_file = os.path.join(mxcube_root,
                            "configuration/example_mxcube_qt4.yml")
    hr_server = os.path.join(mxcube_root,
                             "HardwareRepository/configuration/xml-qt")
    os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server
    from BlissFramework import Qt4_startTestGUI
 
    print("GUI file: %s" % gui_file)

    Qt4_startTestGUI.run_test(gui_file)
