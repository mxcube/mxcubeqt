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
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


class Qt4_StateMachineBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
	
        # Hardware objects ----------------------------------------------------
        self.state_machine_hwobj = None

        # Internal values -----------------------------------------------------
        self.cond_list = None
        self.states_list = None
        self.trans_list = None

        self.state_graph_node_list = []
        self.trans_graph_node_list = []

        # Properties ----------------------------------------------------------
        self.addProperty('hwobj_state_machine', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _cond_states_gbox = QGroupBox("States \ conditions", self)
        self.splitter = QSplitter(Qt.Vertical, self)
        self.cond_states_table = QTableWidget(self.splitter)
        self.log_treewidget = QTreeWidget(self.splitter)
        self.graph_graphics_view = QGraphicsView(self)
        self.graph_graphics_scene = QGraphicsScene(self)

        # Layout --------------------------------------------------------------
        _cond_states_gbox_vlayout = QVBoxLayout(_cond_states_gbox)
        _cond_states_gbox_vlayout.addWidget(self.splitter)
        _cond_states_gbox_vlayout.setSpacing(2) 
        _cond_states_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(_cond_states_gbox)
        _main_vlayout.addWidget(self.graph_graphics_view)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Other ---------------------------------------------------------------
        self.cond_states_table.verticalHeader().setDefaultSectionSize(20)
        self.cond_states_table.horizontalHeader().setDefaultSectionSize(20)
        #setSelectionMode(QAbstractItemView::SingleSelection);
        font = self.cond_states_table.font()
        font.setPointSize(8)
        self.cond_states_table.setFont(font)

        self.splitter.setSizes([200, 20])
        self.log_treewidget.setColumnCount(4)
        self.log_treewidget.setHeaderLabels(["Time", "State", "Previous state", "Notes"])

        self.graph_graphics_view.setFixedSize(900, 600)
        self.graph_graphics_scene.setSceneRect(0, 0, 900, 600)
        self.graph_graphics_view.setScene(self.graph_graphics_scene)
        self.graph_graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graph_graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        
        self.graph_graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graph_graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graph_graphics_view.setRenderHint(QPainter.TextAntialiasing)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'hwobj_state_machine':
            if self.state_machine_hwobj is not None:
                self.state_machine_hwobj.disconnect("stateChanged",
                                                    self.state_changed)
                self.state_machine_hwobj.disconnect("conditionChanged",
                                                    self.condition_changed)
            self.state_machine_hwobj = self.getHardwareObject(new_value)
            if self.state_machine_hwobj is not None:
                self.state_machine_hwobj.connect("stateChanged",
                                                 self.state_changed)
                self.state_machine_hwobj.connect("conditionChanged",
                                                 self.condition_changed)
            self.init_state_machine()
            self.init_state_graph()
            self.state_machine_hwobj.update_values()
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def init_state_machine(self):
        """Initiates GUI"""
        self.cond_list = self.state_machine_hwobj.get_condition_list()
        self.states_list = self.state_machine_hwobj.get_state_list()
        self.trans_list = self.state_machine_hwobj.get_transition_list()

        self.cond_states_table.setRowCount(len(self.cond_list))
        #conditions = []
        #for key in self.cond_list.keys():
        #    conditions.append(self.cond_list[key]['name'])  
        #self.cond_states_table.setVerticalHeaderLabels(self.cond_list.keys())

        self.cond_states_table.setColumnCount(len(self.states_list))
        self.cond_states_table.setHorizontalHeader(RotatedHeaderView(self.cond_states_table))

        states_name_list = []
        for index, state in enumerate(self.states_list):
            states_name_list.append("%d %s" % (index + 1, state["desc"]))
        self.cond_states_table.setHorizontalHeaderLabels(states_name_list)

        condition_name_list = []
        for index, condition in enumerate(self.cond_list):
            condition_name_list.append("%d %s" % (index + 1, condition["desc"]))
        self.cond_states_table.setVerticalHeaderLabels(condition_name_list)
        self.cond_states_table.resizeColumnsToContents()

        for col in range(self.cond_states_table.columnCount()):
            for row in range(self.cond_states_table.rowCount()):
                temp_item = QTableWidgetItem()
                temp_item.setBackground(Qt4_widget_colors.LIGHT_GRAY)
                self.cond_states_table.setItem(row, col, temp_item)


    def init_state_graph(self):
        for index, transition in enumerate(self.trans_list):
            start_coord, end_coord = self.get_coord_by_transition(transition)
            graph_transition = GraphTransition(self, index, start_coord,
                                               end_coord, transition)
            self.trans_graph_node_list.append(graph_transition)
            self.graph_graphics_scene.addItem(graph_transition)
        for index, state in enumerate(self.states_list):
            graph_state_node = GraphStateNode(self, index, state)
            self.state_graph_node_list.append(graph_state_node)
            self.graph_graphics_scene.addItem(graph_state_node)
        self.graph_graphics_scene.update()

    def state_changed(self, new_state):
        """State changed event"""
        temp_item = QTreeWidgetItem()
        temp_item.setText(0, new_state["time"])
        temp_item.setText(1, new_state["current_state"])
        temp_item.setText(2, new_state["previous_state"])        
        self.log_treewidget.insertTopLevelItem(0, temp_item)
        for col in range(4):
            self.log_treewidget.resizeColumnToContents(col)

        for col, state in enumerate(self.states_list):
            if state["name"] == new_state["current_state"]:
                 self.cond_states_table.horizontalHeaderItem(col).\
                      setIcon(Qt4_Icons.load_icon("Check"))
            else:
                 self.cond_states_table.horizontalHeaderItem(col).\
                      setIcon(QIcon())

            for row, condition in enumerate(self.cond_list):
                self.cond_states_table.item(row, col).\
                     setBackground(Qt4_widget_colors.LIGHT_GRAY)
                self.cond_states_table.item(row, col).setText("")

                for index, translation in enumerate(self.trans_list):
                    if translation["source"] == new_state["current_state"] and \
                       translation["dest"] == state["name"]:
                        if condition["name"] in translation["conditions_true"]:
                            self.cond_states_table.item(row, col).\
                              setBackground(Qt4_widget_colors.LIGHT_GREEN)
                            self.cond_states_table.item(row, col).setText(str(index)) 
                        elif condition["name"] in translation["conditions_false"]:
                            self.cond_states_table.item(row, col).\
                              setBackground(Qt4_widget_colors.LIGHT_RED)
                            self.cond_states_table.item(row, col).setText(str(index))

        for graph_node in self.state_graph_node_list:
            graph_node.setSelected(graph_node.state_dict["name"] == \
                                   new_state["current_state"])
        self.graph_graphics_scene.update()

    def condition_changed(self, condition_name, value):
        for row, condition in enumerate(self.cond_list):
            if condition["name"] == condition_name:
                if value:
                    self.cond_states_table.verticalHeaderItem(row).setIcon(\
                         Qt4_Icons.load_icon("Check"))
                else:
                    self.cond_states_table.verticalHeaderItem(row).setIcon(\
                         Qt4_Icons.load_icon("Delete"))

    def get_coord_by_transition(self, transition_dict):
        for state in self.states_list:
            if state["name"] == transition_dict["source"]:
                start_coord = state["coord"]
        for state in self.states_list:
            if state["name"] == transition_dict["dest"]:
                end_coord = state["coord"]
        return start_coord, end_coord

class GraphStateNode(QGraphicsItem):

    def __init__(self, parent, index, state_dict):
        QGraphicsItem.__init__(self)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        #              QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True)
        self.parent = parent
        self.rect = QRectF(0, 0, 0, 0)
        self.setPos(state_dict["coord"][0],
                    state_dict["coord"][1])

        self.index = index
        self.state_dict = state_dict
        self.custom_brush = QBrush(Qt.SolidPattern)

    def boundingRect(self):
        return self.rect.adjusted(0, 0, 40, 40)

    def paint(self, painter, option, widget):
        """
        Descript. :
        """
        pen = QPen(Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        if self.isSelected():
            brush_color = QColor(204, 255, 204)
        else:
            brush_color = QColor(203, 212, 246)
        self.custom_brush.setColor(brush_color)
        painter.setBrush(self.custom_brush)
        painter.drawEllipse(-20, -20, 40, 40)
        paint_rect = QRect(-20, -20, 40, 40)
        painter.drawText(paint_rect, Qt.AlignCenter, str(self.index + 1))

class GraphTransition(QGraphicsItem):

    def __init__(self, parent, index, start_pos, end_pos, trans_dict):
        QGraphicsItem.__init__(self)
        self.parent = parent
        self.rect = QRectF(0, 0, 0, 0)
        self.index = index
        self.start_pos = start_pos
        self.end_pos = end_pos

    def boundingRect(self):
        return self.rect.adjusted(0, 0, 40, 40)

    def paint(self, painter, option, widget):
        """
        Descript. :
        """
        pen = QPen(Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.drawLine(self.start_pos[0], self.start_pos[1],
                         self.end_pos[0], self.end_pos[1])
        painter.drawText(self.start_pos[0] + \
                         (self.end_pos[0] - self.start_pos[0]) / 2.,
                         self.start_pos[1] + \
                         (self.end_pos[1] - self.start_pos[1]) / 2. + self.index,
                         str(self.index + 1))
