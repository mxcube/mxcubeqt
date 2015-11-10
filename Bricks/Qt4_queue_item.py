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

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors

import queue_model_objects_v1 as queue_model_objects


PIN_PIXMAP = Qt4_Icons.load("sample_axis.png")


class QueueItem(QtGui.QTreeWidgetItem):
    """
    Use this class to create a new type of item for the collect tree/queue.
    """
    normal_brush = QtGui.QBrush(QtCore.Qt.black)
    highlighted_brush = QtGui.QBrush(QtGui.QColor(128, 128, 128))
    normal_pen = QtGui.QPen(QtCore.Qt.black)
    highlighted_pen = QtGui.QPen(QtGui.QColor(128, 128, 128))
    bg_brush = QtGui.QBrush(QtGui.QColor(0, 128, 0))
    bg_normal_brush = QtGui.QBrush(QtCore.Qt.white)

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QTreeWidgetItem.__init__(self, args[0], args[2])
        self.deletable = kwargs.pop('deletable', False)
        self.pen = QueueItem.normal_pen
        self.brush = QueueItem.normal_brush
        self.bg_brush = QueueItem.bg_normal_brush
        self.previous_bg_brush = QueueItem.bg_normal_brush
        self._queue_entry = None
        self._data_model = None
        self._checkable = True
        self._previous_check_state = False
        self._font_is_bold = False
        self.setText(1, '')         
 
    def listView(self):
        #remove this
        return self.treeWidget()

    def setOn(self, state):
        """
        Descript. : Backward compatability, because QueueManager and other
                    hwobj are using this method to change state 
        """ 
        if self._checkable:
            if state:
                check_state = QtCore.Qt.Checked
            else:
                check_state = QtCore.Qt.Unchecked
            self.setCheckState(0, check_state)
        else:
            self.setCheckState(0, QtCore.Qt.Unchecked)

    def setCheckState(self, column, check_state):
        """
        Descript. : sets check state for item and all children and parent
                    if they exist
        """    
        self._previous_check_state = self.checkState(0) 
        if isinstance(self, DataCollectionGroupQueueItem):
            self._checkable = False
            if self.childCount() == 0:
                self._checkable = True
            else:
                for index in range(self.childCount()):
                    if self.child(index)._checkable:
                        self._checkable = True
                        break
        if not self._checkable:
            check_state = QtCore.Qt.Unchecked  
        QtGui.QTreeWidgetItem.setCheckState(self, column, check_state)
        if self._queue_entry:
            self._queue_entry.set_enabled(check_state > 0)
        if self._data_model:
            self._data_model.set_enabled(check_state > 0)

    def update_check_state(self):
        """
        Descript. : in qt3 method was called stateChanged.
        """
        self.setCheckState(0, self.checkState(0))
        if type(self) in (SampleQueueItem, DataCollectionGroupQueueItem):
            for index in range(self.childCount()):
                self.child(index).setCheckState(0, self.checkState(0))  
        if isinstance(self.parent(), SampleQueueItem):
            self.parent().setCheckState(0, self.checkState(0))

    def move_item(self, after):
        """
        Descript. :
        """
        self.parent().takeChild(self.parent().indexOfChild(self))
        after.parent().insertChild(after.parent().indexOfChild(after), self)

        container_qe = self.get_queue_entry().get_container()
        after_qe = after.get_queue_entry()
        container_qe.swap(after_qe, self.get_queue_entry())
        
    def setHighlighted(self, enable):    
        """
        Controls highlighting of the list item.

        :param enable: Highlighted True, or not highlighted False.  
        :type enable: bool
        """
        if enable:
            self.pen = QueueItem.highlighted_pen
            self.brush = QueueItem.highlighted_brush
        else:
            self.pen = QueueItem.normal_pen
            self.brush = QueueItem.normal_brush

        if self.treeWidget():
            self.treeWidget().updateGeometry()

    def set_background_color(self, color_index):
        self.previous_bg_brush = self.background(0)
        color = Qt4_widget_colors.QUEUE_ENTRY_COLORS[color_index]
        self.bg_brush = QtGui.QBrush(color)
        self.setBackground(0, self.bg_brush)
        self.setBackground(1, self.bg_brush)

    def restoreBackgroundColor(self):
        self.bg_brush = self.previous_bg_brush
        self.setBackground(0, self.bg_brush)
        self.setBackground(1, self.bg_brush)

    def setFontBold(self, state):
        self._font_is_bold = state

    def reset_style(self):
        self.set_background_color(0)
        self.setFontBold(False)
        self.setHighlighted(False)

    def lastItem(self):
        """
        :returns: The last item of this child.
        :rtype: QueueItem
        """
        if self.childCount() > 0: 
            return self.child(self.childCount())

    def set_checkable(self, state):
        self._checkable = state

    def set_queue_entry(self, queue_entry):
        self._queue_entry = queue_entry

    def get_previous_check_state(self):
        return self._previous_check_state

    def get_queue_entry(self):
        return self._queue_entry

    def get_model(self):
        return self._data_model


