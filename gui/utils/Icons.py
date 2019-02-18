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

import os
from gui.utils.QtImport import QPixmap, QIcon


ROOT_DIR_PARTS = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
ROOT_DIR = os.path.join(*ROOT_DIR_PARTS[1:-2])
ICONS_DIR = os.path.join("/", ROOT_DIR, "gui/icons")


def load(icon_name):
    """
    Try to load an icon from file and return the QPixmap object
    """
    filename = get_icon_path(icon_name)

    try:
        icon = QPixmap(filename)
    except BaseException:
        return QPixmap(os.path.join(ICONS_DIR, "brick.png"))
    else:
        if icon.isNull():
            return QPixmap(os.path.join(ICONS_DIR, "brick.png"))
        else:
            return icon


def get_icon_path(icon_name):
    """
    Return path to an icon
    """
    filename = os.path.join(ICONS_DIR, icon_name)
    if not os.path.exists(filename):
        for ext in ["png", "xpm", "gif", "bmp"]:
            f = ".".join([filename, ext])
            if os.path.exists(f):
                filename = f
                break
    if os.path.exists(filename):
        return filename


def load_icon(icon_name):
    return QIcon(load(icon_name))


def load_pixmap(icon_name):
    return load(icon_name)
