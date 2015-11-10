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
import smtplib
import gevent
import logging
import smtplib

import InstanceServer
import email.Utils

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

from HardwareRepository.HardwareRepository import dispatcher


__category__ = "Qt4_General"


WANTS_CONTROL_EVENT = QtCore.QEvent.User
class WantsControlEvent(QtCore.QEvent):
    """
    Descript. :
    """  
    def __init__(self, client_id):
        QtCore.QEvent.__init__(self, WANTS_CONTROL_EVENT)
        self.client_id = client_id

START_SERVER_EVENT = QtCore.QEvent.User + 1 
class StartServerEvent(QtCore.QEvent):
    """
    Descript. :
    """ 
    def __init__(self):
        QtCore.QEvent.__init__(self, START_SERVER_EVENT)

APP_BRICK_EVENT = QtCore.QEvent.User+2
class AppBrickEvent(QtCore.QEvent):
    """
    Descript. :
    """ 
    def __init__(self, brick_name, widget_name, method_name, method_args, masterSync):
        QtCore.QEvent.__init__(self, APP_BRICK_EVENT)
        self.brick_name = brick_name
        self.widget_name = widget_name
        self.method_name = method_name
        self.method_args = method_args
        self.masterSync = masterSync

APP_TAB_EVENT = QtCore.QEvent.User+3
class AppTabEvent(QtCore.QEvent):
    """
    Descript. :
    """ 
    def __init__(self,tab_name,tab_index):
        QtCore.QEvent.__init__(self, APP_TAB_EVENT)
        self.tab_name = tab_name
        self.tab_index = tab_index

MSG_DIALOG_EVENT = QtCore.QEvent.User+4
class MsgDialogEvent(QtCore.QEvent):
    """
    Descript. :
    """ 
    def __init__(self, icon_type, msg, font_size, callback=None):
        QtCore.QEvent.__init__(self, MSG_DIALOG_EVENT)
        self.icon_type = icon_type
        self.msg = msg
        self.font_size = font_size
        self.callback = callback

USER_INFO_DIALOG_EVENT = QtCore.QEvent.User+5
class UserInfoDialogEvent(QtCore.QEvent):
    """
    Descript. :
    """ 
    def __init__(self, msg, fromaddrs, toaddrs, subject, is_local, font_size):
        QtCore.QEvent.__init__(self, USER_INFO_DIALOG_EVENT)
        self.msg = msg
        self.fromaddrs = fromaddrs
        self.toaddrs = toaddrs
        self.is_local = is_local
        self.subject = subject
        self.font_size = font_size


