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


from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors

import queue_model_objects_v1 as queue_model_objects


PIN_ICON = Qt4_Icons.load_icon("sample_axis")
BALL_UNKNOWN = Qt4_Icons.load_icon("sphere_white")
BALL_RUNNING = Qt4_Icons.load_icon("sphere_orange")
BALL_FAILED = Qt4_Icons.load_icon("sphere_red")
BALL_FINISHED = Qt4_Icons.load_icon("sphere_green")


class QueueItem(QTreeWidgetItem):
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
        """
        Descript. :
        """
        QTreeWidgetItem.__init__(self, args[0])
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
        self._star = False
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
                check_state = Qt.Checked
            else:
                check_state = Qt.Unchecked
            self.setCheckState(0, check_state)
        else:
            self.setCheckState(0, Qt.Unchecked)

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
            self.parent().setCheckState(column, check_state)

        if not self._checkable:
            check_state = Qt.Unchecked  
        QTreeWidgetItem.setCheckState(self, column, check_state)
        if self._queue_entry:
            self._queue_entry.set_enabled(check_state > 0)
        if self._data_model:
            self._data_model.set_enabled(check_state > 0)

    def set_hidden(self, hidden):
        self.setHidden(hidden)
        for index in range(self.childCount()):
            self.child(index).setHidden(hidden)

        if self._queue_entry:
            self._queue_entry.set_enabled(not hidden)
        if self._data_model:
            self._data_model.set_enabled(not hidden)

    def update_check_state(self, new_state):
        """
        Descript. : in qt3 method was called stateChanged.
        """
        if new_state != self._previous_check_state:
            self.setCheckState(0, self.checkState(0))
            if isinstance(self, DataCollectionGroupQueueItem):
               for index in range(self.childCount()):
                   self.child(index).setCheckState(0, self.checkState(0))  

    def move_item(self, after):
        """
        Descript. :
        """
        self.parent().takeChild(self.parent().indexOfChild(self))
        after.parent().insertChild(after.parent().indexOfChild(after) + 1, self)

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
        self.bg_brush = QBrush(color)
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

    def update_display_name(self):
        self.setText(0, self._data_model.get_display_name())

    def update_tool_tip(self):
        pass

    def set_star(self, state):
        self._star = state

    def has_star(self):
        return self._star == True

    def get_all_grand_children(self):
        grand_children_list = []
        for child_index in range(self.childCount()):
            for grand_child_index in range(self.child(child_index).childCount()):
                grand_children_list.append(self.child(child_index).child(grand_child_index))
        return grand_children_list

