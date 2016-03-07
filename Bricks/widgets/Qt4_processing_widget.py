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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables
from widgets.Qt4_widget_utils import DataModelInputBinder


class ProcessingWidget(QtGui.QWidget):

    enableProcessingSignal = QtCore.pyqtSignal(bool)

    def __init__(self, parent = None, name = None, fl = 0, data_model = None):

        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        if data_model is None:
            self._model = queue_model_objects.ProcessingParameters()
        else:
            self._model = data_model

        self._model_mib = DataModelInputBinder(self._model)

        self.processing_widget = self.acq_widget_layout = uic.loadUi(
                           os.path.join(os.path.dirname(__file__),
                           "ui_files/Qt4_processing_widget_vertical_layout.ui"))
      
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.processing_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
       
        self.processing_widget.space_group_cbox.\
            addItems(queue_model_enumerables.XTAL_SPACEGROUPS)
        
        self._model_mib.bind_value_update('cell_a',
                                          self.processing_widget.a_ledit,
                                          float,
                                          None)
        
        self._model_mib.bind_value_update('cell_alpha',
                                          self.processing_widget.alpha_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_b',
                                          self.processing_widget.b_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_beta',
                                          self.processing_widget.beta_ledit,
                                          float,
                                          None)  

        self._model_mib.bind_value_update('cell_c',
                                          self.processing_widget.c_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_gamma',
                                          self.processing_widget.gamma_ledit,
                                          float,
                                          None)  
        
        self._model_mib.bind_value_update('num_residues',
                                          self.processing_widget.num_residues_ledit,
                                          float,
                                          None)

        self.processing_widget.space_group_cbox.activated.connect(\
             self._space_group_change)    
        self.processing_widget.main_groupbox.toggled.connect(
             self._processing_enable_toggled)
 

    def _space_group_change(self, index):
        self._model.space_group = queue_model_enumerables.\
            XTAL_SPACEGROUPS[index]

    def _set_space_group(self, space_group):
        index = 0

        if space_group in queue_model_enumerables.XTAL_SPACEGROUPS:
            index = queue_model_enumerables.XTAL_SPACEGROUPS.index(space_group)
        
        self._space_group_change(index)
        self.processing_widget.space_group_cbox.setCurrentIndex(index)

    def update_data_model(self, model):
        self._model = model
        self._model_mib.set_model(model)
        self._set_space_group(model.space_group)

    def _processing_enable_toggled(self, state):
        self.enableProcessingSignal.emit(state)
