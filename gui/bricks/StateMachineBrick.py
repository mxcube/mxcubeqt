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

from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class StateMachineBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.state_machine_hwobj = None

        # Internal values -----------------------------------------------------
        self.cond_list = None
        self.states_list = None
        self.trans_list = None

        self.state_graph_node_list = []
        self.trans_graph_node_list = []
        self.condition_value_dict = {}

        # Properties ----------------------------------------------------------
        self.add_property("hwobj_state_machine", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _cond_states_gbox = QtImport.QGroupBox(r"States \ conditions", self)
        self.splitter = QtImport.QSplitter(QtImport.Qt.Vertical, self)
        self.cond_states_table = QtImport.QTableWidget(self.splitter)
        self.log_treewidget = QtImport.QTreeWidget(self.splitter)
        self.graph_graphics_view = QtImport.QGraphicsView(self)
        self.graph_graphics_scene = QtImport.QGraphicsScene(self)

        self.check_icon = Icons.load_icon("Check")
        self.reject_icon = Icons.load_icon("Delete")

        # Layout --------------------------------------------------------------
        _cond_states_gbox_vlayout = QtImport.QVBoxLayout(_cond_states_gbox)
        _cond_states_gbox_vlayout.addWidget(self.splitter)
        _cond_states_gbox_vlayout.setSpacing(2)
        _cond_states_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(_cond_states_gbox)
        _main_vlayout.addWidget(self.graph_graphics_view)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Other ---------------------------------------------------------------
        self.cond_states_table.verticalHeader().setDefaultSectionSize(20)
        self.cond_states_table.horizontalHeader().setDefaultSectionSize(20)
        # setSelectionMode(QtImport.QAbstractItemView::SingleSelection);
        font = self.cond_states_table.font()
        font.setPointSize(8)
        self.cond_states_table.setFont(font)

        self.splitter.setSizes([200, 20])
        self.log_treewidget.setColumnCount(6)
        self.log_treewidget.setHeaderLabels(
            ["State", "Start time", "End time", "Total time", "Previous state", "Notes"]
        )
        self.graph_graphics_view.setFixedSize(900, 600)
        self.graph_graphics_scene.setSceneRect(0, 0, 900, 600)
        self.graph_graphics_view.setScene(self.graph_graphics_scene)
        self.graph_graphics_view.setHorizontalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff
        )
        self.graph_graphics_view.setVerticalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff
        )
        self.graph_graphics_view.setDragMode(QtImport.QGraphicsView.RubberBandDrag)
        self.graph_graphics_view.setRenderHint(QtImport.QPainter.Antialiasing)
        self.graph_graphics_view.setRenderHint(QtImport.QPainter.TextAntialiasing)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "hwobj_state_machine":
            if self.state_machine_hwobj is not None:
                self.state_machine_hwobj.disconnect("stateChanged", self.state_changed)
                self.state_machine_hwobj.disconnect(
                    "conditionChanged", self.condition_changed
                )
            self.state_machine_hwobj = self.get_hardware_object(new_value)
            if self.state_machine_hwobj is not None:
                self.state_machine_hwobj.connect("stateChanged", self.state_changed)
                self.state_machine_hwobj.connect(
                    "conditionChanged", self.condition_changed
                )
                self.init_state_machine()
                self.init_state_graph()
                self.state_machine_hwobj.update_values()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def init_state_machine(self):
        self.cond_list = self.state_machine_hwobj.get_condition_list()
        self.states_list = self.state_machine_hwobj.get_state_list()
        self.trans_list = self.state_machine_hwobj.get_transition_list()

        self.cond_states_table.setRowCount(len(self.cond_list))
        # conditions = []
        # for key in self.cond_list.keys():
        #    conditions.append(self.cond_list[key]['name'])
        # self.cond_states_table.setVerticalHeaderLabels(self.cond_list.keys())

        self.cond_states_table.setColumnCount(len(self.states_list))
        self.cond_states_table.setHorizontalHeader(
            QtImport.RotatedHeaderView(self.cond_states_table)
        )

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
                temp_item = QtImport.QTableWidgetItem()
                self.cond_states_table.setItem(row, col, temp_item)

    def init_state_graph(self):
        for index, transition in enumerate(self.trans_list):
            start_coord, end_coord = self.get_coord_by_transition(transition)
            graph_transition = GraphTransition(
                self, index, start_coord, end_coord, transition
            )
            self.trans_graph_node_list.append(graph_transition)
            self.graph_graphics_scene.addItem(graph_transition)
        for index, state in enumerate(self.states_list):
            graph_state_node = GraphStateNode(self, index, state)
            self.state_graph_node_list.append(graph_state_node)
            self.graph_graphics_scene.addItem(graph_state_node)
        self.graph_graphics_scene.update()

    def state_changed(self, state_list):
        self.log_treewidget.clear()
        # state_list = [state_list]

        for state in state_list:
            temp_item = QtImport.QTreeWidgetItem()
            temp_item.setText(0, self.get_state_by_name(state["current_state"])["desc"])
            temp_item.setText(1, state["start_time"])
            temp_item.setText(2, state["end_time"])
            temp_item.setText(3, state["total_time"])
            temp_item.setText(
                4, self.get_state_by_name(state["previous_state"])["desc"]
            )
            self.log_treewidget.insertTopLevelItem(0, temp_item)

        for col in range(5):
            self.log_treewidget.resizeColumnToContents(col)

        new_state = state_list[-1]

        for col, state in enumerate(self.states_list):
            for row, condition in enumerate(self.cond_list):
                color = Colors.WHITE
                # if row % 5:
                #    color = Colors.WHITE
                if not col % 5 or not row % 5:
                    color = Colors.LIGHT_2_GRAY

                self.cond_states_table.item(row, col).setBackground(color)
                self.cond_states_table.item(row, col).setText("")
                self.cond_states_table.item(row, col).setIcon(QtImport.QIcon())

                for translation in self.trans_list:
                    if (
                        translation["source"] == new_state["current_state"]
                        and translation["dest"] == state["name"]
                    ):
                        if condition["name"] in translation["conditions_true"]:
                            self.cond_states_table.item(row, col).setBackground(
                                Colors.LIGHT_GREEN
                            )
                            # self.cond_states_table.item(row, col).setText(str(index))
                        elif condition["name"] in translation["conditions_false"]:
                            self.cond_states_table.item(row, col).setBackground(
                                Colors.LIGHT_RED
                            )
                            # self.cond_states_table.item(row, col).setText(str(index))
                        if (
                            condition["name"] in translation["conditions_true"]
                            or condition["name"] in translation["conditions_false"]
                        ):
                            if condition["value"]:
                                self.cond_states_table.item(row, col).setIcon(
                                    self.check_icon
                                )
                            else:
                                self.cond_states_table.item(row, col).setIcon(
                                    self.reject_icon
                                )

                if state["name"] == new_state["current_state"]:
                    if "error" in state.get("type", []):
                        color = Colors.LIGHT_RED
                    else:
                        color = Colors.LIGHT_GREEN
                    self.cond_states_table.item(row, col).setBackground(color)

        for graph_node in self.state_graph_node_list:
            graph_node.setSelected(
                graph_node.state_dict["name"] == new_state["current_state"]
            )
        self.graph_graphics_scene.update()

    def condition_changed(self, condition_list):
        for row, condition in enumerate(condition_list):
            if condition["value"]:
                self.cond_states_table.verticalHeaderItem(row).setIcon(self.check_icon)
            else:
                self.cond_states_table.verticalHeaderItem(row).setIcon(self.reject_icon)

    def get_coord_by_transition(self, transition_dict):
        for state in self.states_list:
            if state["name"] == transition_dict["source"]:
                start_coord = state["coord"]
        for state in self.states_list:
            if state["name"] == transition_dict["dest"]:
                end_coord = state["coord"]
        return start_coord, end_coord

    def get_state_by_name(self, state_name):
        for state in self.states_list:
            if state["name"] == state_name:
                return state

    def get_condition_index_by_name(self, name):
        for index, condition in enumerate(self.cond_list):
            if condition["name"] == name:
                return index