class Qt4_InstanceListBrick(BlissWidget):
    """
    Descript. :
    """ 

    LOCATIONS = ("UNKNOWN", "LOCAL", "INHOUSE", "INSITE", "EXTERNAL")
    MODES = ("UNKNOWN", "MASTER", "SLAVE")
    ROLES = ("UNKNOWN", "ACTING_AS_SERVER", "LAUNCHING_SERVER", 
             "ACTING_AS_CLIENT","CONNECTING_TO_SERVER")
    IDS = ("UNKNOWN", "USER", "INHOUSE_USER", "INHOUSE_IMPERSONATION")
    RECONNECT_TIME = 5000

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------
        self.addProperty("mnemonic", "string", "")
        self.addProperty("xmlrpc_server", "string", "/Qt4_xml-rpc-server")
        self.addProperty("icons", "string", "")
        self.addProperty("giveControlTimeout", "integer", 30)
        self.addProperty("initializeServer", "boolean", False)
        self.addProperty("controlEmails", "string", "")
        self.addProperty("hutchtrigger", "string", "") 

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setSession',())

        # Hardware objects ----------------------------------------------------
        self.instance_server_hwobj = None
        self.hutch_trigger_hwobj = None
        self.xmlrpc_server = None

        # Internal values -----------------------------------------------------
        self.give_control_chboxDialog = None
        self.timeout_left = -1
        self.my_proposal = None
        self.in_control = None
        self.connections = {}

        # Graphic elements ----------------------------------------------------
        _main_gbox = QtGui.QGroupBox("Current users",self)

        self.users_listwidget = QtGui.QListWidget(_main_gbox)
        self.users_listwidget.setFixedHeight(50)

        #self.users_listwidget.setFixedWidth(150)
        self.give_control_chbox = QtGui.QCheckBox(\
             "Selecting gives control", _main_gbox)
        self.give_control_chbox.setChecked(False)
        self.allow_timeout_control_chbox = QtGui.QCheckBox(\
             "Allow timeout control",_main_gbox)
        self.allow_timeout_control_chbox.setChecked(False)

        self.take_control_button = QtGui.QToolButton(_main_gbox)
        self.take_control_button.setUsesTextLabel(True)
        self.take_control_button.setText("Take control")
        self.take_control_button.setEnabled(True)
        self.take_control_button.hide()

        #self.take_control_button.setFixedWidth(50)

        self.ask_control_button = QtGui.QToolButton(_main_gbox)
        self.ask_control_button.setUsesTextLabel(True)
        self.ask_control_button.setText("Ask for control")
        self.ask_control_button.setEnabled(False)
        #self.ask_control_button.setFixedWidth(50)

        _my_name_widget = QtGui.QWidget(_main_gbox)
        _my_name_label = QtGui.QLabel("My name:", _my_name_widget)
        self.nickname_ledit = NickEditInput(_my_name_widget)
        #self.nickname_ledit.setFixedWidth(50)

        reg_exp = QtCore.QRegExp(".+")
        nick_validator = QtGui.QRegExpValidator(reg_exp, self.nickname_ledit)
        self.nickname_ledit.setValidator(nick_validator)

        self.clientIcon=None
        self.serverIcon=None
        self.externalUserInfoDialog=ExternalUserInfoDialog()

        # Layout --------------------------------------------------------------
        _my_name_widget_layout = QtGui.QHBoxLayout(_my_name_widget)
        _my_name_widget_layout.addWidget(_my_name_label)
        _my_name_widget_layout.addWidget(self.nickname_ledit)
        #_my_name_widget_layout.addStretch(0)
        _my_name_widget_layout.setContentsMargins(0, 0, 0, 0)       

        _main_gbox_vlayout = QtGui.QVBoxLayout(_main_gbox)
        _main_gbox_vlayout.addWidget(self.users_listwidget)
        _main_gbox_vlayout.addWidget(self.give_control_chbox)
        _main_gbox_vlayout.addWidget(self.allow_timeout_control_chbox)
        _main_gbox_vlayout.addWidget(self.take_control_button)
        _main_gbox_vlayout.addWidget(self.ask_control_button)
        _main_gbox_vlayout.addWidget(_my_name_widget)
        _main_gbox_vlayout.setSpacing(0)
        _main_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_gbox)
        _main_vlayout.setSpacing(1)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        
        # SizePolicies --------------------------------------------------------
        #self.take_control_button.setSizePolicy(QtGui.QSizePolicy.Expanding,
        #                                       QtGui.QSizePolicy.Fixed)
        self.ask_control_button.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                              QtGui.QSizePolicy.Fixed)
        
        # Qt signal/slot connections ------------------------------------------
        self.users_listwidget.itemPressed.connect(self.user_selected)
        self.take_control_button.clicked.connect(self.takeControlClicked)
        self.ask_control_button.clicked.connect(self.askForControlClicked)
        self.nickname_ledit.returnPressed.connect(self.changeMyName)

        # Other ---------------------------------------------------------------
        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.timeout.connect(self.timeoutApproaching)


    def propertyChanged(self, propertyName, oldValue, newValue):
        """
        Descript. :
        """
        if propertyName == 'mnemonic':
            if self.instance_server_hwobj is not None:
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('instanceInitializing'),self.instanceInitializing)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('serverInitialized'),self.serverInitialized)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientInitialized'),self.clientInitialized)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('serverClosed'),self.serverClosed)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('newClient'), self.newClient)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('haveControl'), self.haveControl)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('passControl'), self.passControl)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('wantsControl'), self.wantsControl)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('widgetUpdate'), self.widgetUpdate)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientChanged'), self.clientChanged)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('clientClosed'), self.clientClosed)
                self.disconnect(self.instance_server_hwobj, QtCore.SIGNAL('widgetCall'), self.widgetCall)

            self.instance_server_hwobj = self.getHardwareObject(newValue)

            if self.instance_server_hwobj is not None:
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('instanceInitializing'),self.instanceInitializing)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('serverInitialized'),self.serverInitialized)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientInitialized'),self.clientInitialized)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('serverClosed'),self.serverClosed)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('newClient'), self.newClient)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('haveControl'), self.haveControl)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('passControl'), self.passControl)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('wantsControl'), self.wantsControl)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('widgetUpdate'), self.widgetUpdate)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientChanged'), self.clientChanged)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('clientClosed'), self.clientClosed)
                self.connect(self.instance_server_hwobj, QtCore.SIGNAL('widgetCall'), self.widgetCall)
        elif propertyName=="xmlrpc_server":
            self.xmlrpc_server = self.getHardwareObject(newValue)
        elif propertyName == 'hutchtrigger':
            self.hutch_trigger_hwobj = self.getHardwareObject(newValue)
            if self.hutch_trigger_hwobj is not None:
                self.connect(self.hutch_trigger_hwobj,  QtCore.SIGNAL("hutchTrigger"), self.hutchTriggerChanged) 
        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.serverIcon=Qt4_Icons.load(icons_list[0])
                self.clientIcon=Qt4_Icons.load(icons_list[1])
                self.take_control_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[2])))
                self.ask_control_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[3])))
            except IndexError:
                pass
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def hutchTriggerChanged(self, hutch_opened):
        """
        Descript. :
        """
        if hutch_opened:
            if not BlissWidget.isInstanceRoleServer():
              logging.getLogger().info("%s: HUTCH IS OPENED, YOU LOSE CONTROL", self.name())
              self.take_control_button.setEnabled(False)
            else:
              logging.getLogger().info("%s: HUTCH IS OPENED, TAKING CONTROL OVER REMOTE USERS", self.name())
              self.instance_server_hwobj.takeControl()
        else:
            if not BlissWidget.isInstanceRoleServer():
              logging.getLogger().info("%s: HUTCH IS CLOSED, YOU ARE ALLOWED TO TAKE CONTROL AGAIN", self.name())
              self.take_control_button.setEnabled(True) 


    def setSession(self, session_id, prop_code = None, prop_number=None,prop_id=None,expiration=None,orig_prop_code=None,is_inhouse=None):
        """
        Descript. :
        """
        self.externalUserInfoDialog.clearUserInfo()

        if prop_code is not None and prop_number is not None and prop_code!='' and prop_number!='':
            if self.instance_server_hwobj is not None:
                try:
                    proposal_dict={ "code":orig_prop_code,\
                        "alias": prop_code,\
                        "number":prop_number,\
                        "session":int(session_id),\
                        "inhouse":is_inhouse }
                except:
                    logging.getLogger().exception("Qt4_InstanceListBrick: problem setting session")
                    return
                else:
                    self.my_proposal=proposal_dict
                    self.instance_server_hwobj.setProposal(proposal_dict)

            if is_inhouse:
                BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_INHOUSE)
                self.ask_control_button.hide()
                self.take_control_button.show()
                self.take_control_button.setEnabled(BlissWidget.isInstanceRoleServer()) #BlissWidget.isInstanceModeMaster())
                if self.hutch_trigger_hwobj is not None and not BlissWidget.isInstanceModeMaster():
                    hutch_opened = 1-int(self.hutch_trigger_hwobj.getChannelObject("status").getValue())
                    logging.getLogger().info("%s: hutch is %s, %s 'Take control' button", self.name(), hutch_opened and "opened" or "close", hutch_opened and "disabling" or "enabling")
                    self.take_control_button.setEnabled(1-hutch_opened)
            else:
                BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_LOGGED)
                self.take_control_button.hide()
                self.ask_control_button.show()
                self.ask_control_button.setEnabled(not BlissWidget.isInstanceModeMaster())
        else:
            if self.instance_server_hwobj is not None:
                self.my_proposal=None
                self.instance_server_hwobj.setProposal(None)

            BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_UNKNOWN)
            self.take_control_button.hide()
            self.ask_control_button.show()
            #self.ask_control_button.setEnabled(BlissWidget.isInstanceRoleServer() and not BlissWidget.isInstanceModeMaster())
            self.ask_control_button.setEnabled(False)

    def reconnectToServer(self):
        """
        Descript. :
        """
        self.instance_server_hwobj.reconnect(quiet=True)

    def instanceInitializing(self):
        """
        Descript. :
        """
        is_local=self.instance_server_hwobj.isLocal()
        if is_local:
            loc=BlissWidget.INSTANCE_LOCATION_LOCAL
        else:
            loc=BlissWidget.INSTANCE_LOCATION_EXTERNAL
        BlissWidget.setInstanceLocation(loc)

        #TODO fix this to use activeWindow
        for widget in QtGui.QApplication.topLevelWidgets():
            if hasattr(widget, "configuration"):
                active_window = widget.configuration
 
        self.connect(active_window,  
                     QtCore.SIGNAL('applicationBrickChanged'), 
                     self.applicationBrickChanged)
        self.connect(active_window,  
                     QtCore.SIGNAL('applicationTabChanged'), 
                     self.applicationTabChanged)

        """self.connect(QtGui.QApplication.activeWindow(),  
                     QtCore.SIGNAL('applicationBrickChanged'), 
                     self.applicationBrickChanged)
        self.connect(QtGui.QApplication.activeWindow(),  
                     QtCore.SIGNAL('applicationTabChanged'), 
                     self.applicationTabChanged)"""

    def clientInitialized(self,connected,server_id=None,my_nickname=None,quiet=False):
        """
        Descript. :
        """
        if connected is None:
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)
        elif not connected:
            if not quiet:
                msg_event=MsgDialogEvent(QtGui.QMessageBox.Warning,\
                    "Couldn't connect to the server application!",\
                    self.font().pointSize())
                QtGui.QApplication.postEvent(self,msg_event)
                
            QtCore.QTimer.singleShot(Qt4_InstanceListBrick.RECONNECT_TIME,self.reconnectToServer)
        else:
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENT)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)

            server_print=self.instance_server_hwobj.idPrettyPrint(server_id)
            if self.clientIcon is None:
                item = QtGui.QListWidgetItem(server_print, 
                                             self.users_listwidget)
            else:
                item = QtGui.QListWidgetItem(QtGui.QIcon(self.serverIcon),
                                             server_print,
                                             self.users_listwidget)
            item.setSelected(False)
            self.nickname_ledit.setText(my_nickname)
            self.connections[server_id[0]]=(item,server_id[1])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            #item.setSelectable(False)
            self.haveControl(False,gui_only=True)
            self.initName(my_nickname)
            #self.give_control_chbox.setChecked(False)

            camera_brick = None

            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    if "CameraBrick" in str(w.__class__):
                        camera_brick = w
                        camera_brick.installEventFilter(self)
                        break

            # find the video brick, make sure it is hidden when collecting data
            # and that it is shown again when DC is finished
            def disable_video(w=camera_brick):
                w.disable_update()
            self.__disable_video=disable_video
            def enable_video(w=camera_brick):
                w.enable_update()
            self.__enable_video=enable_video
            dispatcher.connect(self.__disable_video, "collect_started")
            dispatcher.connect(self.__enable_video, "collect_finished")

            msg_event = MsgDialogEvent(QtGui.QMessageBox.Information,
                "Successfully connected to the server application.",
                self.font().pointSize())
            QtGui.QApplication.postEvent(self, msg_event)

    def serverInitialized(self,started,server_id=None):
        """
        Descript. :
        """
        if started:
            #BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_UNKNOWN)
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_SERVER)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)

            self.initName(server_id[0])
            self.haveControl(True,gui_only=True)
            #self.give_control_chbox.setChecked(False)
            #self.allow_timeout_control_chbox.setChecked(False)
        else:
            #BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_SERVERSTARTING)
            #BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)
            msg_dialog=QtGui.QMessageBox("mxCuBE",\
                "Couldn't start the multiple instances server!",\
                QtGui.QMessageBox.Critical,QMessageBox.Ok,QMessageBox.NoButton,\
                QtGui.QMessageBox.NoButton,self) # Application name (mxCuBE) is hardwired!!!
            msg_dialog.setButtonText(QtGui.QMessageBox.Ok,"Quit")
            s=self.font().pointSize()
            f=msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.exec_loop()
            os._exit(1)

    def serverClosed(self,server_id):
        """
        Descript. :
        """
        self.users_listwidget.clear()
        self.connections={}
        BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING)
        BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)

        msg_event=MsgDialogEvent(QtGui.QMessageBox.Warning,\
            "The server application closed the connection!",\
            self.font().pointSize())
        QtGui.QApplication.postEvent(self, msg_event)
        QtCore.QTimer.singleShot(Qt4_InstanceListBrick.RECONNECT_TIME,
                                 self.reconnectToServer)

    def widgetUpdate(self,timestamp,method,method_args,masterSync=True):
        """
        Descript. :
        """
        logging.getLogger().debug("widgetUpdate %s %r %r", timestamp, method, method_args)

        if self.instance_server_hwobj.isServer():
            BlissWidget.addEventToCache(timestamp,method,*method_args)
            if not masterSync or BlissWidget.shouldRunEvent():
                try:
                  try:
                    if not masterSync:
                      try:
                        method.im_self.blockSignals(True)
                      except AttributeError:
                        pass
                    method(*method_args)
                  except:
                    pass
                finally:
                  try:
                    method.im_self.blockSignals(False)
                  except AttributeError:
                    pass
        else:
            if not masterSync or BlissWidget.shouldRunEvent():
                try:
                  try:
                    if not masterSync:
                      try:
                        method.im_self.blockSignals(True)
                      except AttributeError:
                        pass
                    method(*method_args)
                  except:
                    pass
                finally:
                  try:
                    method.im_self.blockSignals(False)
                  except AttributeError: 
                    pass
            else:
                BlissWidget.addEventToCache(timestamp,method,*method_args)

    def widgetCall(self,timestamp,method,method_args):
        """
        Descript. :
        """
        try:
            method(*method_args)
        except:
            logging.getLogger().debug("Qt4_InstanceListBrick: problem executing an external call")

    def instanceLocationChanged(self,loc):
        """
        Descript. :
        """
        logging.getLogger().info("Instance running in %s" % Qt4_InstanceListBrick.LOCATIONS[loc].lower())

    def instanceModeChanged(self,mode):
        """
        Descript. :
        """
        logging.getLogger().info("Instance mode set to %s" % Qt4_InstanceListBrick.MODES[mode].lower())
        self.updateMirroring()

    def applicationTabChanged(self,tab_name,tab_index):
        """
        Descript. :
        """
        if self.instance_server_hwobj is not None:
            tab_event=AppTabEvent(tab_name,tab_index)
            QtGui.QApplication.postEvent(self,tab_event)

    def applicationBrickChanged(self,brick_name,widget_name,method_name,method_args,masterSync):
        """
        Descript. :
        """
        if not masterSync or self.instance_server_hwobj is not None:
            brick_event=AppBrickEvent(brick_name,widget_name,method_name,method_args,masterSync)
            QtGui.QApplication.postEvent(self,brick_event)

    def initName(self,new_name):
        """
        Descript. :
        """
        self.nickname_ledit.setText(new_name)
        self.nickname_ledit.acceptInput()

    def changeMyName(self):
        """
        Descript. :
        """
        self.nickname_ledit.setEnabled(False)
        name=str(self.nickname_ledit.text())
        self.instance_server_hwobj.requestIdChange(name)

    def askForControlClicked(self):
        """
        Descript. :
        """ 
        self.instance_server_hwobj.askForControl()

    def takeControlClicked(self):
        """
        Descript. :
        """
        current_user=self.instance_server_hwobj.inControl()
        user_id=current_user[0]
        user_prop=current_user[1]
        control_user_print=self.instance_server_hwobj.idPrettyPrint(current_user)
        take_control_dialog=QtGui.QMessageBox("mxCuBE",\
            "You're about to take control of the application, taking over %s!" % control_user_print,\
            QtGui.QMessageBox.Question,QMessageBox.Ok,QMessageBox.Cancel,\
            QtGui.QMessageBox.NoButton,self) # Application name (mxCuBE) is hardwired!!!
        take_control_dialog.setButtonText(QtGui.QMessageBox.Ok,"Take control")
        s=self.font().pointSize()
        f=take_control_dialog.font()
        f.setPointSize(s)
        take_control_dialog.setFont(f)
        take_control_dialog.updateGeometry()
        if take_control_dialog.exec_loop()==QtGui.QMessageBox.Ok:
            self.instance_server_hwobj.takeControl()

    def run(self):
        """
        Descript. :
        """
        if self['initializeServer']:
            start_server_event=StartServerEvent()
            QtGui.QApplication.postEvent(self,start_server_event)

    def instanceUserIdChanged(self,userid):
        """
        Descript. :
        """
        logging.getLogger().info("Instance user identification is %s" % Qt4_InstanceListBrick.IDS[userid].replace("_"," ").lower())
        self.updateMirroring()

    def instanceRoleChanged(self,role):
        """
        Descript. :
        """
        logging.getLogger().info("Instance role is %s" % Qt4_InstanceListBrick.ROLES[role].replace("_"," ").lower())
        if role!=BlissWidget.INSTANCE_ROLE_UNKNOWN and not self.isVisible():
            self.show()

    def newClient(self,client_id):
        """
        Descript. :
        """
        client_print=self.instance_server_hwobj.idPrettyPrint(client_id)
        if self.clientIcon is None:
            item = QtGui.QListWidgetItem(client_print, self.users_listwidget) 
        else:
            item = QtGui.QListWidgetItem(QtGui.QIcon(self.clientIcon), 
                                         client_print, 
                                         self.users_listwidget)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.connections[client_id[0]]=(item,client_id[1])

    def clientClosed(self,client_id):
        """
        Descript. :
        """
        try:
            item=self.connections[client_id[0]][0]
        except KeyError:
            logging.getLogger().warning('Qt4_InstanceListBrick: unknown client has closed (%s)' % str(client_id))
        else:
            self.connections.pop(client_id[0])
            self.users_listwidget.takeItem(self.users_listwidget.row(item))

    def clientChanged(self,old_client_id,new_client_id):
        """
        Descript. :
        """
        try:
            item=self.connections[old_client_id[0]][0]
        except KeyError:
            self.nickname_ledit.setText(new_client_id[0])
            self.nickname_ledit.setEnabled(True)
            self.nickname_ledit.acceptInput()
        else:
            new_client_print=self.instance_server_hwobj.idPrettyPrint(new_client_id)
            item.setText(new_client_print)
            if new_client_id[0]!=old_client_id[0]:
                self.connections[new_client_id[0]]=self.connections[old_client_id[0]]
                self.connections.pop(old_client_id[0])
                if self.in_control is not None and old_client_id[0]==self.in_control[0]:
                    self.in_control[0]=new_client_id[0]
            else:
                if self.in_control is not None and old_client_id[0]==self.in_control[0]:
                    self.in_control[1]=new_client_id[1]
                    self.updateMirroring()
            self.users_listwidget.updateGeometries()

    def user_selected(self,item):
        """
        Descript. :
        """
        if item is None:
            return
        if BlissWidget.isInstanceModeMaster() and self.give_control_chbox.isChecked():
            for user_id in self.connections:
                if self.connections[user_id][0]==item:
                    self.instance_server_hwobj.giveControl((user_id,self.connections[user_id][1]))
                    break

    def haveControl(self,have_control,gui_only=False):
        """
        Descript. :
        """
        if not gui_only:
            if have_control:
                BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)
            else:
                BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)

        if have_control:
            if self.xmlrpc_server:
              gevent.spawn_later(1, self.xmlrpc_server.open)

            self.in_control=None
            self.take_control_button.setEnabled(False)
            self.ask_control_button.setEnabled(False)

            self.users_listwidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            #self.users_listwidget.setSelectionModel()
            self.users_listwidget.clearSelection()
            for item_index in range(self.users_listwidget.count()):
                self.users_listwidget.item(item_index).setFlags(QtCore.Qt.ItemIsEnabled)
                #tem.setFlags(QtCore.Qt.NoItemFlags)
            self.users_listwidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

        else:
            if self.xmlrpc_server:
                self.xmlrpc_server.close()

            if BlissWidget.isInstanceUserIdLogged():
                self.ask_control_button.setEnabled(True)
            elif BlissWidget.isInstanceUserIdInhouse():
                 if self.hutch_trigger_hwobj is not None:
                    hutch_opened = 1-int(self.hutch_trigger_hwobj.getChannelObject("status").getValue())
                    logging.getLogger().debug("%s: hutch is %s, %s 'Take control' button", self.name(), hutch_opened and "opened" or "close", hutch_opened and "disabling" or "enabling")
                    self.take_control_button.setEnabled(1-hutch_opened)
            #elif BlissWidget.isInstanceRoleServer():
            #    self.ask_control_button.setEnabled(True)
            if BlissWidget.isInstanceRoleServer():
                 self.take_control_button.setEnabled(True)

        if not gui_only:
            if have_control:
                try:
                    frombl = os.environ['SMIS_BEAMLINE_NAME']
                    #user = os.environ['SMIS_BEAMLINE_NAME']
                    #frombl = user.replace(' ','-')
                except (KeyError,TypeError,ValueError,AttributeError):
                    frombl = 'ID??'

                try:
                    proposal="%s-%d" % (self.my_proposal["code"],self.myProposal["number"])
                except:
                    proposal="unknown"

                is_local=BlissWidget.isInstanceLocationLocal()

                if is_local:
                    control_place="LOCAL"
                else:
                    control_place="EXTERNAL"
                email_subject="[MX REMOTE ACCESS] %s control is %s (proposal %s)" % (frombl,control_place,proposal)
                email_toaddrs=self["controlEmails"]
                email_fromaddrs="%s@esrf.fr" % frombl

                msg_event=UserInfoDialogEvent("I've gained control of the application.",\
                    email_fromaddrs,email_toaddrs,email_subject,is_local,\
                    self.font().pointSize())                
                logging.getLogger('user_level_log').warning("You have gained control of the application.")
            else:
                msg_event=MsgDialogEvent(QtGui.QMessageBox.Warning,\
                    "I've lost control of the application!",\
                    self.font().pointSize())
                logging.getLogger('user_level_log').warning("You have lost control of the application!")

    def passControl(self,has_control_id):
        """
        Descript. :
        """
        try:
            control_item=self.connections[has_control_id[0]][0]
        except KeyError:
            pass
        else:
            self.users_listwidget.clearSelection()
            i=self.users_listwidget.item(0)
            for item_index in range(self.users_listwidget.count()):
                self.users_listwidget.item(item_index).setFlags(QtCore.Qt.ItemIsEnabled)
            self.users_listwidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            control_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            control_item.setSelected(True)
            self.users_listwidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.in_control=list(has_control_id)
            self.updateMirroring()

    def updateMirroring(self):
        """
        Descript. :
        """
        if BlissWidget.isInstanceModeSlave():
            if BlissWidget.isInstanceUserIdUnknown():
                if BlissWidget.isInstanceRoleServer() and self.in_control is not None and self.in_control[1] is None:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
                else:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_PREVENT)
            elif BlissWidget.isInstanceUserIdInhouse():
                BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
            else:
                try:
                    control_is_inhouse=self.in_control[1]['inhouse']
                except:
                    control_is_inhouse=False
                if control_is_inhouse or self.in_control[1] is None:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
                else:
                    try:
                        my_prop_codes=[self.my_proposal['code'],self.myProposal['alias']]
                    except:
                        my_prop_codes=[]
                    try:
                        control_prop_codes=[self.in_control[1]['code'],self.in_control[1]['alias']]
                    except:
                        control_prop_codes=[]
                    mirror=BlissWidget.INSTANCE_MIRROR_PREVENT
                    for code in my_prop_codes:
                        try:
                            control_prop_codes.index(code)
                        except:
                            pass
                        else:
                            mirror=BlissWidget.INSTANCE_MIRROR_ALLOW
                            break
                    for code in control_prop_codes:
                        try:
                            my_prop_codes.index(code)
                        except:
                            pass
                        else:
                            mirror=BlissWidget.INSTANCE_MIRROR_ALLOW
                            break
                    BlissWidget.setInstanceMirror(mirror)
        else:
            BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_PREVENT)

    def timeoutApproaching(self):
        """
        Descript. :
        """
        if self.give_control_chboxDialog is not None:
            if self.timeout_left in (30,20,10):
                self.instance_server_hwobj.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,"%s will have control in %d seconds..." % (self.give_control_chboxDialog.nickname,self.timeout_left))
            self.timeout_left-=1
            if self.timeout_left==0:
                self.give_control_chboxDialog.done(QtGui.QMessageBox.Yes)
            else:
                self.give_control_chboxDialog.setButtonText(QtGui.QMessageBox.Yes,"Allow (%d secs)" % self.timeout_left)

    def event(self, event):
        """
        Descript. :
        """
        if self.isRunning():
            if event.type() == WANTS_CONTROL_EVENT:
                try:
                    client_id=event.client_id
                except:
                    logging.getLogger().exception("Qt4_InstanceListBrick: problem in event!")
                else:
                    client_print=self.instance_server_hwobj.idPrettyPrint(client_id)
                    self.give_control_chboxDialog.nickname=client_print

                    self.give_control_chboxDialog.setButtonText(QtGui.QMessageBox.Yes,"Allow (%d secs)" % self.timeout_left)
                    self.give_control_chboxDialog.setButtonText(QtGui.QMessageBox.No,"Deny")
                    s=self.font().pointSize()
                    f=self.give_control_chboxDialog.font()
                    f.setPointSize(s)
                    self.give_control_chboxDialog.setFont(f)
                    self.give_control_chboxDialog.updateGeometry()
                    self.timeout_timer.start(1000)
                    res=self.give_control_chboxDialog.exec_loop()
                    self.timeout_timer.stop()
                    if res==QtGui.QMessageBox.Yes:
                        self.instance_server_hwobj.giveControl(client_id)
                    else:
                        self.instance_server_hwobj.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_HIGH,"Control denied for %s!" % client_print)
                    self.give_control_chboxDialog=None

            elif event.type() == START_SERVER_EVENT:
                if self.instance_server_hwobj is not None:
                    self.instance_server_hwobj.initializeInstance()

            elif event.type() == APP_BRICK_EVENT:
                self.instance_server_hwobj.sendBrickUpdateMessage(event.brick_name,event.widget_name,event.method_name,event.method_args,event.masterSync)

            elif event.type() == APP_TAB_EVENT:
                self.instance_server_hwobj.sendTabUpdateMessage(event.tab_name,event.tab_index)

            elif event.type() == MSG_DIALOG_EVENT:
                msg_dialog = QtGui.QMessageBox("mxCuBE",\
                    event.msg, event.icon_type, QtGui.QMessageBox.Ok,\
                    QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton, 
                    self)  # Application name (mxCuBE) is hardwired!!!
                msg_dialog.exec_()
                if callable(event.callback):
                    event.callback()

            elif event.type() == USER_INFO_DIALOG_EVENT:
                if event.is_local or event.toaddrs=="":
                    msg_dialog = QtGui.QMessageBox("mxCuBE",\
                        event.msg, QtGui.QMessageBox.Information, QtGui.QMessageBox.Ok,\
                        QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton, None)  # Application name (mxCuBE) is hardwired!!!
                else:
                    self.externalUserInfoDialog.setMessage(event.msg)
                    msg_dialog=self.externalUserInfoDialog
                while True:
                    msg_dialog.exec_loop()
                    if event.is_local or event.toaddrs=="":
                        break
                    else:
                        if msg_dialog.result()==QtGui.QDialog.Accepted:
                            break

                if event.toaddrs!="":
                    if event.is_local:
                        email_body=""
                    else:
                        user_info=msg_dialog.getUserInfo()
                        if user_info["usersInESRF"] is True:
                            users_in_esrf="yes"
                        elif user_info["usersInESRF"] is False:
                            users_in_esrf="no"
                        else:
                            users_in_esrf="not sure..."
                        email_body="User name    : %s\nInstitute    : %s\nTelephone    : %s\nEmail address: %s\nUsers at ESRF: %s" % (\
                            user_info["name"],\
                            user_info["institute"],\
                            user_info["phone"],\
                            user_info["email"],\
                            users_in_esrf,\
                            )

                    email_date = email.Utils.formatdate(localtime=True)
                    toaddrs=event.toaddrs.replace(' ', ',')
                    email_message = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                        event.fromaddrs, 
                        toaddrs,
                        event.subject,
                        email_date,
                        email_body)
                    logging.getLogger().debug("Sending email from %s to %s" % (event.fromaddrs,toaddrs))
                    try:
                        smtp = smtplib.SMTP('smtp',smtplib.SMTP_PORT)
                        smtp.sendmail(event.fromaddrs, toaddrs.split(','), email_message)
                    except smtplib.SMTPException, e:
                        logging.getLogger().error("Could not send mail: %s" % str(e))
                        smtp.quit()
                    else:
                        smtp.quit()
        return QtGui.QWidget.event(self, event)

    def wantsControl(self,client_id):
        """
        Descript. :
        """
        if BlissWidget.isInstanceModeMaster() and self.give_control_chboxDialog is None and self.allow_timeout_control_chbox.isChecked():
            self.timeout_left=self['giveControlTimeout']
            client_print=self.instance_server_hwobj.idPrettyPrint(client_id)
            self.give_control_chboxDialog=QtGui.QMessageBox("Pass control",\
                "The user %s wants to have control of the application!" % client_print,\
                QtGui.QMessageBox.Question, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No,\
                QtGui.QMessageBox.NoButton,self)
            custom_event=WantsControlEvent(client_id)
            QtGui.QApplication.postEvent(self,custom_event)


