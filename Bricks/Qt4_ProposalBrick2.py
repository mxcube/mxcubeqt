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

import re
import os
import time
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_General'


PROPOSAL_GUI_EVENT = QtCore.QEvent.User
class ProposalGUIEvent(QtCore.QEvent):
    """
    Descript. :
    """
    def __init__(self, method, arguments):
        QtCore.QEvent.__init__(self, PROPOSAL_GUI_EVENT)
        self.method = method
        self.arguments = arguments

class Qt4_ProposalBrick2(BlissWidget):
    """
    Descript. :
    """
    NOBODY_STR = "<nobr><b>Login is required for collecting data!</b>"

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.ldap_connection_hwobj = None
        self.lims_hwobj = None
        self.local_login_hwobj = None
        self.session_hwobj = None

        # Internal values -----------------------------------------------------
        self.proposal = None
        self.session = None
        self.person = None
        self.laboratory = None
        #self.sessionId=None
        self.inhouseProposal = None
        self.instanceServer = None

        # Properties ----------------------------------------------------------
        self.addProperty('ldapServer', 'string', '')
        self.addProperty('instanceServer', 'string', '')
        self.addProperty('localLogin', 'string', '')
        self.addProperty('titlePrefix', 'string', '')
        self.addProperty('autoSessionUsers', 'string', '')
        self.addProperty('codes', 'string', 'fx ifx ih im ix ls mx opid')
        self.addProperty('icons', 'string', '')
        self.addProperty('serverStartDelay', 'integer', 500)
        self.addProperty('dbConnection', 'string')
        self.addProperty('session', 'string', '/session')

        # Signals ------------------------------------------------------------
        self.defineSignal('sessionSelected', ())
        self.defineSignal('setWindowTitle', ())
        self.defineSignal('loggedIn', ())
        self.defineSignal('user_group_saved', ())
        self.defineSlot('setButtonEnabled', ())
        self.defineSlot('impersonateProposal', ())

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.login_widget = QtGui.QWidget(self)
        code_label = QtGui.QLabel("  Code: ", self.login_widget)
        self.proposal_type_combox = QtGui.QComboBox(self.login_widget)
        self.proposal_type_combox.setEditable(True)
        self.proposal_type_combox.setFixedWidth(50)
        dash_label = QtGui.QLabel(" - ", self.login_widget)
        self.proposal_number_ledit = QtGui.QLineEdit(self.login_widget)
        self.proposal_number_ledit.setFixedWidth(40)
        password_label = QtGui.QLabel("   Password: ", self.login_widget)
        self.proposal_password_ledit = QtGui.QLineEdit(self.login_widget)
        self.proposal_password_ledit.setEchoMode(QtGui.QLineEdit.Password)
        self.proposal_password_ledit.setFixedWidth(40)

        self.login_button = QtGui.QToolButton(self.login_widget)
        self.login_button.setText("Login")
        self.login_button.setUsesTextLabel(True)

        self.user_group_widget = QtGui.QWidget(self)
        self.title_label = QtGui.QLabel(self.user_group_widget)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.user_group_label = QtGui.QLabel("  Group: ", self.user_group_widget)
        self.user_group_ledit = QtGui.QLineEdit(self.user_group_widget)
        self.user_group_ledit.setFixedWidth(70)
        self.user_group_save_button = QtGui.QToolButton(self.user_group_widget)
        self.user_group_save_button.setText("Set")
        self.saved_group = True

        self.logout_button = QtGui.QToolButton(self)
        self.logout_button.setText("Logout")
        font = self.logout_button.font()
        font.setPointSize(10)
        self.logout_button.setFont(font)
        self.logout_button.setUsesTextLabel(True)
        #self.logout_button.setTextPosition(QToolButton.BesideIcon)
        self.logout_button.hide()

        # Layout --------------------------------------------------------------
        _user_group_widget_hlayout = QtGui.QHBoxLayout(self)
        _user_group_widget_hlayout.setSpacing(2)
        _user_group_widget_hlayout.addWidget(self.title_label)
        _user_group_widget_hlayout.addWidget(self.user_group_label) 
        _user_group_widget_hlayout.addWidget(self.user_group_ledit)
        _user_group_widget_hlayout.addWidget(self.user_group_save_button)
        _user_group_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.user_group_widget.setLayout(_user_group_widget_hlayout)
        self.user_group_widget.hide()

        _login_widget_layout = QtGui.QHBoxLayout(self)
        _login_widget_layout.addWidget(code_label)
        _login_widget_layout.addWidget(self.proposal_type_combox)
        _login_widget_layout.addWidget(dash_label)
        _login_widget_layout.addWidget(self.proposal_number_ledit)
        _login_widget_layout.addWidget(password_label)
        _login_widget_layout.addWidget(self.proposal_password_ledit)
        _login_widget_layout.addWidget(self.login_button)
    
        _login_widget_layout.setSpacing(2)
        _login_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.login_widget.setLayout(_login_widget_layout) 

        _main_vlayout = QtGui.QHBoxLayout(self)
        _main_vlayout.addWidget(self.login_widget)
        _main_vlayout.addWidget(self.user_group_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.addWidget(self.logout_button)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------
        """self.proposal_type_combox.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                                QtGui.QSizePolicy.MinimumExpanding)
        self.proposal_number_ledit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.login_widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.proposal_password_ledit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)
        self.login_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.logout_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)"""

        # Qt signal/slot connections ------------------------------------------
        self.proposal_password_ledit.returnPressed.connect(self.login)
        self.login_button.clicked.connect(self.login)
        self.logout_button.clicked.connect(self.logout_clicked)  
        self.user_group_save_button.clicked.connect(self.save_group)
        self.user_group_ledit.returnPressed.connect(self.save_group)
        self.user_group_ledit.textChanged.connect(self.user_group_changed)

        # Other ---------------------------------------------------------------
        """Qt4_widget_colors.set_widget_color(self.proposal_type_combox,
                                           Qt4_widget_colors.LIGHT_RED, 
                                           QtGui.QPalette.Window)"""
        Qt4_widget_colors.set_widget_color(self.proposal_number_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QtGui.QPalette.Base)
        Qt4_widget_colors.set_widget_color(self.proposal_password_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QtGui.QPalette.Base)
 
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.GROUP_BOX_GRAY)

    def save_group(self):
        """
        Descript. :
        """
        user_group = str(self.user_group_ledit.text())

        pattern = r"^[a-zA-Z0-9_-]*$"
        valid = re.match(pattern, user_group, flags = 0).group() == user_group
        
        if valid:
            self.saved_group = True
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
            msg = 'User group set to: %s' % str(self.user_group_ledit.text())
            logging.getLogger("user_level_log").info(msg)
            self.emit(QtCore.SIGNAL("user_group_saved"), self.user_group_ledit.text())
        else:
            msg = 'User group not valid, please enter a valid user group'
            logging.getLogger("user_level_log").info(msg)
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            
    def user_group_changed(self, value):
        """
        Descript. :
        """
        if self.saved_group:
            msg = 'User group changed, press set to apply change'
            logging.getLogger("user_level_log").warning(msg)
            self.user_group_ledit.setPaletteBackgroundColor(widget_colors.LIGHT_RED)

        self.saved_group = False
        
    def customEvent(self, event):
        """
        Descript. :
        """
        if self.isRunning():
            if event.type() == PROPOSAL_GUI_EVENT:
                try:
                    method = event.method
                    arguments = event.arguments
                except Exception, diag:
                    logging.getLogger().exception("Qt4_ProposalBrick2: problem in event! (%s)" % str(diag))
                except:
                    logging.getLogger().exception("Qt4_ProposalBrick2: problem in event!")
                else:
                    #logging.getLogger().debug("Qt4_ProposalBrick2: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception, diag:
                            logging.getLogger().exception("Qt4_ProposalBrick2: uncaught exception! (%s)" % str(diag))
                        except:
                            logging.getLogger().exception("Qt4_ProposalBrick2: uncaught exception!")
                        else:
                            #logging.getLogger().debug("Qt4_ProposalBrick2: custom event finished")
                            pass
                    else:
                        logging.getLogger().warning('Qt4_ProposalBrick2: uncallable custom event!')

    # Enabled/disabled the login/logout button
    def setButtonEnabled(self, state):
        """
        Descript. :
        """
        self.login_button.setEnabled(state)
        self.logout_button.setEnabled(state)

    def impersonateProposal(self, proposal_code, proposal_number):
        """
        Descript. :
        """
        if BlissWidget.isInstanceUserIdInhouse():
            self._do_login(proposal_code, proposal_number, None, \
                self.lims_hwobj.beamline_name, impersonate = True)
        else:
            logging.getLogger().debug('Qt4_ProposalBrick2: cannot impersonate unless logged as the inhouse user!')

    # Opens the logout dialog (modal); if the answer is OK then logout the user
    def logout_clicked(self):
        """
        Descript. :
        """
        if QtGui.QMessageBox.question(self, 
                                      "Confirm logout", 
                                      "Press OK to logout.",
                                      QtGui.QMessageBox.Ok,
                                      QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            self.log_out()

    # Logout the user; reset the brick; changes from logout mode to login mode
    def log_out(self):
        """
        Descript. :
        """
        # Reset brick info
        self.proposal_number_ledit.setText("")
        self.proposal = None
        self.session = None
        #self.sessionId=None
        self.person = None
        self.laboratory = None
        # Change mode from logout to login
        self.login_widget.show()
        self.logout_button.hide()
        self.title_label.hide()
        self.user_group_widget.hide()
       
	#resets active proposal
        self.resetProposal()
 
        #self.proposalLabel.setText(Qt4_ProposalBrick2.NOBODY_STR)
        #QToolTip.add(self.proposalLabel,"")
       
        # Emit signals clearing the proposal and session
        self.emit(QtCore.SIGNAL("setWindowTitle"), self["titlePrefix"])
        self.emit(QtCore.SIGNAL("sessionSelected"), None)
        self.emit(QtCore.SIGNAL("loggedIn"), False)

    def resetProposal(self):
        """
        Descript. :
        """
        self.session_hwobj.proposal_code = None
        self.session_hwobj.session_id = None
        self.session_hwobj.proposal_id = None
        self.session_hwobj.proposal_number = None 	

    # Sets the current session; changes from login mode to logout mode
    def setProposal(self, proposal, person, laboratory, session, localcontact):
        """
        Descript. :
        """
        self.lims_hwobj.enable()
        self.session_hwobj.proposal_code = proposal['code']
        self.session_hwobj.session_id = session['sessionId']
        self.session_hwobj.proposal_id = proposal['proposalId']
        self.session_hwobj.proposal_number = proposal['number']

        # Change mode
        self.login_widget.hide()
        self.logout_button.show()

        # Store info in the brick
        self.proposal = proposal
        self.session = session
        self.person = person
        self.laboratory = laboratory

        code = proposal["code"].lower()
        if code == "":
            #self.proposalLabel.setText("<nobr><i>%s</i>" % personFullName(person))
            session_id = ""
            logging.getLogger().warning("Using local login: the data collected won't be stored in the database")
            self.lims_hwobj.disable()
            expiration_time = 0
        else:
            codes_list = self["codes"].split()
            if code not in codes_list:
                codes = self["codes"] + " " + code
                self["codes"] = codes
                self.propertyBag.getProperty('codes').setValue(codes)

            # Build the info for the interface
            title = str(proposal['title'])
            session_id = session['sessionId']
            start_date = session['startDate'].split()[0]
            end_date = session['endDate'].split()[0]
            try:
                comments = session['comments']
            except KeyError:
                comments = None
            person_name = personFullName(person)
            if laboratory.has_key('name'):
                person_name = person_name + " " + laboratory['name']
            localcontact_name = personFullName(localcontact)
            #title="<big><b>%s-%s %s</b></big>" % (proposal['code'],proposal['number'],title)
            if localcontact:
                header = "%s Dates: %s to %s Local contact: %s" % \
                       (person_name,start_date,end_date,localcontact_name)
            else:
                header = "%s Dates: %s to %s" % (person_name, start_date, end_date)

            # Set interface info and signal the new session
            proposal_text = "%s-%s" % (proposal['code'], proposal['number'])
            self.title_label.setText("<nobr>   User: <b>%s</b>" % proposal_text)
            tooltip = "\n".join([proposal_text, header, title]) 
            if comments:
                tooltip += '\n'
                tooltip += 'Comments: ' + comments 
            self.title_label.setToolTip(tooltip)
            self.user_group_widget.show()
            try:
                end_time = session['endDate'].split()[1]
                end_date_list = end_date.split('-')
                end_time_list = end_time.split(':')
                expiration_time = time.mktime((\
                    int(end_date_list[0]),\
                    int(end_date_list[1]),\
                    int(end_date_list[2]),\
                    23, 59, 59,\
                    0, 0, 0))
            except (TypeError, IndexError, ValueError):
                expiration_time = 0

        is_inhouse = self.session_hwobj.is_inhouse(proposal["code"], proposal["number"])
        win_title = "%s (%s-%s)" % (self["titlePrefix"], \
            self.lims_hwobj.translate(proposal["code"], 'gui'), \
            proposal["number"])
        self.emit(QtCore.SIGNAL("setWindowTitle"), win_title)
        self.emit(QtCore.SIGNAL("sessionSelected"),
                  session_id, 
                  self.lims_hwobj.translate(proposal["code"],'gui'),
                  str(proposal["number"]),
                  proposal["proposalId"],
                  session["startDate"],
                  proposal["code"],
                  is_inhouse)
        self.emit(QtCore.SIGNAL("loggedIn"), True)

    def setCodes(self, codes):
        """
        Descript. :
        """
        codes_list = codes.split()
        self.proposal_type_combox.clear()
        for cd in codes_list:
            self.proposal_type_combox.addItem(cd)

    def run(self):
        """
        Descript. :
        """
        self.setEnabled(self.session_hwobj is not None)
          
        # find if we are using ldap, dbconnection, etc. or not
        if None in (self.ldap_connection_hwobj, self.lims_hwobj):
            self.login_widget.hide()
            self.title_label.setText("<nobr><b>%s</b></nobr>" % os.environ["USER"])
            self.title_label.show()
            self.user_group_widget.show()
            self.session_hwobj.proposal_code = ""
            self.session_hwobj.session_id = 1
            self.session_hwobj.proposal_id = ""
            self.session_hwobj.proposal_number = "" 
    
            self.emit(QtCore.SIGNAL("setWindowTitle"), self["titlePrefix"])
            self.emit(QtCore.SIGNAL("loggedIn"), False)
            self.emit(QtCore.SIGNAL("sessionSelected"), None)
            self.emit(QtCore.SIGNAL("loggedIn"), True)
            self.emit(QtCore.SIGNAL("sessionSelected"), 
                 self.session_hwobj.session_id,
                 str(os.environ["USER"]), 0, '', '',
                 self.session_hwobj.session_id, False)
        else: 
            self.emit(QtCore.SIGNAL("setWindowTitle"), self["titlePrefix"])
            self.emit(QtCore.SIGNAL("sessionSelected"), None)
            self.emit(QtCore.SIGNAL("loggedIn"), False)

        start_server_event = ProposalGUIEvent(self.startServers,())
        QtGui.QApplication.postEvent(self, start_server_event)

    def startServers(self):
        """
        Descript. :
        """
        if self.instanceServer is not None:
            self.instanceServer.initializeInstance()

    def refuseLogin(self, stat, message = None):
        """
        Descript. :
        """
        if message is not None:
            if stat is False:
                icon = QtGui.QMessageBox.Critical
            elif stat is None:
                icon = QtGui.QMessageBox.Warning
            elif stat is True:
                icon = QtGui.QMessageBox.Information
            msg_dialog = QtGui.QMessageBox("Register user", message, \
                icon, QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton,\
                QtGui.QMessageBox.NoButton, self)
            s = self.font().pointSize()
            f = msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.show()

        self.setEnabled(True)

    def acceptLogin(self, proposal_dict, person_dict, lab_dict, session_dict, contact_dict):
        """
        Descript. :
        """
        self.setProposal(proposal_dict, person_dict, lab_dict, 
                         session_dict, contact_dict)
        self.setEnabled(True)

    def ispybDown(self):
        """
        Descript. :
        """
        msg_dialog = QtGui.QMessageBox("Register user", \
            "Couldn't contact the ISPyB database server: you've been logged as the local user.\nYour experiments' information will not be stored in ISPyB!",\
            QtGui.QMessageBox.Warning, 
            QtGui.QMessageBox.Ok, 
            QtGui.QMessageBox.NoButton,
            QtGui.QMessageBox.NoButton,self)
        s = self.font().pointSize()
        f = msg_dialog.font()
        f.setPointSize(s)
        msg_dialog.setFont(f)
        msg_dialog.updateGeometry()
        msg_dialog.show()

        now = time.strftime("%Y-%m-%d %H:%M:S")
        prop_dict = {'code' : '', 'number' : '', 'title' : '', 'proposalId' : ''}
        ses_dict = {'sessionId' : '', 'startDate' : now, 'endDate' : now, 'comments' : ''}
        try:
            locallogin_person = self.local_login_hwobj.person
        except AttributeError:
            locallogin_person = "local user"
        pers_dict = {'familyName' : locallogin_person}
        lab_dict = {'name':'EMBL-HH'}
        cont_dict = {'familyName' : 'local contact'}
        self.acceptLogin(prop_dict, pers_dict, lab_dict, ses_dict, cont_dict)

    def askForNewSession(self):
        """
        Descript. :
        """
        create_session_dialog = QtGui.QMessageBox("Create session", \
            "Unable to find an appropriate session.\nPress OK to create one for today.", \
            QtGui.QMessageBox.Question, 
            QtGui.QMessageBox.Ok,QMessageBox.Cancel,
            QtGui.QMessageBox.NoButton,self)
        s = self.font().pointSize()
        f = create_session_dialog.font()
        f.setPointSize(s)
        create_session_dialog.setFont(f)
        create_session_dialog.updateGeometry()
        answer = create_session_dialog.show()
        return answer == QtGui.QMessageBox.Ok

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """
        self.saved_group = False
        Qt4_widget_colors.set_widget_color(self.user_group_ledit, Qt4_widget_colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)

        prop_type = str(self.proposal_type_combox.currentText())
        prop_number = str(self.proposal_number_ledit.text())
        prop_password = str(self.proposal_password_ledit.text())
        self.proposal_password_ledit.setText("")

        if prop_type == "" and prop_number == "":
            if self.local_login_hwobj is None:
                return self.refuseLogin(False,"Local login not configured.")
            try:
                locallogin_password = self.local_login_hwobj.password
            except AttributeError:
                return self.refuseLogin(False,"Local login not configured.")

            if prop_password != locallogin_password:
                return self.refuseLogin(None,"Invalid local login password.")

            now = time.strftime("%Y-%m-%d %H:%M:S")
            prop_dict = {'code' : '', 'number' : '', 'title' : '', 'proposalId' : ''}
            ses_dict = {'sessionId' : '', 'startDate' : now, 'endDate' : now, 'comments' : ''}
            try:
                locallogin_person = self.local_login_hwobj.person
            except AttributeError:
                locallogin_person = "local user"
            pers_dict = {'familyName' : locallogin_person}
            lab_dict = {'name' : 'EMBL-HH'}
            cont_dict = {'familyName' : 'local contact'}

            logging.getLogger().debug("ProposalBrick: local login password validated")
            
            return self.acceptLogin(prop_dict, pers_dict, lab_dict, ses_dict, cont_dict)

        if self.ldap_connection_hwobj == None:
            return self.refuseLogin(False,'Not connected to LDAP, unable to verify password.')
        if self.lims_hwobj == None:
            return self.refuseLogin(False,'Not connected to the ISPyB database, unable to get proposal.')

        self._do_login(prop_type, prop_number, prop_password, self.lims_hwobj.beamline_name)

    def passControl(self, has_control_id):
        """
        Descript. :
        """
        pass

    def haveControl(self, have_control):
        """
        Descript. :
        """
        pass

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'ldapServer':
            self.ldap_connection_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'codes':
            self.setCodes(new_value)
        elif property_name == 'localLogin':
            self.local_login_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'dbConnection':
            self.lims_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'instanceServer':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer, QtCore.SIGNAL('passControl'), self.passControl)
                self.disconnect(self.instanceServer, QtCore.SIGNAL('haveControl'), self.haveControl)
            self.instanceServer = self.getHardwareObject(new_value)
            if self.instanceServer is not None:
                self.connect(self.instanceServer, QtCore.SIGNAL('passControl'), self.passControl)
                self.connect(self.instanceServer, QtCore.SIGNAL('haveControl'), self.haveControl)
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.login_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[0])))
            except IndexError:
                pass
            try:
                self.logout_button.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[1])))
            except IndexError:
                pass
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def _do_login(self, proposal_code, proposal_number, proposal_password, beamline_name, impersonate=False):
        """
        Descript. :
        """
        if not impersonate:
            login_name = self.lims_hwobj.translate(proposal_code, 'ldap') + \
                             str(proposal_number)
            logging.getLogger().debug('ProposalBrick: querying LDAP...')
            ok, msg = self.ldap_connection_hwobj.login(login_name, proposal_password)
            if not ok:
                msg = "%s." % msg.capitalize()
                self.refuseLogin(None, msg)
                return

            logging.getLogger().debug("ProposalBrick: password for %s-%s validated" % \
                     (proposal_code,proposal_number))

        # Get proposal and sessions
        logging.getLogger().debug('ProposalBrick: querying ISPyB database...')
        prop = self.lims_hwobj.getProposal(proposal_code, proposal_number)

        # Check if everything went ok
        prop_ok = True
        try:
            prop_ok = (prop['status']['code'] == 'ok')
        except KeyError:
            prop_ok = False
        if not prop_ok:
            self.ispybDown()
            return

        logging.getLogger().debug('ProposalBrick: got sessions from ISPyB...')

        proposal = prop['Proposal']
        person = prop['Person']
        laboratory = prop['Laboratory']
        try:
            sessions = prop['Session']
        except KeyError:
            sessions = None

        # Check if there are sessions in the proposal
        todays_session = None
        if sessions is None or len(sessions) == 0:
            pass
        else:
            # Check for today's session
            for session in sessions:
                beamline = session['beamlineName']
                start_date = "%s 00:00:00" % session['startDate'].split()[0]
                end_date = "%s 23:59:59" % session['endDate'].split()[0]
                try:
                    start_struct = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
                else:
                    try:
                        end_struct = time.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    else:
                        start_time = time.mktime(start_struct)
                        end_time = time.mktime(end_struct)
                        current_time = time.time()

                        # Check beamline name
                        if beamline == beamline_name:
                            # Check date
                            if current_time >= start_time and current_time <= end_time:
                                todays_session = session
                                break

        if todays_session is None:
            is_inhouse = self.session_hwobj.is_inhouse(proposal["code"], proposal["number"])
            if not is_inhouse:
                if BlissWidget.isInstanceRoleClient():
                    self.refuseLogin(None, "You don't have a session scheduled for today!")
                    return

                if not self.askForNewSession():
                    self.refuseLogin(None, None)
                    return

            current_time = time.localtime()
            start_time = time.strftime("%Y-%m-%d 00:00:00", current_time)
            end_time = time.mktime(current_time) + 60 * 60 *24
            tomorrow = time.localtime(end_time)
            end_time = time.strftime("%Y-%m-%d 07:59:59", tomorrow)

            # Create a session
            new_session_dict = {}
            new_session_dict['proposalId'] = prop['Proposal']['proposalId']
            new_session_dict['startDate'] = start_time
            new_session_dict['endDate'] = end_time
            new_session_dict['beamlineName'] = beamline_name
            new_session_dict['scheduled'] = 0
            new_session_dict['nbShifts'] = 3
            new_session_dict['comments'] = "Session created by the BCM"
            session_id = self.lims_hwobj.createSession(new_session_dict)
            new_session_dict['sessionId'] = session_id

            todays_session = new_session_dict
            localcontact = None
        else:
            session_id = todays_session['sessionId']
            logging.getLogger().debug('ProposalBrick: getting local contact for %s' % session_id)
            localcontact = self.lims_hwobj.getSessionLocalContact(session_id)

        self.acceptLogin(prop['Proposal'], prop['Person'], prop['Laboratory'],
            todays_session, localcontact)


### Auxiliary method to merge a person's name
def personFullName(person):
    """
    Descript. :
    """
    try:
        name = person['givenName'] + " "
    except KeyError:
        name = ""
    except TypeError:
        return ""
    if person.has_key('familyName') and person['familyName'] is not None:
        name = name + person['familyName']
    return name.strip()

