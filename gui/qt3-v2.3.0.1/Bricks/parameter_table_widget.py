from qt import *
from qttable import QTable, QTableItem


class ParametersTable(QWidget):
    def __init__(self, parent=None, name="parameter_table"):
        QWidget.__init__(self, parent, name)

        self.__dc_parameters = None

        self.add_dc_cb = None

        self.parameters_label = QLabel(self, "parameters_label")

        self.parameter_table = QTable(self, "parameter_table")
        self.parameter_table.setNumCols(3)
        self.parameter_table.horizontalHeader().setLabel(0, self.__tr("Name"), -1)
        self.parameter_table.horizontalHeader().setLabel(1, self.__tr("Value"))
        self.parameter_table.verticalHeader().hide()
        self.parameter_table.horizontalHeader().setClickEnabled(False, 0)
        self.parameter_table.horizontalHeader().setClickEnabled(False, 1)
        self.parameter_table.setColumnWidth(0, 200)
        self.parameter_table.setColumnWidth(1, 200)
        self.parameter_table.hideColumn(2)
        self.parameter_table.setColumnReadOnly(0, True)
        self.parameter_table.setLeftMargin(0)
        self.parameter_table.setNumRows(0)
        self.position_label = QLabel("Positions", self, "position_view")
        self.position_label.setAlignment(Qt.AlignTop)

        ##        self.add_button = QPushButton(self, "add_button")
        # self.add_button.setDisabled(True)

        h_layout = QGridLayout(self, 1, 2)
        v_layout_position = QVBoxLayout(self)
        v_layout_position.addWidget(self.position_label)
        v_layout_table = QVBoxLayout(self)
        h_layout.addLayout(v_layout_table, 0, 0)
        h_layout.addLayout(v_layout_position, 0, 1)
        v_layout_table.addWidget(self.parameters_label)
        v_layout_table.addWidget(self.parameter_table)
        # v_layout_table.addWidget(self.add_button)

        # self.languageChange()

        # QObject.connect(self.add_button, SIGNAL("clicked()"),
        # self.__add_data_collection)

        QObject.connect(
            self.parameter_table,
            SIGNAL("valueChanged(int, int)"),
            self.__parameter_value_change,
        )

        # self.populate_parameter_table(self.__dc_parameters)

    # def languageChange(self):
    # self.add_button.setText("Add")

    def __tr(self, s, c=None):
        return qApp.translate("parameter_table", s, c)

    def __add_data_collection(self):
        return self.add_dc_cb(self.__dc_parameters, self.collection_type)

    def populate_parameter_table(self, parameters):
        self.parameter_table.setNumRows(11)
        i = 0
        for param_key, parameter in parameters.items():

            if param_key != "positions":
                self.parameter_table.setText(i, 0, parameter[0])
                self.parameter_table.setText(i, 1, parameter[1])
                self.parameter_table.setText(i, 2, param_key)
                i += 1

    # def add_positions(self, positions):
    # self.__dc_parameters['positions'].extend(positions)

    def __parameter_value_change(self, row, col):
        self.__dc_parameters[str(self.parameter_table.item(row, 2).text())][1] = str(
            self.parameter_table.item(row, 1).text()
        )


# def dc_parameter_factory():
# return { 'prefix': ['Prefix', 'prefix'],
# 'run_number' : ['Run Number', '1'],
# 'template' : ['Template', '#prefix_1_####.mccd'],
# 'first_image' : ['First image #:', '1'],
# 'num_images' : ['Number of images', '1'],
# 'osc_start' : ['Oscillation start', '0.00'],
# 'osc_range' : ['Oscillation range', '1.00'],
# 'exp_time' : ['Exposure time(s)', '1.0'],
# 'num_passes' : ['Number of passes', '1'],
# 'comments' : ['Comments', 'comments'],
# 'path' : ['Path', '/some/nice/path'],
# 'positions': []}
