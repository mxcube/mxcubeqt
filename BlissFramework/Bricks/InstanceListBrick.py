from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import BaseComponents 
from BlissFramework import Icons
import BlissFramework
import qt
from qt import *
import logging
#import DataCollectBrick2
import InstanceServer
import gevent
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
import email.Utils
import smtplib
import os
from HardwareRepository.HardwareRepository import dispatcher


__category__ = "mxCuBE"

WANTS_CONTROL_EVENT = QEvent.User
class WantsControlEvent(QCustomEvent):
    def __init__(self, client_id):
        QCustomEvent.__init__(self, WANTS_CONTROL_EVENT)
        self.client_id = client_id

START_SERVER_EVENT = QEvent.User+1
class StartServerEvent(QCustomEvent):
    def __init__(self):
        QCustomEvent.__init__(self, START_SERVER_EVENT)

APP_BRICK_EVENT = QEvent.User+2
class AppBrickEvent(QCustomEvent):
    def __init__(self,brick_name,widget_name,method_name,method_args,masterSync):
        QCustomEvent.__init__(self, APP_BRICK_EVENT)
        self.brick_name=brick_name
        self.widget_name=widget_name
        self.method_name=method_name
        self.method_args=method_args
        self.masterSync=masterSync

APP_TAB_EVENT = QEvent.User+3
class AppTabEvent(QCustomEvent):
    def __init__(self,tab_name,tab_index):
        QCustomEvent.__init__(self, APP_TAB_EVENT)
        self.tab_name=tab_name
        self.tab_index=tab_index

MSG_DIALOG_EVENT = QEvent.User+4
class MsgDialogEvent(QCustomEvent):
    def __init__(self,icon_type,msg,font_size,callback=None):
        QCustomEvent.__init__(self, MSG_DIALOG_EVENT)
        self.icon_type=icon_type
        self.msg=msg
        self.font_size=font_size
        self.callback=callback

USER_INFO_DIALOG_EVENT = QEvent.User+5
class UserInfoDialogEvent(QCustomEvent):
    def __init__(self,msg,fromaddrs,toaddrs,subject,is_local,font_size):
        QCustomEvent.__init__(self, USER_INFO_DIALOG_EVENT)
        self.msg=msg
        self.fromaddrs=fromaddrs
        self.toaddrs=toaddrs
        self.is_local=is_local
        self.subject=subject
        self.font_size=font_size

