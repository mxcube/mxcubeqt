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
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Task"


class Qt4_SampleDetailsBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Internal variables ------------------------------------------------
        self.sample = queue_model_objects.Sample()
        self.crystal = self.sample.crystals[0]
        self.sample_mib = DataModelInputBinder(self.sample)
        self.crystal_mib = DataModelInputBinder(self.crystal)
       
        # Signals ------------------------------------------------------------ 

        # Slots --------------------------------------------------------------
        self.defineSlot("populate_sample_details", ({}))

        # Graphic elements ----------------------------------------------------
        _info_widget = QWidget(self)
        self.crystal_widget = loadUi(\
             os.path.join(os.path.dirname(__file__),
             "widgets/ui_files/Qt4_crystal_widget_layout.ui"))
        self.sample_info_widget = loadUi(
              os.path.join(os.path.dirname(__file__),
             "widgets/ui_files/Qt4_sample_info_widget_layout.ui"))
        #self.ispyb_sample_info_widget = ISPyBSampleInfoWidget(self)

        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QHBoxLayout(_info_widget)
        _info_widget_hlayout.addWidget(self.sample_info_widget)
        _info_widget_hlayout.addWidget(self.crystal_widget)
        _info_widget_hlayout.addStretch(0)
        _info_widget_hlayout.setSpacing(0)
        _info_widget_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = QVBoxLayout(self)
        _main_hlayout.addWidget(_info_widget)
        #_main_hlayout.addWidget(self.ispyb_sample_info_widget)
        _main_hlayout.addStretch(0)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.crystal_mib.bind_value_update('space_group',  
                                           self.crystal_widget.space_group_value_label,
                                           str, 
                                           None)

        self.crystal_mib.bind_value_update('protein_acronym',
                                           self.crystal_widget.protein_acronym_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_a',
                                           self.crystal_widget.a_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_alpha',
                                           self.crystal_widget.alpha_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_b',
                                           self.crystal_widget.b_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_beta',
                                           self.crystal_widget.beta_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_c',
                                           self.crystal_widget.c_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_gamma',
                                           self.crystal_widget.gamma_value_label,
                                           str,
                                           None)

        self.sample_mib.bind_value_update('name',
                                          self.sample_info_widget.name_value_label,
                                          str,
                                          None)
        

        self.sample_mib.bind_value_update('code',
                                          self.sample_info_widget.data_matrix_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('holder_length',
                                          self.sample_info_widget.holder_length_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('lims_sample_location',
                                          self.sample_info_widget.sample_location_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('lims_container_location',
                                          self.sample_info_widget.basket_location_value_label,
                                          str,
                                          None)



    def populate_sample_details(self, sample):
        """
        Descript. :
        """
        self.sample = sample
        self.crystal = sample.crystals[0]
        self.crystal_mib.set_model(self.crystal)
        self.sample_mib.set_model(sample)
        
