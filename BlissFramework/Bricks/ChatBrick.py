from qt import *
from BlissFramework import BaseComponents
from BlissFramework import Icons
import BlissFramework
import logging
import InstanceServer
import time
import os

__category__ = "mxCuBE"

class ChatBrick(BaseComponents.BlissWidget):
    PRIORITY_COLORS = ('darkblue', 'black', 'red')
    MY_COLOR = 'darkgrey'

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('myTabLabel', 'string', '')

        self.defineSlot('tabSelected',())
        self.defineSlot('sessionSelected',())

        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        self.conversation=QTextEdit(self)
        self.conversation.setReadOnly(True)

        self.instanceServer = None
        self.session_id = None
        self.nickname = ""
        self.role = BaseComponents.BlissWidget.INSTANCE_ROLE_UNKNOWN

        box1=QHBox(self)
        QLabel("Say:",box1)
        self.message=QLineEdit(box1)
        self.sendButton=QToolButton(box1)
        self.sendButton.setTextLabel('Send')
        self.sendButton.setUsesTextLabel(True)
        self.sendButton.setTextPosition(QToolButton.BesideIcon)
        self.sendButton.setEnabled(False)
        self.sendButton.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        QObject.connect(self.sendButton, SIGNAL('clicked()'), self.sayCurrentMessage)
        QObject.connect(self.message, SIGNAL('returnPressed()'), self.sayCurrentMessage)
        QObject.connect(self.message, SIGNAL('textChanged(const QString &)'), self.messageChanged)

        QVBoxLayout(self)
        self.layout().addWidget(self.conversation)
        self.layout().addWidget(box1)
 
        self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

    def run(self):
        self.setRole(self.role)
        #self.setEnabled(False)

    def sessionSelected(self, *args):
        session_id = args[0]
        is_inhouse = args[-1]
        self.conversation.clear()
        if is_inhouse:
          self.session_id = None
        else:
          self.session_id = session_id
          self.loadChatHistory()

    def loadChatHistory(self):
        chat_history_filename = "/tmp/mxCuBE_chat_%s.%s" % (self.session_id, self.instanceServer.isClient() and "client" or "server")
        try:
            chat_history = open(chat_history_filename, "r")
        except:
            return

        if self.isEnabled():
            for msg in chat_history.readlines():
              self.conversation.append(msg)

    def instanceRoleChanged(self,role):
        self.setRole(role)

    def setRole(self, role):
        self.role = role
        if role!=BaseComponents.BlissWidget.INSTANCE_ROLE_UNKNOWN and not self.isEnabled():
            self.setEnabled(True)
            self.loadChatHistory()

    def messageChanged(self,text):
        self.sendButton.setEnabled(len(str(text))>0)

    def messageArrived(self,priority,user_id,message):
        color=ChatBrick.PRIORITY_COLORS[priority]
        msg_prefix=""
        msg_suffix=""
        if priority==InstanceServer.ChatInstanceMessage.PRIORITY_NORMAL:
            if user_id is None:
                header=""
            else:
                header=" %s:" % self.instanceServer.idPrettyPrint(user_id)
                if user_id[0]==self.nickname:
                    color=ChatBrick.MY_COLOR
        else:
            header=""
            msg_prefix="<i>"
            msg_suffix="</i>"

        now=time.strftime("%T")
        new_line = "<font color=%s><b>(%s)%s</b> %s%s%s</font>" % (color, now,header,msg_prefix,message,msg_suffix)
        self.conversation.append(new_line)
       
        if self.session_id is not None: 
          chat_history_filename = "/tmp/mxCuBE_chat_%s.%s" % (self.session_id, self.instanceServer.isClient() and "client" or "server")
          try:
            if time.time() - os.stat(chat_history_filename).st_mtime > 24*3600:
              os.unlink(chat_history_filename)
          except OSError:
            pass  
          chat_history_file = open(chat_history_filename, "a")
          chat_history_file.write(new_line)
          chat_history_file.write("\n")
          chat_history_file.close()

        self.emit(PYSIGNAL("incUnreadMessages"),(1,True,))

    def newClient(self,client_id):
        msg="%s has joined the conversation." % self.instanceServer.idPrettyPrint(client_id)
        self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def wantsControl(self,client_id):
        msg="%s wants to have control!" % self.instanceServer.idPrettyPrint(client_id)
        self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_HIGH,None,msg)

    def serverInitialized(self,started,server_id=None):
        if started:
            msg="I'm moderating the chat as %s." % server_id[0]
            self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)
            self.nickname=server_id[0]

    def clientClosed(self,client_id):
        msg="%s has left the conversation..." % self.instanceServer.idPrettyPrint(client_id)
        self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def clientInitialized(self,connected,server_id=None,my_nickname=None,quiet=False):
        if connected:
            server_print=self.instanceServer.idPrettyPrint(server_id)
            msg="I've joined the conversation as %s (moderator is %s)." % (my_nickname,server_print)
            self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)
            self.nickname=my_nickname

    def clientChanged(self,old_client_id,new_client_id):
        #print "CHAT CLIENT CHANGED",old_client_id,new_client_id
        if old_client_id[0]==self.nickname:
            self.nickname=new_client_id[0]
        else:
            old_client_print=self.instanceServer.idPrettyPrint(old_client_id)
            new_client_print=self.instanceServer.idPrettyPrint(new_client_id)
            msg="%s has changed to %s." % (old_client_print,new_client_print)
            self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def sayCurrentMessage(self):
        txt=str(self.message.text())
        if len(txt):
            self.instanceServer.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_NORMAL,txt)
            self.message.setText("")

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer,PYSIGNAL('chatMessageReceived'), self.messageArrived)
                self.disconnect(self.instanceServer,PYSIGNAL('newClient'), self.newClient)
                self.disconnect(self.instanceServer,PYSIGNAL('serverInitialized'),self.serverInitialized)
                self.disconnect(self.instanceServer,PYSIGNAL('clientInitialized'),self.clientInitialized)
                self.disconnect(self.instanceServer,PYSIGNAL('serverClosed'), self.clientClosed)
                self.disconnect(self.instanceServer,PYSIGNAL('wantsControl'), self.wantsControl)
                self.disconnect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
                self.disconnect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.disconnect(self.instanceServer,PYSIGNAL('clientClosed'), self.clientClosed)
                self.disconnect(self.instanceServer,PYSIGNAL('clientChanged'), self.clientChanged)

            self.instanceServer = self.getHardwareObject(newValue)
            if self.instanceServer is not None:
                self.connect(self.instanceServer,PYSIGNAL('chatMessageReceived'), self.messageArrived)
                self.connect(self.instanceServer,PYSIGNAL('newClient'), self.newClient)
                self.connect(self.instanceServer,PYSIGNAL('serverInitialized'),self.serverInitialized)
                self.connect(self.instanceServer,PYSIGNAL('clientInitialized'),self.clientInitialized)
                self.connect(self.instanceServer,PYSIGNAL('serverClosed'), self.clientClosed)
                self.connect(self.instanceServer,PYSIGNAL('wantsControl'), self.wantsControl)
                self.connect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
                self.connect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.connect(self.instanceServer,PYSIGNAL('clientClosed'), self.clientClosed)
                self.connect(self.instanceServer,PYSIGNAL('clientChanged'), self.clientChanged)

        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.sendButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        

    def haveControl(self,have_control,gui_only=False):
        if not gui_only:
            if have_control:
                p=InstanceServer.ChatInstanceMessage.PRIORITY_HIGH
                msg="I've gained control!"
            else:
                p=InstanceServer.ChatInstanceMessage.PRIORITY_HIGH
                msg="I've lost control..."
            self.messageArrived(p,None,msg)

    def passControl(self,has_control_id):
        #print "ChatBrick.passControl",has_control_id
        has_control_print=self.instanceServer.idPrettyPrint(has_control_id)
        msg="%s has control." % has_control_print
        self.messageArrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def tabSelected(self,tab_name):
        if tab_name==self['myTabLabel']:
            self.emit(PYSIGNAL("resetUnreadMessages"),(True,))
