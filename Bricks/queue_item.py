import time
import random
import copy
import functools
import queue_model_objects_v1 as queue_model_objects
import gevent
import gevent.event
import collections
import logging
import os
import pprint
import widgets.widget_utils

from qt import *
from widgets.position_history_widget import COLLECTION_METHOD_NAME
from queue_model_objects_v1 import COLLECTION_ORIGIN
from queue_model_objects_v1 import STRATEGY_COMPLEXITY
from queue_model_objects_v1 import EXPERIMENT_TYPE
from queue_model_objects_v1 import STRATEGY_OPTION
from queue_model_objects_v1 import COLLECTION_ORIGIN_STR


class QueueItem(QCheckListItem):
    """
    Use this class to create a new type of item for the collect tree/queue.
    """

    normal_brush = QBrush(Qt.black)
    highlighted_brush = QBrush(QColor(128, 128, 128))
    normal_pen = QPen(Qt.black)
    highlighted_pen = QPen(QColor(128, 128, 128))
    bg_brush = QBrush(QColor(0, 128, 0))
    bg_normal_brush = QBrush(Qt.white)

    def __init__(self, *args, **kwargs):
        # All subclasses should have the following
        # data attributes.
        self.deletable = kwargs.pop('deletable', False)
        controller = kwargs.pop('controller', None)
        args = args + (controller, )

        QCheckListItem.__init__(self, *args, **kwargs)

        self.pen = QueueItem.normal_pen
        self.brush = QueueItem.normal_brush
        self.bg_brush = QueueItem.bg_normal_brush
        self.previous_bg_brush = QueueItem.bg_normal_brush
        self._queue_entry = None
        self._data_model = None

        

    def activate(self):
         """
         Inherited from QCheckListitem, called whenever the user presses the 
         mouse on this item or presses Space on it. 
         """
         QCheckListItem.activate(self)


    def stateChange(self, state):
        QCheckListItem.stateChange(self, state)
        # The QCheckListItem is somewhat tricky:
        # state = 0     The item is unchecked.
        #
        # state = 1     The item is checked but
        #               not all of the children
        #
        # state = 2     The item and all its children are
        #               checked.
        #
        # However the state passed by stateChanged are a boolean
        # we have to use the state() member to get the actual state.
        # Great !

        if self._queue_entry:
            if self.state() > 0:
                self._queue_entry.set_enabled(True)                
            else:
                self._queue_entry.set_enabled(False)

        if self._data_model:
            if self.state() > 0:
                self._data_model.set_enabled(True)                
            else:
                self._data_model.set_enabled(False)


    def paintCell(self, painter, color_group, column, width, align):
        """
        Inherited from QCheckListItem, called before this item is drawn
        on the screen.

        The qt3 documentation has more information about this method that
        can be worth reading.
        """

        try:
            painter.save()
            color_group = QColorGroup(color_group)
            color_group.setColor(QColorGroup.Text, self.brush.color())
            color_group.setBrush(QColorGroup.Text, self.brush)
            color_group.setColor(QColorGroup.Base, self.bg_brush.color())

            QCheckListItem.paintCell(self, painter, color_group, 
                                     column, width, align)
        finally:
            painter.restore()


    def paintFocus(self, painter, color_group, rect):
        """
        Inherited from QCheckListItem, called when the item get focus.

        The qt3 documentation has more information about this method that
        can be worth reading.
        """

        color_group.setColor(QColorGroup.Text, self.brush.color())
        color_group.setBrush(QColorGroup.Text, self.brush)

        QCheckListItem.paintFocus(self, painter, color_group, rect)

        color_group.setColor(QColorGroup.Text, self.normal_brush.color())
        color_group.setBrush(QColorGroup.Text, self.normal_brush)


    def moveItem(self, after):
        QCheckListItem.moveItem(self, after)
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

        self.listView().triggerUpdate()


    def setBackgroundColor(self, color):
        self.previous_bg_brush = self.bg_brush
        self.bg_brush = QBrush(color)


    def restoreBackgroundColor(self):
        self.bg_brush = self.previous_bg_brush

    
    def lastItem(self):
        """
        :returns: The last item of this child.
        :rtype: QueueItem
        """
        sibling = self.firstChild()
        last_child = None

        while(sibling):
            last_child = sibling
            sibling = sibling.nextSibling()
            
        return last_child


    def setOn(self, state):
        QCheckListItem.setOn(self, state)

        if self._queue_entry:
            self._queue_entry.set_enabled(state)

        if self._data_model:
            self._data_model.set_enabled(state)


    def set_queue_entry(self, queue_entry):
        self._queue_entry = queue_entry


    def get_queue_entry(self):
        return self._queue_entry


    def get_model(self):
        return self._data_model


    def get_next_free_name(self, name):
        names = []
        current_item = self.firstChild()

        while current_item:
            names.append(str(current_item.text()))
            current_item = current_item.nextSibling()

        num = widgets.widget_utils.next_free_name(names, name)

        return name + ' - ' + str(num)


