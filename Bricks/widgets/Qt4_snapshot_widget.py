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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors


class SnapshotWidget(QtGui.QWidget):
    """
    """

    def __init__(self, parent, realtime_plot = False):
        """
        """
        QtGui.QWidget.__init__(self, parent)
       
        _main_gbox = QtGui.QGroupBox('Snapshot', self) 
        self.snapshot_label = QtGui.QLabel(_main_gbox)

        # Layout --------------------------------------------------------------
        _parameters_gbox_hlayout = QtGui.QHBoxLayout(_main_gbox)
        _parameters_gbox_hlayout.addWidget(self.snapshot_label)
        _parameters_gbox_hlayout.addStretch(0)
        _parameters_gbox_hlayout.setSpacing(2)
        _parameters_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.addStretch(0)

    def display_snapshot(self, image, width=600):
        ration = image.height() / float(image.width())
        image = image.scaled(width, 
                             width * ration, 
                             QtCore.Qt.KeepAspectRatio,
                             QtCore.Qt.SmoothTransformation)
        self.snapshot_label.setPixmap(QtGui.QPixmap(image))
