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

from BlissFramework.Utils import Qt4_widget_colors


class OptimisationParametersWidgetLayout(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("OptimisationParametersWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.opt_param_widget = loadUi(os.path.join(os.path.dirname(__file__),
             "ui_files/Qt4_optimization_parameters_widget_layout.ui"))

        # Layout --------------------------------------------------------------
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.opt_param_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Size policies -------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.setAttribute(Qt.WA_WState_Polished)
