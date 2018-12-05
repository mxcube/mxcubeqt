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

import os

from QtImport import *

import queue_model_objects

from widgets.Qt4_widget_utils import DataModelInputBinder


class XrayImagingParametersWidget(QWidget):

    def __init__(self, parent=None, name=None, fl=0, xray_imaging_params=None):

        QWidget.__init__(self, parent, Qt.WindowFlags(fl))
        
        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ---------------------------------------------------------- 

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        if xray_imaging_params is None: 
            self._xray_imaging_parameters = \
               queue_model_objects.XrayImagingParameters()
        else:
            self._xray_imaging_parameters = xray_imaging_params 

        self._xray_imaging_mib = DataModelInputBinder(self._xray_imaging_parameters)

        self._parameters_widget = loadUi(os.path.join(\
             os.path.dirname(__file__),
             "ui_files/Qt4_xray_imaging_parameters_widget_layout.ui"))
        # Layout --------------------------------------------------------------
        __main_vlayout = QVBoxLayout(self)
        __main_vlayout.addWidget(self._parameters_widget)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other --------------------------------------------------------------- 

    def set_beamline_setup(self, beamline_setup):
        """Sets beamline setup and links qt gui with data model
        """
        self._beamline_setup_hwobj = beamline_setup

        self._xray_imaging_mib.\
             bind_value_update('camera_hw_binning',
                               self._parameters_widget.camera_hw_binning_combo,
                               int,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('camera_hw_roi',
                               self._parameters_widget.camera_hw_roi_combo,
                               int,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('store_data',
                               self._parameters_widget.store_data_cbox,
                               bool,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('live_display',
                               self._parameters_widget.live_display_cbox,
                               bool,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('pre_flat_field_frames',
                               self._parameters_widget.pre_flat_cbox,
                               bool,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('post_flat_field_frames',
                               self._parameters_widget.post_flat_cbox,
                               bool,
                               None)

        self._xray_imaging_mib.\
             bind_value_update('apply_pre_flat_field_frames',
                               self._parameters_widget.apply_flat_cbox,
                               bool,
                               None)
 
    def update_data_model(self, xray_imaging_parameters):
        """
        Descript. :
        """
        self._xray_imaging_parameters = xray_imaging_parameters
        self._xray_imaging_mib.set_model(xray_imaging_parameters)
