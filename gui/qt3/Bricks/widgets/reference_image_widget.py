from qt import *

from widgets.acquisition_widget import AcquisitionWidget
from widgets.data_path_widget import DataPathWidget


class ReferenceImageWidget(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("ReferenceImageWidget")

        self.main_layout = QVBoxLayout(self, 0, 4, "main_layout")
        self.gbox = QVGroupBox(self, "group_box")
        self.gbox.setTitle("Reference images")
        self.tool_box = QToolBox(self.gbox, "tool_box")
        self.page_layout = QVBox(self.tool_box, "page_layout")
        self.page_layout.setSpacing(7)

        self.path_widget = DataPathWidget(self.page_layout)
        self.path_widget.setBackgroundMode(QWidget.PaletteBackground)

        self.acq_gbox = QVGroupBox(self.page_layout)
        self.acq_gbox.setInsideMargin(2)
        self.acq_gbox.setTitle("Acquisition")

        self.acq_widget = AcquisitionWidget(self.acq_gbox, "horizontal")
        self.acq_widget.setBackgroundMode(QWidget.PaletteBackground)
        self.acq_widget.acq_widget_layout.child("inverse_beam_cbx").hide()
        self.acq_widget.acq_widget_layout.child("shutterless_cbx").hide()
        self.acq_widget.acq_widget_layout.child("subwedge_size_label").hide()
        self.acq_widget.acq_widget_layout.child("subwedge_size_ledit").hide()
        self.acq_widget.acq_widget_layout.setFixedHeight(160)

        self.tool_box.addItem(self.page_layout, "Acquisition parameters")

        self.main_layout.addWidget(self.gbox)
        # self.main_layout.addStretch()
