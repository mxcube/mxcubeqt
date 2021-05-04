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

from random import randint, uniform
from mxcubeqt.utils.qt_import import Qt, QColor, QPalette
from mxcubecore.BaseHardwareObjects import HardwareObjectState

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


# Basic core colors
BLUE = QColor(Qt.blue)
WHITE = QColor(Qt.white)
BLACK = QColor(Qt.black)
GRAY = QColor(Qt.gray)
LIGHT_GRAY = QColor(Qt.lightGray)
DARK_BLUE = QColor(Qt.darkBlue)
DARK_GRAY = QColor(Qt.darkGray)
GREEN = QColor(Qt.green)
DARK_GREEN = QColor(Qt.darkGreen)
RED = QColor(Qt.red)
YELLOW = QColor(Qt.yellow)

LIGHT_GREEN = QColor(204, 255, 204)
LIGHT_RED = QColor(255, 204, 204)
LIGHT_YELLOW = QColor(254, 254, 121)
LIGHT_BLUE = QColor(72, 191, 255)
LIGHT_2_GRAY = QColor(240, 240, 240)
LIGHT_ORANGE = QColor(255, 185, 56)
SKY_BLUE = QColor(190, 225, 255)
PLUM = QColor(142, 69, 133, 70)

LINE_EDIT_ORIGINAL = QColor(0, 0, 12)
LINE_EDIT_ACTIVE = QColor(204, 255, 204)
LINE_EDIT_CHANGED = LIGHT_YELLOW
LINE_EDIT_ERROR = QColor(255, 204, 204)

BUTTON_ORIGINAL = QColor(242, 241, 240)
GROUP_BOX_GRAY = QColor(230, 230, 230)
QUEUE_ENTRY_COLORS = [WHITE, LIGHT_GREEN, LIGHT_YELLOW, LIGHT_RED, LIGHT_GRAY]

TREE_ITEM_SAMPLE = QColor(240, 240, 240)
TREE_ITEM_COLLECTION = QColor(255, 230, 210)

TASK_GROUP = [QColor("#B0DBFF"), QColor("#E57935"), QColor("#B1FF52")]

COLOR_STATES = {
    HardwareObjectState.UNKNOWN: DARK_GRAY,
    HardwareObjectState.WARNING: LIGHT_ORANGE,
    HardwareObjectState.READY: LIGHT_GREEN,
    HardwareObjectState.BUSY: LIGHT_YELLOW,
    HardwareObjectState.FAULT: LIGHT_RED,
    HardwareObjectState.OFF: LIGHT_GRAY,
}

def get_state_color(state):
    return COLOR_STATES.get(state, LIGHT_GRAY)

def set_widget_color(widget, color, color_role=None):
    if color_role is None:
        color_role = QPalette.Window
    widget_palette = widget.palette()
    widget_palette.setColor(color_role, color)
    widget.setAutoFillBackground(True)
    widget.setPalette(widget_palette)


def get_random_color(alpha=255):
    return QColor(randint(0, 255), randint(0, 255), randint(0, 255), alpha)


def get_random_rgb(alpha=255):
    return [randint(0, 255), randint(0, 255), randint(0, 255), alpha]


def get_random_hex(alpha=255):
    return "#{0:02x}{1:02x}{2:02x}".format(
        randint(0, 255), randint(0, 255), randint(0, 255)
    )


def get_random_numpy_color():
    return (uniform(0, 1),
            uniform(0, 1),
            uniform(0, 1))

def color_to_hexa(color):
    return "#%x%x%x" % (color.red(), color.green(), color.blue())
