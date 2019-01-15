from qt import *
from BlissFramework import Icons
from BlissFramework import Configuration

class MyListBox(QListBox):
    def __init__(self, *args):
        QListBox.__init__(self, *args)

        self.itemChanged = False

        QObject.connect(self, SIGNAL('clicked(QListBoxItem *)'), self.itemClicked)
        QObject.connect(self, SIGNAL('currentChanged(QListBoxItem *)'), self.currentItemChanged)


    def currentItemChanged(self, item):
        self.itemChanged = True
        self.emit(PYSIGNAL('itemSelected'), (item, ))
        

    def itemClicked(self, item):
        if not self.itemChanged:
            self.clearSelection()
            self.emit(PYSIGNAL('itemSelected'), (None, ))

        self.itemChanged = False
   
        
class ConnectionEditor(QDialog):   
    def __init__(self, configuration):
        QDialog.__init__(self, None)

        self.configuration = configuration
        self.signallingChildren = {}
        self.receivingChildren = {}
        self.connectingChildren = {}
                               
        self.setCaption('Connection Editor')

        topPanel = QHBox(self)
        bottomPanel = QHBox(self)

        emitterPanel = QWidget(topPanel)
        emitterListboxesPanel = QGrid(3, emitterPanel)
        emitterWindowsListboxPanel = QVBox(emitterListboxesPanel)
        QLabel('Windows', emitterWindowsListboxPanel)
        self.lstEmitterWindows = QListBox(emitterWindowsListboxPanel)
        emitterObjectsListboxPanel = QVBox(emitterListboxesPanel)
        QLabel('Objects', emitterObjectsListboxPanel)
        self.lstEmitterObjects = MyListBox(emitterObjectsListboxPanel)
        signalsListboxPanel = QVBox(emitterListboxesPanel)
        QLabel('Signals', signalsListboxPanel)
        self.lstSignals = QListBox(signalsListboxPanel)

        receiverPanel = QWidget(topPanel)
        receiverListboxesPanel = QGrid(3, receiverPanel)
        receiverWindowsListboxPanel = QVBox(receiverListboxesPanel)
        QLabel('Windows', receiverWindowsListboxPanel)
        self.lstReceiverWindows = QListBox(receiverWindowsListboxPanel)
        receiverObjectsListboxPanel = QVBox(receiverListboxesPanel)
        QLabel('Objects', receiverObjectsListboxPanel)
        self.lstReceiverObjects = MyListBox(receiverObjectsListboxPanel)
        slotsListboxPanel = QVBox(receiverListboxesPanel)
        QLabel('Slots', slotsListboxPanel)
        self.lstSlots = QListBox(slotsListboxPanel)

        connectionsPanel = QVBox(bottomPanel)
        QLabel('Established connections', connectionsPanel)
        self.lstConnections = QListView(connectionsPanel)
        self.cmdRemoveConnection = QPushButton('Remove', bottomPanel)

        self.cmdAddConnection = QPushButton('Add connection', self)
        self.cmdOK = QPushButton('OK', self)
        self.cmdCancel = QPushButton('Cancel', self)

        self.lstEmitterWindows.setSelectionMode(QListBox.Single)
        emitterListboxesPanel.setSpacing(5)
        receiverListboxesPanel.setSpacing(5)
        topPanel.setSpacing(20)
        bottomPanel.setSpacing(5)
        bottomPanel.setMargin(5)
        self.lstConnections.addColumn(' ')
        self.lstConnections.addColumn('Emitter window')
        self.lstConnections.addColumn('Emitter object')
        self.lstConnections.addColumn('Signal')
        self.lstConnections.addColumn('Receiver window')
        self.lstConnections.addColumn('Receiver object')
        self.lstConnections.addColumn('Slot')
        self.cmdRemoveConnection.setEnabled(False)
    
        QVBoxLayout(emitterPanel, 5, 5)
        emitterPanel.layout().addWidget(QLabel('<h3>Emitters</h3>', emitterPanel), 0, Qt.AlignHCenter)
        emitterPanel.layout().addWidget(emitterListboxesPanel)

        QVBoxLayout(receiverPanel, 5, 5)
        receiverPanel.layout().addWidget(QLabel('<h3>Receivers</h3>', receiverPanel), 0, Qt.AlignHCenter) 
        receiverPanel.layout().addWidget(receiverListboxesPanel)

        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(topPanel, 1)
        self.layout().addWidget(self.cmdAddConnection, 0, Qt.AlignCenter)
        self.layout().addWidget(bottomPanel, 0)
        self.layout().addWidget(self.cmdOK, 0, Qt.AlignRight)
        self.layout().addWidget(self.cmdCancel, 0, Qt.AlignRight)

        QObject.connect(self.lstEmitterWindows, SIGNAL('currentChanged(QListBoxItem *)'), self.emitterWindowChanged)
        QObject.connect(self.lstEmitterObjects, PYSIGNAL('itemSelected'), self.emitterObjectChanged)
        QObject.connect(self.lstReceiverWindows, SIGNAL('currentChanged(QListBoxItem *)'), self.receiverWindowChanged)
        QObject.connect(self.lstReceiverObjects, PYSIGNAL('itemSelected'), self.receiverObjectChanged)
        QObject.connect(self.cmdRemoveConnection, SIGNAL('clicked()'), self.cmdRemoveConnectionClicked)
        QObject.connect(self.cmdAddConnection, SIGNAL('clicked()'), self.cmdAddConnectionClicked)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.cmdOKClicked)
        QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.cmdCancelClicked)
        QObject.connect(self.lstConnections, SIGNAL('selectionChanged(QListViewItem *)'), self.lstConnectionsSelectionChanged)

        #
        # add each window in the corresponding lists
        # 
        for senderWindow in self.configuration.windows_list:
            window_name = senderWindow["name"]
            self.lstEmitterWindows.insertItem(window_name)
            self.lstReceiverWindows.insertItem(window_name)

        # force geometry updating on listbox
        self.lstEmitterWindows.setFont(self.lstEmitterWindows.font())
        self.lstReceiverWindows.setFont(self.lstReceiverWindows.font())

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
            
            self.signallingChildren[windowName] = self.getSignallingChildren(window)

            ok = False
            for sender in self.signallingChildren[windowName]:
                if sender["name"] == senderName:
                    ok = True
                    break      

            return ok

        def receiverInWindow(receiverName, window):
            windowName = window["name"]
            
            self.receivingChildren[windowName] = self.getReceiverChildren(window)

            ok = False
            for receiver in self.receivingChildren[windowName]:
                if receiver["name"] == receiverName:
                    ok = True
                    break      

            return ok

        def addConnection(senderWindow, sender, connection):
            newItem = QListViewItem(self.lstConnections)

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
                newItem.setPixmap(0, Icons.load('button_ok_small'))
            else:
                newItem.setPixmap(0, Icons.load('button_cancel_small'))

            newItem.setText(3, connection['signal'])
            newItem.setText(6, connection['slot'])
            self.lstConnections.insertItem(newItem)

        for window in self.configuration.windows.itervalues():
            for connection in window["connections"]:
                addConnection(window, window, connection)

            children = self.getConnectingChildren(window)
            self.connectingChildren[window["name"]] = children

            for child in children:
                for connection in child["connections"]:
                    addConnection(window, child, connection)
            
       
    def emitterWindowChanged(self, item):
        self.lstEmitterObjects.clear()
        self.lstSignals.clear()

        if item is None:
            return
        
        windowName = str(item.text())

        try:
            window = self.configuration.windows[windowName]
        except KeyError:
            pass
        else:
            try:
                signallingChildren = self.signallingChildren[windowName]
            except KeyError:
                signallingChildren = self.getSignallingChildren(window)
                self.signallingChildren[windowName] = signallingChildren
            
            for child in signallingChildren:
                self.lstEmitterObjects.insertItem(child["name"])
            self.lstEmitterObjects.setFont(self.lstEmitterObjects.font())
            
            for signalName in window["signals"]:
                self.lstSignals.insertItem(signalName)
            self.lstSignals.setFont(self.lstSignals.font())
 

    def emitterObjectChanged(self, item):
        if item is None:
            self.emitterWindowChanged(self.lstEmitterWindows.selectedItem())
            return
        
        objectName = str(item.text())

        try:
            object = self.configuration.bricks[objectName]
        except KeyError:
            signals = self.configuration.items[objectName]["signals"]
        else:
            signals = object["brick"].getSignals()
        
        self.lstSignals.clear()
        for signalName in signals:
            self.lstSignals.insertItem(signalName)
        self.lstSignals.setFont(self.lstSignals.font())
        

    def receiverWindowChanged(self, item):
        self.lstReceiverObjects.clear()
        self.lstSlots.clear()

        if item is None:
            return
        
        windowName = str(item.text())

        try:
            window = self.configuration.windows[windowName]
        except KeyError:
            pass
        else:
            try:
                receiverChildren = self.receivingChildren[windowName]
            except KeyError:
                receiverChildren = self.getReceiverChildren(window)
                self.receivingChildren[windowName] = receiverChildren
            
            for child in self.receivingChildren[windowName]:
                self.lstReceiverObjects.insertItem(child["name"])
            self.lstReceiverObjects.setFont(self.lstReceiverObjects.font())
            
            for slotName in window["slots"]:
                self.lstSlots.insertItem(slotName)
            self.lstSlots.setFont(self.lstSlots.font())
 

    def receiverObjectChanged(self, item):
        if item is None:
            self.receiverWindowChanged(self.lstReceiverWindows.selectedItem())
            return
        
        objectName = str(item.text())

        try:
            object = self.configuration.bricks[objectName]
        except KeyError:
            slots = self.configuration.items[objectName]["slots"]
        else:
            slots = object["brick"].getSlots()
        
        self.lstSlots.clear()
        for slotName in slots:
            self.lstSlots.insertItem(slotName)
        self.lstSlots.setFont(self.lstSlots.font())
        

    def cmdAddConnectionClicked(self):
        senderWindowItem = self.lstEmitterWindows.selectedItem()
        if senderWindowItem:
            senderWindowName = str(senderWindowItem.text())
        else:
            QMessageBox.warning(self, 'Cannot add connection', 'Missing sender window.')
            return

        senderObjectItem = self.lstEmitterObjects.selectedItem()
        if senderObjectItem:
            senderObjectName = str(senderObjectItem.text())
        else:
            senderObjectName = ""
        
        signalItem = self.lstSignals.selectedItem()
        if signalItem:
            signalName = str(signalItem.text())
        else:
            QMessageBox.warning(self, 'Cannot add connection', 'Missing signal.')
            return

        receiverWindowItem = self.lstReceiverWindows.selectedItem()
        if receiverWindowItem:
            receiverWindowName = str(receiverWindowItem.text())
        else:
            QMessageBox.warning(self, 'Cannot add connection', 'Missing receiver window.')
            return
        
        receiverObjectItem=self.lstReceiverObjects.selectedItem()
        if receiverObjectItem:
            receiverObjectName=str(receiverObjectItem.text())
        else:
            receiverObjectName=""
            
        slotItem = self.lstSlots.selectedItem()
        if slotItem:
            slotName = str(slotItem.text())
        else:
            QMessageBox.warning(self, 'Cannot add connection', 'Missing slot.')
            return
        
        self.addPendingConnection({'senderWindow': senderWindowName,
                                   'senderObject': senderObjectName,
                                   'signal': signalName,
                                   'receiverWindow': receiverWindowName,
                                   'receiverObject': receiverObjectName,
                                   'slot': slotName})
        

    def addPendingConnection(self, connectionDict):
        newItem = QListViewItem(self.lstConnections,
                                '',
                                connectionDict['senderWindow'],
                                connectionDict['senderObject'],
                                connectionDict['signal'],
                                connectionDict['receiverWindow'],
                                connectionDict['receiverObject'],
                                connectionDict['slot'])
        newItem.setPixmap(0, Icons.load('button_ok_small'))
        
        self.lstConnections.insertItem(newItem)

    
    def lstConnectionsSelectionChanged(self, item):
        self.cmdRemoveConnection.setEnabled(True)

        
    def cmdRemoveConnectionClicked(self):
        self.lstConnections.takeItem(self.lstConnections.currentItem())
        self.cmdRemoveConnection.setEnabled(False)
        

    def cmdOKClicked(self):
        #
        # erase previous connections
        #
        for window in self.configuration.windows.itervalues():
            window["connections"] = []

            try:
                children = self.connectingChildren[window["name"]]
            except KeyError:
                children = self.getConnectingChildren(window)

            for child in children:
                child["connections"] = []

        #
        # rewrite connections
        #
        connection = self.lstConnections.firstChild()

        while connection is not None:    
            senderWindow = str(connection.text(1))
            senderObject = str(connection.text(2))
            signal = str(connection.text(3))
            receiverWindow = str(connection.text(4))
            receiverObject = str(connection.text(5))
            slot = str(connection.text(6))

            newConnection = { 'receiverWindow': receiverWindow,
                              'receiver': receiverObject,
                              'signal': signal,
                              'slot': slot }

            #
            # create connection
            #
            if len(senderObject) == 0:
                #
                # sender is a window
                #
                window = self.configuration.windows[senderWindow]

                window["connections"].append(newConnection)
            else:
                #
                # find sender object
                #
                objects = self.signallingChildren[senderWindow]

                for object in objects:
                    if object["name"] == senderObject:
                        break

                object["connections"].append(newConnection)

            connection = connection.nextSibling()              

        #self.configuration.dump()
        
        self.done(True)


    def cmdCancelClicked(self):
        self.done(False)

















