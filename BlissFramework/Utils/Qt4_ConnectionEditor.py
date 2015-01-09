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

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework import Qt4_Configuration


class Qt4_ConnectionEditor(QtGui.QDialog):   
    """
    Descript. :
    """ 
    def __init__(self, configuration):
        """
        Descript. :
        """   
        QtGui.QDialog.__init__(self, None)

        # Internal values -----------------------------------------------------
        self.configuration = configuration
        self.signalling_child_dict = {}
        self.receiving_child_dict = {}
        self.connecting_child_dict = {}

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        top_panel = QtGui.QWidget(self)
        bottom_panel = QtGui.QWidget(self)

        emitter_panel = QtGui.QWidget(top_panel)
        self.emitter_windows_listwidget = QtGui.QListWidget(emitter_panel)
        self.emitter_objects_listwidget = QtGui.QListWidget(emitter_panel)
        self.emitter_signals_listwidget = QtGui.QListWidget(emitter_panel)

        receiver_panel = QtGui.QWidget(top_panel)
        self.receiver_windows_listwidget = QtGui.QListWidget(emitter_panel)
        self.receiver_objects_listwidget = QtGui.QListWidget(emitter_panel)
        self.receiver_slots_listwidget = QtGui.QListWidget(emitter_panel)

        self.add_connection_button = QtGui.QPushButton('Add connection', self)

        self.connections_treewidget = QtGui.QTreeWidget(self) 
        self.remove_connection_button = QtGui.QPushButton('Remove connection', self)

        button_panel = QtGui.QWidget(self)
        self.ok_button = QtGui.QPushButton('OK', button_panel)
        self.cancel_button = QtGui.QPushButton('Cancel', button_panel)

        # Layout --------------------------------------------------------------

        emitter_panel_layout = QtGui.QGridLayout(self)
        emitter_panel_layout.addWidget(QtGui.QLabel('<h3>Emitters</h3>', self), 0, 1, 
                                       QtCore.Qt.AlignHCenter)
        emitter_panel_layout.addWidget(QtGui.QLabel('Windows', self), 1, 0)
        emitter_panel_layout.addWidget(QtGui.QLabel('Objects', self), 1, 1)
        emitter_panel_layout.addWidget(QtGui.QLabel('Signals', self), 1, 2)
        emitter_panel_layout.addWidget(self.emitter_windows_listwidget, 2, 0)
        emitter_panel_layout.addWidget(self.emitter_objects_listwidget, 2, 1)
        emitter_panel_layout.addWidget(self.emitter_signals_listwidget, 2, 2) 
        emitter_panel.setLayout(emitter_panel_layout)

        receiver_panel_layout = QtGui.QGridLayout(self)
        receiver_panel_layout.addWidget(QtGui.QLabel('<h3>Receivers</h3>', self), 0, 1, 
                                       QtCore.Qt.AlignHCenter)
        receiver_panel_layout.addWidget(QtGui.QLabel('Windows', self), 1, 0)
        receiver_panel_layout.addWidget(QtGui.QLabel('Objects', self), 1, 1)
        receiver_panel_layout.addWidget(QtGui.QLabel('Slots', self), 1, 2)
        receiver_panel_layout.addWidget(self.receiver_windows_listwidget, 2, 0)
        receiver_panel_layout.addWidget(self.receiver_objects_listwidget, 2, 1)
        receiver_panel_layout.addWidget(self.receiver_slots_listwidget, 2, 2)
        receiver_panel.setLayout(receiver_panel_layout) 

        top_panel_layout = QtGui.QHBoxLayout(self)
        top_panel_layout.addWidget(emitter_panel)
        top_panel_layout.addWidget(receiver_panel) 
        top_panel_layout.setSpacing(0)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)
        top_panel.setLayout(top_panel_layout) 

        bottom_panel_layout = QtGui.QVBoxLayout(self)
        bottom_panel_layout.addWidget(QtGui.QLabel('<h3>Established connections</h3>', self), 
                                      QtCore.Qt.AlignHCenter)
        bottom_panel_layout.addWidget(self.connections_treewidget)
        bottom_panel_layout.setSpacing(0)
        bottom_panel_layout.setContentsMargins(0, 0, 0, 0)
        bottom_panel.setLayout(bottom_panel_layout)

        button_panel_layout = QtGui.QHBoxLayout(self)
        button_panel_layout.addStretch(0)
        button_panel_layout.addWidget(self.ok_button, QtCore.Qt.AlignRight)
        button_panel_layout.addWidget(self.cancel_button, QtCore.Qt.AlignRight)
        button_panel.setLayout(button_panel_layout)

        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.add_connection_button, QtCore.Qt.AlignHCenter)
        main_layout.addWidget(bottom_panel)
        main_layout.addWidget(self.remove_connection_button, QtCore.Qt.AlignHCenter) 
        main_layout.addWidget(button_panel)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(2, 2, 2, 2) 
        main_layout.addStretch(0)
        self.setLayout(main_layout)

        # SizePolicies --------------------------------------------------------
        self.add_connection_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.remove_connection_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ok_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.cancel_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed) 

        # Qt signal/slot connections ------------------------------------------
        #self.connect(self.emitter_windows_listwidget, QtCore.SIGNAL('itemChanged (QListWidgetItem * item )'), 
        #             self.emitter_window_changed)

        self.emitter_windows_listwidget.currentItemChanged.connect(self.emitter_window_changed)
        self.emitter_objects_listwidget.currentItemChanged.connect(self.emitter_object_changed) 
        self.receiver_windows_listwidget.currentItemChanged.connect(self.receiver_window_changed)
        self.receiver_objects_listwidget.currentItemChanged.connect(self.receiver_object_changed)
        self.connect(self.add_connection_button, QtCore.SIGNAL('clicked()'), self.add_connection_button_clicked)
        self.connect(self.remove_connection_button, QtCore.SIGNAL('clicked()'), self.remove_connection_button_clicked)
        self.connect(self.ok_button, QtCore.SIGNAL('clicked()'), self.ok_button_clicked)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'), self.cancel_button_clicked)
        self.connect(self.connections_treewidget, QtCore.SIGNAL('itemSelectionChanged()'), 
                    self.connections_treewidget_selection_changed)

        # Other ---------------------------------------------------------------
        self.connections_treewidget.setColumnCount(7)
        self.connections_treewidget.setHeaderLabels(['', 'Emitter window', 'Emitter object', 
                                                     'Signal', 'Receiver window', 
                                                     'Receiver object', 'Slot'])
        self.setWindowTitle('Connection Editor')
        for senderWindow in self.configuration.windows_list:
            window_name = senderWindow["name"]
            self.emitter_windows_listwidget.addItem(window_name)
            self.receiver_windows_listwidget.addItem(window_name)
        self.emitter_windows_listwidget.setFont(self.emitter_windows_listwidget.font())
        self.receiver_windows_listwidget.setFont(self.receiver_windows_listwidget.font())
        self.showConnections()

    def getSignallingChildren(self, parent):
        children = []
        
        for child in parent["children"]:
            try:
                n_signals = len(child["signals"])
            except KeyError:
                # item is a brick
                n_signals = len(child["brick"].getSignals())
                
            if n_signals > 0:
                children.append(child)
                    
            children += self.getSignallingChildren(child)
                    
        return children

            
    def getReceiverChildren(self, parent):
        children = []
                
        for child in parent["children"]:
            try:
                n_slots = len(child["slots"])
            except KeyError:
                # item is a brick
                n_slots = len(child["brick"].getSlots())

            if n_slots > 0:
                children.append(child)

            children += self.getReceiverChildren(child)

        return children


    def getConnectingChildren(self, parent):
        children = []
                
        for child in parent["children"]:
            if len(child["connections"]):
                children.append(child)
        
            children += self.getConnectingChildren(child)

        return children
        
    
    def showConnections(self):
        def senderInWindow(senderName, window):
            windowName = window["name"]
            
            self.signalling_child_dict[windowName] = self.getSignallingChildren(window)

            ok = False
            for sender in self.signalling_child_dict[windowName]:
                if sender["name"] == senderName:
                    ok = True
                    break      

            return ok

        def receiverInWindow(receiverName, window):
            windowName = window["name"]
            
            self.receiving_child_dict[windowName] = self.getReceiverChildren(window)

            ok = False
            for receiver in self.receiving_child_dict[windowName]:
                if receiver["name"] == receiverName:
                    ok = True
                    break      

            return ok

        def addConnection(senderWindow, sender, connection):
            newItem = QtGui.QTreeWidgetItem(self.connections_treewidget)

            windowName = senderWindow["name"]
            
            newItem.setText(1, windowName)

            if sender != senderWindow:
                # object-*
                newItem.setText(2, sender["name"])
            
            newItem.setText(4, connection["receiverWindow"])
                
            try:
                receiverWindow = self.configuration.windows[connection["receiverWindow"]]
            except KeyError:
                receiverWindow = {}
                ok = False
            else:
                ok = True

            if len(connection["receiver"]):
                # *-object
                newItem.setText(5, connection["receiver"])

                ok = ok and receiverInWindow(connection["receiver"], receiverWindow)

            if ok:
                newItem.setIcon(0, QtGui.QIcon(Qt4_Icons.load('button_ok_small')))
            else:
                newItem.setIcon(0, QtGui.QIcon(Qt4_Icons.load('button_cancel_small')))

            newItem.setText(3, connection['signal'])
            newItem.setText(6, connection['slot'])
            #self.connections_treewidget.addItem(newItem)

        for window in self.configuration.windows.itervalues():
            for connection in window["connections"]:
                addConnection(window, window, connection)

            children = self.getConnectingChildren(window)
            self.connecting_child_dict[window["name"]] = children

            for child in children:
                for connection in child["connections"]:
                    addConnection(window, child, connection)
            
       
    def emitter_window_changed(self, item):
        self.emitter_objects_listwidget.clear()
        self.emitter_signals_listwidget.clear()

        if item is None:
            return
        
        windowName = str(item.text())

        try:
            window = self.configuration.windows[windowName]
        except KeyError:
            pass
        else:
            try:
                signallingChildren = self.signalling_child_dict[windowName]
            except KeyError:
                signallingChildren = self.getSignallingChildren(window)
                self.signalling_child_dict[windowName] = signallingChildren
            
            for child in signallingChildren:
                self.emitter_objects_listwidget.addItem(child["name"])
            self.emitter_objects_listwidget.setFont(self.emitter_objects_listwidget.font())
            
            for signalName in window["signals"]:
                self.emitter_signals_listwidget.addItem(signalName)
            self.emitter_signals_listwidget.setFont(self.emitter_signals_listwidget.font())
 

    def emitter_object_changed(self, item):
        if item is None:
            self.emitter_window_changed(self.emitter_windows_listwidget.currentItem())
            return
        
        objectName = str(item.text())

        try:
            object = self.configuration.bricks[objectName]
        except KeyError:
            signals = self.configuration.items[objectName]["signals"]
        else:
            signals = object["brick"].getSignals()
        
        self.emitter_signals_listwidget.clear()
        for signalName in signals:
            self.emitter_signals_listwidget.addItem(signalName)
        self.emitter_signals_listwidget.setFont(self.emitter_signals_listwidget.font())
        

    def receiver_window_changed(self, item):
        self.receiver_objects_listwidget.clear()
        self.receiver_slots_listwidget.clear()

        if item is None:
            return
        
        windowName = str(item.text())

        try:
            window = self.configuration.windows[windowName]
        except KeyError:
            pass
        else:
            try:
                receiverChildren = self.receiving_child_dict[windowName]
            except KeyError:
                receiverChildren = self.getReceiverChildren(window)
                self.receiving_child_dict[windowName] = receiverChildren
            
            for child in self.receiving_child_dict[windowName]:
                self.receiver_objects_listwidget.addItem(child["name"])
            self.receiver_objects_listwidget.setFont(self.receiver_objects_listwidget.font())
            
            for slotName in window["slots"]:
                self.receiver_slots_listwidget.addItem(slotName)
            self.receiver_slots_listwidget.setFont(self.receiver_slots_listwidget.font())
 

    def receiver_object_changed(self, item):
        if item is None:
            self.receiver_window_changed(self.receiver_windows_listwidget.currentItem())
            return
        
        objectName = str(item.text())

        try:
            object = self.configuration.bricks[objectName]
        except KeyError:
            slots = self.configuration.items[objectName]["slots"]
        else:
            slots = object["brick"].getSlots()
        
        self.receiver_slots_listwidget.clear()
        for slotName in slots:
            self.receiver_slots_listwidget.addItem(slotName)
        self.receiver_slots_listwidget.setFont(self.receiver_slots_listwidget.font())
        

    def add_connection_button_clicked(self):
        senderWindowItem = self.emitter_windows_listwidget.currentItem()
        if senderWindowItem:
            senderWindowName = str(senderWindowItem.text())
        else:
            QtGui.QMessageBox.warning(self, 'Cannot add connection', 'Missing sender window.')
            return

        senderObjectItem = self.emitter_objects_listwidget.currentItem()
        if senderObjectItem:
            senderObjectName = str(senderObjectItem.text())
        else:
            senderObjectName = ""
        
        signalItem = self.emitter_signals_listwidget.currentItem()
        if signalItem:
            signalName = str(signalItem.text())
        else:
            QtGui.QMessageBox.warning(self, 'Cannot add connection', 'Missing signal.')
            return

        receiverWindowItem = self.receiver_windows_listwidget.currentItem()
        if receiverWindowItem:
            receiverWindowName = str(receiverWindowItem.text())
        else:
            QtGui.QMessageBox.warning(self, 'Cannot add connection', 'Missing receiver window.')
            return
        
        receiverObjectItem=self.receiver_objects_listwidget.currentItem()
        if receiverObjectItem:
            receiverObjectName=str(receiverObjectItem.text())
        else:
            receiverObjectName=""
            
        slotItem = self.receiver_slots_listwidget.currentItem()
        if slotItem:
            slotName = str(slotItem.text())
        else:
            QtGui.QMessageBox.warning(self, 'Cannot add connection', 'Missing slot.')
            return
        
        self.addPendingConnection({'senderWindow': senderWindowName,
                                   'senderObject': senderObjectName,
                                   'signal': signalName,
                                   'receiverWindow': receiverWindowName,
                                   'receiverObject': receiverObjectName,
                                   'slot': slotName})
        

    def addPendingConnection(self, connectionDict):
        newItem = QtGui.QTreeWidgetItem(self.connections_treewidget, QtCore.QStringList([
                                '',
                                connectionDict['senderWindow'],
                                connectionDict['senderObject'],
                                connectionDict['signal'],
                                connectionDict['receiverWindow'],
                                connectionDict['receiverObject'],
                                connectionDict['slot']]))
        newItem.setIcon(0, QtGui.QIcon(Qt4_Icons.load('button_ok_small')))
        self.connections_treewidget.addTopLevelItem(newItem)
    
    def connections_treewidget_selection_changed(self):
        self.remove_connection_button.setEnabled(True)

        
    def remove_connection_button_clicked(self):
      	#item = self.connections_treewidget.currentItem();
        self.connections_treewidget.takeTopLevelItem(self.connections_treewidget.currentIndex().row())
        self.remove_connection_button.setEnabled(False)
        

    def ok_button_clicked(self):
        #
        # erase previous connections
        #
        for window in self.configuration.windows.itervalues():
            window["connections"] = []

            try:
                children = self.connecting_child_dict[window["name"]]
            except KeyError:
                children = self.getConnectingChildren(window)

            for child in children:
                child["connections"] = []

        connection_count = self.connections_treewidget.topLevelItemCount()
        if connection_count > 0:
            for connection_index in range(connection_count):
                connection = self.connections_treewidget.topLevelItem(connection_index)
                senderWindow = str(connection.text(1))
                senderObject = str(connection.text(2))
                newConnection = {'receiverWindow': str(connection.text(4)),
                                 'receiver': str(connection.text(5)),
                                 'signal': str(connection.text(3)),
                                 'slot': str(connection.text(6))}

                if len(senderObject) == 0:
                     #sender is a window
                     window = self.configuration.windows[senderWindow]
                     window["connections"].append(newConnection)
                else:
                     con_objects = self.signalling_child_dict[senderWindow]
                     for con_object in con_objects:
                         if con_object["name"] == senderObject:
                             break
                     con_object["connections"].append(newConnection)
        self.done(True)

    def cancel_button_clicked(self):
        self.done(False)

















