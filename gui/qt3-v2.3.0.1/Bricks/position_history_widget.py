from collections import namedtuple
from qt import *
import logging


CollectionType = namedtuple(
    "CollectionType", ["SIMPLE", "HELICAL", "MUTIPOS", "MAD", "MESH"]
)
COLLECTION_TYPE = CollectionType(0, 1, 2, 3, 4)
CollectionTypeName = namedtuple(
    "CollectionTypeName", ["SIMPLE", "HELICAL", "MUTIPOS", "MAD", "MESH"]
)
COLLECTION_TYPE_NAME = CollectionTypeName(
    "Simple", "Helical", "Multi-position", "MAD", "Mesh"
)


class PositionHistoryBrickWidget(QWidget):
    def __init__(self, parent=None, name="position_history"):
        QWidget.__init__(self, parent, name)

        self.__stored_positions = []

        self.create_dc_db = None
        self.new_position_cb = None
        self.position_selected_cb = None
        self.delete_centrings_cb = None

        self.v_layout = QVBoxLayout(self)
        self.listbox_grid = QGridLayout(self, 2, 3)
        self.v_layout.addLayout(self.listbox_grid)
        self.h_layout = QHBoxLayout(self)

        self.point_label = QLabel("Positions", self)
        self.point_list_box = QListBox(self)
        self.point_list_box.setSelectionMode(QListBox.Extended)

        self.delete_point_button = QPushButton("-", self, "delete_shape_button")

        self.method_group_box = QVGroupBox("Collection method", self)
        self.method_combo_box = QComboBox(self.method_group_box, "method_combo_box")
        self.method_combo_box.insertItem(COLLECTION_TYPE_NAME.SIMPLE)
        self.method_combo_box.insertItem(COLLECTION_TYPE_NAME.HELICAL)
        self.method_combo_box.insertItem("Multi-position")
        self.method_combo_box.insertItem("MAD")
        self.method_combo_box.insertItem("Mesh")
        self.position_treatment_cbx = QCheckBox(
            "Independent centrings", self.method_group_box
        )
        self.use_characterisation_cbx = QCheckBox(
            "Use characterisation", self.method_group_box
        )
        self.create_collection_button = QPushButton("Create", self.method_group_box)

        self.listbox_grid.addWidget(self.point_label, 0, 0)
        self.listbox_grid.addWidget(self.point_list_box, 1, 0)
        self.listbox_grid.addLayout(self.h_layout, 2, 0)
        self.h_layout.addWidget(self.delete_point_button)
        self.v_layout.addWidget(self.method_group_box)

        QObject.connect(
            self.delete_point_button, SIGNAL("clicked()"), self.__delete_point
        )

        QObject.connect(
            self.create_collection_button, SIGNAL("clicked()"), self.__create_collection
        )

        QObject.connect(
            self.point_list_box, SIGNAL("selectionChanged()"), self.__selection_changed
        )

    def add_centred_position(self, state, centring_status):
        point = point_factory()
        point.update(centring_status["motors"])
        point.update(centring_status["extraMotors"])

        self.__stored_positions.append(point)
        QListBoxText(
            self.point_list_box, "Point " + str(self.point_list_box.numRows() + 1)
        )

        self.new_position_cb(point)

    def __selected_points_idx(self):
        selected_items = []

        for item_index in range(0, self.point_list_box.numRows()):
            if self.point_list_box.isSelected(item_index):
                selected_items.append(item_index)

        selected_items.reverse()

        return selected_items

    def selected_points(self):
        points = []

        for index in self.__selected_points_idx():
            points.append(self.__stored_positions[index])

        return points

    def get_collection_type(self):
        return COLLECTION_TYPE[self.method_combo_box.currentItem()]

    def __delete_point(self):
        points_to_delete = self.__selected_points_idx()
        for i in range(len(points_to_delete)):
            item_index = points_to_delete[i]
            self.point_list_box.removeItem(item_index - i)
            self.__stored_positions.pop(item_index - i)
        self.delete_centrings_cb(points_to_delete)

    def __create_collection(self):
        self.create_dc_cb()

    def __selection_changed(self, *args):
        self.position_selected_cb(self.__selected_points_idx())


def point_factory():
    return {"sampx": 0, "sampy": 0, "phi": 0, "phiz": 0, "phiy": 0, "zoom": 0}
