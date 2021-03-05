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

"""Connection editor"""

from gui.utils import Icons, QtImport


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class ConnectionEditor(QtImport.QDialog):
    """Connection editor"""

    def __init__(self, configuration):

        QtImport.QDialog.__init__(self, None)

        # Internal values -----------------------------------------------------
        self.has_changed = None
        self.configuration = configuration
        self.signalling_child_dict = {}
        self.receiving_child_dict = {}
        self.connecting_child_dict = {}

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        main_splitter = QtImport.QSplitter(QtImport.Qt.Vertical, self)
        top_panel = QtImport.QWidget(main_splitter)
        bot_panel = QtImport.QWidget(main_splitter)

        emitter_panel = QtImport.QWidget(top_panel)
        self.emitter_windows_listwidget = QtImport.QListWidget(emitter_panel)
        self.emitter_objects_listwidget = QtImport.QListWidget(emitter_panel)
        self.emitter_signals_listwidget = QtImport.QListWidget(emitter_panel)
        self.emitter_objects_listwidget.setSortingEnabled(True)
        self.emitter_signals_listwidget.setSortingEnabled(True)

        receiver_panel = QtImport.QWidget(top_panel)
        self.receiver_windows_listwidget = QtImport.QListWidget(emitter_panel)
        self.receiver_objects_listwidget = QtImport.QListWidget(emitter_panel)
        self.receiver_slots_listwidget = QtImport.QListWidget(emitter_panel)
        self.receiver_objects_listwidget.setSortingEnabled(True)
        self.receiver_slots_listwidget.setSortingEnabled(True)

        self.add_connection_button = QtImport.QPushButton("Add connection", self)

        self.connections_treewidget = QtImport.QTreeWidget(bot_panel)
        button_panel = QtImport.QWidget(bot_panel)
        self.remove_connection_button = QtImport.QPushButton(
            "Remove connection", button_panel
        )
        self.ok_button = QtImport.QPushButton("OK", button_panel)
        self.cancel_button = QtImport.QPushButton("Cancel", button_panel)

        # Layout --------------------------------------------------------------
        emitter_panel_layout = QtImport.QGridLayout(emitter_panel)
        emitter_panel_layout.addWidget(
            QtImport.QLabel("<h3>Emitters</h3>", self), 0, 1, QtImport.Qt.AlignHCenter
        )
        emitter_panel_layout.addWidget(QtImport.QLabel("Windows", self), 1, 0)
        emitter_panel_layout.addWidget(QtImport.QLabel("Objects", self), 1, 1)
        emitter_panel_layout.addWidget(QtImport.QLabel("Signals", self), 1, 2)
        emitter_panel_layout.addWidget(self.emitter_windows_listwidget, 2, 0)
        emitter_panel_layout.addWidget(self.emitter_objects_listwidget, 2, 1)
        emitter_panel_layout.addWidget(self.emitter_signals_listwidget, 2, 2)

        receiver_panel_layout = QtImport.QGridLayout(receiver_panel)
        receiver_panel_layout.addWidget(
            QtImport.QLabel("<h3>Receivers</h3>", self), 0, 1, QtImport.Qt.AlignHCenter
        )
        receiver_panel_layout.addWidget(QtImport.QLabel("Windows", self), 1, 0)
        receiver_panel_layout.addWidget(QtImport.QLabel("Objects", self), 1, 1)
        receiver_panel_layout.addWidget(QtImport.QLabel("Slots", self), 1, 2)
        receiver_panel_layout.addWidget(self.receiver_windows_listwidget, 2, 0)
        receiver_panel_layout.addWidget(self.receiver_objects_listwidget, 2, 1)
        receiver_panel_layout.addWidget(self.receiver_slots_listwidget, 2, 2)

        top_panel_layout = QtImport.QHBoxLayout(top_panel)
        top_panel_layout.addWidget(emitter_panel)
        top_panel_layout.addWidget(receiver_panel)
        top_panel_layout.addWidget(self.add_connection_button)
        top_panel_layout.setSpacing(0)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)

        button_panel_layout = QtImport.QHBoxLayout(button_panel)
        button_panel_layout.addWidget(self.remove_connection_button)
        button_panel_layout.addStretch(0)
        button_panel_layout.addWidget(self.ok_button, QtImport.Qt.AlignRight)
        button_panel_layout.addWidget(self.cancel_button, QtImport.Qt.AlignRight)

        bot_panel_vlayout = QtImport.QVBoxLayout(bot_panel)
        bot_panel_vlayout.addWidget(
            QtImport.QLabel("<h3>Established connections</h3>", bot_panel)
        )
        bot_panel_vlayout.addWidget(self.connections_treewidget)
        bot_panel_vlayout.addWidget(button_panel)

        main_splitter_vbox = QtImport.QVBoxLayout(main_splitter)
        main_splitter_vbox.addWidget(top_panel)
        main_splitter_vbox.addWidget(bot_panel)
        main_splitter_vbox.setSpacing(5)
        main_splitter_vbox.setContentsMargins(2, 2, 2, 2)

        main_layout = QtImport.QVBoxLayout(self)
        main_layout.addWidget(main_splitter)

        # SizePolicies --------------------------------------------------------
        self.add_connection_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.remove_connection_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.ok_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.cancel_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.connections_treewidget.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding
        )

        # Qt signal/slot connections ------------------------------------------
        self.emitter_windows_listwidget.currentItemChanged.connect(
            self.emitter_window_changed
        )
        self.emitter_objects_listwidget.currentItemChanged.connect(
            self.emitter_object_changed
        )
        self.receiver_windows_listwidget.currentItemChanged.connect(
            self.receiver_window_changed
        )
        self.receiver_objects_listwidget.currentItemChanged.connect(
            self.receiver_object_changed
        )
        self.add_connection_button.clicked.connect(self.add_connection_button_clicked)
        self.remove_connection_button.clicked.connect(
            self.remove_connection_button_clicked
        )
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.connections_treewidget.itemSelectionChanged.connect(
            self.connections_treewidget_selection_changed
        )

        # Other ---------------------------------------------------------------
        self.connections_treewidget.setColumnCount(7)
        self.connections_treewidget.setHeaderLabels(
            [
                "",
                "Emitter window",
                "Emitter object",
                "Signal",
                "Receiver window",
                "Receiver object",
                "Slot",
            ]
        )
        self.setWindowTitle("Connection Editor")
        self.connections_treewidget.setSortingEnabled(True)

    def get_signalling_children(self, parent):
        """Gets signalling children"""

        children = []
        for child in parent["children"]:
            n_signals = 0
            try:
                n_signals = len(child["signals"])
            except KeyError:
                # item is a brick
                if hasattr(child, "brick"):
                    n_signals = len(child["brick"].get_signals())

            if n_signals > 0:
                children.append(child)

            children += self.get_signalling_children(child)

        return children

    def get_receiver_children(self, parent):
        """Returns receiver children"""

        children = []
        for child in parent["children"]:
            n_slots = 0
            try:
                n_slots = len(child["slots"])
            except KeyError:
                # item is a brick
                if hasattr(child, "brick"):
                    n_slots = len(child["brick"].get_slots())

            if n_slots > 0:
                children.append(child)

            children += self.get_receiver_children(child)

        return children

    def get_connecting_children(self, parent):
        """Returns connecting children"""

        children = []
        for child in parent["children"]:
            if len(child["connections"]):
                children.append(child)

            children += self.get_connecting_children(child)

        return children

    def show_connections(self, configuration):
        """Show all connections"""

        self.configuration = configuration
        self.has_changed = False

        self.emitter_windows_listwidget.clear()
        self.receiver_windows_listwidget.clear()
        for sender_window in self.configuration.windows_list:
            self.emitter_windows_listwidget.addItem(sender_window["name"])
            self.receiver_windows_listwidget.addItem(sender_window["name"])
        self.emitter_windows_listwidget.setFont(self.emitter_windows_listwidget.font())
        self.receiver_windows_listwidget.setFont(
            self.receiver_windows_listwidget.font()
        )

        def __sender_in_window(sender_name, window):
            """Checks if sender in window"""

            window_name = window["name"]

            self.signalling_child_dict[window_name] = self.get_signalling_children(
                window
            )

            result = False
            for sender in self.signalling_child_dict[window_name]:
                if sender["name"] == sender_name:
                    result = True
                    break

            return result

        def __receiver_in_window(receiver_name, window):
            """Checks if receiver in window"""

            window_name = window["name"]

            self.receiving_child_dict[window_name] = self.get_receiver_children(window)

            result = False
            for receiver in self.receiving_child_dict[window_name]:
                if receiver["name"] == receiver_name:
                    result = True
                    break

            return result

        def __add_connection(sender_window, sender, connection):
            """Adds connection"""

            new_item = QtImport.QTreeWidgetItem(self.connections_treewidget)

            window_name = sender_window["name"]
            new_item.setText(1, window_name)

            if sender != sender_window:
                new_item.setText(2, sender["name"])

            new_item.setText(4, connection["receiverWindow"])

            try:
                receiver_window = self.configuration.windows[
                    connection["receiverWindow"]
                ]
            except KeyError:
                receiver_window = {}
                result = False
            else:
                result = True

            if len(connection["receiver"]):
                # *-object
                new_item.setText(5, connection["receiver"])

                result = result and __receiver_in_window(
                    connection["receiver"], receiver_window
                )

            if result:
                new_item.setIcon(0, Icons.load_icon("button_ok_small"))
            else:
                new_item.setIcon(0, Icons.load_icon("button_cancel_small"))

            new_item.setText(3, connection["signal"])
            new_item.setText(6, connection["slot"])

        for window in self.configuration.windows.values():

            for connection in window["connections"]:
                __add_connection(window, window, connection)

            children = self.get_connecting_children(window)
            self.connecting_child_dict[window["name"]] = children

            for child in children:
                for connection in child["connections"]:
                    __add_connection(window, child, connection)

    def emitter_window_changed(self, item):
        """Event when emitter window changes"""

        self.emitter_objects_listwidget.clear()
        self.emitter_signals_listwidget.clear()

        if item is None:
            return

        window_name = str(item.text())

        try:
            window = self.configuration.windows[window_name]
        except KeyError:
            pass
        else:
            try:
                signalling_children = self.signalling_child_dict[window_name]
            except KeyError:
                signalling_children = self.get_signalling_children(window)
                self.signalling_child_dict[window_name] = signalling_children

            for child in signalling_children:
                self.emitter_objects_listwidget.addItem(child["name"])
            self.emitter_objects_listwidget.setFont(
                self.emitter_objects_listwidget.font()
            )

            for signal_name in window["signals"]:
                self.emitter_signals_listwidget.addItem(signal_name)
            self.emitter_signals_listwidget.setFont(
                self.emitter_signals_listwidget.font()
            )

    def emitter_object_changed(self, item):
        """Event when emitter object changed"""

        if item is None:
            self.emitter_window_changed(self.emitter_windows_listwidget.currentItem())
            return

        object_name = str(item.text())

        try:
            object_item = self.configuration.bricks[object_name]
        except KeyError:
            signals = self.configuration.items[object_name]["signals"]
        else:
            signals = object_item["brick"].get_signals()

        self.emitter_signals_listwidget.clear()
        for signal_name in signals:
            self.emitter_signals_listwidget.addItem(signal_name)
        self.emitter_signals_listwidget.setFont(self.emitter_signals_listwidget.font())

    def receiver_window_changed(self, item):
        """Event when receiver window changed"""

        self.receiver_objects_listwidget.clear()
        self.receiver_slots_listwidget.clear()

        if item is None:
            return

        window_name = str(item.text())

        try:
            window = self.configuration.windows[window_name]
        except KeyError:
            pass
        else:
            try:
                receiver_children = self.receiving_child_dict[window_name]
            except KeyError:
                receiver_children = self.get_receiver_children(window)
                self.receiving_child_dict[window_name] = receiver_children

            for child in self.receiving_child_dict[window_name]:
                self.receiver_objects_listwidget.addItem(child["name"])
            self.receiver_objects_listwidget.setFont(
                self.receiver_objects_listwidget.font()
            )

            if hasattr(window, "slots"):
                for slot_name in window["slots"]:
                    self.receiver_slots_listwidget.addItem(slot_name)
            else:
                self.receiver_slots_listwidget.addItem("show")
                self.receiver_slots_listwidget.addItem("hide")
            self.receiver_slots_listwidget.setFont(
                self.receiver_slots_listwidget.font()
            )

    def receiver_object_changed(self, item):
        """Event when receiver object changed"""

        if item is None:
            self.receiver_window_changed(self.receiver_windows_listwidget.currentItem())
            return

        object_name = str(item.text())

        try:
            object_item = self.configuration.bricks[object_name]
        except KeyError:
            slots = self.configuration.items[object_name]["slots"]
        else:
            slots = object_item["brick"].get_slots()

        self.receiver_slots_listwidget.clear()
        for slot_name in slots:
            self.receiver_slots_listwidget.addItem(slot_name)
        self.receiver_slots_listwidget.setFont(self.receiver_slots_listwidget.font())

    def add_connection_button_clicked(self):
        """Add connection"""

        sender_window_item = self.emitter_windows_listwidget.currentItem()
        if sender_window_item:
            sender_window_name = str(sender_window_item.text())
        else:
            QtImport.QMessageBox.warning(
                self, "Cannot add connection", "Missing sender window."
            )
            return

        sender_object_item = self.emitter_objects_listwidget.currentItem()
        if sender_object_item:
            sender_object_name = str(sender_object_item.text())
        else:
            sender_object_name = ""

        signal_item = self.emitter_signals_listwidget.currentItem()
        if signal_item:
            signal_name = str(signal_item.text())
        else:
            QtImport.QMessageBox.warning(
                self, "Cannot add connection", "Missing signal."
            )
            return

        receiver_window_item = self.receiver_windows_listwidget.currentItem()
        if receiver_window_item:
            receiver_window_name = str(receiver_window_item.text())
        else:
            QtImport.QMessageBox.warning(
                self, "Cannot add connection", "Missing receiver window."
            )
            return

        receiver_object_item = self.receiver_objects_listwidget.currentItem()
        if receiver_object_item:
            receiver_object_name = str(receiver_object_item.text())
        else:
            receiver_object_name = ""

        slot_item = self.receiver_slots_listwidget.currentItem()
        if slot_item:
            slot_name = str(slot_item.text())
        else:
            QtImport.QMessageBox.warning(self, "Cannot add connection", "Missing slot.")
            return

        self.add_pending_connection(
            {
                "senderWindow": sender_window_name,
                "senderObject": sender_object_name,
                "signal": signal_name,
                "receiverWindow": receiver_window_name,
                "receiverObject": receiver_object_name,
                "slot": slot_name,
            }
        )
        self.has_changed = True

    def add_pending_connection(self, connection_dict):
        """Adds pendinf connection"""

        parameter_list = (
            "",
            connection_dict["senderWindow"],
            connection_dict["senderObject"],
            connection_dict["signal"],
            connection_dict["receiverWindow"],
            connection_dict["receiverObject"],
            connection_dict["slot"],
        )

        new_item = QtImport.QTreeWidgetItem(self.connections_treewidget, parameter_list)
        new_item.setIcon(0, Icons.load_icon("button_ok_small"))
        self.connections_treewidget.addTopLevelItem(new_item)

    def connections_treewidget_selection_changed(self):
        """Event when an item is selected"""

        self.remove_connection_button.setEnabled(True)

    def remove_connection_button_clicked(self):
        """Remove connection"""

        self.connections_treewidget.takeTopLevelItem(
            self.connections_treewidget.currentIndex().row()
        )
        self.remove_connection_button.setEnabled(False)
        self.has_changed = True

    def ok_button_clicked(self):
        """Accept"""

        # erase previous connections
        for window in self.configuration.windows.values():
            window["connections"] = []

            try:
                children = self.connecting_child_dict[window["name"]]
            except KeyError:
                children = self.get_connecting_children(window)

            for child in children:
                child["connections"] = []

        connection_count = self.connections_treewidget.topLevelItemCount()
        if connection_count > 0:
            for connection_index in range(connection_count):
                connection = self.connections_treewidget.topLevelItem(connection_index)
                sender_window = str(connection.text(1))
                sender_object = str(connection.text(2))
                new_connection = {
                    "receiverWindow": str(connection.text(4)),
                    "receiver": str(connection.text(5)),
                    "signal": str(connection.text(3)),
                    "slot": str(connection.text(6)),
                }

                if len(sender_object) == 0:
                    # sender is a window
                    window = self.configuration.windows[sender_window]
                    window["connections"].append(new_connection)
                else:
                    connection_objects = self.signalling_child_dict[sender_window]
                    for connection_object in connection_objects:
                        if connection_object["name"] == sender_object:
                            break
                    connection_object["connections"].append(new_connection)
        self.done(True)

    def cancel_button_clicked(self):
        """Cancel"""

        self.has_changed = False
        self.done(False)
