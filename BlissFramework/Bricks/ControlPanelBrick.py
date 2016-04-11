"""ControlPanelBrick

A brick to be able to execute macros/functions
and display/update variables values in remote
Spec versions.

It has 2 views : in design mode, you can create
a 'panel' containings the items took from a
Hardware Object, whereas in execution mode you
use the controls previously selected.
"""

__author__ = "Matias Guijarro"
__version__ = 0.0
__category__ = "General"


from BlissFramework.BaseComponents import BlissWidget
from HardwareRepository.CommandContainer import CommandContainer
from qt import *
from qttable import QTable
import Icons
import types
import weakref


class HorizontalSpacer(QWidget):
    """Helper class to have a horizontal spacer widget"""
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args)
        
        h_size = kwargs.get("size", None)
    
        if h_size is not None:
            self.setFixedWidth(h_size)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class ToolButton(QToolButton):
    def __init__(self, parent, icon, text=None, callback=None, tooltip=None):
        QToolButton.__init__(self, parent)

        self.setIconSet(QIconSet(Icons.load(icon)))

        if type(text) != types.StringType:
            tooltip = callback
            callback = text
        else:
            self.setTextLabel(text)
            self.setTextPosition(QToolButton.BesideIcon)
            self.setUsesTextLabel(True)

        if callback is not None:
            QObject.connect(self, SIGNAL("clicked()"), callback)

        if tooltip is not None:
            QToolTip.add(self, tooltip)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class ControlPanelWidget(QFrame):
    selected = None
    
    def __init__(self, parent, config = None, running=False):
        QFrame.__init__(self, parent)

        self._running = running
        self._config = config
        self._frame_color = self.colorGroup().foreground()
        self._rowstretch = 1
        self._colstretch = 1
        
        if not running:
            self.setFrameStyle(QFrame.Plain | QFrame.Box)
            self.setLineWidth(1)
            self.setMidLineWidth(1)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        

    def __repr__(self):
        return repr(self._config)


    def _widgetClicked(self):
        self._select()
        
        self.emit(PYSIGNAL("widgetClicked"), (self, ))
        

    def mouseReleaseEvent(self, mouseEvent):
        if not self._running:
            if mouseEvent.button() == Qt.LeftButton:
                self._widgetClicked()
                

    def _select(self):
        if ControlPanelWidget.selected is not None:
            w = ControlPanelWidget.selected()
            if w is not None:
                w._unselect()
                if w == self:
                    return
        
        ControlPanelWidget.selected = weakref.ref(self)
        self.setPaletteBackgroundColor(self.colorGroup().dark())
        self.update()
        

    def _unselect(self):
        ControlPanelWidget.selected = None
        self.setPaletteBackgroundColor(self.parent().colorGroup().background())
        self.update()
    

    def enterEvent(self, mouseEvent):
        if not self._running:
            self.setPaletteForegroundColor(self.colorGroup().brightText())
            self.update()
        

    def leaveEvent(self, mouseEvent):
        if not self._running:
            self.setPaletteForegroundColor(self._frame_color)
            self.update()


class ControlPanelCommandWidget(ControlPanelWidget):
    def __init__(self, *args, **kwargs):
        ControlPanelWidget.__init__(self, *args, **kwargs)

    def _commandLaunched(self, *args):
        pass


    def _commandReplyArrived(self, *args):
        pass


    def _connected(self):
        self.setEnabled(True)


    def _disconnected(self):
        self.setEnabled(False)
        
        