class LineEditInput(QtGui.QLineEdit):
    """
    Descript: Single-line input field. Changes color depending on the validity
              of the input: red for invalid (or whatever DataCollectBrick2.
                                PARAMETER_STATE["INVALID"] has)
                            white for valid (or whatever DataCollectBrick2.
                                PARAMETER_STATE["OK"]).
    Type       : class (qt.QtGui.QLineEdit)
    API        : setReadOnly(readonly<bool>)
                 <string> text()
    Signals    : returnPressed(), inputValid(valid<bool>), textChanged(txt<string>)
    Notes      : Returns 1/3 of the width in the sizeHint from QtGui.QLineEdit
    """

    PARAMETER_STATE={"INVALID" : QtCore.Qt.red,\
                     "OK" : QtCore.Qt.white,\
                     "WARNING" : QtCore.Qt.yellow}
    
    def __init__(self, parent):
        """
        Descript. :
        """
        QtGui.QLineEdit.__init__(self, parent)
        QtCore.QObject.connect(self, QtCore.SIGNAL('textChanged(const QString &)'), self.txtChanged)
        QtCore.QObject.connect(self, QtCore.SIGNAL('returnPressed()'), self.retPressed)
        self.colorDefault=None
        self.origPalette=QtGui.QPalette(self.palette())
        self.palette2=QtGui.QPalette(self.origPalette)
        self.palette2.setColor(QtGui.QPalette.Active, 
                               QtGui.QPalette.Base, 
                               self.origPalette.brush(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.Background).color())
        self.palette2.setColor(QtGui.QPalette.Inactive, 
                               QtGui.QPalette.Base,
                               self.origPalette.brush(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.Background).color())
        self.palette2.setColor(QtGui.QPalette.Disabled, 
                               QtGui.QPalette.Base,
                               self.origPalette.brush(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.Background).color())

    def retPressed(self):
        """
        Descript. :
        """
        if self.validator() is not None:
            if self.hasAcceptableInput():
                self.emit(QtCore.SIGNAL("returnPressed"))
        else:
            self.emit(QtCore.SIGNAL("returnPressed"))

    def text(self):
        """
        Descript. :
        """
        return str(QtGui.QLineEdit.text(self))

    def txtChanged(self,txt):
        """
        Descript. :
        """
        txt=str(txt)
        valid=None
        if self.validator() is not None:
            if self.hasAcceptableInput():
                valid=True
                if txt=="":
                    if self.colorDefault is None:
                        color=LineEditInput.PARAMETER_STATE["OK"]
                    else:
                        color=self.colorDefault
                else:
                    color=LineEditInput.PARAMETER_STATE["OK"]
            else:
                if txt=="":
                    if self.colorDefault is None:
                        valid=False
                        color=LineEditInput.PARAMETER_STATE["INVALID"]
                    else:
                        color=self.colorDefault
                else:
                    valid=False
                    color=LineEditInput.PARAMETER_STATE["INVALID"]
            self.setPaletteBackgroundColor(color)
        else:
            if txt=="":
                if self.colorDefault is None:
                    if self.isReadOnly():
                        color=self.origBackgroundColor()
                    else:
                        color=LineEditInput.PARAMETER_STATE["OK"]
                else:
                    color=self.colorDefault
            else:
                #color=DataCollectBrick2.PARAMETER_STATE["OK"]
                if self.isReadOnly():
                    color=self.origBackgroundColor()
                else:
                    color=LineEditInput.PARAMETER_STATE["OK"]
            self.setPaletteBackgroundColor(color)
        self.emit(QtCore.SIGNAL("textChanged"), txt)
        if valid is not None:
            self.emit(QtCore.SIGNAL("inputValid"), self, valid)

    def sizeHint(self):
        """
        Descript. :
        """
        size_hint=QtGui.QLineEdit.sizeHint(self)
        size_hint.setWidth(size_hint.width()/3)
        return size_hint
                
    def setReadOnly(self,readonly):
        """
        Descript. :
        """
        if readonly:
            self.setPalette(self.palette2)
        else:
            self.setPalette(self.origPalette)
        QtGui.QLineEdit.setReadOnly(self,readonly)       
 
    def origBackgroundColor(self):
        """
        Descript. :
        """
        return self.origPalette.disabled().background()

    def setDefaultColor(self,color=None):
        """
        Descript. :
        """
        self.colorDefault=color
        self.txtChanged(self.text())


