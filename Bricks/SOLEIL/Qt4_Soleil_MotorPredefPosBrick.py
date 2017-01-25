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
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons

__category__ = 'SOLEIL'
from BlissFramework.Bricks import Qt4_MotorSpinBoxBrick

class Qt4_MotorPredefPosBrick(Qt4_MotorSpinBoxBrick):

    def __init__(self, *args):
        Qt4_MotorSpinBoxBrick.__init__(self, *args)

        self.move_left_button.setIcon(Qt4_Icons.load_icon('Minus2'))
        self.move_right_button.setIcon(Qt4_Icons.load_icon('Plus2'))
    
    def propertyChanged(self, property_name, old_value, new_value):
        Qt4_MotorSpinBoxBrick.propertyChanged(self, property_name, old_value, new_value)

