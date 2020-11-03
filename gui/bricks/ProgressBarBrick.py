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
#
#  Please user PEP 0008 -- "Style Guide for Python Code" to format code
#  https://www.python.org/dev/peps/pep-0008/

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ProgressBarBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.use_dialog = False

        # Properties ----------------------------------------------------------
        self.add_property("mnemonicList", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.progress_type_label = QtImport.QLabel("", self)
        self.progress_bar = QtImport.QProgressBar(self)
        # $self.progress_bar.setCenterIndicator(True)
        self.progress_bar.setMinimum(0)

        main_layout = QtImport.QVBoxLayout(self)
        main_layout.addWidget(self.progress_type_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setEnabled(False)

        new_palette = QtImport.QPalette()
        new_palette.setColor(QtImport.QPalette.Highlight, Colors.DARK_GREEN)
        self.progress_bar.setPalette(new_palette)

    def stop_progress(self, *args):
        # if self.use_dialog:
        #    BaseWidget.close_progress_dialog()
        # else:
        self.progress_bar.reset()
        self.progress_type_label.setText("")
        self.setEnabled(False)
        # BaseWidget.set_status_info("status", "")
        #    BaseWidget.stop_progress_bar()

    def step_progress(self, step, msg=None):
        # f self.use_dialog:
        #   BaseWidget.set_progress_dialog_step(step)
        # lse:
        self.progress_bar.setValue(step)
        self.setEnabled(True)
        #   BaseWidget.set_progress_bar_step(step)

    def init_progress(self, progress_type, number_of_steps, use_dialog=False):
        # elf.use_dialog = use_dialog

        # f self.use_dialog:
        #   BaseWidget.open_progress_dialog(progress_type, number_of_steps)
        # lse:
        print("init progress ", progress_type, number_of_steps)
        self.setEnabled(True)
        self.progress_bar.reset()
        self.progress_type_label.setText(progress_type)
        self.progress_bar.setMaximum(number_of_steps)

        print("init progress ", progress_type, number_of_steps)
        # lissWidget.set_status_info("status", progress_type)
        # lissWidget.init_progress_bar(progress_type, number_of_steps)

    def property_changed(self, property_name, old_value, new_value):
        print(property_name, old_value, new_value)
        if property_name == "mnemonicList":
            hwobj_role_list = new_value.split()
            self.hwobj_list = []
            for hwobj_role in hwobj_role_list:
                print(hwobj_role)
                hwobj = self.get_hardware_object(hwobj_role)
                if hwobj is not None:
                    print(111111111111111)
                    print(hwobj)
                    self.hwobj_list.append(hwobj)
                    self.connect(
                        self.hwobj_list[-1], "progressInit", self.init_progress
                    )
                    self.connect(
                        self.hwobj_list[-1], "progressStep", self.step_progress
                    )
                    self.connect(
                        self.hwobj_list[-1], "progressStop", self.stop_progress
                    )
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
