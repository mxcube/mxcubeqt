#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
#
#  Please user PEP 0008 -- "Style Guide for Python Code" to format code
#  https://www.python.org/dev/peps/pep-0008/


import os

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

class ImageTrackingWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "image_tracking_widget"):
        QtGui.QWidget.__init__(self, parent)

        self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self.image_tracking_hwobj = None

        # Internal values -----------------------------------------------------
        self.image_path = None
        self.data_collection = None

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.image_tracking_widget_layout = uic.loadUi(os.path.join(\
                 os.path.dirname(__file__),
                 "ui_files/Qt4_image_tracking_widget_layout.ui"))

        # Layout --------------------------------------------------------------
        __main_vlayout = QtGui.QVBoxLayout(self)
        __main_vlayout.addWidget(self.image_tracking_widget_layout)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.image_tracking_widget_layout.view_current_button.clicked.\
             connect(self.open_in_viewer_clicked)
        self.image_tracking_widget_layout.view_previous_button.clicked.\
             connect(self.previous_button_clicked)
        self.image_tracking_widget_layout.view_next_button.clicked.\
             connect(self.next_button_clicked)
        self.image_tracking_widget_layout.image_num_spinbox.valueChanged.\
             connect(self.image_num_changed) 

        self.setEnabled(False)

    def previous_button_clicked(self):
        value = self.image_tracking_widget_layout.\
             image_num_spinbox.value() - 1 
        self.image_tracking_widget_layout.image_num_spinbox.setValue(value)
        self.image_tracking_widget_layout.current_path_ledit.setText(\
             self.image_path % value)
        self.view_current_image()

    def next_button_clicked(self):
        value = self.image_tracking_widget_layout.\
             image_num_spinbox.value() + 1
        self.image_tracking_widget_layout.image_num_spinbox.setValue(value)
        self.image_tracking_widget_layout.current_path_ledit.setText(\
            self.image_path % value)        
        self.view_current_image()

    def open_in_viewer_clicked(self):
        self.view_current_image()
 
    def view_current_image(self):
        print self.image_tracking_hwobj
        if self.image_tracking_hwobj is not None:
            self.image_tracking_hwobj.load_image(self.image_path % \
                 self.image_tracking_widget_layout.image_num_spinbox.value())    

    def image_num_changed(self, value):
        self.image_tracking_widget_layout.current_path_ledit.\
             setText(self.image_path % value)

    def set_image_tracking_hwobj(self, image_tracking_hwobj):
        self.image_tracking_hwobj = image_tracking_hwobj

    def set_data_collection(self, data_collection):
        self.setEnabled(True) 
        self.data_collection = data_collection
        self.refresh()

    def refresh(self):
        if self.data_collection is not None:
            acq = self.data_collection.acquisitions[0]
            paths = acq.get_preview_image_paths()
            if acq.acquisition_parameters.shutterless:
                temp = [paths[0], paths[-1]]
                paths = temp

            self.image_path = acq.path_template.get_image_path() 
            
            self.image_tracking_widget_layout.current_path_ledit.setText(\
                 self.image_path % acq.acquisition_parameters.first_image)
            self.image_tracking_widget_layout.image_num_spinbox.setValue(\
                 acq.acquisition_parameters.first_image)
            self.image_tracking_widget_layout.image_num_spinbox.setRange(\
                 acq.acquisition_parameters.first_image,
                 acq.acquisition_parameters.first_image + \
                     acq.acquisition_parameters.num_images - 1)

            #
            #self._first_image_label.setPixmap(qt.QPixmap(paths[0]))
            #3if len(paths) > 1:
            #    self._last_image_label.setPixmap(qt.QPixmap(paths[1]))