class SampleQueueItem(QueueItem):
    def __init__(self, *args, **kwargs):
        #kwargs['controller'] = QtGui.QCheckListItem.CheckBoxController
        #kwargs['deletable'] = False
        self.mounted_style = False

        QueueItem.__init__(self, *args, **kwargs)
        

    def update_pin_icon(self):
        dc_tree_widget = self.listView().parent()

        if dc_tree_widget._loaded_sample_item:
            dc_tree_widget._loaded_sample_item.setIcon(0, QPixmap())
            
        dc_tree_widget._loaded_sample_item = self
        self.setIcon(0, QIcon(dc_tree_widget.pin_pixmap))

    def set_mounted_style(self, state, clear_background = False):
        self.mounted_style = state

        if state:
            self.setIcon(0, PIN_ICON)
            self.setBackground(0, QBrush(Qt4_widget_colors.PLUM)) 
            self.setBackground(1, QBrush(Qt4_widget_colors.PLUM))
            self.setSelected(True)
            bold_fond = self.font(1)
            bold_fond.setBold(True)
            self.setFont(1, bold_fond)
            if self.parent():
                self.parent().setExpanded(True)
        else:
            self.setIcon(0, QIcon())

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


    def init_processing_info(self):
        dc_model = self.get_model()
        dc_parameters = dc_model.as_dict()
        if dc_parameters["num_images"] > 19:
            pass
            # @~@~ Code below breaks - no such attribute 'processing_methods'
            # for index, processing_method in enumerate(dc_model.processing_methods):
            #     self.setIcon(2 + index, BALL_UNKNOWN)

    def init_tool_tip(self):
        dc_model = self.get_model()
        dc_parameters = dc_model.as_dict()
        dc_parameters_table = \
          '''<b>Collection parameters:</b>
             <table border='0.5'>
             <tr><td>Osc start</td><td>%.2f</td></tr>
             <tr><td>Osc range</td><td>%.2f</td></tr>
             <tr><td>Num images</td><td>%d</td></tr>
             <tr><td>Exposure time</td><td>%.4fs</td></tr>
             <tr><td>Energy</td><td>%.2f keV</td></tr>
             <tr><td>Resolution</td><td>%.2f Ang</td></tr>
             <tr><td>Transmission</td><td>%.2f %%</td></tr>
             </table>
          ''' % (dc_parameters["osc_start"],
                 dc_parameters["osc_range"],
                 dc_parameters["num_images"],
                 dc_parameters["exp_time"],
                 dc_parameters["energy"],
                 dc_parameters["resolution"],
                 dc_parameters["transmission"])

        thumb_info = ''
        if dc_model.is_executed():
            paths = dc_model.acquisitions[0].get_preview_image_paths()
            first_image_path = dc_model.acquisitions[0].path_template.\
                get_image_file_name() % dc_parameters["first_image"]
            if len(paths) == 1:
                thumb_info = \
                   '''<br><table border='0.5'>
                      <tr><td>%s</td></tr>
                      <tr><td><img src="%s" width=200></td></tr>
                      </table>
                  ''' % (first_image_path, paths[0])
            else:
                last_image_path = dc_model.acquisitions[0].\
                   path_template.get_image_file_name() % (dc_parameters["first_image"] + \
                                                          dc_parameters["num_images"])
                thumb_info = \
                   '''<br><table border='0.5'>
                      <tr><td>%s</td><td>%s</td></tr>
                      <tr><td><img src="%s" width=200></td>
                          <td><img src="%s" width=200></tr>
                      </table>
                  ''' % (first_image_path, last_image_path, paths[0], paths[-1])

        processing_msg = ''
        if len(dc_model.processing_msg_list) > 0:
            processing_msg = '<br><br><b>Processing info</b>'
            for msg in dc_model.processing_msg_list:
                processing_msg += '<br>%s' % msg

        tool_tip = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                    <html lang="en">
                    <body>
                       %s
                       %s
                       %s
                    </body>
                    </html>''' % (dc_parameters_table,
                                  thumb_info,
                                  processing_msg)
        self.setToolTip(0, tool_tip)

class CharacterisationQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class EnergyScanQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class XRFSpectrumQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class GenericWorkflowQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class GphlWorkflowQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


class SampleCentringQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)

class OpticalCentringQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)

class XrayCenteringQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)

class XrayImagingQueueItem(TaskQueueItem):
    def __init__(self, *args, **kwargs):
        TaskQueueItem.__init__(self, *args, **kwargs)


MODEL_VIEW_MAPPINGS = \
    {queue_model_objects.DataCollection: DataCollectionQueueItem,
     queue_model_objects.Characterisation: CharacterisationQueueItem,
     queue_model_objects.EnergyScan: EnergyScanQueueItem,
     queue_model_objects.XRFSpectrum: XRFSpectrumQueueItem,
     queue_model_objects.SampleCentring: SampleCentringQueueItem,
     queue_model_objects.OpticalCentring: OpticalCentringQueueItem,
     queue_model_objects.Sample: SampleQueueItem,
     queue_model_objects.Basket: BasketQueueItem, 
     queue_model_objects.Workflow: GenericWorkflowQueueItem,
     queue_model_objects.GphlWorkflow: GphlWorkflowQueueItem,
     queue_model_objects.XrayCentering: XrayCenteringQueueItem,
     #queue_model_objects.XrayImaging: XrayImagingQueueItem,
     queue_model_objects.TaskGroup: DataCollectionGroupQueueItem}

