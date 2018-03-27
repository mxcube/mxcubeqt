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

from QtImport import *

from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
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

        # Internal values -----------------------------------------------------
        self.use_dialog = False

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonicList', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.progress_type_label = QLabel('', self)
        self.progress_bar = QProgressBar(self)
        #$self.progress_bar.setCenterIndicator(True)
        self.progress_bar.setMinimum(0)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.progress_type_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setEnabled(False)

    def stop_progress(self, *args):
        #if self.use_dialog:
        #    BlissWidget.close_progress_dialog()
        #else:
        self.progress_bar.reset()
        self.progress_type_label.setText("")
        self.setEnabled(False)
        #BlissWidget.set_status_info("status", "")
        #    BlissWidget.stop_progress_bar()

    def step_progress(self, step, msg=None):
        #f self.use_dialog:
        #   BlissWidget.set_progress_dialog_step(step)
        #lse:
        self.progress_bar.setValue(step)
        self.setEnabled(True)
        #   BlissWidget.set_progress_bar_step(step)

    def init_progress(self, progress_type, number_of_steps, use_dialog=False):
        #elf.use_dialog = use_dialog

        #f self.use_dialog:
        #   BlissWidget.open_progress_dialog(progress_type, number_of_steps)
        #lse:
        self.setEnabled(True)
        self.progress_bar.reset()
        self.progress_type_label.setText(progress_type)
        self.progress_bar.setMaximum(number_of_steps)
        #lissWidget.set_status_info("status", progress_type)
        #lissWidget.init_progress_bar(progress_type, number_of_steps)

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
