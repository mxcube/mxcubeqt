from collections import namedtuple
from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
import dc_tree_widget
import logging
import sys

__category__ = "mxCuBE"

ViewType = namedtuple("ViewType", ["ISPYB", "MANUAL", "SC"])
TREE_VIEW_TYPE = ViewType(0, 1, 2)


class MXTreeBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        reload(dc_tree_widget)

        self.defineSlot("add_data_collection", ())
        self.defineSlot("get_selected_sample", ())
        self.defineSignal("hideParametersTab", ())
        self.defineSignal("hideSampleCentringTab", ())
        self.defineSignal("populateParameterTable", ())
        self.defineSignal("get_tree_selection_changed", ())

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.view_combo_box = QComboBox(self, "view_combo_box")
        self.view_combo_box.insertItem("ISPyB")
        self.view_combo_box.insertItem("Manual")
        self.view_combo_box.insertItem("Sample changer")
        self.view_combo_box.setCurrentItem(2)

        self.sc_tree_widget = dc_tree_widget.DataCollectTree(self)
        self.sc_tree_widget.selection_changed_cb = self.selection_changed

        sc_content = get_sample_changer_data()
        sc_content.reverse()
        self.sc_tree_widget.init_with_sc_content(sc_content)

        self.cs_tree_widget = dc_tree_widget.DataCollectTree(self)
        self.cs_tree_widget.selection_changed_cb = self.selection_changed
        self.cs_tree_widget.init_with_sample(get_sample_data())
        self.cs_tree_widget.hide()

        self.ispyb_tree_widget = dc_tree_widget.DataCollectTree(self)
        self.ispyb_tree_widget.selection_changed_cb = self.selection_changed
        self.ispyb_tree_widget.init_with_ispyb_data(get_sample_data())
        self.ispyb_tree_widget.hide()

        QObject.connect(
            self.view_combo_box, SIGNAL("activated(int)"), self.combo_box_activated
        )

        QVBoxLayout(self)
        self.layout().addWidget(self.view_combo_box)
        self.layout().addWidget(self.sc_tree_widget)
        self.layout().addWidget(self.cs_tree_widget)
        self.layout().addWidget(self.ispyb_tree_widget)

    def combo_box_activated(self, index):

        if index == TREE_VIEW_TYPE.ISPYB:
            self.cs_tree_widget.hide()
            self.sc_tree_widget.hide()
            self.ispyb_tree_widget.show()
        elif index == TREE_VIEW_TYPE.MANUAL:
            self.cs_tree_widget.show()
            self.sc_tree_widget.hide()
            self.ispyb_tree_widget.hide()
        elif index == TREE_VIEW_TYPE.SC:
            self.sc_tree_widget.show()
            self.cs_tree_widget.hide()
            self.ispyb_tree_widget.hide()

    def selection_changed(self, item, dc):
        if item.node_type == dc_tree_widget.ITEM_TYPES.SAMPLE:
            self.emit(PYSIGNAL("hideParametersTab"), (True,))
            self.emit(PYSIGNAL("hideSampleCentringTab"), (False,))

        if item.node_type == dc_tree_widget.ITEM_TYPES.DC:
            self.emit(PYSIGNAL("hideSampleCentringTab"), (True,))
            self.emit(PYSIGNAL("hideParametersTab"), (False,))
            self.emit(PYSIGNAL("populateParameterTable"), (dc,))

        self.emit(PYSIGNAL("tree_selection_changed"), (item,))

    def get_selected_sample(self, selected_sample_dict):
        index = self.view_combo_box.currentItem()
        selected_sample = None

        if index == TREE_VIEW_TYPE.ISPYB:
            selected_sample = self.ispyb_tree_widget.get_selected_item()
        elif index == TREE_VIEW_TYPE.MANUAL:
            selected_sample = self.cs_tree_widget.get_selected_item()
        elif index == TREE_VIEW_TYPE.SC:
            selected_sample = self.sc_tree_widget.get_selected_item()

        if selected_sample:
            if selected_sample.node_type != dc_tree_widget.ITEM_TYPES.SAMPLE:
                selected_sample = None
        selected_sample_dict["sample_item"] = selected_sample

    def run(self):
        self.emit(PYSIGNAL("hideParametersTab"), (True,))
        self.emit(PYSIGNAL("hideSampleCentringTab"), (False,))

    def propertyChanged(self, propertyName, oldValue, newValue):
        # SAMPLE CODE: HOW TO DEAL WITH PROPERTY CHANGES
        # (PROPERTIES ARE SHOWN IN PROPERTY EDITOR IN DESIGN MODE ;
        # PROPERTIES COME FROM ADDPROPERTY IN CONSTRUCTOR)
        """
        if propertyName=="sampleChanger":
            self.clearList()
            if self.sampleChanger is not None:
                self.disconnect(self.sampleChanger, PYSIGNAL("loadedSampleChanged"), self.loadedSampleChanged)
            self.sampleChanger=self.getHardwareObject(newValue)
            if self.sampleChanger is not None:
                self.connect(self.sampleChanger, PYSIGNAL("loadedSampleChanged"), self.loadedSampleChanged)
                self.loadedSampleChanged(self.sampleChanger.getLoadedSample())
        """
        pass

    def add_data_collection(self, parameters, collection_type):

        index = self.view_combo_box.currentItem()

        if index == TREE_VIEW_TYPE.ISPYB:
            self.ispyb_tree_widget.add_data_collection(parameters, collection_type)
        elif index == TREE_VIEW_TYPE.MANUAL:
            self.cs_tree_widget.add_data_collection(parameters, collection_type)
        elif index == TREE_VIEW_TYPE.SC:
            self.sc_tree_widget.add_data_collection(parameters, collection_type)


def get_sample_changer_data():

    sc_data = [
        ("#ABCDEF12345", 1, 1, "", 16),
        ("#ABCDEF12345", 1, 2, "", 1),
        ("#ABCDEF12345", 1, 3, "", 1),
        ("#ABCDEF12345", 1, 4, "", 1),
        ("#ABCDEF12345", 1, 5, "", 1),
        ("#ABCDEF12345", 1, 6, "", 1),
        ("#ABCDEF12345", 1, 7, "", 1),
        ("#ABCDEF12345", 1, 8, "", 1),
        ("#ABCDEF12345", 1, 9, "", 1),
        ("#ABCDEF12345", 1, 10, "", 1),
        ("#ABCDEF12345", 5, 10, "", 1),
    ]

    return sc_data


def get_sample_data():
    sc_data = [("Current sample", "0:0", "", 16)]
    return sc_data