class CommandWidgetSettingsDialog(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)

        self.setCaption("%s - command properties" % str(self.name()))
        grid = QGrid(2, self)
        grid.setSpacing(5)
        grid.setMargin(5)
        QLabel("label", grid)
        self.txtLabel = QLineEdit(grid)
        
        ok_cancel = QHBox(self)
        self.cmdOk = QPushButton("ok", ok_cancel)
        HorizontalSpacer(ok_cancel)
        self.cmdCancel = QPushButton("cancel", ok_cancel)
        QObject.connect(self.cmdOk, SIGNAL("clicked()"), self.accept)
        QObject.connect(self.cmdCancel, SIGNAL("clicked()"), self.reject)
        
        QVBoxLayout(self, 5, 10)
        self.layout().addWidget(grid)
        self.layout().addWidget(ok_cancel)


    def commandWidget(self, parent, running=False, config=None):
        if config is None:
            config = self.commandConfig()
        else:
            self.setCommandConfig(config)

        w = ControlPanelCommandWidget(parent, config, running=running)

        w.command = QPushButton(config["label"], w)
        QHBoxLayout(w)
        w.layout().addWidget(w.command)

        QObject.connect(w.command, SIGNAL("clicked()"), w._widgetClicked)
        
        return w


    def setCommandConfig(self, config):
        self.txtLabel.setText(config["label"])
        

    def commandConfig(self):
        config = { "type": "command",
                   "name": str(self.name()),
                   "label": str(self.txtLabel.text()) }

        return config
    

class ChannelWidgetSettingsDialog(QDialog):
    value_display_widgets = { "LCD": QLCDNumber,
                            "label": QLabel,
                            "combo": QComboBox,
                            "editable": QLineEdit }
    alignment_flags = { 'vleft': Qt.AlignLeft | Qt.AlignBottom,
                        'vright': Qt.AlignRight | Qt.AlignBottom,
                        'vcentre': Qt.AlignHCenter | Qt.AlignBottom,
                        'hleft': Qt.AlignLeft | Qt.AlignVCenter,
                        'hright': Qt.AlignRight | Qt.AlignVCenter,
                        'hcentre': Qt.AlignCenter }
    
    def __init__(self, *args):
        QDialog.__init__(self, *args)

        self.setCaption("%s - channel properties" % str(self.name()))
        self.innerbox = QSplitter(Qt.Horizontal, self)
        grid = QGrid(2, self.innerbox)
        grid.setSpacing(5)
        grid.setMargin(5)
        QLabel("Label", grid)
        self.txtLabel = QLineEdit(grid)
        QLabel("Label position", grid)
        labelpos_group = QVButtonGroup(grid)
        self.optLabelAbove = QRadioButton("above", labelpos_group)
        self.optLabelLeft = QRadioButton("on the left", labelpos_group)
        self.optLabelLeft.setChecked(True)
        QLabel("Label alignment", grid)
        labelalign_group = QHButtonGroup(grid)
        self.optLabelAlignLeft = QRadioButton("left", labelalign_group)
        self.optLabelAlignCenter = QRadioButton("centre", labelalign_group)
        self.optLabelAlignRight = QRadioButton("right", labelalign_group)
        self.optLabelAlignLeft.setChecked(True)
        QLabel("Value display format", grid)
        self.txtFormat = QLineEdit(grid)
        QLabel("Value display style", grid)
        self.lstChannelStyles = QComboBox(grid)
        self.lstChannelStyles.insertStrList(["LCD", "label", "combo", "editable"])
        QObject.connect(self.lstChannelStyles, SIGNAL('activated(int)'), self.lstChannelStylesChanged)
        self.combopanel = QHBox(self.innerbox)
        self.tblComboChoices = QTable(self.combopanel)
        self.tblComboChoices.setNumCols(2)
        self.tblComboChoices.setNumRows(10)
        for i in range(10):
            self.tblComboChoices.verticalHeader().setLabel(i, "%2.0f" % (i+1))
            self.tblComboChoices.setText(i, 0, "%2.0f" % (i+1))
        self.tblComboChoices.horizontalHeader().setLabel(0, "value")
        self.tblComboChoices.horizontalHeader().setLabel(1, "label")
        self.combopanel.hide()

        ok_cancel = QHBox(self)
        self.cmdOk = QPushButton("ok", ok_cancel)
        HorizontalSpacer(ok_cancel)
        self.cmdCancel = QPushButton("cancel", ok_cancel)
        QObject.connect(self.cmdOk, SIGNAL("clicked()"), self.accept)
        QObject.connect(self.cmdCancel, SIGNAL("clicked()"), self.reject)
        
        QVBoxLayout(self, 5, 10)
        self.layout().addWidget(self.innerbox)
        self.layout().addWidget(ok_cancel)
            

    def _showComboPanel(self, show=True):
        if show:
            self.resize(QSize(self.width()*2, self.height()))
            self.combopanel.show()
            self.innerbox.setSizes([self.width()/2,self.width()/2])
        else:
            self.resize(QSize(self.width()/2, self.height()))
            self.combopanel.hide()


    def lstChannelStylesChanged(self, idx):
        if idx == 2:
            # combo
            self._showComboPanel()
        else:
            self._showComboPanel(False)
            

    def channelWidget(self, parent, running=False, config=None):
        if config is None:
            config = self.channelConfig()
        else:
            self.setChannelConfig(config)

        w = ControlPanelWidget(parent, config, running=running)
        
        if config["label_pos"] == "above":
            QVBoxLayout(w, 2, 0)
            alignment_prefix = "v"
        else:
            QHBoxLayout(w, 2, 0)
            alignment_prefix = "h"
        
        alignment_flag = ChannelWidgetSettingsDialog.alignment_flags[alignment_prefix + config["label_align"]]
        w.layout().addWidget(QLabel(config["label"], w), 0, alignment_flag)
        w.value = ChannelWidgetSettingsDialog.value_display_widgets[config["value_display_style"]](w)
        if "combo" in config:
            for value, label in config["combo"]:
                w.value.insertItem(label)
        w.layout().addWidget(w.value)
        
        return w


    def setChannelConfig(self, config):
        self.txtLabel.setText(config["label"])
        self.optLabelAbove.setChecked(config["label_pos"]=="above")
        self.optLabelLeft.setChecked(config["label_pos"]=="left")
        self.optLabelAlignLeft.setChecked(config["label_align"]=="left")
        self.optLabelAlignRight.setChecked(config["label_align"]=="right")
        self.optLabelAlignCenter.setChecked(config["label_align"]=="centre")
        self.lstChannelStyles.setCurrentText(config["value_display_style"])
        self.txtFormat.setText(config["value_display_format"])
        if "combo" in config:
            i = 0
            for value, label in config["combo"]:
                self.tblComboChoices.setText(i, 0, value)
                self.tblComboChoices.setText(i, 1, label)
                i += 1
            self._showComboPanel()
        

    def channelConfig(self):
        config = { "type": "channel",
                   "name": str(self.name()),
                   "label": str(self.txtLabel.text()),
                   "label_pos": self.optLabelAbove.isChecked() and "above" or "left",
                   "value_display_style": str(self.lstChannelStyles.currentText()),
                   "label_align": self.optLabelAlignLeft.isChecked() and "left" or self.optLabelAlignRight.isChecked() and "right" or "centre",
                   "value_display_format": str(self.txtFormat.text()) }

        if config["value_display_style"] == "combo":
            combocfg = []
            for i in range(10):
                value = self.tblComboChoices.text(i, 0)
                label = self.tblComboChoices.text(i, 1)
                combocfg.append((value, label))
            config["combo"] = combocfg
            
        return config


