import logging
import queue_item

from collections import namedtuple
from widgets.create_helical_widget import CreateHelicalWidget
from widgets.create_discrete_widget import CreateDiscreteWidget
from widgets.create_mesh_widget import CreateMeshWidget
from widgets.create_char_widget import CreateCharWidget
from qt import *


CollectionMethod = namedtuple(
    "CollectionMethod", ["DISCRETE", "HELICAL", "MESH", "MULTI_POS"]
)

COLLECTION_METHOD = CollectionMethod(0, 1, 2, 3)

CollectionMethodName = namedtuple(
    "CollectionMethodName", ["DISCRETE", "HELICAL", "MESH", "MULTI_POS"]
)

COLLECTION_METHOD_NAME = CollectionMethodName(
    "Discrete", "Helical", "Mesh", "Multi position"
)

ExperimentType = namedtuple(
    "ExperimentType", ["SAD", "SAD_INV", "OSC", "MAD", "BURN", "MAD_INV", "SCREENING"]
)


class PositionHistoryBrickWidget(QWidget):
    def __init__(self, parent=None, name="position_history", qub_helper=None):
        QWidget.__init__(self, parent, name)

        #
        # Data attributes
        #

        self.__stored_positions = []

        self.tree_brick = None
        self.qub_helper = qub_helper

        self.create_dcg_db = None
        self.new_position_cb = None
        self.position_selected_cb = None
        self.delete_centrings_cb = None

        self.points_cnt = 0
        self.prev_point = None
        self.current_point = None

        # Diffractometer hardware object
        self.diffractometer_hwobj = None

        #
        # Layout
        #
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setSpacing(10)
        # self.v_layout = QVGroupBox("Centred positions", self)
        # self.method_group_box = QVGroupBox("Collection method", self)

        self.point_list_box = QListBox(self)
        self.point_list_box.setFixedWidth(125)
        self.point_list_box.setSelectionMode(QListBox.Extended)

        self.delete_point_button = QPushButton("Remove", self, "delete_point_button")

        # self.method_group_box.setFixedWidth(300)

        # self.tool_box = QToolBox(self.method_group_box , "tool_box")

        # self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete",
        #                                          qub_helper = qub_helper)
        # self.discrete_page.setBackgroundMode(QWidget.PaletteBackground)

        # self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        # self.char_page.setBackgroundMode(QWidget.PaletteBackground)

        # self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page",
        #                                        qub_helper = qub_helper)
        # self.helical_page.setBackgroundMode(QWidget.PaletteBackground)

        # self.mesh_page = CreateMeshWidget(self.tool_box, "Mesh")
        # self.mesh_page.setBackgroundMode(QWidget.PaletteBackground)

        # self.tool_box.addItem(self.discrete_page, "Discrete")
        # self.tool_box.addItem(self.char_page, "Characterise")
        # self.tool_box.addItem(self.helical_page, "Helical")
        # self.tool_box.addItem(self.mesh_page, "Mesh")

        # self.create_collection_button = \
        #    QPushButton("Add", self.method_group_box)

        # self.h_layout.addWidget(self.v_layout)
        # self.h_layout.addWidget(self.method_group_box)
        self.v_layout.addWidget(self.point_list_box)
        self.v_layout.addWidget(self.delete_point_button)
        # self.v_layout.addStretch()

        QObject.connect(
            self.delete_point_button, SIGNAL("clicked()"), self.delete_clicked
        )

        # QObject.connect(self.create_collection_button, SIGNAL("clicked()"),
        #                self.create_collection)

        QObject.connect(
            self.point_list_box, SIGNAL("selectionChanged()"), self.__selection_changed
        )

        QObject.connect(
            self.point_list_box, SIGNAL("clicked(QListBoxItem*)"), self.__list_box_click
        )

        QObject.connect(
            self.point_list_box,
            SIGNAL("doubleClicked(QListBoxItem*)"),
            self.__list_box_double_click,
        )

    def page_changed(self, index):
        if index != 1:
            self.qub_helper.hide_lines()

    def add_centred_position(self, state, cpos):
        self.points_cnt += 1
        self.__stored_positions.append(cpos)
        QListBoxText(self.point_list_box, "Point " + str(self.points_cnt))

        if callable(self.new_position_cb):
            self.new_position_cb(cpos)

        return cpos

    def __selected_points_idx(self):
        selected_items = []

        for item_index in range(0, self.point_list_box.numRows()):
            if self.point_list_box.isSelected(item_index):
                selected_items.append(item_index)

        selected_items.reverse()

        return selected_items

    def selected_points(self):
        """
        :returns: List with tuples on the form
            (CPosition pos, QString name, int index)
        """
        points = []

        for index in self.__selected_points_idx():
            points.append(
                (
                    self.__stored_positions[index],
                    self.point_list_box.item(index).text(),
                    index,
                )
            )

        return points

    def delete_positions(self, positions):
        for cpos in positions:
            self.qub_helper.remove_line(qub_pos=self.qub_helper.qub_points[cpos[0]])
            self.point_list_box.removeItem(cpos[2])
            self.__stored_positions.pop(cpos[2])

        self.delete_centrings_cb(positions)

    def delete_clicked(self):
        selected_positions = self.selected_points()
        self.delete_positions(selected_positions)

    def clear_positions(self):
        points = []

        indices = range(0, self.point_list_box.numRows())
        indices.reverse()

        for index in indices:
            points.append(
                (
                    self.__stored_positions[index],
                    self.point_list_box.item(index).text(),
                    index,
                )
            )

        self.delete_positions(points)

    def __selection_changed(self):
        self.position_selected_cb(self.selected_points())

    def __list_box_click(self, item):
        if not item:
            self.position_selected_cb([])

    def __list_box_double_click(self, item):
        if item:
            points = self.selected_points()

            if len(points) == 1:
                self.diffractometer_hwobj.moveToCentredPosition(
                    points[0][0], wait=False
                )