class SampleQueueItem(QueueItem):
    def __init__(self, *args, **kwargs):
        kwargs['controller'] = QCheckListItem.CheckBoxController
        kwargs['deletable'] = False
        
        QueueItem.__init__(self, *args, **kwargs)


    def update_pin_icon(self):
        dc_tree_widget = self.listView().parent()

        if  dc_tree_widget._loaded_sample_item:
            dc_tree_widget._loaded_sample_item.setPixmap(0, QPixmap())
            
        dc_tree_widget._loaded_sample_item = self
        self.setPixmap(0, dc_tree_widget.pin_pixmap)
        

class TaskQueueItem(QueueItem):
    def __init__(self, *args, **kwargs):
        kwargs['controller'] = QCheckListItem.CheckBoxController
        kwargs['deletable'] = True
        
        QueueItem.__init__(self, *args, **kwargs)


    def get_sample_view_item(self):
        if isinstance(self.parent(), SampleQueueItem):
            return self.parent()
        else:
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
        TaskQueueItem.__init__(self, args, kwargs)


class GenericWorkflowQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class SampleCentringQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


#
# Functional API for QListItems
#
def perform_on_children(node, cond, fun):
    child = node.firstChild()
    result = []

    while child:
        if isinstance(child, QueueItem):
            if cond(child):
                res = fun(child)
                if res:
                    result.append(res)

            result.extend(perform_on_children(child, cond, fun))

        child = child.nextSibling()

    return result    


def is_selected(node):
    return node.isSelected()


def is_selected_sample(node):
    return node.isSelected() and isinstance(node, SampleQueueItem)


def is_selected_dc(node):
    return node.isSelected() and isinstance(node, DataCollectionQueueItem)


def is_selected_task_node(node):
    return node.isSelected() and isinstance(node, DataCollectionGroupQueueItem)


def is_selected_task(node):
    return node.isSelected() and isinstance(node, TaskQueueItem)


def is_task(node):
    return isinstance(node, TaskQueueItem)


def is_dc(node):
    return isinstance(node, DCListItem)


def is_sample(node):
    return isinstance(node, SampleQueueItem)


def get_item(node):
    return node


def is_child_on(node):
    return node.state() > 0


def is_checked(node):
    return node.state() > 0


def print_text(node):
    print "Executing node: " + node.text()


MODEL_VIEW_MAPPINGS = \
    {queue_model_objects.DataCollection: DataCollectionQueueItem,
     queue_model_objects.Characterisation: CharacterisationQueueItem,
     queue_model_objects.EnergyScan: EnergyScanQueueItem,
     queue_model_objects.SampleCentring: SampleCentringQueueItem,
     queue_model_objects.Sample: SampleQueueItem,
     queue_model_objects.Workflow: GenericWorkflowQueueItem,
     queue_model_objects.TaskGroup: DataCollectionGroupQueueItem}

