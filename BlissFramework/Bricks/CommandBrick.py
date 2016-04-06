import logging
import types
import Icons

from qt import *

from BlissFramework.BaseComponents import BlissWidget


class ChannelLabel(QLabel):
    def __init__(self, chanObject, *args):
        QLabel.__init__(self, *args)

        self.chanObject = chanObject
        self.formatString = None
        self.oldValue = None

        chanObject.connectSignal("update", self.updateValue)
        chanObject.connectSignal("connected", self.enable)
        chanObject.connectSignal("disconnected", self.disable)

        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setText('%s: -' % chanObject.userName())


    def updateValue(self, value):
        #print 'updated value = ', value
        if value is None:
            self.setText('-')
            return
                
        if type(value) == float or type(value) == int:
            if self.formatString is not None:
                self.setText('%s' % self.formatString % value)
            else:
                self.setText('%s' % str(value))
        elif type(value) == dict:
            text = '<table>'
            for key, val in value.items():
                text += '<tr><td>%s</td><td>%s</td></tr>' % (key, val)
            text+='</table>'
            self.setText(text)
        elif type(value) == bytes:
            self.setText('%s' % value)
        else:
            logging.getLogger().error('Cannot display variable value : unknown type %s', type(value))

        self.oldValue = value


    def setNumberFormatString(self, format):
        self.formatString = format
        self.updateValue(self.oldValue)
        

    def enable(self):
        self.setEnabled(True)


    def disable(self):
        self.setEnabled(False)


class HorizontalSpacer(QWidget):
    def __init__(self, *args):
       QWidget.__init__(self, *args)
   
       self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

class DummyCallable:
    def __call__(self, *args, **kwargs):
        pass

