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

import sys
import copy
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import Qt4_queue_item
import queue_model_objects_v1 as queue_model_objects

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget


__category__ = 'Qt4_TaskToolbox_Tabs'


class CreateXRFScanWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, QtCore.Qt.WindowFlags(fl), 'XRF-scan')
 
        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
	self.count_time = None

        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = 'vertical')

	_parameters_gbox = QtGui.QGroupBox('Parameters', self)
	_count_time_label = QtGui.QLabel("Count time (sec.):", _parameters_gbox)
	self.count_time_ledit = QtGui.QLineEdit("1", _parameters_gbox)
        self.count_time_ledit.setMaximumWidth(75)

        # Layout --------------------------------------------------------------
        self._data_path_gbox_vlayout = QtGui.QVBoxLayout(self)
        self._data_path_gbox_vlayout.addWidget(self._data_path_widget)
        self._data_path_gbox_vlayout.setSpacing(0)
        self._data_path_gbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self._data_path_gbox.setLayout(self._data_path_gbox_vlayout)

        _parameters_gbox_hlayout = QtGui.QHBoxLayout(self)
        _parameters_gbox_hlayout.addWidget(_count_time_label)
        _parameters_gbox_hlayout.addWidget(self.count_time_ledit)
        _parameters_gbox_hlayout.addStretch(0)
        _parameters_gbox_hlayout.setSpacing(2)
        _parameters_gbox_hlayout.setContentsMargins(0, 0, 0, 0)
        _parameters_gbox.setLayout(_parameters_gbox_hlayout)

        _main_vlayout = QtGui.QVBoxLayout(self)
	_main_vlayout.addWidget(self._data_path_gbox)
	_main_vlayout.addWidget(_parameters_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.addStretch(0)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        
        self.connect(self._data_path_widget,
                     QtCore.SIGNAL("path_template_changed"),
                     self.handle_path_conflict)

        # Other ---------------------------------------------------------------

    def init_models(self):
        CreateTaskBase.init_models(self)
        self.enery_scan = queue_model_objects.XRFScan()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = 'raw'

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        escan_model = tree_item.get_model()

        if isinstance(tree_item, Qt4_queue_item.XRFScanQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)    

            if escan_model.get_path_template():
                self._path_template = escan_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not(isinstance(tree_item, Qt4_queue_item.SampleQueueItem) or \
                     isinstance(tree_item, Qt4_queue_item.DataCollectionGroupQueueItem)):
            self.setDisabled(True)


    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)

	self.count_time = None

	try:
	   self.count_time = float(str(self.count_time_ledit.text()))
	except:
	   logging.getLogger("user_level_log").\
                info("Incorrect count time value.")

        return base_result and self.count_time


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        data_collections = []

	if self.count_time is not None:
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = self._graphics_manager_hwobj.get_snapshot([])
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, graphics_manager.Point):
                    snapshot = self._graphics_manager_hwobj.\
                               get_snapshot([shape.qub_point])

                    cpos = copy.deepcopy(shape.get_centred_positions()[0])
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)
           
            xrf_scan = queue_model_objects.XRFScan(sample, path_template, cpos)
            xrf_scan.set_name(path_template.get_prefix())
            xrf_scan.set_number(path_template.run_number)
            xrf_scan.count_time = self.count_time
            
            data_collections.append(xrf_scan)
        else:
            logging.getLogger("user_level_log").\
                info("No count time specified.") 

        return data_collections


if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    widget = CreateXRFScanWidget()
    app.setMainWidget(widget)
    widget.show()
    app.exec_loop()
