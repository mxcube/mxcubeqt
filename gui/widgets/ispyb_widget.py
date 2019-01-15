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


class ISPyBSampleInfoWidget(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self.ispyb_sample_widget = loadUi(
            os.path.join(
                os.path.dirname(__file__), "ui_files/Qt4_ispyb_widget_layout.ui"
            )
        )

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.ispyb_sample_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
