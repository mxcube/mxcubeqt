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

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


PROPOSAL_GUI_EVENT = QEvent.User
class ProposalGUIEvent(QEvent):
    """
    Descript. :
    """
    def __init__(self, method, arguments):
        QEvent.__init__(self, PROPOSAL_GUI_EVENT)
        self.method = method
        self.arguments = arguments

class Qt4_ProposalBrick2(BlissWidget):
    """
    Descript. :
    """

    sessionSelected = pyqtSignal(int, str, str, int, str, str, bool)
    setWindowTitle = pyqtSignal(str)
    loggedIn = pyqtSignal(bool)
    userGroupSaved = pyqtSignal(str)

    NOBODY_STR = "<nobr><b>Login is required for collecting data!</b>"

    def __init__(self, *args):
        """
        Descript. : Proposal brick is used to authentificate current user.
                    Brick can be used in two modes defined by ispyb hwobj
                    - loginAsUser = True, Brick displays combobox with all
                      proposals from ISPyB that are associated to the current user
                    - loginAsUser = False. Brick displays combobox to choose proposal
                      type and linedits to enter proposal number and password. 
                      In this case user is authentificated with 
                      LDAP and proposal from ISPyB is retrieved.
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.lims_hwobj = None
        self.local_login_hwobj = None
        self.session_hwobj = None

        # Internal values -----------------------------------------------------
        self.login_as_user = None

        self.proposal = None
        self.session = None
        self.person = None
        self.laboratory = None
        #self.sessionId=None
        self.inhouseProposal = None
        self.instanceServer = None
        self.secondary_proposals = []

        # Properties ----------------------------------------------------------
        self.addProperty('instanceServer', 'string', '')
        self.addProperty('localLogin', 'string', '')
        self.addProperty('titlePrefix', 'string', '')
        self.addProperty('autoSessionUsers', 'string', '')
        self.addProperty('codes', 'string', 'fx ifx ih im ix ls mx opid')
        self.addProperty('secondaryProposals', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('serverStartDelay', 'integer', 500)
        self.addProperty('dbConnection', 'string')
        self.addProperty('session', 'string', '/session')

        # Signals ------------------------------------------------------------
        self.defineSignal('sessionSelected', ())
        self.defineSignal('setWindowTitle', ())
        self.defineSignal('loggedIn', ())
        self.defineSignal('userGroupSaved', ())

        # Slots ---------------------------------------------------------------
        self.defineSlot('setButtonEnabled', ())
        self.defineSlot('impersonateProposal', ())

        # Graphic elements ----------------------------------------------------
        self.main_gbox = QGroupBox("ISPyB proposal", self)

        self.login_as_proposal_widget = QWidget(self.main_gbox)
        code_label = QLabel("  Code: ", self.login_as_proposal_widget)
        self.proposal_type_combox = QComboBox(self.login_as_proposal_widget)
        self.proposal_type_combox.setEditable(True)
        self.proposal_type_combox.setFixedWidth(60)
        dash_label = QLabel(" - ", self.login_as_proposal_widget)
        self.proposal_number_ledit = QLineEdit(self.login_as_proposal_widget)
        self.proposal_number_ledit.setFixedWidth(60)
        password_label = QLabel("   Password: ", self.login_as_proposal_widget)
        self.proposal_password_ledit = QLineEdit(self.login_as_proposal_widget)
        self.proposal_password_ledit.setEchoMode(QLineEdit.Password)
        #self.proposal_password_ledit.setFixedWidth(40)
        self.login_button = QPushButton("Login", self.login_as_proposal_widget)
        self.login_button.setFixedWidth(70)
        self.logout_button = QPushButton("Logout", self.main_gbox)
        self.logout_button.hide()
        self.logout_button.setFixedWidth(70)
        self.login_as_proposal_widget.hide()
        

        self.login_as_user_widget = QWidget(self.main_gbox)
        self.proposal_combo = QComboBox(self.login_as_user_widget)
        self.proposal_combo.setFixedWidth(140)

        self.user_group_widget = QWidget(self.main_gbox)
        #self.title_label = QtGui.QLabel(self.user_group_widget)
        #self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.user_group_label = QLabel("  Group: ", self.user_group_widget)
        self.user_group_ledit = QLineEdit(self.user_group_widget)
        self.user_group_ledit.setFixedHeight(27)
        self.user_group_save_button = QToolButton(self.user_group_widget)
        self.user_group_save_button.setText("Set")
        self.user_group_save_button.setFixedHeight(27)
        self.saved_group = True 

        # Layout --------------------------------------------------------------
        _user_group_widget_hlayout = QHBoxLayout(self.user_group_widget)
        _user_group_widget_hlayout.setSpacing(2)
        #_user_group_widget_hlayout.addWidget(self.title_label)
        _user_group_widget_hlayout.addWidget(self.user_group_label) 
        _user_group_widget_hlayout.addWidget(self.user_group_ledit)
        _user_group_widget_hlayout.addWidget(self.user_group_save_button)
        _user_group_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.user_group_widget.hide()

        _login_as_proposal_widget_layout = QHBoxLayout(self.login_as_proposal_widget)
        _login_as_proposal_widget_layout.addWidget(code_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_type_combox)
        _login_as_proposal_widget_layout.addWidget(dash_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_number_ledit)
        _login_as_proposal_widget_layout.addWidget(password_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_password_ledit)
        _login_as_proposal_widget_layout.addWidget(self.login_button)
        _login_as_proposal_widget_layout.setSpacing(2)
        _login_as_proposal_widget_layout.setContentsMargins(0, 0, 0, 0)

        _login_as_user_widget_layout = QHBoxLayout(self.login_as_user_widget)
        _login_as_user_widget_layout.addWidget(self.proposal_combo)
        _login_as_user_widget_layout.setSpacing(2)
        _login_as_user_widget_layout.setContentsMargins(0, 0, 0, 0)

        _main_gboxlayout = QHBoxLayout(self.main_gbox)
        _main_gboxlayout.addWidget(self.login_as_proposal_widget)
        _main_gboxlayout.addWidget(self.logout_button)
        _main_gboxlayout.addWidget(self.login_as_user_widget)
        #_main_vlayout.addSpacing(10)
        _main_gboxlayout.addWidget(self.user_group_widget)
        _main_gboxlayout.setSpacing(2)
        _main_gboxlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        #  self.user_group_ledit

        # Qt signal/slot connections ------------------------------------------
        self.proposal_password_ledit.returnPressed.connect(self.login)
        self.login_button.clicked.connect(self.login)
        self.logout_button.clicked.connect(self.logout_clicked)  
        self.proposal_combo.activated.connect(self.proposal_combo_activated)
        self.user_group_save_button.clicked.connect(self.save_group)
        self.user_group_ledit.returnPressed.connect(self.save_group)
        self.user_group_ledit.textChanged.connect(self.user_group_changed)

        # Other ---------------------------------------------------------------
        """Qt4_widget_colors.set_widget_color(self.proposal_type_combox,
                                           Qt4_widget_colors.LIGHT_RED, 
                                           QtGui.QPalette.Window)"""
        Qt4_widget_colors.set_widget_color(self.proposal_number_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QPalette.Base)
        Qt4_widget_colors.set_widget_color(self.proposal_password_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QPalette.Base)
 
    def save_group(self):
        """
        Descript. :
        """
        user_group = str(self.user_group_ledit.text())

        pattern = r"^[a-zA-Z0-9_-]*$"
        valid = re.match(pattern, user_group, flags = 0).group() == user_group
        
        if valid:
            self.saved_group = True
            Qt4_widget_colors.set_widget_color(self.user_group_ledit,
                                               Qt4_widget_colors.LIGHT_GREEN,
                                               QPalette.Base)  
            msg = 'User group set to: %s' % str(self.user_group_ledit.text())
            logging.getLogger("GUI").info(msg)
            self.userGroupSaved.emit(self.user_group_ledit.text())
        else:
            msg = 'User group not valid, please enter a valid user group'
            logging.getLogger("GUI").info(msg)
            Qt4_widget_colors.set_widget_color(self.user_group_ledit,
                                               Qt4_widget_colors.LIGHT_RED,
                                               QPalette.Base)
            
    def user_group_changed(self, value):
        """
        Descript. :
        """
        if self.saved_group:
            msg = 'User group changed, press set to apply change'
            logging.getLogger("GUI").warning(msg)
            Qt4_widget_colors.set_widget_color(self.user_group_ledit,
                                               Qt4_widget_colors.LINE_EDIT_CHANGED,
                                               QPalette.Base)
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
                except (Exception, diag):
                    logging.getLogger().exception("Qt4_ProposalBrick2: problem in event! (%s)" % str(diag))
                except:
                    logging.getLogger().exception("Qt4_ProposalBrick2: problem in event!")
                else:
                    #logging.getLogger().debug("Qt4_ProposalBrick2: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception as diag:
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
            self._do_login_as_proposal(proposal_code, proposal_number, None, \
                self.lims_hwobj.beamline_name, impersonate = True)
        else:
            logging.getLogger().debug('Qt4_ProposalBrick2: cannot impersonate unless logged as the inhouse user!')

    # Opens the logout dialog (modal); if the answer is OK then logout the user
    def logout_clicked(self):
        """
        Descript. :
        """
        if QMessageBox.question(self, "Confirm logout", 
            "Press OK to logout.", QMessageBox.Ok,
            QMessageBox.Cancel) == QMessageBox.Ok:
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
        if not self.login_as_user: 
            self.login_as_proposal_widget.setEnabled(True)
            self.login_button.show()
            self.logout_button.hide()
        #self.title_label.hide()
        self.user_group_widget.hide()
       
        #resets active proposal
        self.resetProposal()
 
        #self.proposalLabel.setText(Qt4_ProposalBrick2.NOBODY_STR)
        #QToolTip.add(self.proposalLabel,"")
       
        # Emit signals clearing the proposal and session
        self.setWindowTitle.emit(self["titlePrefix"])
        #self.sessionSelected.emit(None, None, None, None, None, None, None)
        self.loggedIne.mit(False)

    def resetProposal(self):
        """
        Descript. :
        """
        self.session_hwobj.proposal_code = None
        self.session_hwobj.session_id = None
        self.session_hwobj.proposal_id = None
        self.session_hwobj.proposal_number = None

    # Sets the current session; changes from login mode to logout mode
    def setProposal(self, proposal, session):
        """
        Descript. :
        """
        self.lims_hwobj.enable()
        self.session_hwobj.proposal_code = proposal['code']
        self.session_hwobj.session_id = session['sessionId']
        self.session_hwobj.proposal_id = proposal['proposalId']
        self.session_hwobj.proposal_number = proposal['number']

        # Change mode
        if not self.login_as_user:
            self.login_button.hide()
            self.login_as_proposal_widget.setDisabled(True)
            self.logout_button.show()

        # Store info in the brick
        self.proposal = proposal
        self.session = session
        #self.person = person
        #self.laboratory = laboratory

        code = proposal["code"].lower()

        if code == "":
            #self.proposalLabel.setText("<nobr><i>%s</i>" % personFullName(person))
            session_id = ""
            logging.getLogger().warning("Using local login: the data collected won't be stored in the database")
            self.lims_hwobj.disable()
            expiration_time = 0
        else:
            msg = "Results in ISPyB will be stored under proposal %s%s - '%s'" % \
                 (proposal["code"],
                  str(proposal["number"]),
                  proposal["title"])
            logging.getLogger("GUI").debug(msg)  

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

            """
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
            """
            #Not implemented in REST
            header = ""

            # Set interface info and signal the new session
            proposal_text = "%s-%s" % (proposal['code'], proposal['number'])
            #self.title_label.setText("<nobr>   User: <b>%s</b>" % proposal_text)
            tooltip = "\n".join([proposal_text, header, title]) 
            if comments:
                tooltip += '\n'
                tooltip += 'Comments: ' + comments 
            #self.title_label.setToolTip(tooltip)
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
        self.setWindowTitle.emit(win_title)
        self.sessionSelected.emit(
                  session_id, 
                  self.lims_hwobj.translate(proposal["code"],'gui'),
                  str(proposal["number"]),
                  proposal["proposalId"],
                  session["startDate"],
                  proposal["code"],
                  is_inhouse)
        self.loggedIn.emit(True)

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

        # find if we are using dbconnection, etc. or not
        if not self.lims_hwobj:
            self.login_as_proposal_widget.hide()
            self.login_button.hide()
            #self.title_label.setText("<nobr><b>%s</b></nobr>" % os.environ["USER"])
            #self.title_label.show()
            self.user_group_widget.show()
            self.session_hwobj.proposal_code = ""
            self.session_hwobj.session_id = 1
            self.session_hwobj.proposal_id = ""
            self.session_hwobj.proposal_number = "" 
    
            self.setWindowTitle.emit(self["titlePrefix"])
            #self.loggedIn.emit(False)
            #self.sessionSelected.emit(None, None, None, None, None, None, None)
            self.loggedIn.emit(True)
            self.sessionSelected.emit(self.session_hwobj.session_id,
                 str(os.environ["USER"]), 0, '', '',
                 self.session_hwobj.session_id, False)
        else: 
            self.setWindowTitle.emit(self["titlePrefix"])
            #self.sessionSelected.emit(None, None, None, None, None, None, None)
            self.loggedIn.emit(False)

            if self.login_as_user:
               if os.getenv("SUDO_USER"):
                   user_name = os.getenv("SUDO_USER")
               else:
                   user_name = os.getenv("USER")
               self._do_login_as_user(user_name)

        start_server_event = ProposalGUIEvent(self.startServers,())
        QApplication.postEvent(self, start_server_event)

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
                icon = QMessageBox.Critical
            elif stat is None:
                icon = QMessageBox.Warning
            elif stat is True:
                icon = QMessageBox.Information
            msg_dialog = QMessageBox("Register user", message, \
                icon, QMessageBox.Ok, QMessageBox.NoButton,\
                QMessageBox.NoButton, self)
            s = self.font().pointSize()
            f = msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.show()

        self.setEnabled(True)

    def acceptLogin(self, proposal_dict, session_dict):
        """
        Descript. :
        """
        #self.setProposal(proposal_dict, person_dict, lab_dict, 
        #                 session_dict, contact_dict)
        self.setProposal(proposal_dict, session_dict)
        self.setEnabled(True)

    def ispybDown(self):
        """
        Descript. :
        """
        msg_dialog = QMessageBox("Register user", "Couldn't contact " + \
            "the ISPyB database server: you've been logged as the local user.\n" + \
            "Your experiments' information will not be stored in ISPyB!",\
            QMessageBox.Warning, 
            QMessageBox.Ok, 
            QMessageBox.NoButton,
            QMessageBox.NoButton,self)
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
        lab_dict = {'name': 'lab'}
        cont_dict = {'familyName' : 'local contact'}
        #self.acceptLogin(prop_dict, pers_dict, lab_dict, ses_dict, cont_dict)
        self.acceptLogin(prop_dict, ses_dict)

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """
        self.saved_group = False
        Qt4_widget_colors.set_widget_color(self.user_group_ledit, 
                                           Qt4_widget_colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)

        if not self.login_as_user:
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
                lab_dict = {'name' : 'local lab'}
                cont_dict = {'familyName' : 'local contact'}
                logging.getLogger().debug("ProposalBrick: local login password validated")
             
                #return self.acceptLogin(prop_dict, pers_dict, lab_dict, ses_dict, cont_dict)
                return self.acceptLogin(prop_dict, ses_dict)

            if self.lims_hwobj == None:
                return self.refuseLogin(False,'Not connected to the ISPyB database, unable to get proposal.')

            self._do_login_as_proposal(prop_type, prop_number, prop_password, self.lims_hwobj.beamline_name)

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
        if property_name == 'codes':
            self.setCodes(new_value)
        elif property_name == 'localLogin':
            self.local_login_hwobj = self.getHardwareObject(new_value, optional=True)
        elif property_name == 'dbConnection':
            self.lims_hwobj = self.getHardwareObject(new_value)
            self.login_as_user = self.lims_hwobj.get_login_type() == "user"
            if self.login_as_user:
               self.login_as_user_widget.show()
               self.login_as_proposal_widget.hide()
            else:
               self.login_as_user_widget.hide()
               self.login_as_proposal_widget.show()
        elif property_name == 'instanceServer':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer,
                                'passControl',
                                self.passControl)
                self.disconnect(self.instanceServer,
                                'haveControl',
                                self.haveControl)
            self.instanceServer = self.getHardwareObject(new_value, optional=True)
            if self.instanceServer is not None:
                self.connect(self.instanceServer,
                             'passControl',
                             self.passControl)
                self.connect(self.instanceServer,
                             'haveControl',
                             self.haveControl)
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.login_button.setIcon(Qt4_Icons.load_icon(icons_list[0]))
            except IndexError:
                pass
            try:
                self.logout_button.setIcon(Qt4_Icons.load_icon(icons_list[1]))
            except IndexError:
                pass
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'secondaryProposals':
            self.secondary_proposals = new_value.split() 
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def _do_login_as_proposal(self, proposal_code, proposal_number, proposal_password, beamline_name, impersonate=False):
        """
        Descript. :
        """
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
        else:
            self.select_proposal(prop)
            BlissWidget.set_status_info("user", "%s%s@%s" % \
               (proposal_code, str(proposal_number), beamline_name))

    def proposal_combo_activated(self, item_index):
        self.select_proposal(self.proposals[item_index])

    def select_proposal(self, selected_proposal):
        beamline_name = self.lims_hwobj.beamline_name
        proposal = selected_proposal['Proposal']
        #person = selected_proposal['Person']
        #laboratory = selected_proposal['Laboratory']
        sessions = selected_proposal['Session']
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

                #if not self.askForNewSession():
                #    self.refuseLogin(None, None)
                #    return

            current_time = time.localtime()
            start_time = time.strftime("%Y-%m-%d 00:00:00", current_time)
            end_time = time.mktime(current_time) + 60 * 60 *24
            tomorrow = time.localtime(end_time)
            end_time = time.strftime("%Y-%m-%d 07:59:59", tomorrow)

            # Create a session
            new_session_dict = {}
            new_session_dict['proposalId'] = selected_proposal['Proposal']['proposalId']
            new_session_dict['startDate'] = start_time
            new_session_dict['endDate'] = end_time
            new_session_dict['beamlineName'] = beamline_name
            new_session_dict['scheduled'] = 0
            new_session_dict['nbShifts'] = 3
            new_session_dict['comments'] = "Session created by the BCM"
            session_id = self.lims_hwobj.create_session(new_session_dict)
            new_session_dict['sessionId'] = session_id

            todays_session = new_session_dict
            localcontact = None
        else:
            session_id = todays_session['sessionId']
            logging.getLogger().debug('ProposalBrick: getting local contact for %s' % session_id)
            localcontact = self.lims_hwobj.get_session_local_contact(session_id)

        #self.acceptLogin(selected_proposal['Proposal'], 
        #                 selected_proposal['Person'], 
        #                 selected_proposal['Laboratory'],
        #                 todays_session, 
        #                 localcontact)
        self.acceptLogin(selected_proposal['Proposal'], todays_session)
    
    def _do_login_as_user(self, user_name):
        logging.getLogger().debug('ProposalBrick: querying ISPyB database...')
 
        self.proposals = self.lims_hwobj.get_proposals_by_user(user_name)

        if len(self.proposals) == 0:
            logging.getLogger("GUI").error("No proposals for user %s found in ISPyB" % user_name)
            self.ispybDown()
        else: 
            self.proposal_combo.clear()
            proposal_tooltip = "Available proposals:"
            for proposal in self.proposals:
                proposal_info = "%s%s - %s" % (proposal["Proposal"]["code"],
                                               proposal["Proposal"]["number"],
                                               proposal["Proposal"]["title"])
                self.proposal_combo.addItem(proposal_info)
                proposal_tooltip += "\n   %s" % proposal_info
       
            if len(self.proposals) > 1:
                proposal_index = self.select_todays_proposal(self.proposals)
                self.proposal_combo.setEnabled(True)
            else:
                proposal_tooltip = ""
                proposal_index = 0
                self.proposal_combo.setEnabled(False)

            self.select_proposal(self.proposals[proposal_index])
            self.proposal_combo.setCurrentIndex(proposal_index)
            proposal_info = "%s%s - %s" % (
                self.proposals[proposal_index]["Proposal"]["code"],
                self.proposals[proposal_index]["Proposal"]["number"],                           
                self.proposals[proposal_index]["Proposal"]["title"])
            proposal_tooltip += "\nSelected proposal:\n   %s" % proposal_info
            self.proposal_combo.setToolTip(proposal_tooltip)
            logging.getLogger("GUI").info("ISPyB proposal: %s" % proposal_info)

            BlissWidget.set_status_info("user", "%s@%s" % \
               (user_name, self.lims_hwobj.beamline_name))

    def select_todays_proposal(self, proposal_list):
        """
        Descript. Selects a proposal that is assigned for current day
                  If no session found then returns first proposal
        """
        for prop_index, proposal in enumerate(proposal_list):
            sessions = proposal['Session']
            proposal_code_number = proposal["Proposal"]["code"] + \
                                   proposal["Proposal"]["number"]
            if len(sessions) > 0 and \
               not proposal_code_number in self.secondary_proposals:
                # Check for today's session
                for session in sessions:
                    beamline = session['beamlineName']
                    start_date = "%s 00:00:00" % session['startDate'].split()[0]
                    end_date = "%s 23:59:59" % session['endDate'].split()[0]
                    try:
                        start_struct = time.strptime(start_date,"%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                    else:
                        try:
                            end_struct = time.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass
                        else:
                            start_time = time.mktime(start_struct)
                            end_time = time.mktime(end_struct)
                            current_time = time.time()
                            # Check beamline name
                            if beamline == self.lims_hwobj.beamline_name:
                                # Check date
                                if current_time >= start_time and current_time <= end_time:
                                    return prop_index

              
        # If no proposal with valid session found then the last
        # proposal from the list is selected
        return len(proposal_list) - 1

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