class NickEditInput(LineEditInput):
    def txtChanged(self,txt):
        """
        Descript. :
        """
        txt=str(txt)
        valid=None
        if self.validator() is not None:
            if self.hasAcceptableInput():
                valid=True
                Qt4_widget_colors.set_widget_color(self,
                                           LineEditInput.PARAMETER_STATE["WARNING"],
                                           QtGui.QPalette.Base)
            else:
                valid=False
                Qt4_widget_colors.set_widget_color(self,
                                           LineEditInput.PARAMETER_STATE["INVALID"],
                                           QtGui.QPalette.Base)
        self.emit(QtCore.SIGNAL("textChanged"), txt)
        if valid is not None:
            self.emit(QtCore.SIGNAL("inputValid"), self, valid)

    def acceptInput(self):
        """
        Descript. :
        """
        Qt4_widget_colors.set_widget_color(self, 
                                           LineEditInput.PARAMETER_STATE["OK"],
                                           QtGui.QPalette.Base)

class ExternalUserInfoDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self,None)
        self.setWindowTitle('mxCuBE')  # Application name (mxCuBE) is hardwired!!!

        return

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.messageBox = QtGui.QGroupBox("Your info",self) #v
        self.message1 = QtGui.QLabel(self.messageBox)
        self.message1.setAlignment(QtGui.Qt.AlignCenter)
        self.message2 = QtGui.QLabel("<nobr>Please enter the following information, <u>required</u> for the experimental hall operator:",self.messageBox)

        my_name_widget = QtGui.QWidget(self.messageBox)
        #QtGui.QGridLayout(my_name_widget, 2, 5, 1, 1)

        name_label = QtGui.QLabel("Your name:",my_name_widget)
        #my_name_widget.layout().addWidget(name_label, 0, 0)
        self.nameInput = QtGui.QLineEdit(my_name_widget)
        #my_name_widget.layout().addWidget(self.nameInput,0,1)

        institute_label=QtGui.QLabel("Your institute:",my_name_widget)
        my_name_widget.layout().addWidget(institute_label, 1, 0)
        self.instituteInput=QtGui.QLineEdit(my_name_widget)
        my_name_widget.layout().addWidget(self.instituteInput,1,1)

        phone_label=QtGui.QLabel("Your telephone:",my_name_widget)
        my_name_widget.layout().addWidget(phone_label, 2, 0)
        self.phoneInput=QtGui.QLineEdit(my_name_widget)
        my_name_widget.layout().addWidget(self.phoneInput,2,1)

        email_label=QtGui.QLabel("Your email:",my_name_widget)
        my_name_widget.layout().addWidget(email_label, 3, 0)
        self.emailInput=QtGui.QLineEdit(my_name_widget)
        my_name_widget.layout().addWidget(self.emailInput,3,1)

        box2=QtGui.QHBox(my_name_widget)
        QtGui.QLabel("Are there users at the ESRF?",box2)
        self.radioBox=QtGui.QHButtonGroup(box2)
        self.radioBox.setFrameShape(self.radioBox.NoFrame)
        self.radioBox.setInsideMargin(0)
        self.radioBox.setInsideSpacing(0)            
        self.yesBox = QtGui.QRadioButton("Yes",self.radioBox)
        self.noBox = QtGui.QRadioButton("No",self.radioBox)

        self.buttonsBox = DialogButtonsBar(self, "Continue", None, None, 
              self.buttonClicked, 0, DialogButtonsBar.DEFAULT_SPACING)

        # Layout --------------------------------------------------------------

        # SizePolicies --------------------------------------------------------
        self.messageBox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                                      QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.messageBox)
        main_layout.addWidget(box2)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.buttonsBox)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.nameInput.textChanged.connect(self.validateParameters)
        self.instituteInput.textChanged.connect(self.validateParameters)
        self.phoneInput.textChanged.connect(self.validateParameters)
        self.emailInput.textChanged.connect(self.validateParameters)
  

    def exec_loop(self):
        self.validateParameters()
        return QtGui.QDialog.exec_loop(self)

    def validateParameters(self):
        if len(str(self.nameInput.text())) and len(str(self.instituteInput.text())) and\
            len(str(self.phoneInput.text())) and len(str(self.emailInput.text())):
            self.buttonsBox.setEnabled(True)
        else:
            self.buttonsBox.setEnabled(False)

    def buttonClicked(self,text):
        self.accept()

    def setMessage(self,msg):
        self.message1.setText("<b>%s</b>" % msg)

    def clearUserInfo(self):
        self.nameInput.setText("")
        self.instituteInput.setText("")
        self.phoneInput.setText("")
        self.emailInput.setText("")
        self.yesBox.setChecked(False)
        self.noBox.setChecked(False)
        
    def getUserInfo(self):
        if self.radioBox.selectedId()==0:
            users_in_esrf=True
        elif self.radioBox.selectedId()==1:
            users_in_esrf=False
        else:
            users_in_esrf=None
        user_info_dict={"name":str(self.nameInput.text()),\
            "institute":str(self.instituteInput.text()),\
            "phone":str(self.phoneInput.text()),\
            "email":str(self.emailInput.text()),\
            "usersInESRF":users_in_esrf}
        return user_info_dict
