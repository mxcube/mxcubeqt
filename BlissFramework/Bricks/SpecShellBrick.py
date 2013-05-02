from qt import *
from BlissFramework import BaseComponents
from BlissFramework import Icons
import BlissFramework
import logging
import os
import string

'''

Doc please

'''

__category__ = 'Spec'


class SpecShellBrick(BaseComponents.BlissWidget):
    ABORT_COMMAND_ICON="Stop2"

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.specShellHO = None

        self.hasAllCommands = False
        self.standardColor=None

        self.executeIcon=None
        self.abortIcon=None

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('myTabLabel', 'string', '')
        self.addProperty('allCommandsAvailable', 'boolean', False)
        self.addProperty('shellFontSize', 'integer', 8)
        self.addProperty('shellBackgroundColor', 'string', "AAAAFF")
        self.addProperty('shellForegroundColor', 'string', "000000")

        self.defineSlot('tabSelected',())

        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        self.messageBox=QTextEdit(self)
        self.messageBox.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.messageBox.setTextFormat(QTextEdit.LogText)

        self.commandsBox=QHBox(self)
        self.label=QLabel("Command:",self.commandsBox)
        self.label.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.specCommand=QComboBox(self.commandsBox)
        self.specCommand.setDuplicatesEnabled(False)
        self.executeButton=QToolButton(self.commandsBox)
        self.executeButton.setTextLabel('Execute')
        self.executeButton.setUsesTextLabel(True)
        self.executeButton.setTextPosition(QToolButton.BesideIcon)
        self.executeButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        QObject.connect(self.executeButton, SIGNAL('clicked()'), self.executeSpecCommand)
        self.commandEditor=None

        QVBoxLayout(self)
        self.layout().addWidget(self.messageBox)
        self.layout().addWidget(self.commandsBox)

        self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

        self.specDisconnected()

    def setExpertMode(self,state):
        state=state or self['allCommandsAvailable']

        if self.specShellHO is None:
            return

        if self.commandEditor is not None:
            QObject.disconnect(self.commandEditor,SIGNAL('returnPressed()'),self.executeSpecCommand)
            self.commandEditor=None

        self.specCommand.setEditable(state)
        if not state:
            self.specCommand.clear()
            usercmds=self.specShellHO.getUserCommands()
            for cmd in usercmds:
                self.specCommand.insertItem(cmd)
        else:
            self.commandEditor=self.specCommand.lineEdit()
            QObject.connect(self.commandEditor,SIGNAL('returnPressed()'),self.executeSpecCommand)
        self.specCommand.setAutoCompletion(state)

    def executeSpecCommand(self):
        self.executeButton.setEnabled(False)
        if self.specShellHO.isRunning():
            self.specShellHO.abortCommand()
        else:
            command=str(self.specCommand.currentText())
            self.specShellHO.executeCommand(command)

    def specConnected(self):
        self.specCommand.clear()
        self.hasAllCommands = False
        if not self['allCommandsAvailable']:
            usercmds=self.specShellHO.getUserCommands()
            for cmd in usercmds:
                self.specCommand.insertItem(cmd)
        self.messageBox.setEnabled(True)
        self.commandsBox.setEnabled(True)


    def getAllCommands(self):
        self.specShellHO.getAllCommands()

    def allCommandsList(self,commands):
        #if len(commands):
        #    self.hasAllCommands = True
        self.hasAllCommands = True
        self.specCommand.clear()
        i=0
        wa_i=0
        for cmd in commands:
            self.specCommand.insertItem(cmd)
            if cmd=="wa":
                wa_i=i
            i+=1
        try:
            self.specCommand.setCurrentItem(wa_i)
        except:
            pass
        self.specShellHO.executeCommand("wa")

    def specDisconnected(self):
        self.messageBox.setEnabled(False)
        self.commandsBox.setEnabled(False)

    def specReady(self):
        #self.setEnabled(True)
        self.commandsBox.setEnabled(True)
        if not self.hasAllCommands and self['allCommandsAvailable']:
            #QTimer.singleShot(SpecShellBrick.GETALLCOMMANDS_DELAY,self.getAllCommands)
            self.getAllCommands()

    def specBusy(self):
        #self.setEnabled(False)
        self.commandsBox.setEnabled(False)

    def specOutput(self,line):
        self.messageBox.append("%s" % line)
        self.messageBox.scrollToBottom()
        try:
            lines=len(line.split("\n"))
        except:
            lines=1
        self.emit(PYSIGNAL("incUnreadMessages"),(lines,True,))

    def commandFailed(self,result):
        self.label.setEnabled(True)
        self.specCommand.setEnabled(True)
        if self.standardColor is not None:
            self.executeButton.setPaletteBackgroundColor(self.standardColor)
        if self.executeIcon is not None:
            self.executeButton.setPixmap(self.executeIcon)
        self.executeButton.setEnabled(True)

    def commandFinished(self,result):
        self.label.setEnabled(True)
        self.specCommand.setEnabled(True)
        if self.standardColor is not None:
            self.executeButton.setPaletteBackgroundColor(self.standardColor)
        if self.executeIcon is not None:
            self.executeButton.setPixmap(self.executeIcon)
        self.executeButton.setEnabled(True)

    def commandAborted(self):
        pass

    def commandStarted(self):
        self.executeButton.setEnabled(True)
        self.label.setEnabled(False)
        self.specCommand.setEnabled(False)
        if self.standardColor is None:
            self.standardColor=self.executeButton.paletteBackgroundColor()
        self.executeButton.setPaletteBackgroundColor(QWidget.yellow)
        if self.abortIcon is not None:
            self.executeButton.setPixmap(self.abortIcon)

    def tabSelected(self,tab_name):
        if tab_name==self['myTabLabel']:
            self.emit(PYSIGNAL("resetUnreadMessages"),(True,))

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.specShellHO is not None:
                self.disconnect(self.specShellHO,'connected',self.specConnected)
                self.disconnect(self.specShellHO,'disconnected',self.specDisconnected)
                self.disconnect(self.specShellHO,'output',self.specOutput)
                self.disconnect(self.specShellHO,'ready',self.specReady)
                self.disconnect(self.specShellHO,'busy',self.specBusy)
                self.disconnect(self.specShellHO,'started',self.commandStarted)
                self.disconnect(self.specShellHO,'finished',self.commandFinished)
                self.disconnect(self.specShellHO,'aborted',self.commandAborted)
                self.disconnect(self.specShellHO,'failed',self.commandFailed)
                self.disconnect(self.specShellHO,'allCommandsList',self.allCommandsList)
            self.specShellHO=self.getHardwareObject(newValue)
            if self.specShellHO is not None:
                self.connect(self.specShellHO,'connected',self.specConnected)
                self.connect(self.specShellHO,'disconnected',self.specDisconnected)
                self.connect(self.specShellHO,'output',self.specOutput)
                self.connect(self.specShellHO,'ready',self.specReady)
                self.connect(self.specShellHO,'busy',self.specBusy)
                self.connect(self.specShellHO,'started',self.commandStarted)
                self.connect(self.specShellHO,'finished',self.commandFinished)
                self.connect(self.specShellHO,'aborted',self.commandAborted)
                self.connect(self.specShellHO,'failed',self.commandFailed)
                self.connect(self.specShellHO,'allCommandsList',self.allCommandsList)
                if self.specShellHO.isConnected():
                    self.specConnected()
                    if self.specShellHO.isReady():
                        self.specReady()
                else:
                    self.specDisconnected()
            else:
                self.specDisconnected()

        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.executeIcon=Icons.load(icons_list[0])
            except IndexError:
                pass
            else:
                self.executeButton.setPixmap(self.executeIcon)
                try:
                    abort_icon_name=icons_list[1]
                except IndexError:
                    abort_icon_name=SpecShellBrick.ABORT_COMMAND_ICON
                self.abortIcon=Icons.load(abort_icon_name)

        elif propertyName == 'shellFontSize':
            self.messageBox.setFont(QFont("courier",newValue))

        elif propertyName == 'shellBackgroundColor':
            paper=self.messageBox.paper()
            try:
                r=string.atoi(newValue[0:2],16)
                g=string.atoi(newValue[2:4],16)
                b=string.atoi(newValue[4:6],16)
            except:
                logging.getLogger().exception("SpecShellBrick: problem setting background color")
            else:
                paper.setColor(QColor(r,g,b))
                self.messageBox.setPaper(paper)

        elif propertyName == 'shellForegroundColor':
            try:
                r=string.atoi(newValue[0:2],16)
                g=string.atoi(newValue[2:4],16)
                b=string.atoi(newValue[4:6],16)
            except:
                logging.getLogger().exception("SpecShellBrick: problem setting text color")
            else:
                self.messageBox.setColor(QColor(r,g,b))

        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        
