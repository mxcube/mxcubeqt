from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import logging
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar

__category__ = 'mxCuBE'


class CommandMenuBrick(BlissWidget):
    STOP_COMMAND_ICON="Stop"
    CANCEL_COMMAND_ICON="Delete"

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.inExpert=None

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('safetyShutter', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('iconsStopCancel', 'string', '')
        self.addProperty('label', 'string', '')
        self.addProperty('showBorder', 'boolean', True)
        self.addProperty('confirmationMessages', 'string', '')
        self.addProperty('toolTips', 'string', '')
        self.addProperty('userModeMask', 'string', '')
        self.addProperty('expertModeMask', 'string', '')
        self.defineSlot('setEnabled',())
        self.defineSignal('commandStarted',())
        self.defineSignal('commandDone',())
        self.defineSignal('commandFailed',())
        #self.defineSlot('enable_widget', ())

        self.safetyShutter = None
        self.commandHO = None
        self.commandButtons = {}

        self.commands2Hide=[]

        self.containerBox = QVBox(self)
        #self.containerBox.setInsideMargin(4)
        #self.containerBox.setInsideSpacing(2)

        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.containerBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self.containerBox)

    def setExpertMode(self,mode):
        self.inExpert=mode

        if mode:
            masks_list=self['expertModeMask'].split('/')
        else:
            masks_list=self['userModeMask'].split('/')
        masks_dict={}
        for mask in masks_list:
            mask_list=mask.split('=')
            try:
                masks_dict[mask_list[0]]=mask_list[1]
            except IndexError:
                pass

        for but_name in self.commandButtons:
            but=self.commandButtons[but_name]
            try:
                mask=masks_dict[but_name]
            except KeyError:
                but.setEnableMask(True)
            else:
                if mask=='0':
                    but.setEnableMask(False)
                else:
                    but.setEnableMask(True)

    def run(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def hideCommands(self,commands):
        self.commands2Hide.extend(commands)

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.commandHO is not None:
                for but_name in self.commandButtons:
                    but=self.commandButtons[but_name]
                    QObject.disconnect(but,PYSIGNAL("macroStarted"),self.macroStarted)
                    QObject.disconnect(but,PYSIGNAL("macroDone"),self.macroDone)
                    QObject.disconnect(but,PYSIGNAL("macroFailed"),self.macroFailed)
                    but.close(True)
                self.commandButtons = {}

            self.commandHO = self.getHardwareObject(newValue)
            if self.commandHO is None:
                return

            for cmd in self.commandHO.getCommands():
                try:
                    self.commands2Hide.index(cmd.name())
                except ValueError:
                    but=MenuButton(self.containerBox,cmd,self.isSearchDone)
                    but.setMinimumSize(QSize(75,50))
                    QObject.connect(but,PYSIGNAL("macroStarted"),self.macroStarted)
                    QObject.connect(but,PYSIGNAL("macroDone"),self.macroDone)
                    QObject.connect(but,PYSIGNAL("macroFailed"),self.macroFailed)
                    self.commandButtons[but.userName()]=but
                    if cmd.isConnected():
                        but.connected()
                    else:
                        but.disconnected()
            self['icons']=self['icons']
            self['label']=self['label']
            self['confirmationMessages']=self['confirmationMessages']
            self['toolTips']=self['toolTips']
        elif property == 'safetyShutter':
            self.safetyShutter=self.getHardwareObject(newValue)
            if self.safetyShutter is None:
                logging.getLogger().warning("CommandMenuBrick: safety shutter not configured")
        elif property == 'icons':
            self.setIcons(newValue)
        elif property == 'label':
            if self.commandHO is not None:
                if self['showBorder']:
                    self.containerBox.setTitle(newValue)
                #else:
                #    self.containerBox.setTitle("")
        elif property == 'showBorder':
            if newValue:
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
            else:
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                #self.containerBox.setInsideMargin(0)
            self['label']=self['label']            
        elif property == 'confirmationMessages':
            self.setConfirmationMessages(newValue)
        elif property == 'toolTips':
            self.setToolTips(newValue)
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    def macroStarted(self,cmd):
        self.emit(PYSIGNAL("commandStarted"), (cmd,))
        
    def macroDone(self,cmd):
        self.emit(PYSIGNAL("commandDone"), (cmd,))

    def macroFailed(self,cmd):
        self.emit(PYSIGNAL("commandFailed"), (cmd,))

    def setIcons(self,icons):
        stop_cancel_icons=self['iconsStopCancel'].split()
        try:
            stop_icon_name=stop_cancel_icons[0]
        except IndexError:
            stop_icon_name=CommandMenuBrick.STOP_COMMAND_ICON
        try:
            cancel_icon_name=stop_cancel_icons[1]
        except IndexError:
            cancel_icon_name=CommandMenuBrick.CANCEL_COMMAND_ICON

        icons_list=icons.split('/')
        icons_dict={}
        for icon in icons_list:
            icon_list=icon.split('=')
            try:
                icons_dict[icon_list[0]]=icon_list[1]
            except IndexError:
                pass

        for but_name in self.commandButtons:
            try:
                icon_name=icons_dict[but_name]
            except KeyError:
                pass
            else:
                but=self.commandButtons[but_name]
                but.setIcons(icon_name,stop_icon_name,cancel_icon_name)
                
    #def enable_widget(self, state):
    #    if state:
    #        self.setEnabled(True)
    #    else:
    #        self.setDisabled(True)

    def setConfirmationMessages(self,confirmations):
        confirmations_list=confirmations.split('/')
        confirmations_dict={}
        for confirmation in confirmations_list:
            confirmation_list=confirmation.split('=')
            try:
                confirmations_dict[confirmation_list[0]]=confirmation_list[1]
            except IndexError:
                pass

        for but_name in self.commandButtons:
            try:
                confirmation=confirmations_dict[but_name]
            except KeyError:
                pass
            else:
                but=self.commandButtons[but_name]
                but.setConfirmationMessage(confirmation)

    def isSearchDone(self):
        if self.safetyShutter is not None:
            if self.safetyShutter.getShutterState() in ('disabled','fault','error','moving','unknown'):
                return False
        return True

    def setToolTips(self,tips):
        tips_list=tips.split('/')
        tips_dict={}
        for tip in tips_list:
            tip_list=tip.split('=')
            try:
                tips_dict[tip_list[0]]=tip_list[1]
            except IndexError:
                pass

        for but_name in self.commandButtons:
            try:
                tip=tips_dict[but_name]
            except KeyError:
                pass
            else:
                but=self.commandButtons[but_name]
                QToolTip.add(but,tip)

class MenuButton(QToolButton):
    def __init__(self, parent, cmd, is_search_done):
        QToolButton.__init__(self,parent)

        self.cmd=cmd
        self.confirmationMsg=None
        self.executing=None
        self.arguments = cmd.getArguments()
        self.argumentsDialog=None
        self.confirmDialog=None
        self.isSearchDone=is_search_done

        self.prevEnable=None
        self.enableMask=True

        self.runIcon=None
        self.stopIcon=None
        self.cancelIcon=None
        self.standardColor=None

        self.setTextLabel(cmd.userName())
        self.setUsesTextLabel(True)

        QObject.connect(self, SIGNAL('clicked()'), self.buttonClicked)

        self.cmd.connectSignal('commandBeginWaitReply', self.macroStarted)
        self.cmd.connectSignal('commandReplyArrived', self.macroDone)
        self.cmd.connectSignal('commandFailed', self.macroFailed)
        self.cmd.connectSignal('commandAborted', self.macroAborted)
        self.cmd.connectSignal('connected', self.connected)
        self.cmd.connectSignal('disconnected', self.disconnected)
        self.cmd.connectSignal('commandReady', self.commandReady)
        self.cmd.connectSignal('commandNotReady', self.commandNotReady)

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

    def setEnableMask(self,mask):
        self.enableMask=mask
        self.setEnabled(self.prevEnable and self.enableMask)

    def setConfirmationMessage(self,confirmation):
        self.confirmationMsg=confirmation

    def setIcons(self,icon_run,icon_stop,icon_cancel):
        self.runIcon=Icons.load(icon_run)
        self.stopIcon=Icons.load(icon_stop)
        self.cancelIcon=Icons.load(icon_cancel)

        if self.executing:
            self.setPixmap(self.stopIcon)
        else:
            self.setPixmap(self.runIcon)

    def buttonClicked(self):
        if self.executing:
            self.cancelCommand()
        else:
            self.executeCommand()

    def executeCommand(self):
        go=True

        searched=True
        if callable(self.isSearchDone):
            searched=self.isSearchDone()

        if not len(self.arguments):
            if self.confirmationMsg is not None:
                conf_msg=self.confirmationMsg
                if not searched:
                    conf_msg="Warning: the hutch hasn't been searched!\n%s" % conf_msg
                self.confirmDialog=QMessageBox(self.cmd.userName(),conf_msg,QMessageBox.Question,
                    QMessageBox.Ok,QMessageBox.Cancel,QMessageBox.NoButton)

                go=(self.confirmDialog.exec_loop()==QMessageBox.Ok)
                self.confirmDialog=None
            elif not searched:
                conf_msg="The hutch hasn't been searched! Press OK to continue anyway."
                self.confirmDialog=QMessageBox(self.cmd.userName(),conf_msg,QMessageBox.Question,
                    QMessageBox.Ok,QMessageBox.Cancel,QMessageBox.NoButton)
                go=(self.confirmDialog.exec_loop()==QMessageBox.Ok)
                self.confirmDialog=None
        else:
            go=True
            if not searched:
                conf_msg="<b>%s</b><br>Warning: the hutch hasn't been searched!" % self.confirmationMsg
            else:
                conf_msg="<b>%s</b>" % self.confirmationMsg

        if go:
            args=[]
            if len(self.arguments)>0:
                if self.argumentsDialog is None:
                    self.argumentsDialog=ArgumentsDialog(self,self.cmd.userName(),self.arguments,conf_msg)
                else:
                    self.argumentsDialog.setEnabled(True)
                go=False
                if self.argumentsDialog.exec_loop()==QMessageBox.Ok:
                    go=True
                    args=self.argumentsDialog.getArguments()

            if go:
                self.prevEnable=False
                self.setEnabled(False)
                self.cmd(*tuple(args))

    def userName(self):
        return self.cmd.userName()

    def cancelCommand(self):
        self.prevEnable=False
        self.setEnabled(False)
        self.cmd.abort()

    def disconnected(self):
        if self.confirmDialog is not None:
            self.confirmDialog.reject()
        if self.argumentsDialog is not None:
            self.argumentsDialog.reject()
        self.prevEnable=False
        self.setEnabled(False and self.enableMask)

    def connected(self):
        self.prevEnable=True
        self.setEnabled(True and self.enableMask)

    def commandReady(self):
        self.connected()

    def commandNotReady(self):
        if not self.executing:
            self.disconnected()

    def macroStarted(self,*args):
        #print "STARTED"
        self.executing=True
        if self.standardColor is None:
            self.standardColor=self.paletteBackgroundColor()
        self.setPaletteBackgroundColor(QWidget.yellow)
        if self.stopIcon is not None:
            self.setPixmap(self.stopIcon)
        self.prevEnable=True
        self.setEnabled(True)
        self.emit(PYSIGNAL("macroStarted"), (self.cmd,))

    def macroDone(self,*args):
        #print "DONE"
        self.executing=False
        if self.standardColor is not None:
            self.setPaletteBackgroundColor(self.standardColor)
        if self.runIcon is not None:
            self.setPixmap(self.runIcon)
        self.emit(PYSIGNAL("macroDone"), (self.cmd,))

    def macroFailed(self,*args):
        #print "FAILED"
        self.executing=False
        if self.standardColor is not None:
            self.setPaletteBackgroundColor(self.standardColor)
        if self.runIcon is not None:
            self.setPixmap(self.runIcon)
        self.emit(PYSIGNAL("macroFailed"), (self.cmd,))

    def macroAborted(self,*args):
        #print "ABORTED"
        pass


###
### Dialog box to login and change the proposal
###
class ArgumentsDialog(QDialog):
    VALIDATOR_TYPE={'integer':QIntValidator, 'float':QDoubleValidator}
    CONVERTER_FUN={'integer':int, 'float':float, 'string':str}

    def __init__(self,parent,name,arguments,confirmation_msg):
        QDialog.__init__(self,parent,'',False)
        self.cmdName=name
        self.arguments=arguments
        self.inputs={}
        self.inputArguments=[]

        self.warningDialog=None
        self.argsOk=False

        self.setCaption("%s arguments" % name)

        if confirmation_msg is not None and len(confirmation_msg):
            conf_label=QLabel("%s"% confirmation_msg,self)
            conf_label.setAlignment(Qt.AlignCenter)
        else:
            conf_label=None

        self.contentsBox=QHGroupBox('Arguments',self)
        self.argsGrid=QWidget(self.contentsBox)
        QGridLayout(self.argsGrid, 0, 0, 2, 2)

        buttons_box=DialogButtonsBar(self,name,"Cancel",None,self.buttonClicked)

        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        if conf_label is not None:
            self.layout().addWidget(conf_label)
        self.layout().addWidget(self.contentsBox)
        self.layout().addWidget(buttons_box)

        i=0
        
        for arg in self.arguments:
            arg_name=arg[0]
            arg_type=arg[1]
            label=QLabel("%s:" % arg_name,self.argsGrid)
            editor=QLineEdit(self.argsGrid)
            self.inputs[arg_name]=editor
            self.argsGrid.layout().addWidget(label, i, 0)
            self.argsGrid.layout().addWidget(editor, i, 1)
            i+=1

            try:
                validator_class=ArgumentsDialog.VALIDATOR_TYPE[arg_type]
            except KeyError:
                pass
            else:
                validator=validator_class(editor)
                editor.setValidator(validator)

    def getArguments(self):
        return self.inputArguments

    def reject(self):
        if self.warningDialog is not None:
            self.warningDialog.reject()
        self.argsOk=True
        QDialog.reject(self)

    def buttonClicked(self,text):
        if text==self.cmdName:
            return self.accept()
        else:
            return self.reject()

    def exec_loop(self):
        self.argsOk=False
        while not self.argsOk:
            res=QDialog.exec_loop(self)
            self.inputArguments=[]
            if res==QMessageBox.Ok:
                problems=[]
                for arg in self.arguments:
                    arg_name=arg[0]
                    arg_type=arg[1]
                    arg=str(self.inputs[arg_name].text())

                    try:
                        validator_fun=ArgumentsDialog.CONVERTER_FUN[arg_type]
                    except KeyError:
                        validator_fun=str

                    try:
                        input_arg=validator_fun(arg)
                    except (ValueError,TypeError):
                        problems.append("The value <%s> isn't a valid %s for %s." % (arg,arg_type,arg_name))
                    else:
                        self.inputArguments.append(input_arg)
            
                if len(problems)>0:
                    res=QMessageBox.Cancel
                    problems_str="\n".join(problems)
                    self.warningDialog=QMessageBox("Invalid arguments",problems_str,\
                        QMessageBox.Question,QMessageBox.Ok,QMessageBox.NoButton,QMessageBox.NoButton)
                    self.warningDialog.exec_loop()
                    self.warningDialog=None
                else:
                    self.argsOk=True
            else:
                self.argsOk=True

        return res

class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