class InstanceListBrick(BlissWidget):
    LOCATIONS=("UNKNOWN","LOCAL","INHOUSE","INSITE","EXTERNAL")
    MODES=("UNKNOWN","MASTER","SLAVE")
    ROLES=("UNKNOWN","ACTING_AS_SERVER","LAUNCHING_SERVER","ACTING_AS_CLIENT","CONNECTING_TO_SERVER")
    IDS=("UNKNOWN","USER","INHOUSE_USER","INHOUSE_IMPERSONATION")
    RECONNECT_TIME=5000

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty("mnemonic", "string", "")
        self.addProperty("xmlrpc_server", "string", "/xml-rpc-server")
        self.addProperty("icons", "string", "")
        self.addProperty("giveControlTimeout", "integer", 30)
        self.addProperty("initializeServer", "boolean", False)
        self.addProperty("controlEmails", "string", "")
        self.addProperty("hutchtrigger", "string", "") 

        self.defineSlot('setSession',())

        self.instanceServer = None
        self.hutchtrigger = None
        self.xmlrpc_server = None

        self.giveControlDialog=None
        self.timeoutLeft=-1
        self.myProposal=None
        self.inControl=None

        self.containerBox=QVGroupBox("Current users",self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.containerBox.setAlignment(QLabel.AlignCenter)

        self.listBox=QListBox(self.containerBox)
        #QObject.connect(self.listBox,SIGNAL('clicked(QListBoxItem *)'), self.giveControlTo)
        QObject.connect(self.listBox,SIGNAL('pressed(QListBoxItem *)'), self.giveControlTo)
        self.connections={}
        self.listBox.setSelectionMode(QListBox.NoSelection)
        self.listBox.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed)

        self.controlBox=QVBox(self.containerBox)
        self.giveControl=QCheckBox("Selecting gives control",self.controlBox)
        self.allowTimeoutControl=QCheckBox("Allow timeout control",self.controlBox)
        self.giveControl.setChecked(False)
        self.allowTimeoutControl.setChecked(False)

        self.takeControlButton = QToolButton(self.containerBox)
        self.takeControlButton.setUsesTextLabel(True)
        self.takeControlButton.setTextLabel("Take control")
        self.takeControlButton.setEnabled(True)
        self.takeControlButton.hide()
        QObject.connect(self.takeControlButton, SIGNAL('clicked()'), self.takeControlClicked)

        self.askForControlButton = QToolButton(self.containerBox)
        self.askForControlButton.setUsesTextLabel(True)
        self.askForControlButton.setTextLabel("Ask for control")
        self.askForControlButton.setEnabled(False)
        QObject.connect(self.askForControlButton, SIGNAL('clicked()'), self.askForControlClicked)

        box1=QHBox(self.containerBox)
        QLabel("My name:",box1)
        self.nickname=NickEditInput(box1)
        self.connect(self.nickname,PYSIGNAL('returnPressed'), self.changeMyName)

        reg=QRegExp(".+")
        nick_validator=QRegExpValidator(reg,self.nickname)
        self.nickname.setValidator(nick_validator)

        self.clientIcon=None
        self.serverIcon=None

        self.externalUserInfoDialog=ExternalUserInfoDialog()

        self.timeoutTimer=QTimer(self)
        QObject.connect(self.timeoutTimer,SIGNAL('timeout()'),self.timeoutApproaching)

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer,PYSIGNAL('instanceInitializing'),self.instanceInitializing)
                self.disconnect(self.instanceServer,PYSIGNAL('serverInitialized'),self.serverInitialized)
                self.disconnect(self.instanceServer,PYSIGNAL('clientInitialized'),self.clientInitialized)
                self.disconnect(self.instanceServer,PYSIGNAL('serverClosed'),self.serverClosed)
                self.disconnect(self.instanceServer,PYSIGNAL('newClient'), self.newClient)
                self.disconnect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
                self.disconnect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.disconnect(self.instanceServer,PYSIGNAL('wantsControl'), self.wantsControl)
                self.disconnect(self.instanceServer,PYSIGNAL('widgetUpdate'), self.widgetUpdate)
                self.disconnect(self.instanceServer,PYSIGNAL('clientChanged'), self.clientChanged)
                self.disconnect(self.instanceServer,PYSIGNAL('clientClosed'), self.clientClosed)
                self.disconnect(self.instanceServer,PYSIGNAL('widgetCall'), self.widgetCall)

            self.instanceServer = self.getHardwareObject(newValue)
            if self.instanceServer is not None:
                self.connect(self.instanceServer,PYSIGNAL('instanceInitializing'),self.instanceInitializing)
                self.connect(self.instanceServer,PYSIGNAL('serverInitialized'),self.serverInitialized)
                self.connect(self.instanceServer,PYSIGNAL('clientInitialized'),self.clientInitialized)
                self.connect(self.instanceServer,PYSIGNAL('serverClosed'),self.serverClosed)
                self.connect(self.instanceServer,PYSIGNAL('newClient'), self.newClient)
                self.connect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
                self.connect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.connect(self.instanceServer,PYSIGNAL('wantsControl'), self.wantsControl)
                self.connect(self.instanceServer,PYSIGNAL('widgetUpdate'), self.widgetUpdate)
                self.connect(self.instanceServer,PYSIGNAL('clientChanged'), self.clientChanged)
                self.connect(self.instanceServer,PYSIGNAL('clientClosed'), self.clientClosed)
                self.connect(self.instanceServer,PYSIGNAL('widgetCall'), self.widgetCall)
        elif propertyName=="xmlrpc_server":
            self.xmlrpc_server = self.getHardwareObject(newValue)
        elif propertyName == 'hutchtrigger':
            self.hutchtrigger = self.getHardwareObject(newValue)
            if self.hutchtrigger is not None:
                self.connect(self.hutchtrigger, PYSIGNAL("hutchTrigger"), self.hutchTriggerChanged) 
        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.serverIcon=Icons.load(icons_list[0])
            except IndexError:
                pass
            try:
                self.clientIcon=Icons.load(icons_list[1])
            except IndexError:
                pass                
            try:
                self.takeControlButton.setPixmap(Icons.load(icons_list[2]))
            except IndexError:
                pass
            try:
                self.askForControlButton.setPixmap(Icons.load(icons_list[3]))
            except IndexError:
                pass
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def hutchTriggerChanged(self, hutch_opened):
        if hutch_opened:
            if not BlissWidget.isInstanceRoleServer():
              logging.getLogger().info("%s: HUTCH IS OPENED, YOU LOSE CONTROL", self.name())
              self.takeControlButton.setEnabled(False)
            else:
              logging.getLogger().info("%s: HUTCH IS OPENED, TAKING CONTROL OVER REMOTE USERS", self.name())
              self.instanceServer.takeControl()
        else:
            if not BlissWidget.isInstanceRoleServer():
              logging.getLogger().info("%s: HUTCH IS CLOSED, YOU ARE ALLOWED TO TAKE CONTROL AGAIN", self.name())
              self.takeControlButton.setEnabled(True) 


    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration=None,orig_prop_code=None,is_inhouse=None):
        self.externalUserInfoDialog.clearUserInfo()

        if prop_code is not None and prop_number is not None and prop_code!='' and prop_number!='':
            if self.instanceServer is not None:
                try:
                    proposal_dict={ "code":orig_prop_code,\
                        "alias": prop_code,\
                        "number":prop_number,\
                        "session":int(session_id),\
                        "inhouse":is_inhouse }
                except:
                    logging.getLogger().exception("InstanceListBrick: problem setting session")
                    return
                else:
                    self.myProposal=proposal_dict
                    self.instanceServer.setProposal(proposal_dict)

            if is_inhouse:
                BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_INHOUSE)
                self.askForControlButton.hide()
                self.takeControlButton.show()
                self.takeControlButton.setEnabled(BlissWidget.isInstanceRoleServer()) #BlissWidget.isInstanceModeMaster())
                if self.hutchtrigger is not None and not BlissWidget.isInstanceModeMaster():
                    hutch_opened = self.hutchtrigger.hutchIsOpened()
                    #hutch_opened = 1-int(self.hutchtrigger.getChannelObject("status").getValue())
                    logging.getLogger().info("%s: hutch is %s, %s 'Take control' button", self.name(), hutch_opened and "opened" or "close", hutch_opened and "disabling" or "enabling")
                    self.takeControlButton.setEnabled(1-hutch_opened)
            else:
                BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_LOGGED)
                self.takeControlButton.hide()
                self.askForControlButton.show()
                self.askForControlButton.setEnabled(not BlissWidget.isInstanceModeMaster())
        else:
            if self.instanceServer is not None:
                self.myProposal=None
                self.instanceServer.setProposal(None)

            BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_UNKNOWN)
            self.takeControlButton.hide()
            self.askForControlButton.show()
            #self.askForControlButton.setEnabled(BlissWidget.isInstanceRoleServer() and not BlissWidget.isInstanceModeMaster())
            self.askForControlButton.setEnabled(False)

    def reconnectToServer(self):
        self.instanceServer.reconnect(quiet=True)

    def instanceInitializing(self):
        is_local=self.instanceServer.isLocal()
        if is_local:
            loc=BlissWidget.INSTANCE_LOCATION_LOCAL
        else:
            loc=BlissWidget.INSTANCE_LOCATION_EXTERNAL
        BlissWidget.setInstanceLocation(loc)

        self.connect(qApp.mainWidget(), PYSIGNAL('applicationBrickChanged'), self.applicationBrickChanged)
        self.connect(qApp.mainWidget(), PYSIGNAL('applicationTabChanged'), self.applicationTabChanged)

    def clientInitialized(self,connected,server_id=None,my_nickname=None,quiet=False):
        if connected is None:
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)
        elif not connected:
            if not quiet:
                msg_event=MsgDialogEvent(QMessageBox.Warning,\
                    "Couldn't connect to the server application!",\
                    self.font().pointSize())
                qApp.postEvent(self,msg_event)
                
            QTimer.singleShot(InstanceListBrick.RECONNECT_TIME,self.reconnectToServer)
        else:
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENT)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)

            server_print=self.instanceServer.idPrettyPrint(server_id)

            if self.clientIcon is None:
                item=QListBoxText(self.listBox,server_print)
            else:
                item=QListBoxPixmap(self.listBox,self.serverIcon,server_print)
            self.nickname.setText(my_nickname)
            self.connections[server_id[0]]=(item,server_id[1])
            item.setSelectable(False)
            self.haveControl(False,gui_only=True)
            self.initName(my_nickname)
            #self.giveControl.setChecked(False)

            # workaround for the remote access problem
            # (have to disable video display when DC is running)
            camera_brick = None

            for w in qt.QApplication.allWidgets():
                if isinstance(w, BaseComponents.BlissWidget):
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

            msg_event=MsgDialogEvent(QMessageBox.Information,\
                "Successfully connected to the server application.",\
                self.font().pointSize())
            qApp.postEvent(self,msg_event)

    def serverInitialized(self,started,server_id=None):
        if started:
            #BlissWidget.setInstanceUserId(BlissWidget.INSTANCE_USERID_UNKNOWN)
            BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_SERVER)
            BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)

            self.initName(server_id[0])
            self.haveControl(True,gui_only=True)
            #self.giveControl.setChecked(False)
            #self.allowTimeoutControl.setChecked(False)
        else:
            #BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_SERVERSTARTING)
            #BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)
            msg_dialog=QMessageBox("mxCuBE",\
                "Couldn't start the multiple instances server!",\
                QMessageBox.Critical,QMessageBox.Ok,QMessageBox.NoButton,\
                QMessageBox.NoButton,self) # Application name (mxCuBE) is hardwired!!!
            msg_dialog.setButtonText(QMessageBox.Ok,"Quit")
            s=self.font().pointSize()
            f=msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.exec_loop()
            os._exit(1)

    def serverClosed(self,server_id):
        self.listBox.clear()
        self.connections={}
        BlissWidget.setInstanceRole(BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING)
        BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)
        msg_event=MsgDialogEvent(QMessageBox.Warning,\
            "The server application closed the connection!",\
            self.font().pointSize())
        qApp.postEvent(self,msg_event)
        QTimer.singleShot(InstanceListBrick.RECONNECT_TIME,self.reconnectToServer)

    def widgetUpdate(self,timestamp,method,method_args,masterSync=True):
        #logging.getLogger().debug("widgetUpdate %s %r %r", timestamp, method, method_args)
        if self.instanceServer.isServer():
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
        try:
            method(*method_args)
        except:
            logging.getLogger().debug("InstanceListBrick: problem executing an external call")

    def instanceLocationChanged(self,loc):
        logging.getLogger().info("Instance running in %s" % InstanceListBrick.LOCATIONS[loc].lower())

    def instanceModeChanged(self,mode):
        logging.getLogger().info("Instance mode set to %s" % InstanceListBrick.MODES[mode].lower())
        self.updateMirroring()

    def applicationTabChanged(self,tab_name,tab_index):
        if self.instanceServer is not None:
            tab_event=AppTabEvent(tab_name,tab_index)
            qApp.postEvent(self,tab_event)

    def applicationBrickChanged(self,brick_name,widget_name,method_name,method_args,masterSync):
        if not masterSync or self.instanceServer is not None:
            brick_event=AppBrickEvent(brick_name,widget_name,method_name,method_args,masterSync)
            qApp.postEvent(self,brick_event)

    def initName(self,new_name):
        self.nickname.setText(new_name)
        self.nickname.acceptInput()

    def changeMyName(self):
        self.nickname.setEnabled(False)
        name=str(self.nickname.text())
        self.instanceServer.requestIdChange(name)

    def askForControlClicked(self):
        self.instanceServer.askForControl()

    def takeControlClicked(self):
        current_user=self.instanceServer.inControl()
        user_id=current_user[0]
        user_prop=current_user[1]
        control_user_print=self.instanceServer.idPrettyPrint(current_user)
        take_control_dialog=QMessageBox("mxCuBE",\
            "You're about to take control of the application, taking over %s!" % control_user_print,\
            QMessageBox.Question,QMessageBox.Ok,QMessageBox.Cancel,\
            QMessageBox.NoButton,self) # Application name (mxCuBE) is hardwired!!!
        take_control_dialog.setButtonText(QMessageBox.Ok,"Take control")
        s=self.font().pointSize()
        f=take_control_dialog.font()
        f.setPointSize(s)
        take_control_dialog.setFont(f)
        take_control_dialog.updateGeometry()
        if take_control_dialog.exec_loop()==QMessageBox.Ok:
            self.instanceServer.takeControl()

    def run(self):
        if self['initializeServer']:
            start_server_event=StartServerEvent()
            qApp.postEvent(self,start_server_event)
        
    def instanceUserIdChanged(self,userid):
        logging.getLogger().info("Instance user identification is %s" % InstanceListBrick.IDS[userid].replace("_"," ").lower())
        self.updateMirroring()

    def instanceRoleChanged(self,role):
        logging.getLogger().info("Instance role is %s" % InstanceListBrick.ROLES[role].replace("_"," ").lower())
        if role!=BlissWidget.INSTANCE_ROLE_UNKNOWN and not self.isShown():
            self.show()

    def newClient(self,client_id):
        #print "InstanceListBrick.newClient",client_id,self.connections

        client_print=self.instanceServer.idPrettyPrint(client_id)

        if self.clientIcon is None:
            item=QListBoxText(self.listBox,client_print)
        else:
            item=QListBoxPixmap(self.listBox,self.clientIcon,client_print)
        item.setSelectable(False)
        self.connections[client_id[0]]=(item,client_id[1])

    def clientClosed(self,client_id):
        #print "InstanceListBrick.clientClosed",client_id,self.connections
        try:
            item=self.connections[client_id[0]][0]
        except KeyError:
            logging.getLogger().warning('InstanceListBrick: unknown client has closed (%s)' % str(client_id))
        else:
            self.connections.pop(client_id[0])
            self.listBox.takeItem(item)

    def clientChanged(self,old_client_id,new_client_id):
        #print "CLIENT CHANGED",old_client_id,new_client_id

        try:
            item=self.connections[old_client_id[0]][0]
        except KeyError:
            self.nickname.setText(new_client_id[0])
            self.nickname.setEnabled(True)
            self.nickname.acceptInput()
        else:
            new_client_print=self.instanceServer.idPrettyPrint(new_client_id)
            item.setText(new_client_print)
            if new_client_id[0]!=old_client_id[0]:
                self.connections[new_client_id[0]]=self.connections[old_client_id[0]]
                self.connections.pop(old_client_id[0])
                if self.inControl is not None and old_client_id[0]==self.inControl[0]:
                    self.inControl[0]=new_client_id[0]
            else:
                if self.inControl is not None and old_client_id[0]==self.inControl[0]:
                    self.inControl[1]=new_client_id[1]
                    self.updateMirroring()
            self.listBox.updateItem(item)

    def giveControlTo(self,item):
        if item is None:
            return
        #print "GIVE CONTROL",item.text(),BlissWidget.isInstanceModeMaster(),self.giveControl.isChecked(),self.connections
        if BlissWidget.isInstanceModeMaster() and self.giveControl.isChecked():
            for user_id in self.connections:
                if self.connections[user_id][0]==item:
                    self.instanceServer.giveControl((user_id,self.connections[user_id][1]))
                    break

    def haveControl(self,have_control,gui_only=False):
        #print "INSTANCELISTBRICK.HAVECONTROL",have_control,gui_only
        if not gui_only:
            if have_control:
                BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_MASTER)
            else:
                BlissWidget.setInstanceMode(BlissWidget.INSTANCE_MODE_SLAVE)

        if have_control:
            if self.xmlrpc_server:
              gevent.spawn_later(1, self.xmlrpc_server.open)

            self.inControl=None
            self.takeControlButton.setEnabled(False)
            self.askForControlButton.setEnabled(False)

            self.listBox.setSelectionMode(QListBox.Single)
            self.listBox.clearSelection()
            i=self.listBox.firstItem()
            while i is not None:
                i.setSelectable(False)
                i=i.next()
            self.listBox.setSelectionMode(QListBox.NoSelection)

        else:
            if self.xmlrpc_server:
                self.xmlrpc_server.close()

            if BlissWidget.isInstanceUserIdLogged():
                self.askForControlButton.setEnabled(True)
            elif BlissWidget.isInstanceUserIdInhouse():
                 if self.hutchtrigger is not None:
                    hutch_opened = self.hutchtrigger.hutchIsOpened()
                    #hutch_opened = 1-int(self.hutchtrigger.getChannelObject("status").getValue())
                    logging.getLogger().debug("%s: hutch is %s, %s 'Take control' button", self.name(), hutch_opened and "opened" or "close", hutch_opened and "disabling" or "enabling")
                    self.takeControlButton.setEnabled(1-hutch_opened)
            #elif BlissWidget.isInstanceRoleServer():
            #    self.askForControlButton.setEnabled(True)
            if BlissWidget.isInstanceRoleServer():
                 self.takeControlButton.setEnabled(True)

        if not gui_only:
            if have_control:
                try:
                    frombl = os.environ['SMIS_BEAMLINE_NAME']
                    #user = os.environ['SMIS_BEAMLINE_NAME']
                    #frombl = user.replace(' ','-')
                except (KeyError,TypeError,ValueError,AttributeError):
                    frombl = 'ID??'

                try:
                    proposal="%s-%d" % (self.myProposal["code"],self.myProposal["number"])
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
                #qApp.postEvent(self,msg_event)
            else:
                msg_event=MsgDialogEvent(QMessageBox.Warning,\
                    "I've lost control of the application!",\
                    self.font().pointSize())
                logging.getLogger('user_level_log').warning("You have lost control of the application!")
                #qApp.postEvent(self,msg_event)

    def passControl(self,has_control_id):
        #print "InstanceListBrick.passControl",has_control_id,self.connections

        try:
            control_item=self.connections[has_control_id[0]][0]
        except KeyError:
            pass
        else:
            self.listBox.clearSelection()
            i=self.listBox.firstItem()
            while i is not None:
                i.setSelectable(False)
                i=i.next()

            #print "SELECTING",control_item,control_item.text()
            self.listBox.setSelectionMode(QListBox.Single)
            control_item.setSelectable(True)
            self.listBox.setSelected(control_item,True)
            self.listBox.setSelectionMode(QListBox.NoSelection)
            
            self.inControl=list(has_control_id)
            
            self.updateMirroring()

    def updateMirroring(self):
        #print "UPDATE MIRRORING",self.myProposal,self.inControl

        if BlissWidget.isInstanceModeSlave():
            if BlissWidget.isInstanceUserIdUnknown():
                if BlissWidget.isInstanceRoleServer() and self.inControl is not None and self.inControl[1] is None:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
                else:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_PREVENT)
            elif BlissWidget.isInstanceUserIdInhouse():
                BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
            else:
                try:
                    control_is_inhouse=self.inControl[1]['inhouse']
                except:
                    control_is_inhouse=False
                if control_is_inhouse or self.inControl[1] is None:
                    BlissWidget.setInstanceMirror(BlissWidget.INSTANCE_MIRROR_ALLOW)
                else:
                    try:
                        my_prop_codes=[self.myProposal['code'],self.myProposal['alias']]
                    except:
                        my_prop_codes=[]
                    try:
                        control_prop_codes=[self.inControl[1]['code'],self.inControl[1]['alias']]
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
        if self.giveControlDialog is not None:
            if self.timeoutLeft in (30,20,10):
                self.instanceServer.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_LOW,"%s will have control in %d seconds..." % (self.giveControlDialog.nickname,self.timeoutLeft))
            self.timeoutLeft-=1
            if self.timeoutLeft==0:
                self.giveControlDialog.done(QMessageBox.Yes)
            else:
                self.giveControlDialog.setButtonText(QMessageBox.Yes,"Allow (%d secs)" % self.timeoutLeft)

    def customEvent(self,event):
        #logging.getLogger().debug("InstanceListBrick: custom event (%s)" % str(event))
        if self.isRunning():
            if event.type() == WANTS_CONTROL_EVENT:
                try:
                    client_id=event.client_id
                except:
                    logging.getLogger().exception("InstanceListBrick: problem in event!")
                else:
                    client_print=self.instanceServer.idPrettyPrint(client_id)
                    self.giveControlDialog.nickname=client_print

                    self.giveControlDialog.setButtonText(QMessageBox.Yes,"Allow (%d secs)" % self.timeoutLeft)
                    self.giveControlDialog.setButtonText(QMessageBox.No,"Deny")
                    s=self.font().pointSize()
                    f=self.giveControlDialog.font()
                    f.setPointSize(s)
                    self.giveControlDialog.setFont(f)
                    self.giveControlDialog.updateGeometry()
                    self.timeoutTimer.start(1000)
                    res=self.giveControlDialog.exec_loop()
                    self.timeoutTimer.stop()
                    if res==QMessageBox.Yes:
                        self.instanceServer.giveControl(client_id)
                    else:
                        self.instanceServer.sendChatMessage(InstanceServer.ChatInstanceMessage.PRIORITY_HIGH,"Control denied for %s!" % client_print)
                    self.giveControlDialog=None

            elif event.type() == START_SERVER_EVENT:
                if self.instanceServer is not None:
                    self.instanceServer.initializeInstance()

            elif event.type() == APP_BRICK_EVENT:
                self.instanceServer.sendBrickUpdateMessage(event.brick_name,event.widget_name,event.method_name,event.method_args,event.masterSync)

            elif event.type() == APP_TAB_EVENT:
                self.instanceServer.sendTabUpdateMessage(event.tab_name,event.tab_index)

            elif event.type() == MSG_DIALOG_EVENT:
                msg_dialog=QMessageBox("mxCuBE",\
                    event.msg,event.icon_type,QMessageBox.Ok,\
                    QMessageBox.NoButton,QMessageBox.NoButton,None)  # Application name (mxCuBE) is hardwired!!!
                f=msg_dialog.font()
                f.setPointSize(event.font_size)
                msg_dialog.setFont(f)
                msg_dialog.updateGeometry()
                msg_dialog.exec_loop()
                if callable(event.callback):
                    event.callback()

            elif event.type() == USER_INFO_DIALOG_EVENT:
                if event.is_local or event.toaddrs=="":
                    msg_dialog=QMessageBox("mxCuBE",\
                        event.msg,QMessageBox.Information,QMessageBox.Ok,\
                        QMessageBox.NoButton,QMessageBox.NoButton,None)  # Application name (mxCuBE) is hardwired!!!
                else:
                    self.externalUserInfoDialog.setMessage(event.msg)
                    msg_dialog=self.externalUserInfoDialog
                f=msg_dialog.font()
                f.setPointSize(event.font_size)
                msg_dialog.setFont(f)
                msg_dialog.updateGeometry()

                while True:
                    msg_dialog.exec_loop()
                    if event.is_local or event.toaddrs=="":
                        break
                    else:
                        if msg_dialog.result()==QDialog.Accepted:
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

    def wantsControl(self,client_id):
        #print "INSTANCE LIST BRICK WANTS CONTROL",client_id
        if BlissWidget.isInstanceModeMaster() and self.giveControlDialog is None and self.allowTimeoutControl.isChecked():
            self.timeoutLeft=self['giveControlTimeout']
            client_print=self.instanceServer.idPrettyPrint(client_id)
            self.giveControlDialog=QMessageBox("Pass control",\
                "The user %s wants to have control of the application!" % client_print,\
                QMessageBox.Question,QMessageBox.Yes,QMessageBox.No,\
                QMessageBox.NoButton,self)
            custom_event=WantsControlEvent(client_id)
            qApp.postEvent(self,custom_event)


