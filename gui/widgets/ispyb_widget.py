#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import QtImport


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


class ISPyBSampleInfoWidget(QtImport.QWidget):

    def __init__(self, parent):

        QtImport.QWidget.__init__(self, parent)

        self.ispyb_sample_widget = QtImport.load_ui_file(
            "ispyb_widget_layout.ui"
        )

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.ispyb_sample_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
