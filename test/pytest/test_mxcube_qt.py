import os
import gevent
import pytest
import QtImport

def test_mxcube_qt(mxcube_root):

    def wait_and_close_app():
        Qt4_startGUI.test_ready_event.wait()
        app = QtImport.getQApp()
        app.exit(0)

    gui_file = os.path.join(mxcube_root,
                            "ExampleFiles/example_mxcube_qt4.yml")
    hr_server = os.path.join(mxcube_root,
                             "HardwareRepository/configuration/xml-qt")
    os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server

    from BlissFramework import Qt4_startGUI

    gevent.spawn_later(10, wait_and_close_app)
    Qt4_startGUI.run(gui_file, test_mode=True)