"""
LineEditInput
    Description: Single-line input field. Changes color depending on the validity of the input:
                 red for invalid (or whatever DataCollectBrick2.PARAMETER_STATE["INVALID"] has)
                 and white for valid (or whatever DataCollectBrick2.PARAMETER_STATE["OK"]).
    Type       : class (qt.QLineEdit)
    API        : setReadOnly(readonly<bool>)
                 <string> text()
    Signals    : returnPressed(), inputValid(valid<bool>), textChanged(txt<string>)
    Notes      : Returns 1/3 of the width in the sizeHint from QLineEdit
"""
class LineEditInput(QLineEdit):

    PARAMETER_STATE={"INVALID":QWidget.red,\
                     "OK":QWidget.white,\
                     "WARNING":QWidget.yellow}
    
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        QObject.connect(self, SIGNAL('textChanged(const QString &)'), self.txtChanged)
        QObject.connect(self, SIGNAL('returnPressed()'), self.retPressed)
        self.colorDefault=None
        self.origPalette=QPalette(self.palette())
        self.palette2=QPalette(self.origPalette)
        self.palette2.setColor(QPalette.Active,QColorGroup.Base,self.origPalette.disabled().background())
        self.palette2.setColor(QPalette.Inactive,QColorGroup.Base,self.origPalette.disabled().background())
        self.palette2.setColor(QPalette.Disabled,QColorGroup.Base,self.origPalette.disabled().background())

    def retPressed(self):
        if self.validator() is not None:
            if self.hasAcceptableInput():
                self.emit(PYSIGNAL("returnPressed"),())
        else:
            self.emit(PYSIGNAL("returnPressed"),())

    def text(self):
        return str(QLineEdit.text(self))

    def txtChanged(self,txt):
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
        self.emit(PYSIGNAL("textChanged"),(txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"),(self,valid,))

    def sizeHint(self):
        size_hint=QLineEdit.sizeHint(self)
        size_hint.setWidth(size_hint.width()/3)
        return size_hint
                
    def setReadOnly(self,readonly):
        if readonly:
            self.setPalette(self.palette2)
        else:
            self.setPalette(self.origPalette)
        QLineEdit.setReadOnly(self,readonly)
        
    def origBackgroundColor(self):
        return self.origPalette.disabled().background()

    def setDefaultColor(self,color=None):
        self.colorDefault=color
        self.txtChanged(self.text())


class NickEditInput(LineEditInput):
    def txtChanged(self,txt):
        txt=str(txt)
        valid=None
        if self.validator() is not None:
            if self.hasAcceptableInput():
                valid=True
                self.setPaletteBackgroundColor(LineEditInput.PARAMETER_STATE["WARNING"])
            else:
                valid=False
                self.setPaletteBackgroundColor(LineEditInput.PARAMETER_STATE["INVALID"])
        self.emit(PYSIGNAL("textChanged"),(txt,))
        if valid is not None:
            self.emit(PYSIGNAL("inputValid"),(self,valid,))

    def acceptInput(self):
        self.setPaletteBackgroundColor(LineEditInput.PARAMETER_STATE["OK"])


class ExternalUserInfoDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self,None)
        self.setCaption('mxCuBE')  # Application name (mxCuBE) is hardwired!!!

        self.messageBox=QVGroupBox("Your info",self)
        self.message1=QLabel(self.messageBox)
        self.message1.setAlignment(Qt.AlignCenter)
        self.message2=QLabel("<nobr>Please enter the following information, <u>required</u> for the experimental hall operator:",self.messageBox)

        box1=QWidget(self.messageBox)
        QGridLayout(box1, 2, 5, 1, 1)

        name_label=QLabel("Your name:",box1)
        box1.layout().addWidget(name_label, 0, 0)
        self.nameInput=QLineEdit(box1)
        box1.layout().addWidget(self.nameInput,0,1)
        QObject.connect(self.nameInput,SIGNAL('textChanged(const QString &)'), self.validateParameters)

        institute_label=QLabel("Your institute:",box1)
        box1.layout().addWidget(institute_label, 1, 0)
        self.instituteInput=QLineEdit(box1)
        box1.layout().addWidget(self.instituteInput,1,1)
        QObject.connect(self.instituteInput,SIGNAL('textChanged(const QString &)'), self.validateParameters)

        phone_label=QLabel("Your telephone:",box1)
        box1.layout().addWidget(phone_label, 2, 0)
        self.phoneInput=QLineEdit(box1)
        box1.layout().addWidget(self.phoneInput,2,1)
        QObject.connect(self.phoneInput,SIGNAL('textChanged(const QString &)'), self.validateParameters)

        email_label=QLabel("Your email:",box1)
        box1.layout().addWidget(email_label, 3, 0)
        self.emailInput=QLineEdit(box1)
        box1.layout().addWidget(self.emailInput,3,1)
        QObject.connect(self.emailInput,SIGNAL('textChanged(const QString &)'), self.validateParameters)

        box2=QHBox(box1)
        QLabel("Are there users at the ESRF?",box2)
        self.radioBox=QHButtonGroup(box2)
        self.radioBox.setFrameShape(self.radioBox.NoFrame)
        self.radioBox.setInsideMargin(0)
        self.radioBox.setInsideSpacing(0)            
        self.yesBox=QRadioButton("Yes",self.radioBox)
        self.noBox=QRadioButton("No",self.radioBox)

        spacer=QWidget(box2)
        spacer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

        box1.layout().addMultiCellWidget(box2, 4, 4, 0, 1)

        self.buttonsBox=DialogButtonsBar(self,"Continue",None,None,self.buttonClicked,0,DialogButtonsBar.DEFAULT_SPACING)

        QVBoxLayout(self,DialogButtonsBar.DEFAULT_MARGIN,DialogButtonsBar.DEFAULT_SPACING)
        self.layout().addWidget(self.messageBox)
        self.layout().addWidget(box2)
        self.layout().addWidget(VerticalSpacer2(self))
        self.layout().addWidget(self.buttonsBox)

        self.messageBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

    def exec_loop(self):
        self.validateParameters()
        return QDialog.exec_loop(self)

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

class VerticalSpacer2(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