class VerticalGridSpacer(ControlPanelWidget):
    def __init__(self, *args, **kwargs):
        ControlPanelWidget.__init__(self, *args, **kwargs)

        self._colstretch = 2
        self._rowstretch = 2
        
        QHBoxLayout(self)
        self.layoutItem = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.layout().addItem(self.layoutItem)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)


    def __repr__(self):
        return '"vertical_spacer"'
        
        
    def paintEvent(self, event):
        if not self._running:
            p = QPainter(self)
            p.setPen(QPen(Qt.black, 3))
            
            w = self.width() / 2
            p.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
            p.drawLine(w, 0, w - 5, 5)
            p.drawLine(w, 0, w + 5, 5)
            p.drawLine(w, self.height(), w - 5, self.height() - 5)
            p.drawLine(w, self.height(), w + 5, self.height() - 5)


class HorizontalGridSpacer(ControlPanelWidget):
    def __init__(self, *args, **kwargs):
        ControlPanelWidget.__init__(self, *args, **kwargs)

        self._colstretch = 2
        self._rowstretch = 2
        
        QHBoxLayout(self)
        self.layoutItem = QSpacerItem(10, 10, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.layout().addItem(self.layoutItem)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)


    def __repr__(self):
        return '"horizontal_spacer"'
        
    
    def paintEvent(self, event):
        if not self._running:
            p = QPainter(self)
            p.setPen(QPen(Qt.black, 3))
            
            h = self.height() / 2
            p.drawLine(0, h, self.width(), h)
            p.drawLine(0, h, 5, h - 5)
            p.drawLine(0, h, 5, h + 5)
            p.drawLine(self.width(), h, self.width() - 5, h - 5)
            p.drawLine(self.width(), h, self.width() - 5, h + 5)
        

