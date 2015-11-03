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

import time
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "Qt4_General"


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
	self.addProperty('mnemonic', 'string', '')

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

    def set_progress_total(self, value, exp_time):
        self.progress_bar.setMaximum(value)
        self.setEnabled(True)

    def stop_progress(self, *args):
        self.progress_type_label.setText("")
        self.progress_bar.setValue(0)
        self.setEnabled(False)

    def set_progress_step(self, step):
        self.progress_bar.setValue(step)
        if step == self.progress_bar.maximum():
            self.stop_progress()

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.collect_hwobj is not None:
		self.disconnect(self.collect_hwobj, QtCore.SIGNAL('collectNumberOfFrames'), self.set_progress_total)
		self.disconnect(self.collect_hwobj, QtCore.SIGNAL('collectImageTaken'), self.set_progress_step)
		self.disconnect(self.collect_hwobj, QtCore.SIGNAL('collectEnded'), self.stop_progress) 
            self.collect_hwobj = self.getHardwareObject(new_value)
            if self.collect_hwobj is not None:
		self.connect(self.collect_hwobj, QtCore.SIGNAL('collectNumberOfFrames'), self.set_progress_total)
                self.connect(self.collect_hwobj, QtCore.SIGNAL('collectImageTaken'), self.set_progress_step)
                self.connect(self.collect_hwobj, QtCore.SIGNAL('collectEnded'), self.stop_progress)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)
