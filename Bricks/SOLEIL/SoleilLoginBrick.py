from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *
import logging
import time
import os
from BlissFramework.Utils import widget_colors

__category__ = 'mxCuBE'

PROPOSAL_GUI_EVENT = QEvent.User
class ProposalGUIEvent(QCustomEvent):
    def __init__(self, method, arguments):
        QCustomEvent.__init__(self, PROPOSAL_GUI_EVENT)
        self.method = method
        self.arguments = arguments

###
### Brick to show the current proposal & session (and login/out the user)
###
class SoleilLoginBrick(BlissWidget):
    NOBODY_STR="<nobr><b>Login is required for collecting data!</b>"

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Initialize HO
        self.ldapConnection = None
        self.dbConnection   = None
        self.localLogin     = None
        self.session_hwobj  = None

        # Initialize session info
        self.proposal   = None
        self.session    = None
        self.person     = None
        self.laboratory = None

        #self.sessionId=None
        self.inhouseProposal=None

        self.instanceServer=None

        # Initialize properties
        self.addProperty('ldapServer','string','')
        self.addProperty('instanceServer','string','')
        self.addProperty('localLogin','string','')
        self.addProperty('titlePrefix','string','')
        self.addProperty('autoSessionUsers','string','')
        self.addProperty('codes','string','fx ifx ih im ix ls mx opid')
        self.addProperty('icons','string','')
        self.addProperty('serverStartDelay','integer',500)
        self.addProperty('dbConnection','string')
        self.addProperty('session', 'string', '/session')

        self.defineSignal('sessionSelected',())
        self.defineSignal('setWindowTitle',())
        self.defineSignal('loggedIn', ())
        self.defineSignal('user_group_saved', ())
        self.defineSlot('setButtonEnabled',())
        self.defineSlot('impersonateProposal',())

        # Initialize GUI elements
        self.contentsBox=QHGroupBox("User",self)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(5)

        self.loginBox=QHBox(self.contentsBox, 'login_box')
        code_label=QLabel("  Username: ",self.loginBox)

        self.userName=QLineEdit(self.loginBox)
        self.userName.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.userName.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
        self.userName.setFixedWidth(50)

        #self.propType=QComboBox(self.loginBox)
        #self.propType.setEditable(True)
        #self.propType.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        #self.propType.setPaletteBackgroundColor(widget_colors.LIGHT_RED)

        dash_label=QLabel(" - ",self.loginBox)
        #self.propNumber=QLineEdit(self.loginBox)
        #self.propNumber.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        #self.propNumber.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
        #self.propNumber.setFixedWidth(50)
        password_label=QLabel("   Password: ",self.loginBox)
        self.propPassword=QLineEdit(self.loginBox)
        self.propPassword.setEchoMode(QLineEdit.Password)
        self.propPassword.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.propPassword.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
        self.propPassword.setFixedWidth(75)
        self.connect(self.propPassword, SIGNAL('returnPressed()'), self.login)

        self.loginButton=QToolButton(self.loginBox)
        self.loginButton.setTextLabel("Login")
        self.loginButton.setUsesTextLabel(True)
        self.loginButton.setTextPosition(QToolButton.BesideIcon)
        self.loginButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.connect(self.loginButton,SIGNAL('clicked()'),self.login)

        #labels_box=QHBox(self.contentsBox, 'contents_box')
        #labels_box.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        #font = labels_box.font()
        #font.setPointSize(10)
        #labels_box.setFont(font)

        #self.proposalLabel=QLabel(SoleilLoginBrick2.NOBODY_STR,labels_box)
        #self.proposalLabel.setAlignment(Qt.AlignCenter)

        self.user_group_layout = QHBox(self.contentsBox, 'group_box')

        self.titleLabel=QLabel(self.user_group_layout)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.hide()

        self.user_group_label = QLabel("  Group: ", self.user_group_layout)
        self.user_group_ledit = QLineEdit(self.user_group_layout)
        self.user_group_ledit.setFixedWidth(100)
        self.user_group_save_button = QToolButton(self.user_group_layout)
        self.user_group_save_button.setText("Set")
        self.connect(self.user_group_save_button, SIGNAL('clicked()'), self.save_group)
        self.connect(self.user_group_ledit, SIGNAL('returnPressed ()'), self.save_group)
        self.connect(self.user_group_ledit,
                     SIGNAL('textChanged(const QString &)'), self.user_group_changed)
        self.user_group_label.hide()
        self.user_group_ledit.hide()
        self.user_group_save_button.hide()
        self.saved_group = True

        self.logoutButton=QToolButton(self.contentsBox)
        self.logoutButton.setTextLabel("Logout")
        font = self.logoutButton.font()
        font.setPointSize(10)
        self.logoutButton.setFont(font)
        self.logoutButton.setUsesTextLabel(True)
        self.logoutButton.setTextPosition(QToolButton.BesideIcon)
        self.logoutButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.connect(self.logoutButton,SIGNAL('clicked()'),self.openLogoutDialog)
        self.logoutButton.hide()

        # Initialize layout
        QHBoxLayout(self)
        self.layout().addWidget(self.contentsBox)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.contentsBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

    def save_group(self):
        user_group = str(self.user_group_ledit.text())

        if user_group.isalnum() or user_group == "":
            self.saved_group = True
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
            msg = 'User group set to: %s' % str(self.user_group_ledit.text())
            logging.getLogger("user_level_log").info(msg)
            self.emit(PYSIGNAL("user_group_saved"), (self.user_group_ledit.text(),))
        else:
            msg = 'User group not valid, please enter a valid user group'
            logging.getLogger("user_level_log").info(msg)
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            
    def user_group_changed(self, value):
        if self.saved_group:
            msg = 'User group changed, press set to apply change'
            logging.getLogger("user_level_log").warning(msg)
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_RED)

        self.saved_group = False
        
    def customEvent(self,event):
        #logging.getLogger().debug("SoleilLoginBrick2: custom event (%s)" % str(event))

        if self.isRunning():
            if event.type() == PROPOSAL_GUI_EVENT:
                try:
                    method=event.method
                    arguments=event.arguments
                except Exception,diag:
                    logging.getLogger().exception("SoleilLoginBrick: problem in event! (%s)" % str(diag))
                except:
                    logging.getLogger().exception("SoleilLoginBrick: problem in event!")
                else:
                    #logging.getLogger().debug("SoleilLoginBrick: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception,diag:
                            logging.getLogger().exception("SoleilLoginBrick: uncaught exception! (%s)" % str(diag))
                        except:
                            logging.getLogger().exception("SoleilLoginBrick: uncaught exception!")
                        else:
                            #logging.getLogger().debug("SoleilLoginBrick: custom event finished")
                            pass
                    else:
                        logging.getLogger().warning('SoleilLoginBrick: uncallable custom event!')

    # Enabled/disabled the login/logout button
    def setButtonEnabled(self,state):
        self.loginButton.setEnabled(state)
        self.logoutButton.setEnabled(state)

    def impersonateProposal(self,proposal_code,proposal_number):
        if BlissWidget.isInstanceUserIdInhouse():
            self._do_login(proposal_code, proposal_number, None, self.dbConnection.beamline_name, impersonate=True)
        else:
            logging.getLogger().debug('SoleilLoginBrick: cannot impersonate unless logged as the inhouse user!')

    # Opens the logout dialog (modal); if the answer is OK then logout the user
    def openLogoutDialog(self):
        logout_dialog=QMessageBox("Confirm logout","Press OK to logout.",\
            QMessageBox.Question,QMessageBox.Ok,QMessageBox.Cancel,\
            QMessageBox.NoButton,self)
        s=self.font().pointSize()
        f = logout_dialog.font()
        f.setPointSize(s)
        logout_dialog.setFont(f)
        logout_dialog.updateGeometry()
        if logout_dialog.exec_loop()==QMessageBox.Ok:
            self.logout()

    # Logout the user; reset the brick; changes from logout mode to login mode
    def logout(self):
        # Reset brick info
        #self.propNumber.setText("")
        self.userName.setText("")
        self.proposal=None
        self.session=None
        #self.sessionId=None
        self.person=None
        self.laboratory=None
        # Change mode from logout to login
        self.loginBox.show()
        self.logoutButton.hide()
        self.titleLabel.hide()
        self.user_group_label.hide()
        self.user_group_ledit.hide()
        self.user_group_save_button.hide()

        self.session_hwobj.set_user_info( '','','' )
        
        #self.proposalLabel.setText(SoleilLoginBrick.NOBODY_STR)
        #QToolTip.add(self.proposalLabel,"")
       
        # Emit signals clearing the proposal and session
        self.emit(PYSIGNAL("setWindowTitle"),(self["titlePrefix"],))
        self.emit(PYSIGNAL("sessionSelected"),(None, ))
        self.emit(PYSIGNAL("loggedIn"), (False, ))

    # Sets the current session; changes from login mode to logout mode
    def setProposal(self,proposal,person,laboratory,session,localcontact):
        self.dbConnection.enable()
        self.session_hwobj.proposal_code = proposal['code']
        self.session_hwobj.session_id = session['sessionId']
        self.session_hwobj.proposal_id = proposal['proposalId']
        self.session_hwobj.proposal_number = proposal['number']

        # Change mode
        self.loginBox.hide()
        self.logoutButton.show()

        # Store info in the brick
        self.proposal=proposal
        self.session=session
        self.person=person
        self.laboratory=laboratory

        code=proposal["code"].lower()
        if code=="":
            #self.proposalLabel.setText("<nobr><i>%s</i>" % personFullName(person))
            session_id=""
            logging.getLogger("user_level_log").warning("Using local login: the data collected won't be stored in the database")
            self.dbConnection.disable()
            expiration_time=0
        else:
            codes_list=self["codes"].split()
            if code not in codes_list:
                codes=self["codes"]+" "+code
                self["codes"]=codes
                self.propertyBag.getProperty('codes').setValue(codes)

            # Build the info for the interface
            title=str(proposal['title'])
            session_id=session['sessionId']
            start_date=session['startDate'].split()[0]
            end_date=session['endDate'].split()[0]
            try:
                comments=session['comments']
            except KeyError:
                comments=None
            person_name=personFullName(person)
            if laboratory.has_key('name'):
                person_name=person_name+" "+laboratory['name']
            localcontact_name=personFullName(localcontact)
            #title="<big><b>%s-%s %s</b></big>" % (proposal['code'],proposal['number'],title)
            if localcontact:
                header="%s Dates: %s to %s Local contact: %s" % (person_name,start_date,end_date,localcontact_name)
            else:
                header="%s Dates: %s to %s" % (person_name,start_date,end_date)

            # Set interface info and signal the new session
            proposal_text = "%s-%s" % (proposal['code'],proposal['number'])
            self.titleLabel.setText("<nobr>   User: <b>%s</b>" % proposal_text)
            tooltip = "\n".join([proposal_text, header, title]) 
            if comments:
                tooltip+='\n'
                tooltip+='Comments: '+comments 
            QToolTip.add(self.titleLabel, tooltip)
            self.titleLabel.show()
            self.user_group_label.show()
            self.user_group_ledit.show()
            self.user_group_save_button.show()
        
            try:
                end_time=session['endDate'].split()[1]
                end_date_list=end_date.split('-')
                end_time_list=end_time.split(':')
                expiration_time=time.mktime((\
                    int(end_date_list[0]),\
                    int(end_date_list[1]),\
                    int(end_date_list[2]),\
                    23,59,59,\
                    0,0,0))
            except (TypeError,IndexError,ValueError):
                expiration_time=0

        is_inhouse = self.session_hwobj.is_inhouse(proposal["code"], proposal["number"])
        win_title="%s (%s-%s)" % (self["titlePrefix"],\
            self.dbConnection.translate(proposal["code"],'gui'),\
            proposal["number"])
        self.emit(PYSIGNAL("setWindowTitle"),(win_title,))
        self.emit(PYSIGNAL("sessionSelected"),\
            (session_id,self.dbConnection.translate(proposal["code"],'gui'),\
            str(proposal["number"]),\
            proposal["proposalId"],\
            session["startDate"],\
            proposal["code"],\
            is_inhouse))
        self.emit(PYSIGNAL("loggedIn"), (True, ))

    #def setCodes(self,codes):
        #codes_list=codes.split()
        #self.propType.clear()
        #for cd in codes_list:
            #self.propType.insertItem(cd)

    def run(self):
        self.setEnabled(self.session_hwobj is not None)
          
        # find if we are using ldap, dbconnection, etc. or not
        if None in (self.ldapConnection, self.dbConnection):
          self.loginBox.hide()
          self.titleLabel.setText("<nobr><b>%s</b></nobr>" % os.environ["USER"])
          self.titleLabel.show()
          self.user_group_label.show()
          self.user_group_ledit.show()
          self.user_group_save_button.show()

          self.session_hwobj.proposal_code = ""
          self.session_hwobj.session_id = 1
          self.session_hwobj.proposal_id = ""
          self.session_hwobj.proposal_number = "" 

          self.emit(PYSIGNAL("setWindowTitle"), (self["titlePrefix"],))
          self.emit(PYSIGNAL("loggedIn"), (False, ))
          self.emit(PYSIGNAL("sessionSelected"),(None, ))
          self.emit(PYSIGNAL("loggedIn"), (True, ))
          self.emit(PYSIGNAL("sessionSelected"), (self.session_hwobj.session_id,
                                                  str(os.environ["USER"]),
                                                  0,
                                                  '',
                                                  '',
                                                  self.session_hwobj.session_id, 
                                                  False))
        else: 
          self.emit(PYSIGNAL("setWindowTitle"),(self["titlePrefix"],))
          self.emit(PYSIGNAL("sessionSelected"),(None, ))
          self.emit(PYSIGNAL("loggedIn"), (False, ))

        start_server_event=ProposalGUIEvent(self.startServers,())
        qApp.postEvent(self,start_server_event)

        #self.contentsBox.font()
        #font.setPointSize(12)
        #self.contentsBox.setFont(font)

        #font = self.loginBox.font()
        #font.setPointSize(10)
        #self.loginBox.setFont(font)
        

    def startServers(self):
        if self.instanceServer is not None:
            self.instanceServer.initializeInstance()

    def refuseLogin(self,stat,message=None):
        if message is not None:
            if stat is False:
                icon=QMessageBox.Critical
            elif stat is None:
                icon=QMessageBox.Warning
            elif stat is True:
                icon=QMessageBox.Information
            msg_dialog=QMessageBox("Register user",message,\
                icon,QMessageBox.Ok,QMessageBox.NoButton,\
                QMessageBox.NoButton,self)
            s=self.font().pointSize()
            f = msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.exec_loop()

        self.setEnabled(True)

    def acceptLogin(self,proposal_dict,person_dict,lab_dict,session_dict,contact_dict):
        self.setProposal(proposal_dict,person_dict,lab_dict,session_dict,contact_dict)
        self.setEnabled(True)

    def ispybDown(self):
        msg_dialog=QMessageBox("Register user",\
            "Couldn't contact the ISPyB database server: you've been logged as the local user.\nYour experiments' information will not be stored in ISPyB!",\
            QMessageBox.Warning,QMessageBox.Ok,QMessageBox.NoButton,\
            QMessageBox.NoButton,self)
        s=self.font().pointSize()
        f=msg_dialog.font()
        f.setPointSize(s)
        msg_dialog.setFont(f)
        msg_dialog.updateGeometry()
        msg_dialog.exec_loop()

        now=time.strftime("%Y-%m-%d %H:%M:S")
        prop_dict={'code':'', 'number':'', 'title':'', 'proposalId':''}
        ses_dict={'sessionId':'', 'startDate':now, 'endDate':now, 'comments':''}
        try:
            locallogin_person=self.localLogin.person
        except AttributeError:
            locallogin_person="local user"
        pers_dict={'familyName':locallogin_person}
        lab_dict={'name':'SOLEIL'}
        cont_dict={'familyName':'local contact'}
        self.acceptLogin(prop_dict,pers_dict,lab_dict,ses_dict,cont_dict)

    def askForNewSession(self):
        create_session_dialog=QMessageBox("Create session",\
            "Unable to find an appropriate session.\nPress OK to create one for today.",\
            QMessageBox.Question,QMessageBox.Ok,QMessageBox.Cancel,\
            QMessageBox.NoButton,self)
        s=self.font().pointSize()
        f = create_session_dialog.font()
        f.setPointSize(s)
        create_session_dialog.setFont(f)
        create_session_dialog.updateGeometry()
        answer=create_session_dialog.exec_loop()
        return answer==QMessageBox.Ok

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        self.saved_group = False
        self.user_group_ledit.setPaletteBackgroundColor(widget_colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)

        #prop_type=str(self.propType.currentText())
        #prop_number=str(self.propNumber.text())
        username=str(self.userName.text())
        prop_password=str(self.propPassword.text())
        self.propPassword.setText("")

        #if username=="" and prop_password=="":
        if username=="":
            if self.localLogin is None:
                return self.refuseLogin(False,"Local login not configured.")
            try:
                locallogin_password=self.localLogin.password
            except AttributeError:
                return self.refuseLogin(False,"Local login not configured.")

            if prop_password!=locallogin_password:
                return self.refuseLogin(None,"Invalid local login password.")

            now=time.strftime("%Y-%m-%d %H:%M:S")
            prop_dict={'code':'', 'number':'', 'title':'', 'proposalId':''}
            ses_dict={'sessionId':'', 'startDate':now, 'endDate':now, 'comments':''}
            try:
                locallogin_person=self.localLogin.person
            except AttributeError:
                locallogin_person="local user"
            pers_dict={'familyName':locallogin_person}
            lab_dict={'name':'ESRF'}
            cont_dict={'familyName':'local contact'}

            logging.getLogger().debug("ProposalBrick: local login password validated")
            
            return self.acceptLogin(prop_dict,pers_dict,lab_dict,ses_dict,cont_dict)

        if self.ldapConnection is None:
            return self.refuseLogin(False,'Not connected to LDAP, unable to verify password.')
        if self.dbConnection is None:
            return self.refuseLogin(False,'Not connected to the ISPyB database, unable to get proposal.')

        #self._do_login(prop_type,prop_number,prop_password, self.dbConnection.beamline_name)
        logging.getLogger().debug('SoleilLoginBrick login: proposal_code %s' % username)
        logging.getLogger().debug('SoleilLoginBrick login: prop_password %s' % prop_password)
        logging.getLogger().debug('SoleilLoginBrick login: self.dbConnection.beamline_name %s' % self.dbConnection.beamline_name)
        #if self.dbConnection.beamline_name == 'Proxima2':
            #beamline_name = 'proxima2a'
            #logging.getLogger().debug('SoleilLoginBrick login: beamline_name %s' % beamline_name)
        self._do_login(username, prop_password, self.dbConnection.beamline_name)

    def passControl(self,has_control_id):
        pass

    def haveControl(self,have_control):
        pass

    # Callback fot the brick's properties
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='ldapServer':
            self.ldapConnection=self.getHardwareObject(newValue)
        elif propertyName=='codes':
            pass
            #self.setCodes(newValue)
        elif propertyName=='localLogin':
            self.localLogin=self.getHardwareObject(newValue)
        elif propertyName=='dbConnection':
            self.dbConnection = self.getHardwareObject(newValue)
        elif propertyName=='instanceServer':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.disconnect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
            self.instanceServer=self.getHardwareObject(newValue)
            if self.instanceServer is not None:
                self.connect(self.instanceServer,PYSIGNAL('passControl'), self.passControl)
                self.connect(self.instanceServer,PYSIGNAL('haveControl'), self.haveControl)
        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.loginButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
            try:
                self.logoutButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass
        elif propertyName == 'session':
            self.session_hwobj = self.getHardwareObject(newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def _do_login(self, username, proposal_password, beamline_name, impersonate=False):
        logging.getLogger().debug('SoleilLoginBrick _do_login: username %s' % username)
        logging.getLogger().debug('SoleilLoginBrick _do_login: proposal_password %s' % proposal_password)
        logging.getLogger().debug('SoleilLoginBrick _do_login: beamline_name %s' % beamline_name)
        logging.getLogger().debug('SoleilLoginBrick _do_login: impersonate %s' % impersonate)
        if not impersonate:
            #login_name=self.dbConnection.translate(proposal_code,'ldap')+str(proposal_number)
            login_name=username
            logging.getLogger().debug('SoleilLoginBrick: querying LDAP...')
            ok, msg=self.ldapConnection.login(login_name,proposal_password)
            logging.getLogger().debug("SoleilLoginBrick: password for %s validated" % (username,))

            if not ok:
                msg="%s." % msg.capitalize()
                self.refuseLogin(None,msg)
                return

            userinfo = self.ldapConnection.getinfo(login_name)

            gid = userinfo.get('gidNumber','')
            uid = userinfo.get('uidNumber','')

            if gid and len(gid) > 0:
                gid = gid[0]
            else:
                gid = ''
            if uid and len(uid) > 0:
                uid = uid[0]
            else:
                uid = ''
            
            msg = "SoleilLoginBrick: Searching today's valid session for "
            msg += "User %s on beamline %s..." % (login_name, beamline_name)
            logging.getLogger().debug(msg)
            validsess = self.ldapConnection.find_valid_sessions_for_user(login_name, beamline_name)
            logging.getLogger().debug("SoleilLoginBrick: validsess: %s" % validsess)
            if len(validsess) > 0:
                projuser = validsess[0].username
            else:
                projuser = None
            logging.getLogger().debug("SoleilLoginBrick: Number of valid session found: %d" % len(validsess))
            logging.getLogger().debug("SoleilLoginBrick: Project users: %s" % (projuser))

            self.session_hwobj.set_user_info( login_name, uid, gid, projuser )

        # Get proposal and sessions
        logging.getLogger().debug('SoleilLoginBrick: querying ISPyB database ...')
        
        logging.getLogger().debug("SoleilLoginBrick: Project users: %s" % (projuser))
        
        proposal_code = "mx"
        logging.getLogger().debug("SoleilLoginBrick: proposal_code: %s" % proposal_code)
        
        proposal_number = projuser
        if proposal_number == None:
            proposal_number = "2014"
        logging.getLogger().debug("SoleilLoginBrick: proposal_number: %s" % proposal_number)
        
        prop=self.dbConnection.getProposal(proposal_code, proposal_number)
        logging.getLogger().debug("SoleilLoginBrick: prop: %s" % prop)
        # Check if everything went ok
        prop_ok=True
        try:
            prop_ok=(prop['status']['code']=='ok')
        except KeyError:
            prop_ok=False
        if not prop_ok:
            self.ispybDown()
            return

        logging.getLogger().debug('SoleilLoginBrick: got sessions from ISPyB: % s' % (prop))

        proposal=prop['Proposal']
        person=prop['Person']
        laboratory=prop['Laboratory']
        try:
            sessions=prop['Session']
        except KeyError:
            sessions=None

        # Check if there are sessions in the proposal
        # TODO: remove most of this code next 30 lines is not needed anymore it
        #       is in the SOLEILLdapLogin hwobj in find_valid_sessions_for_user()
        todays_session=None
        if sessions is None or len(sessions)==0:
            pass
        else:
            # Check for today's session
            for session in sessions:
                beamline=session['beamlineName']
                start_date="%s 00:00:00" % session['startDate'].split()[0]
                end_date="%s 23:59:59" % session['endDate'].split()[0]
                logging.getLogger().debug('SoleilLoginBrick: beamline % s start %s end %s' % (beamline, start_date, end_date))
                todays_session=sessions[0]
                #try:
                #    start_struct=time.strptime(start_date,"%Y-%m-%d %H:%M:%S")
                #except ValueError:
                #    pass
                #else:
                #    try:
                #       end_struct=time.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                #    except ValueError:
                #        pass
                #    else:
                #        start_time=time.mktime(start_struct)
                #        end_time=time.mktime(end_struct)
                #        current_time=time.time()

                #        # Check beamline name
                #        if beamline.lower() == beamline_name.lower():
                #            # Check date
                #            if current_time>=start_time and current_time<=end_time:
                #                todays_session=session
                #                break

        if todays_session is None:
            is_inhouse = self.session_hwobj.is_inhouse(proposal["code"], proposal["number"])
            if not is_inhouse:
                if BlissWidget.isInstanceRoleClient():
                    self.refuseLogin(None,"You don't have a session scheduled for today!")
                    return

                if not self.askForNewSession():
                    self.refuseLogin(None,None)
                    return

            current_time=time.localtime()
            start_time=time.strftime("%Y-%m-%d 00:00:00", current_time)
            end_time=time.mktime(current_time)+60*60*24
            tomorrow=time.localtime(end_time)
            end_time=time.strftime("%Y-%m-%d 07:59:59", tomorrow)

            # Create a session
            new_session_dict={}
            new_session_dict['proposalId']=prop['Proposal']['proposalId']
            new_session_dict['startDate']=start_time
            new_session_dict['endDate']=end_time
            new_session_dict['beamlineName']=beamline_name
            new_session_dict['scheduled']=0
            new_session_dict['nbShifts']=3
            new_session_dict['comments']="Session created by the BCM"
            session_id=self.dbConnection.createSession(new_session_dict)
            new_session_dict['sessionId']=session_id

            todays_session=new_session_dict
            localcontact=None
        else:
            session_id=todays_session['sessionId']
            logging.getLogger().debug('SoleilLoginBrick: getting local contact for %s' % session_id)
            localcontact=self.dbConnection.getSessionLocalContact(session_id)

        self.acceptLogin(prop['Proposal'],\
            prop['Person'],\
            prop['Laboratory'],\
            todays_session,\
            localcontact)


### Auxiliary method to merge a person's name
def personFullName(person):
    try:
        name=person['givenName']+" "
    except KeyError:
        name=""
    except TypeError:
        return ""
    if person.has_key('familyName') and person['familyName'] is not None:
        name=name+person['familyName']
    return name.strip()