class GraphStateNode(QtImport.QGraphicsItem):
    def __init__(self, parent, index, state_dict):
        QtImport.QGraphicsItem.__init__(self)
        self.setFlags(QtImport.QGraphicsItem.ItemIsSelectable)
        #              QtImport.QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True)
        self.parent = parent
        self.rect = QtImport.QRectF(0, 0, 0, 0)
        self.setPos(state_dict["coord"][0], state_dict["coord"][1])

        self.index = index
        self.state_dict = state_dict
        self.custom_brush = QtImport.QBrush(QtImport.Qt.SolidPattern)

    def boundingRect(self):
        return self.rect.adjusted(0, 0, 40, 40)

    def paint(self, painter, option, widget):
        pen = QtImport.QPen(QtImport.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtImport.Qt.black)
        painter.setPen(pen)
        if self.isSelected():
            brush_color = QtImport.QColor(204, 255, 204)
        else:
            brush_color = QtImport.QColor(203, 212, 246)
        self.custom_brush.setColor(brush_color)
        painter.setBrush(self.custom_brush)
        painter.drawEllipse(-20, -20, 40, 40)
        paint_rect = QtImport.QRect(-20, -20, 40, 40)
        painter.drawText(paint_rect, QtImport.Qt.AlignCenter, str(self.index + 1))


class GraphTransition(QtImport.QGraphicsItem):
    def __init__(self, parent, index, start_pos, end_pos, trans_dict):
        QtImport.QGraphicsItem.__init__(self)
        self.parent = parent
        self.rect = QtImport.QRectF(0, 0, 0, 0)
        self.index = index
        self.start_pos = start_pos
        self.end_pos = end_pos

    def boundingRect(self):
        return self.rect.adjusted(0, 0, 40, 40)

    def paint(self, painter, option, widget):
        pen = QtImport.QPen(QtImport.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtImport.Qt.black)
        painter.setPen(pen)
        painter.drawLine(
            self.start_pos[0], self.start_pos[1], self.end_pos[0], self.end_pos[1]
        )
        painter.drawText(
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) / 2.0,
            self.start_pos[1]
            + (self.end_pos[1] - self.start_pos[1]) / 2.0
            + self.index,
            str(self.index + 1),
        )
