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

import os
import time
import logging
import InstanceServer

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget
#import BlissFramework


__category__ = "Qt4_General"


class Qt4_ChatBrick(BlissWidget):
    """
    Descript. :
    """
    PRIORITY_COLORS = ('darkblue', 'black', 'red')
    MY_COLOR = 'darkgrey'

    def __init__(self, *args):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        BlissWidget.__init__(self, *args)

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('myTabLabel', 'string', '')

        # Signals ------------------------------------------------------------
        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        # Slots ---------------------------------------------------------------
        self.defineSlot('tabSelected',())
        self.defineSlot('sessionSelected',())

        # Hardware objects ----------------------------------------------------
        self.instance_server_hwobj = None

        # Internal values -----------------------------------------------------
        self.session_id = None
        self.nickname = ""
        self.role = BlissWidget.INSTANCE_ROLE_UNKNOWN

        # Graphic elements ----------------------------------------------------
        self.conversation_textedit = QtGui.QTextEdit(self)
        self.conversation_textedit.setReadOnly(True)
        _controls_widget = QtGui.QWidget(self)
        _say_label = QtGui.QLabel("Say:", _controls_widget)
        self.message_ledit = QtGui.QLineEdit(_controls_widget)
        self.send_button = QtGui.QPushButton("Send", _controls_widget)
        self.send_button.setEnabled(False)

        # Layout --------------------------------------------------------------
        _controls_widget_hlayout = QtGui.QHBoxLayout(_controls_widget)
        _controls_widget_hlayout.addWidget(_say_label)
        _controls_widget_hlayout.addWidget(self.message_ledit)
        _controls_widget_hlayout.addWidget(self.send_button)
        _controls_widget_hlayout.setSpacing(2)
        _controls_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.conversation_textedit)
        _main_vlayout.addWidget(_controls_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.send_button.clicked.connect(self.send_current_message)
        self.message_ledit.returnPressed.connect(self.send_current_message)
        self.message_ledit.textChanged.connect(self.message_changed)

        #self.setFixedHeight(120)
        #self.setFixedWidth(790)

    def run(self):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        self.set_role(self.role)

    def session_selected(self, *args):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        session_id = args[0]
        is_inhouse = args[-1]
        self.conversation_textedit.clear()
        if is_inhouse:
          self.session_id = None
        else:
          self.session_id = session_id
          self.load_chat_history()

    def load_chat_history(self):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if self.instance_server_hwobj is not None:
            chat_history_filename = "/tmp/mxCuBE_chat_%s.%s" % (self.session_id, self.instance_server_hwobj.isClient() and "client" or "server")
        else:
            return
        try:
            chat_history = open(chat_history_filename, "r")
        except:
            return

        if self.isEnabled():
            for msg in chat_history.readlines():
              self.conversation_textedit.append(msg)

    def instance_role_changed(self,role):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        self.set_role(role)

    def set_role(self, role):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        self.role = role
        if role != BlissWidget.INSTANCE_ROLE_UNKNOWN and not self.isEnabled():
            self.setEnabled(True)
            self.load_chat_history()

    def message_changed(self,text):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        self.send_button.setEnabled(len(str(text))>0)

    def message_arrived(self,priority,user_id,message):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        color=Qt4_ChatBrick.PRIORITY_COLORS[priority]
        msg_prefix=""
        msg_suffix=""
        if priority==InstanceServer.ChatInstanceMessage.PRIORITY_NORMAL:
            if user_id is None:
                header=""
            else:
                header=" %s:" % self.instance_server_hwobj.idPrettyPrint(user_id)
                if user_id[0]==self.nickname:
                    color=Qt4_ChatBrick.MY_COLOR
        else:
            header=""
            msg_prefix="<i>"
            msg_suffix="</i>"

        now = time.strftime("%T")
        new_line = "<font color=%s><b>(%s)%s</b> %s%s%s</font>" % (color, now,header,msg_prefix,message,msg_suffix)
        self.conversation_textedit.append(new_line)
       
        if self.session_id is not None and self.instance_server_hwobj is not None: 
          chat_history_filename = "/tmp/mxCuBE_chat_%s.%s" % (self.session_id, self.instance_server_hwobj.isClient() and "client" or "server")
          try:
            if time.time() - os.stat(chat_history_filename).st_mtime > 24*3600:
              os.unlink(chat_history_filename)
          except OSError:
            pass  
          chat_history_file = open(chat_history_filename, "a")
          chat_history_file.write(new_line)
          chat_history_file.write("\n")
          chat_history_file.close()

        self.emit(QtCore.SIGNAL("incUnreadMessages"),1, True)

    def new_client(self,client_id):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        msg="%s has joined the conversation." % self.instance_server_hwobj.idPrettyPrint(client_id)
        self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def wants_control(self,client_id):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        msg="%s wants to have control!" % self.instance_server_hwobj.idPrettyPrint(client_id)
        self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_HIGH,None,msg)

    def server_initialized(self,started,server_id=None):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if started:
            msg="I'm moderating the chat as %s." % server_id[0]
            self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)
            self.nickname=server_id[0]

    def client_closed(self,client_id):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        msg="%s has left the conversation..." % self.instance_server_hwobj.idPrettyPrint(client_id)
        self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def client_initialized(self,connected,server_id=None,my_nickname=None,quiet=False):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if connected:
            server_print=self.instance_server_hwobj.idPrettyPrint(server_id)
            msg="I've joined the conversation as %s (moderator is %s)." % (my_nickname,server_print)
            self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)
            self.nickname=my_nickname

    def client_changed(self,old_client_id,new_client_id):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        #print "CHAT CLIENT CHANGED",old_client_id,new_client_id
        if old_client_id[0]==self.nickname:
            self.nickname=new_client_id[0]
        else:
            old_client_print=self.instance_server_hwobj.idPrettyPrint(old_client_id)
            new_client_print=self.instance_server_hwobj.idPrettyPrint(new_client_id)
            msg="%s has changed to %s." % (old_client_print,new_client_print)
            self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def send_current_message(self):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        txt=str(self.message_ledit.text())
        if len(txt):
            self.instance_server_hwobj.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_NORMAL,txt)
            self.message_ledit.setText("")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if property_name == 'mnemonic':
            if self.instance_server_hwobj is not None:
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('chatMessageReceived'), self.message_arrived)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('newClient'), self.new_client)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('serverInitialized'),self.server_initialized)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientInitialized'),self.client_initialized)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('serverClosed'), self.client_closed)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('wantsControl'), self.wants_control)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('haveControl'), self.have_control)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('passControl'), self.pass_control)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientClosed'), self.client_closed)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientChanged'), self.client_changed)

            self.instance_server_hwobj = self.getHardwareObject(new_value)
            if self.instance_server_hwobj is not None:
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('chatMessageReceived'), self.message_arrived)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('newClient'), self.new_client)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('serverInitialized'),self.server_initialized)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientInitialized'),self.client_initialized)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('serverClosed'), self.client_closed)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('wantsControl'), self.wants_control)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('haveControl'), self.have_control)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('passControl'), self.pass_control)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientClosed'), self.client_closed)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientChanged'), self.client_changed)

        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.send_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[0])))
            except IndexError:
                pass
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)        

    def have_control(self,have_control,gui_only=False):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if not gui_only:
            if have_control:
                p=InstanceServer.ChatInstanceMessage.PRIORITY_HIGH
                msg="I've gained control!"
            else:
                p=InstanceServer.ChatInstanceMessage.PRIORITY_HIGH
                msg="I've lost control..."
            self.message_arrived(p,None,msg)

    def pass_control(self,has_control_id):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        has_control_print=self.instance_server_hwobj.idPrettyPrint(has_control_id)
        msg="%s has control." % has_control_print
        self.message_arrived(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,None,msg)

    def tabSelected(self,tab_name):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        if tab_name==self['myTabLabel']:
            self.emit(QtCore.SIGNAL("resetUnreadMessages"), True)
