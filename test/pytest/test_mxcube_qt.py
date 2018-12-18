import sys
import os
import pytest

def test_mxcube_qt(mxcube_root):
    gui_file = os.path.join(mxcube_root,
                            "ExampleFiles/example_mxcube_qt4.yml")
    hr_server = os.path.join(mxcube_root,
                             "HardwareRepository/configuration/xml-qt")
    os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server
    from BlissFramework import Qt4_startGUI
 
    print("GUI file: %s" % gui_file)
    Qt4_startGUI.run(gui_file)

     
    #for widget in QtImport.getQApp().allWidgets():
    #    if hasattr(widget, "test_pytest"):
    #        widget.test_pytest()
