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
#
#  Please user PEP 0008 -- "Style Guide for Python Code" to format code
#  https://www.python.org/dev/peps/pep-0008/


from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "General"


class Qt4_ProgressBarBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
	self.collect_hwobj = None	

        # Internal values -----------------------------------------------------
        self.number_of_steps = 0

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonicList', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.progress_type_label = QtGui.QLabel('', self)
        self.progress_bar = QtGui.QProgressBar(self)
        #$self.progress_bar.setCenterIndicator(True)
        self.progress_bar.setMinimum(0)

        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addWidget(self.progress_type_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setEnabled(False)

    def stop_progress(self, *args):
        self.progress_bar.reset()
        self.progress_type_label.setText("")
        self.setEnabled(False)

    def step_progress(self, step):
        self.progress_bar.setValue(step)
        self.setEnabled(True)
        #if step >= self.number_of_steps:
        #    self.stop_progress()

    def init_progress(self, progress_type, number_of_steps):
        self.setEnabled(True)
        self.progress_bar.reset()
        self.progress_type_label.setText(progress_type)
        self.number_of_steps = number_of_steps
        self.progress_bar.setMaximum(self.number_of_steps)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == "mnemonicList":
            hwobj_role_list = new_value.split()
            self.hwobj_list = []
            for hwobj_role in hwobj_role_list:
                hwobj = self.getHardwareObject(hwobj_role)
                if hwobj is not None:
                    self.hwobj_list.append(hwobj)
                    self.connect(self.hwobj_list[-1],
                                 'progressInit',
                                 self.init_progress)
                    self.connect(self.hwobj_list[-1],
                                 'progressStep',
                                 self.step_progress)
                    self.connect(self.hwobj_list[-1],
                                 'progressStop',
                                 self.stop_progress)
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)
