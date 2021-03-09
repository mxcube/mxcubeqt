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


from mxcubeqt.utils import qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class SnapshotWidget(qt_import.QWidget):

    def __init__(self, parent, realtime_plot=False):

        qt_import.QWidget.__init__(self, parent)

        self.snapshot_gbox = qt_import.QGroupBox("Snapshot", self)
        self.animation_gbox = qt_import.QGroupBox("Animation", self)
        self.snapshot_label = qt_import.QLabel(self.snapshot_gbox)
        self.animation_label = qt_import.QLabel(self.animation_gbox)

        # Layout --------------------------------------------------------------
        _snaphot_gbox_hlayout = qt_import.QHBoxLayout(self.snapshot_gbox)
        _snaphot_gbox_hlayout.addWidget(self.snapshot_label)
        _snaphot_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _animation_gbox_hlayout = qt_import.QHBoxLayout(self.animation_gbox)
        _animation_gbox_hlayout.addWidget(self.animation_label)
        _animation_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.snapshot_gbox)
        _main_vlayout.addWidget(self.animation_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.addStretch(0)

        self.animation_gbox.setHidden(True)

    def display_snapshot(self, image, width=None):
        if image is not None:
            if width is not None:
                ration = image.height() / float(image.width())
                image = image.scaled(
                    width, width * ration, qt_import.Qt.KeepAspectRatio, qt_import.Qt.SmoothTransformation
                )
                self.setFixedWidth(width)

            self.snapshot_label.setPixmap(qt_import.QPixmap(image))

    def display_animation(self, animation_filename):
        self.animation_gbox.setVisible(True)
        movie = qt_import.QMovie(animation_filename)
        self.animation_label.setMovie(movie)
        movie.start()