class GridElement(ControlPanelWidget):
    def __init__(self, parent, row, col):
        ControlPanelWidget.__init__(self, parent)

        self.row = row
        self.col = col
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)


    def __repr__(self):
        return '"grid_element"'
        
    
    def sizeHint(self):
        return QSize(10, 10)  
    

class ControlPanelBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.hardwareObject = None
        self.panel = QGrid(1, self)
        self._widgets_list = [ self._newGridElement(1,1,self.panel) ]
        self.panel.setSpacing(5)
        self.__forcedSelectedGridElement = None

        self.addProperty("mnemonic", "string", "")
        self.addProperty("settings", "", {}, hidden=True)
        self.addProperty("ncols", "integer", 1, hidden=True)
        self.addProperty("nrows", "integer", 1, hidden=True)

        self.panelEditor = QVBox(self)
        self.panelEditor.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.panelEditor.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.panelEditor.setLineWidth(2)
        self.panelEditor.setMidLineWidth(3)
        self.panelEditor.setSpacing(5)
        self.panelEditor.setMargin(0)

        cmdspanel = QHBox(self.panelEditor)
        cmdspanel.setSpacing(0)
        cmdspanel.setMargin(0)
        QLabel("commands:", cmdspanel)
        self.lstCommands = QComboBox(cmdspanel)
        HorizontalSpacer(cmdspanel, size=10)
        self.cmdAddCmd = ToolButton(cmdspanel, "Plus2", self.cmdAddCmdClicked, "add command")
        self.cmdAddCmd.setEnabled(False)
        HorizontalSpacer(cmdspanel)
        QLabel("<b>Grid&nbsp;layout&nbsp;:</b>", cmdspanel)
        HorizontalSpacer(cmdspanel, size=5)
        self.cmdAddCol = ToolButton(cmdspanel, "add_col", self.cmdAddColClicked, "add column in grid")
        self.cmdAddRow = ToolButton(cmdspanel, "add_row", self.cmdAddRowClicked, "add row in grid")
        HorizontalSpacer(cmdspanel, size=5)
        self.cmdDelCol = ToolButton(cmdspanel, "delete_last_col", self.cmdDelColClicked, "delete column")
        self.cmdDelRow = ToolButton(cmdspanel, "delete_last_row", self.cmdDelRowClicked, "delete row")
        
        chanspanel = QHBox(self.panelEditor)
        chanspanel.setSpacing(0)
        chanspanel.setMargin(0)
        QLabel("channels:", chanspanel)
        self.lstChannels = QComboBox(chanspanel)
        HorizontalSpacer(chanspanel, size=10)
        self.cmdAddChan = ToolButton(chanspanel, "Plus2", self.cmdAddChanClicked, "add channel")
        self.cmdAddChan.setEnabled(False)
        HorizontalSpacer(chanspanel)
        self.cmdEdit = ToolButton(chanspanel, "Draw2", self.cmdEditClicked, "edit")
        self.cmdEdit.setEnabled(False)
        self.cmdEdit._type=""
        self.cmdEdit._config=None
        HorizontalSpacer(cmdspanel, size=5)
        self.cmdRemove = ToolButton(chanspanel, "delete_small", self.cmdRemoveClicked, "remove")
        self.cmdRemove.setEnabled(False)
        HorizontalSpacer(chanspanel)
        self.cmdGridAddVSpacer = ToolButton(chanspanel, "vspacer", self.cmdGridAddVSpacerClicked, "add vertical spacer")
        self.cmdGridAddHSpacer = ToolButton(chanspanel, "hspacer", self.cmdGridAddHSpacerClicked, "add horizontal spacer")

        QVBoxLayout(self, 0, 5)
        self.layout().addWidget(self.panelEditor)
        self.layout().addWidget(self.panel)
        

    def run(self):
        """Go to execution mode"""
        self.panelEditor.hide()

        #self.panel.close(True)
        self._widgets_list = []

        self.readSettings()

        # make the link between the widgets and
        # the channels and commands
        for w in self._widgets_list:
            if w._config is not None:
                if w._config["type"] == "channel":
                    pass
                else:
                    cmd_obj = self.hardwareObject.getCommandObject(w._config["name"])
                    w._cmd_obj = cmd_obj

                    cmd_obj.connectSignal("commandBeginWaitReply", w._commandLaunched)
                    cmd_obj.connectSignal('commandReplyArrived', w._commandReplyArrived)
                    cmd_obj.connectSignal('commandFailed', w._commandReplyArrived)
                    cmd_obj.connectSignal('commandAborted', w._commandReplyArrived)
                    cmd_obj.connectSignal('connected', w._connected)
                    cmd_obj.connectSignal('disconnected', w._disconnected)
                    cmd_obj.connectSignal('commandReady', w._connected)
                    cmd_obj.connectSignal('commandNotReady', w._disconnected)

                    if cmd_obj.isConnected():
                        w._connected()
                    else:
                        w._disconnected()
                        
                    QObject.connect(w.command, SIGNAL("clicked()"), w._cmd_obj)


    def stop(self):
        """Go to design mode"""
        self.panelEditor.show()

        # unblock signals
        for child in self.panelEditor.queryList('QObject'):
            child.blockSignals(False)
        self.panelEditor.blockSignals(False)


    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.hardwareObject is not None:
                self.clearGUI()
                
            self.hardwareObject = self.getHardwareObject(newValue)

            if self.hardwareObject is not None:
                if isinstance(self.hardwareObject, CommandContainer):
                    cmd_names = self.hardwareObject.getCommandNamesList()
                    chan_names = self.hardwareObject.getChannelNamesList()
                    self.lstCommands.insertStrList(cmd_names)
                    self.lstChannels.insertStrList(chan_names)

                    if len(cmd_names) > 0:
                        self.cmdAddCmd.setEnabled(True)
                    if len(chan_names) > 0:
                        self.cmdAddChan.setEnabled(True)

                    if self.hardwareObject.name() in self["settings"]:
                        self.readSettings()
                    else:
                        self["settings"][self.hardwareObject.name()] = []
                        
                    return
                
            self.clearGUI()
            self.cmdAddCmd.setEnabled(False)
            self.cmdAddChan.setEnabled(False)
            self.cmdEdit.setEnabled(False)
            self.cmdRemove.setEnabled(False)
            self.hardwareObject = None


    def readSettings(self):
        if self.hardwareObject is None:
            return

        settings = eval(self["settings"][self.hardwareObject.name()])

        #print settings
        
        i = 0
        for config in settings:
            self.__forcedSelectedGridElement = i
            
            if type(config) == types.StringType:
                if config == "vertical_spacer":
                    self.cmdGridAddVSpacerClicked()
                elif config == "horizontal_spacer":
                    self.cmdGridAddHSpacerClicked()
                else:
                    self._destroyPanel()
                    row = (i / self["ncols"])+1
                    col = i % self["ncols"]
                    self._widgets_list.append(self._newGridElement(row, col))
                    self._rebuildPanel()
            else:
                if config["type"] == "channel":
                    self._addChannel(config["name"], i, config)
                else:
                    self._addCommand(config["name"], i, config)

            i += 1

        self.__forcedSelectedGridElement = None

        # select first element
        if len(self._widgets_list) > 0:
            #print 'posting event'
            qApp.postEvent(self._widgets_list[0], QMouseEvent(QEvent.MouseButtonRelease,
                                                              QPoint(1,1),
                                                              Qt.LeftButton,
                                                              Qt.LeftButton))
            

    def saveSettings(self):
        try:
            self["settings"][self.hardwareObject.name()] = repr(self._widgets_list)
        except AttributeError:
            pass
    

    def clearGUI(self):
        self._widgets_list = []
        
        self["ncols"] = 0
        self["nrows"] = 1
        self.cmdAddColClicked()


    def _newGridElement(self, row, col, parent=None):
        new_empty = GridElement(parent, row, col)
        QObject.connect(new_empty, PYSIGNAL("widgetClicked"), self._widgetClicked)
        return new_empty

        
    def _getSelectedElementIndex(self):
        if self.__forcedSelectedGridElement is not None:
            return self.__forcedSelectedGridElement
        if ControlPanelWidget.selected is not None:
            selected_element = ControlPanelWidget.selected()
            if selected_element is not None and isinstance(selected_element, GridElement):
                return self._widgets_list.index(selected_element)


    def _addWidgetToList(self, widget, idx):
        self._widgets_list.insert(idx, widget)
        widget._i = idx
        QObject.connect(widget, PYSIGNAL("widgetClicked"), self._widgetClicked)

        self.saveSettings()

        return widget
       

    def _addWidget(self, klass, *args, **kwargs):    
        #print 'adding', klass
        i = kwargs.get("i", None)
            
        if i is None:
            i = self._getSelectedElementIndex()
        if i is None:
            return

        try:
            del kwargs["i"]
        except KeyError:
            pass
        
        self._destroyPanel()
        try:
            self._widgets_list[i].close(True)
            del self._widgets_list[i]
        except IndexError:
            pass
        if len(args) == 0:
            w = self._addWidgetToList(klass(None, **kwargs), i)
        else:
            w = self._addWidgetToList(klass(*args, **kwargs), i)
        #print self._widgets_list
        self._rebuildPanel()

        return w
    

    def _removeWidget(self, i):
        row = (i / self["ncols"])+1
        col = i % self["ncols"]

        self._destroyPanel()
        self._widgets_list[i].close(True)
        self._widgets_list[i]=self._newGridElement(row, col)
        self._rebuildPanel()

        self.saveSettings()

        self.cmdEdit.setEnabled(False)
        self.cmdRemove.setEnabled(False)


    def cmdAddCmdClicked(self):
        cmd_name = str(self.lstCommands.currentText())

        if len(cmd_name):
            self._addCommand(cmd_name)


    def cmdAddChanClicked(self):
        chan_name = str(self.lstChannels.currentText())
        
        if len(chan_name):
            self._addChannel(chan_name)


    def _addChannel(self, chan_name, i=None, config=None):
        if i is None and self._getSelectedElementIndex() is None:
            return

        chan_widget_settings_dialog = ChannelWidgetSettingsDialog(self, chan_name)
        
        if config is not None:
            chan_widget_settings_dialog.setChannelConfig(config)
        else:
            if chan_widget_settings_dialog.exec_loop() != QDialog.Accepted:
                return

        w = self._addWidget(chan_widget_settings_dialog.channelWidget,
                            i=i,
                            running=self.isRunning())
        #print self._widgets_list


    def _addCommand(self, cmd_name, i=None, config=None):
        if i is None and self._getSelectedElementIndex() is None:
            return

        cmd_widget_settings_dialog = CommandWidgetSettingsDialog(self, cmd_name)
        
        if config is not None:
            cmd_widget_settings_dialog.setCommandConfig(config)
        else:
            if cmd_widget_settings_dialog.exec_loop() != QDialog.Accepted:
                return

        w = self._addWidget(cmd_widget_settings_dialog.commandWidget,
                            i=i,
                            running=self.isRunning())
        

    def _editChannel(self, chan_name, i, config):
        chan_widget_settings_dialog = ChannelWidgetSettingsDialog(self, chan_name)
        chan_widget_settings_dialog.setChannelConfig(config)
        if chan_widget_settings_dialog.exec_loop() == QDialog.Accepted:
            w = self._addWidget(chan_widget_settings_dialog.channelWidget,
                                i=i,
                                running=self.isRunning())


    def _editCommand(self, cmd_name, i, config):
        cmd_widget_settings_dialog = CommandWidgetSettingsDialog(self, cmd_name)
        cmd_widget_settings_dialog.setCommandConfig(config)
        if cmd_widget_settings_dialog.exec_loop() == QDialog.Accepted:
            w = self._addWidget(cmd_widget_settings_dialog.commandWidget,
                                i=i,
                                running=self.isRunning())


    def _widgetClicked(self, w):
        self.cmdEdit.setEnabled(False)
        self.cmdRemove.setEnabled(False)

        if isinstance(w, HorizontalGridSpacer) or isinstance(w, VerticalGridSpacer):
            if ControlPanelWidget.selected is not None:
                self.cmdEdit.setEnabled(False)
                self.cmdRemove.setEnabled(True)
                self.cmdEdit._i = w._i
        elif isinstance(w, GridElement):
            pass
        else:
            if ControlPanelWidget.selected is not None:
                self.cmdEdit.setEnabled(True)
                self.cmdRemove.setEnabled(True)
                self.cmdEdit._type = w._config["type"]
                self.cmdEdit._config = w._config
                self.cmdEdit._i = w._i
                if w._config["type"] == "channel":
                    self.lstChannels.setCurrentText(w._config["name"])
                else:
                    self.lstCommands.setCurrentText(w._config["name"])
     

    def cmdRemoveClicked(self):
        self._removeWidget(self.cmdEdit._i)


    def cmdEditClicked(self):
        if self.cmdEdit._type == 'channel':
            self._editChannel(self.cmdEdit._config["name"], self.cmdEdit._i, config=self.cmdEdit._config)
        else:
            self._editCommand(self.cmdEdit._config["name"], self.cmdEdit._i, config=self.cmdEdit._config)
            
    
    def cmdGridAddVSpacerClicked(self):
        self._addWidget(VerticalGridSpacer, running=self.isRunning())
        

    def cmdGridAddHSpacerClicked(self):
        self._addWidget(HorizontalGridSpacer, running=self.isRunning())
        

    def _destroyPanel(self):
        for w in self._widgets_list:
            w.hide()
            w.reparent(None, 0, QPoint(0,0))

        self.panel.close(True)


    def _rebuildPanel(self):
        self.panel = QWidget(self)
        self.panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        QGridLayout(self.panel, self["nrows"], self["ncols"], 0, 5)
        self.layout().addWidget(self.panel)

        i = 0
        for w in self._widgets_list:
            #print w
            w.reparent(self.panel, 0, QPoint(0,0))
            row = (i / self["ncols"])+1
            col = i % self["ncols"]
            self.panel.layout().addWidget(w, row, col)
            self.panel.layout().setColStretch(col, w._colstretch)
            self.panel.layout().setRowStretch(row, w._rowstretch)
            w.show()
            i += 1

        self.panel.show()


    def cmdAddColClicked(self):
        self._destroyPanel()

        self["ncols"] += 1

        i = 0; row = 0
        nitems = len(self._widgets_list)
        ngriditems = self["ncols"]*self["nrows"]
        while nitems < ngriditems:
            if i % self["ncols"] == 0:
                row += 1; nitems += 1
                #print "adding new item, row=", row, "col=", self["ncols"]
                self._addWidgetToList(self._newGridElement(row, self["ncols"]), i+1)

            i += 1

        self._rebuildPanel()
        

    def cmdAddRowClicked(self):
        self._destroyPanel()
        
        self["nrows"] += 1
        nitems = len(self._widgets_list)
        ngriditems = self["ncols"]*self["nrows"]

        while nitems < ngriditems:
            nitems += 1
            #print "adding new item,row=",nitems/self["ncols"], "col=",  (nitems % self["ncols"])+1
            self._addWidgetToList(self._newGridElement(nitems/self["ncols"],(nitems % self["ncols"])+1), nitems-1)
            
        self._rebuildPanel()


    def cmdDelColClicked(self):
        pass


    def cmdDelRowClicked(self):
        pass