class CommandButton(QVBox):
    def __init__(self, cmdObject, *args):
        QVBox.__init__(self, *args)
        
        self.cmdObject = cmdObject
        self.entryWidgets = {}
        self.arguments = cmdObject.getArguments()

        self.setSpacing(5)
        self.setMargin(0)

        if len(self.arguments) > 0: 
          entryWidgetsGrid = QGrid(3, self)
          entryWidgetsGrid.setSpacing(0)
          entryWidgetsGrid.setMargin(5)

          for argname, argtype, onchange, valuefrom in self.arguments:
	    QLabel(argname, entryWidgetsGrid)
            QLabel(' : ', entryWidgetsGrid)
            cmdobj = DummyCallable()
            chanobj = None
            if onchange is not None:
               cmd, container_ref = onchange
               container = container_ref()
               if container is not None:
                 cmdobj = container.getCommandObject(cmd)
            if valuefrom is not None:
               chan, container_ref = valuefrom
               container = container_ref()
               if container is not None:
                  chanobj = container.getChannelObject(chan)
                  
            if argtype == 'combo':
                combobox = QComboBox(entryWidgetsGrid)
                combobox._items = {}
                for name, value in cmdObject.getComboArgumentItems(argname):
                    combobox.insertItem(name)
                    combobox._items[name]=value
                    
                    def activated(text, widget=combobox, cmdobj=cmdobj):
                        cmdobj(str(widget._items[str(text)]))

                    QObject.connect(combobox, SIGNAL("activated(const QString&)"), activated)
                combobox._activated=activated   
                def valuechanged(value, widget=combobox, chanobj=chanobj):
                    try:
                      for i in range(widget.count()):
                        if widget._items[str(widget.text(i))]==value:
                           widget.setCurrentItem(i)
                           break
                    except:
                      logging.getLogger().exception("%s: could not set item", self.name())
                if chanobj is not None:
                    chanobj.connectSignal("update", valuechanged)
                
                combobox._valuechanged=valuechanged
                self.entryWidgets[argname] = combobox 
            else:
                lineedit=QLineEdit('', entryWidgetsGrid)
                def onreturnpressed(widget=lineedit, cmdobj=cmdobj):
                    cmdobj(str(widget.text()))
                QObject.connect(lineedit, SIGNAL("returnPressed()"), onreturnpressed) 
                def valuechanged(value, widget=lineedit, chanobj=chanobj):
                    try:
                       widget.setText(str(value))
                    except:
                      logging.getLogger().exception("%s: could not set text", self.name())
                if chanobj is not None:
                    chanobj.connectSignal("update", valuechanged)
                lineedit._valuechanged=valuechanged
                lineedit._onreturnpressed=onreturnpressed
                self.entryWidgets[argname]=lineedit
            self.entryWidgets[argname]._onchange = cmdobj
            self.entryWidgets[argname]._from = chanobj
        cmdExecuteBox = QHBox(self)
        HorizontalSpacer(cmdExecuteBox)
        self.cmdExecute = QToolButton(cmdExecuteBox)
        self.cmdExecute.setTextLabel(cmdObject.userName())
        self.cmdExecute.setUsesTextLabel(True)
        self.cmdExecute.setIconSet(QIconSet(Icons.load("launch")))
        self.cmdExecute.setTextPosition(QToolButton.BesideIcon)
        HorizontalSpacer(cmdExecuteBox)        

        cmdObject.connectSignal("commandBeginWaitReply", self.commandLaunched)
        cmdObject.connectSignal('commandReplyArrived', self.commandReplyArrived)
        cmdObject.connectSignal('commandFailed', self.commandReplyArrived)
        cmdObject.connectSignal('commandAborted', self.commandReplyArrived)
        cmdObject.connectSignal('connected', self.connected)
        cmdObject.connectSignal('disconnected', self.disconnected)
	cmdObject.connectSignal('commandReady', self.enableCommand)
	cmdObject.connectSignal('commandNotReady', self.disableCommand)
        self.connect(self.cmdExecute, SIGNAL('clicked()'), self.launchCommand)


    def commandLaunched(self,*args):
        self.cmdExecute.setTextLabel("abort")
        self.cmdExecute.setIconSet(QIconSet(Icons.load("stop")))


    def commandReplyArrived(self, *args):
        self.enableCommand()

    def enableCommand(self):
        self.cmdExecute.setTextLabel(self.cmdObject.userName())
        self.cmdExecute.setEnabled(True)
        self.cmdExecute.setIconSet(QIconSet(Icons.load("launch")))


    def disableCommand(self):
        if str(self.cmdExecute.textLabel()) != 'abort':
          self.cmdExecute.setEnabled(False)


    def launchCommand(self, *args):
        if str(self.cmdExecute.textLabel()) == 'abort':
            self.cmdObject.abort()
        else:
            args = []
            for argName, argType, onChange, valueFrom in self.arguments:
                entryWidget = self.entryWidgets[argName]
                if argType == 'combo':
                    svalue = str(entryWidget.currentText())
                else:
                    svalue = str(entryWidget.text())

                if argType == 'float':
                    convertFunc = float
                elif argType == 'integer':
                    convertFunc = int
                elif argType == 'string':
                    convertFunc = str
                elif argType == 'combo':
                    convertFunc = lambda s: entryWidget._items[s]
                else:
                    QMessageBox.warning(self, 'Bad argument type', 'Do not know how to convert %s to %s.' % (svalue, argType), QMessageBox.Ok)
                    return

                try:
                    value = convertFunc(svalue)
                except ValueError:
                    QMessageBox.warning(self, 'Invalid value', '%s is not a valid %s value.' % (svalue, argType), QMessageBox.Ok)
                    return
                else:
                    args.append(value)
            self.cmdObject(*tuple(args))


    def disconnected(self):
        self.cmdExecute.setEnabled(False)


    def connected(self):
        self.cmdExecute.setEnabled(True)
        

class CommandBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty('mnemonic', 'string')
        self.addProperty('numberFormatString', 'formatString', '+####.##')
        self.addProperty('title', 'string', '')
        self.addProperty('commands_channels', 'string', '', hidden=True)
 
        self.__brick_properties = list(self.propertyBag.properties.keys())
        self.__commands_channels = {}
        
        self.defineSlot("showBrick", ())

        self.hardwareObject = None

        self.cmdButtons = []
        self.channelLabels = []
        
        self.lblTitle = QLabel(self)
        self.channelsBox = QGrid(2, self)
        self.commandsBox = QVBox(self)
        self.lblTitle.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        QVBoxLayout(self, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self.lblTitle)
        self.layout().addWidget(self.channelsBox, 0, Qt.AlignHCenter)
        self.layout().addWidget(self.commandsBox, 0, Qt.AlignHCenter)


    def showBrick(self, show):
        if show:
          self.show()
        else:
          self.hide()


    def run(self):
        self['commands_channels']=self['commands_channels']
        self.adjustSize()
        

    def setExpertMode(self, expert):
       for cmdbtn in self.cmdButtons:
         property = "[cmd] %s expert only" % cmdbtn.cmdObject.name()
         try:
           expert_only = self[property]
         except:
           continue
         else:
           if expert_only:
             cmdbtn.setEnabled(expert)


    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.hardwareObject is not None:
                if not self.isRunning():
                    # we are changing hardware object in Design mode
                    for propname in list(self.propertyBag.properties.keys()):
                        if not propname in self.__brick_properties:
                            self.delProperty(propname)
                
                for cmdbtn in self.cmdButtons:
                    cmdbtn.close(True)
                self.cmdButtons = []
               
                for lblchan in self.channelLabels:
                    lblchan.close(True)
                self.channelLabels = []
                    
            self.hardwareObject = self.getHardwareObject(newValue)

            if self.hardwareObject is None:
                return

            if hasattr(self.hardwareObject, 'getChannels'):
                for chan in self.hardwareObject.getChannels():
	            self.channelLabels.append(QLabel('<nobr><b>%s</b></nobr>' % str(chan.name()), self.channelsBox))
                    self.channelLabels[-1].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.channelLabels.append(ChannelLabel(chan, self.channelsBox))
                    self.channelLabels[-1].setNumberFormatString(self['numberFormatString'])
                    if not self.isRunning():
                        propname = "[channel] %s" % chan.name()
                        self.addProperty(propname, "boolean", True)
                        self.showProperty(chan.name())
                       
                    if chan.isConnected():
                        self.channelLabels[-1].enable()
                        self.channelLabels[-1].updateValue(chan.getValue())
                    else:
                        self.channelLabels[-1].disable()
                    
                for cmd in self.hardwareObject.getCommands():
                    self.cmdButtons.append(CommandButton(cmd, self.commandsBox))
                    if not self.isRunning():
                        propname = "[cmd] %s" % cmd.name()
                        self.addProperty(propname, "boolean", True)
                        self.addProperty(propname+" expert only", "boolean", False)
                        self.showProperty(cmd.name())
                   
                    if cmd.isConnected():
                        self.cmdButtons[-1].connected()
                    else:
                        self.cmdButtons[-1].disconnected()
	    else:
                self.hardwareObject = None
                logging.getLogger().error("%s: hardware object does not contain any command", ho.name())

            self["commands_channels"]=self["commands_channels"]
            
            self.adjustSize()
        elif property == 'numberFormatString':
            for i in range(len(self.channelLabels)):
                if i % 2:
                    self.channelLabels[i].setNumberFormatString(self['numberFormatString'])
        elif property == 'title':
	    if len(newValue) == 0:
	       self.lblTitle.hide()
            else:
	       self.lblTitle.show()
	       self.lblTitle.setText(newValue)
            self.adjustSize()
        elif property == 'commands_channels': 
            try:
                self.__commands_channels = eval(newValue)
            except:
                return

            print(self.__commands_channels)

            for objname, cmdchan_info in self.__commands_channels.items():
                try:
                  show, expert_only = cmdchan_info
                except:
                  # compatibility with old config.
                  show = cmdchan_info 

                for i in range(0, len(self.channelLabels), 2):
                    label, channel_label = self.channelLabels[i:i+2]
              
                    if channel_label.chanObject.name()==objname:
                        if show:
                            label.show()
                            channel_label.show()
                        else:
                            label.hide()
                            channel_label.hide()
                        self.getProperty("[channel] %s" % objname).setValue(show)
                for cmdbtn in self.cmdButtons:
                    if cmdbtn.cmdObject.name()==objname:
                        if show:
                            cmdbtn.show()
                        else:
                            cmdbtn.hide()

                        self.getProperty("[cmd] %s" % objname).setValue(show)
                        try:
                          self.getProperty("[cmd] %s expert only" % objname).setValue(expert_only)
                        except:
                          logging.getLogger().exception("fuck")

            self.propertyBag.updateEditor()
        else:
            try:
                #n = "".join(property.split()[1:])
                n = property[property.find(" ")+1:]
            except:
                return
            else:
                if n.endswith("expert only"):
                  n = n[:-12]
                  self.__commands_channels[n]=(self[property[:-12]], newValue)
                else: 
                  try:
                    self.__commands_channels[n] = (newValue, self[n+" expert only"])
                  except:
                    self.__commands_channels[n] = (newValue, False)

                self["commands_channels"] = str(self.__commands_channels)
                logging.getLogger().info("%s", self["commands_channels"])