class SampleQueueItem(QueueItem):
    def __init__(self, *args, **kwargs):
        #kwargs['controller'] = QtGui.QCheckListItem.CheckBoxController
        #kwargs['deletable'] = False
        self.mounted_style = False

        QueueItem.__init__(self, *args, **kwargs)
        

    def update_pin_icon(self):
        dc_tree_widget = self.listView().parent()

        if  dc_tree_widget._loaded_sample_item:
            dc_tree_widget._loaded_sample_item.setIcon(0, qt.QPixmap())
            
        dc_tree_widget._loaded_sample_item = self
        self.setIcon(0, QtGui.QIcon(dc_tree_widget.pin_pixmap))

    def set_mounted_style(self, state, clear_background = False):
        self.mounted_style = state

        if state:
            self.setIcon(0, QtGui.QIcon(PIN_PIXMAP))
            self.setBackground(0, QtGui.QBrush(Qt4_widget_colors.SKY_BLUE)) 
            self.setSelected(True)
            bold_fond = self.font(1)
            bold_fond.setBold(True)
            self.setFont(1, bold_fond)
            if self.parent():
                self.parent().setExpanded(True)
        else:
            self.setIcon(0, QtGui.QIcon())

            if clear_background:
               self.set_background_color(0)  
            else:
                queue_entry = self.get_queue_entry()

                if queue_entry:
                    queue_entry._set_background_color()

            self.setSelected(False)
            self.setFontBold(False)
            self.setText(1, '')

    def reset_style(self):
        #QueueItem.reset_style(self)
        self.set_background_color(0)
        self.setFontBold(False)
        self.setHighlighted(False)
        self.set_mounted_style(self.mounted_style, clear_background = True)
            
class BasketQueueItem(QueueItem):
    """
    In principle is just a group of samples (for example puck)
    """
    def __init__(self, *args, **kwargs):
        QueueItem.__init__(self, *args, **kwargs)

class TaskQueueItem(QueueItem):
    def __init__(self, *args, **kwargs):
        kwargs['deletable'] = True
        
        QueueItem.__init__(self, *args, **kwargs)

    def get_sample_view_item(self):
        if isinstance(self.parent(), SampleQueueItem):
            return self.parent()
        elif self.parent():
            return self.parent().get_sample_view_item()

class DataCollectionGroupQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)
    

class DataCollectionQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class CharacterisationQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class EnergyScanQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class XRFScanQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class GenericWorkflowQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class SampleCentringQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)

class AdvancedQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        print args, kwargs
        TaskQueueItem.__init__(self, *args, **kwargs)


MODEL_VIEW_MAPPINGS = \
    {queue_model_objects.DataCollection: DataCollectionQueueItem,
     queue_model_objects.Characterisation: CharacterisationQueueItem,
     queue_model_objects.EnergyScan: EnergyScanQueueItem,
     queue_model_objects.XRFScan: XRFScanQueueItem,
     queue_model_objects.SampleCentring: SampleCentringQueueItem,
     queue_model_objects.Sample: SampleQueueItem,
     queue_model_objects.Basket: BasketQueueItem, 
     queue_model_objects.Workflow: GenericWorkflowQueueItem,
     queue_model_objects.Advanced: AdvancedQueueItem,
     queue_model_objects.TaskGroup: DataCollectionGroupQueueItem}

