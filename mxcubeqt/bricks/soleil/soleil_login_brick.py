#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import time
import logging

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR

import string
from datetime import date
from bag_info import BagInfo

__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "SOLEIL"


PROPOSAL_GUI_EVENT = qt_import.QEvent.User

class ProposalGUIEvent(QEvent):
    """
    Descript. :
    """
    def __init__(self, method, arguments):
        qt_import.QEvent.__init__(self, PROPOSAL_GUI_EVENT)
        self.method = method
        self.arguments = arguments

class SoleilLoginBrick(BaseWidget):
    """
    Descript. :
    """
    sessionSelected = qt_import.pyqtSignal(int, str, str, int, str, str, bool)
    setWindowTitle = qt_import.pyqtSignal(str)
    loggedIn = qt_import.pyqtSignal(bool)
    userGroupSaved = qt_import.pyqtSignal(str)

    NOBODY_STR = "<nobr><b>Login is required for collecting data!</b>"

    def __init__(self, *args):
        """
        Proposal brick is used to authentificate current user.
        Brick can be used in two modes defined by ispyb hwobj
         - loginAsUser = True, Brick displays combobox with all
           proposals from ISPyB that are associated to the current user
         - loginAsUser = False. Brick displays combobox to choose proposal
           type and linedits to enter proposal number and password.
           In this case user is authentificated with
           LDAP and proposal from ISPyB is retrieved.
        """
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.lims_hwobj = None
        self.local_login_hwobj = None
        self.session_hwobj = None

        # Internal values -----------------------------------------------------
        self.instanceServer = None
        self.bag_records = None
        self.bag_user = None

        # Properties ----------------------------------------------------------
        self.add_property("instanceServer", "string", "")
        self.add_property("localLogin", "string", "")
        self.add_property("titlePrefix", "string", "")
        self.add_property("autoSessionUsers", "string", "")
        self.add_property("codes", "string", "fx ifx ih im ix ls mx opid")
        self.add_property("secondaryProposals", "string", "")
        self.add_property("icons", "string", "")
        self.add_property("serverStartDelay", "integer", 500)
        self.add_property("dbConnection", "string")

        # Signals ------------------------------------------------------------
        self.define_signal("sessionSelected", ())
        self.define_signal("setWindowTitle", ())
        self.define_signal("loggedIn", ())
        self.define_signal("userGroupSaved", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("setButtonEnabled", ())
        self.define_slot("impersonateProposal", ())

        # Graphic elements ----------------------------------------------------
        self.main_gbox = qt_import.QGroupBox("ISPyB proposal", self)

        self.login_as_proposal_widget = qt_import.QWidget(self.main_gbox)
        code_label = qt_import.QLabel("  Code: ", self.login_as_proposal_widget)
        self.proposal_type_combox = qt_import.QComboBox(self.login_as_proposal_widget)
        self.proposal_type_combox.setEditable(True)
        self.proposal_type_combox.setFixedWidth(60)
        dash_label = qt_import.QLabel(" - ", self.login_as_proposal_widget)
        self.proposal_number_ledit = qt_import.QLineEdit(self.login_as_proposal_widget)
        self.proposal_number_ledit.setFixedWidth(60)
        password_label = qt_import.QLabel("   Password: ", self.login_as_proposal_widget)
        self.proposal_password_ledit = qt_import.QLineEdit(self.login_as_proposal_widget)
        self.proposal_password_ledit.setEchoMode(qt_import.QLineEdit.Password)
        # self.proposal_password_ledit.setFixedWidth(40)
        self.login_button = qt_import.QPushButton("Login", self.login_as_proposal_widget)
        self.login_button.setFixedWidth(70)
        self.logout_button = qt_import.QPushButton("Logout", self.main_gbox)
        self.logout_button.hide()
        self.logout_button.setFixedWidth(70)
        self.login_as_proposal_widget.hide()

        self.login_as_user_widget = qt_import.QWidget(self.main_gbox)
        self.proposal_combo = qt_import.QComboBox(self.login_as_user_widget)

        self.user_group_widget = qt_import.QWidget(self.main_gbox)
        # self.title_label = QtGui.QLabel(self.user_group_widget)
        # self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.user_group_label = qt_import.QLabel("  Group: ", self.user_group_widget)
        self.user_group_ledit = qt_import.QLineEdit(self.user_group_widget)
        self.user_group_ledit.setFixedSize(100, 27)
        self.user_group_save_button = qt_import.QToolButton(self.user_group_widget)
        self.user_group_save_button.setText("Set")
        self.user_group_save_button.setFixedHeight(27)
        self.saved_group = True

        # Layout --------------------------------------------------------------
        _user_group_widget_hlayout = qt_import.QHBoxLayout(self.user_group_widget)
        _user_group_widget_hlayout.setSpacing(2)
        # _user_group_widget_hlayout.addWidget(self.title_label)
        _user_group_widget_hlayout.addWidget(self.user_group_label)
        _user_group_widget_hlayout.addWidget(self.user_group_ledit)
        _user_group_widget_hlayout.addWidget(self.user_group_save_button)
        _user_group_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.user_group_widget.hide()

        _login_widget = QHBoxLayout(self.login_widget)
        _login_widget.addWidget(self.username_label)
        _login_widget.addWidget(self.proposal_number_ledit)
        _login_widget.addWidget(self.proposal_combo) 
        _login_widget.addWidget(self.spacer_combo) 
        _login_widget.addWidget(password_label)
        _login_widget.addWidget(self.proposal_password_ledit)
        _login_widget.addWidget(self.login_button)
        _login_widget.setSpacing(2)
        _login_widget.setContentsMargins(0, 0, 0, 0)

        _main_gboxlayout = QHBoxLayout(self.main_gbox)
        _main_gboxlayout.addWidget(self.login_widget)
        _main_gboxlayout.addWidget(self.logout_button)
        #_main_vlayout.addSpacing(10)
        _main_gboxlayout.addWidget(self.user_group_widget)
        _main_gboxlayout.setSpacing(2)
        _main_gboxlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.proposal_password_ledit.returnPressed.connect(self.login)
        self.login_button.clicked.connect(self.login)
        self.logout_button.clicked.connect(self.logout_clicked)  
        self.user_group_save_button.clicked.connect(self.save_user_group)
        self.user_group_ledit.returnPressed.connect(self.save_user_group)
        self.user_group_ledit.textChanged.connect(self.user_group_changed)

        # Other ---------------------------------------------------------------
        Qt4_widget_colors.set_widget_color(self.proposal_number_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QPalette.Base)
        Qt4_widget_colors.set_widget_color(self.proposal_password_ledit,
                                           Qt4_widget_colors.LIGHT_RED,
                                           QPalette.Base)
 
    def run(self):
        """
        Descript. :
        """
        self.setEnabled(self.session_hwobj is not None)

        # find if we are using dbconnection, etc. or not
        if not self.lims_hwobj:
            self.set_widget_logout_mode()
            self.logout_button.hide()
            self.title_label.setText("<nobr><b>%s</b></nobr>" % os.environ["USER"])
            self.title_label.show()
            self.user_group_widget.show()

            self.session_hwobj.set_proposal() # reset to default values
    
            self.setWindowTitle.emit(self["titlePrefix"])
            self.loggedIn.emit(True)
            self.sessionSelected.emit(self.session_hwobj.session_id,
                 str(os.environ["USER"]), 0, '', '',
                 self.session_hwobj.session_id, False)
        else: 
            self.setWindowTitle.emit(self["titlePrefix"])
            self.loggedIn.emit(False)

        start_server_event = ProposalGUIEvent(self.start_servers,())
        QApplication.postEvent(self, start_server_event)

    def property_changed(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'localLogin':
            self.local_login_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'login_title':
            self.main_gbox.setTitle(new_value) 
        elif property_name == 'dbConnection':
            self.lims_hwobj = self.getHardwareObject(new_value)

            try:
                self.identifiers_location = self.lims_hwobj.get_identifiers_location()
            except:
                self.identifiers_location = None

            self.login_widget.show()
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'instanceServer':
            if self.instanceServer is not None:
                self.disconnect(self.instanceServer,
                                'passControl',
                                self.pass_control)
                self.disconnect(self.instanceServer,
                                'haveControl',
                                self.have_control)
            self.instanceServer = self.getHardwareObject(new_value)
            if self.instanceServer is not None:
                self.connect(self.instanceServer,
                             'passControl',
                             self.pass_control)
                self.connect(self.instanceServer,
                             'haveControl',
                             self.have_control)
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.login_button.setIcon(icons.load_icon(icons_list[0]))
            except IndexError:
                pass
            try:
                self.logout_button.setIcon(icons.load_icon(icons_list[1]))
            except IndexError:
                pass
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def start_servers(self):
        """
        Descript. :
        """
        if self.instanceServer is not None:
            self.instanceServer.initializeInstance()

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
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception as diag:
                            logging.getLogger().exception("Qt4_ProposalBrick2: uncaught exception! (%s)" % str(diag))
                        except:
                            logging.getLogger().exception("Qt4_ProposalBrick2: uncaught exception!")
                        else:
                            pass
                    else:
                        logging.getLogger().warning('Qt4_ProposalBrick2: uncallable custom event!')

    def pass_control(self, has_control_id):
        """
        Descript. :
        """
        pass

    def have_control(self, have_control):
        """
        Descript. :
        """
        pass

    def user_group_changed(self, value):
        """
        Descript. :
        """
        cursor_pos = self.user_group_ledit.cursorPosition()
        cur_text = str(self.user_group_ledit.text())

        if len(cur_text) > 0:
            valid_chars = string.ascii_lowercase + string.ascii_uppercase + \
                              string.digits + "-_"
            cur_text = ''.join(i for i in str(cur_text) if i in valid_chars)

        self.user_group_ledit.setText(cur_text)
        self.user_group_ledit.setCursorPosition(cursor_pos)

        if self.saved_group:
            msg = 'User group changed, press set to apply change'
            logging.getLogger("GUI").warning(msg)
            colors.set_widget_color(self.user_group_ledit,
                                               colors.LINE_EDIT_CHANGED,
                                               QPalette.Base)
            self.saved_group = False
        
    def save_user_group(self):
        """
        Descript. :
        """
        colors.set_widget_color(self.user_group_ledit,
               colors.LIGHT_GREEN,
               QPalette.Base)  

        user_group = str(self.user_group_ledit.text())
        self.userGroupSaved.emit(user_group)

        self.saved_group = True
            
    def reset_user_group(self):
        self.saved_group = False
        colors.set_widget_color(self.user_group_ledit, 
                                           colors.WHITE)
        self.user_group_ledit.setText('')

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """

        # local  users are not writing in ispyb
        # master users are local users with special right to control remote access 
        # master users are also local users
        #     if no master user defined in system, all local users are master

        prop_number = str(self.proposal_number_ledit.text())
        prop_password = str(self.proposal_password_ledit.text())
        self.proposal_password_ledit.setText("")

        if self.bag_records:
            idx = self.proposal_combo.currentIndex()
            if idx > 0:
                self.bag_user = self.bag_records[idx-1]
                project_id = self.bag_user.projectid
                logging.getLogger("HWR").debug("LoginBrick: user is " + \
                    "{0.proposal} ({0.ldaplogin}) / ProjectID: {0.projectid}".format(self.bag_user))
            else:
                project_id = None
                self.bag_user = None
        else:
            project_id = None
            self.bag_user = None

        logging.getLogger("HWR").debug("LoginBrick: user is %s (project_id=%s)" % (prop_number, project_id))

        self.reset_user_group()
        self.setEnabled(False)

        is_locallogin = False
        is_master = False  

        if prop_number == "": 
            # check if locallogin ok
            if self.local_login_hwobj is None:
                return self.refuse_login(False,"Local login not configured.")

            try:
                locallogin_password = self.local_login_hwobj.password
            except AttributeError:
                return self.refuse_login(False,"Local login not configured.")

            if prop_password != locallogin_password:
                return self.refuse_login(None,"Invalid local login password.")

            try:
                locallogin_person = self.local_login_hwobj.person
            except AttributeError:
                locallogin_person = "local user"

            is_locallogin = True
            is_master = False
        else:
            # a user name is provided / check if master user
            try:
                master_name = self.session_hwobj.is_master_user(prop_number, prop_password, check_password=True)
                if master_name:
                    logging.getLogger("HWR").debug("ProposalBrick: Login as master user")
                    locallogin_person = master_name
                    is_locallogin = True
                    is_master = True
            except:
                import traceback
                logging.getLogger("HWR").debug("ProposalBrick: error looking for master user: %s" % traceback.format_exc())

        if is_locallogin:
            now = time.strftime("%Y-%m-%d %H:%M:S")
            if is_master:
                prop_dict = {'code' : '', 'number' : prop_number, 'title' : '', 'proposalId' : ''}
            else:
                prop_dict = {'code' : '', 'number' : '', 'title' : '', 'proposalId' : ''}
            ses_dict = {'sessionId' : '', 'startDate' : now, 'endDate' : now, 'comments' : ''}

            logging.getLogger().debug("ProposalBrick: local login password validated")

            return self.accept_login(prop_dict, ses_dict, is_master)

        elif self.lims_hwobj == None:
            return self.refuse_login(False,'Not connected to the ISPyB database, unable to get proposal.')

        # if we got this far... it should be a user to be checked in lims
        self._do_lims_login(prop_number, prop_password, project_id)

    def _do_lims_login(self, proposal_number, proposal_password, project_id):
        """
        Descript. :
        """

        # Get proposal and sessions
        if project_id:
            login_name = project_id
            ldap_name = proposal_number
        else:
            login_name = proposal_number
            ldap_name = proposal_number

        prop = self.lims_hwobj.login(login_name, proposal_password, ldap_name=ldap_name)

        ispybdown = False

        # Check if everything went ok
        try:
            prop_ok = (prop['status']['code'] == 'ok')
            if not prop_ok:
               ispybdown = (prop['status']['code'] == 'ispybDown')
        except KeyError:
            prop_ok = False
        except:
            import traceback
            logging.getLogger().debug('ProposalBrick: cannot login / %s ' % traceback.format_exc())
            prop_ok = False

        if not prop_ok:
            # maybe ispyb is down
            if ispybdown:
                self.ispyb_is_down(proposal=prop['Proposal'])
            else:
                self.refuse_login(False,prop['status']['msg'])
            return
        
        logging.getLogger("HWR").debug( str(prop) )
        self.accept_login(prop['Proposal'], prop['Session']['session'])

        BaseWidget.set_status_info("user", str(proposal_number), str(proposal_number))

    def logout_clicked(self):
        """
        Description: Opens the logout dialog (modal); 
              If the answer is OK then logout the user
        """
        if QMessageBox.question(self, "Confirm logout", 
            "Press OK to logout.", QMessageBox.Ok,
            QMessageBox.Cancel) == QMessageBox.Ok:
            self._do_logout()

    # Logout the user; reset the brick; changes from logout mode to login mode
    def _do_logout(self):
        """
        Descript. :
        """
        # Change mode from logout to login
        self.setWindowTitle.emit(self["titlePrefix"])
        self.proposal_number_ledit.setText("")
        self.set_widget_login_mode()

        #resets active proposal
        self.reset_proposal()
 
        # Emit signals 
        self.loggedIn.emit(False)

        # Inform general app status
        BaseWidget.set_status_info("user", "","")

    def ispyb_is_down(self, proposal=None):
        """
        Descript. :
        """
        msg = "Couldn't contact the ISPyB database server: " + \
            "Your experiments information will not be stored in ISPyB!"

        self.show_popup_message(msg, title="Register user", message_type='warning')

        now = time.strftime("%Y-%m-%d %H:%M:S")
        if proposal is not None:
            prop_dict = {'code' : proposal['code'], 'number' : proposal['number'], 'title' : '', 'proposalId' : ''}
        else:
            prop_dict = {'code' : '', 'number' : '', 'title' : '', 'proposalId' : ''}

        ses_dict = {'sessionId' : '', 'startDate' : now, 'endDate' : now, 'comments' : ''}

        self.accept_login(prop_dict, ses_dict)

    def accept_login(self, proposal_dict ,ses_dict,is_master=False):
        """
        Descript. :
        """
        self.set_proposal(proposal_dict, ses_dict, is_master)

        # Emit signals

        prop_number = proposal_dict["number"]
        prop_code = proposal_dict["code"]
        prop_id = proposal_dict["proposalId"]

        session_id = ses_dict['sessionId']
        start_date = ses_dict['startDate']

        gui_user = self.lims_hwobj.translate(prop_code, "gui") 
        is_inhouse = self.session_hwobj.is_inhouse(prop_code, prop_number)

        win_title = "%s (%s-%s)" % (self["titlePrefix"], gui_user, prop_number)

        self.setWindowTitle.emit(win_title)
        self.sessionSelected.emit(
                  session_id, 
                  gui_user,
                  str(prop_number),
                  prop_id,
                  start_date,
                  prop_code,
                  is_inhouse)

        self.loggedIn.emit(True)

        # Change mode

        self.set_widget_logout_mode()
        self.setEnabled(True)

    def refuse_login(self, stat, message = None):
        """
        Descript. :
        """
        if message is not None:
            if stat is False:
                mtype = 'error'
            elif stat is None:
                mtype = 'warning'
            elif stat is True:
                mtype = 'info'

            self.show_popup_message( message, title='Register user', message_type=mtype)

        self.setEnabled(True)

    # Sets the current session; changes from login mode to logout mode
    def set_proposal(self, proposal, session, is_master=False):
        """
        Descript. :
        """

        self.lims_hwobj.enable()
        self.session_hwobj.set_proposal(code=proposal['code'],
                                       number=proposal['number'], 
                                       proposal_id=proposal['proposalId'], 
                                       session_id=session['sessionId'] )


        code = proposal["code"].lower()

        if code == "":
            session_id = ""
            if is_master:
                is_inhouse = True
                logging.getLogger().warning("Using master login: the data collected won't be stored in the database")
            else:
                is_inhouse = False
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

            # Build the info for the interface
            title = str(proposal['title'])
            session_id = session['sessionId']
            start_date = session['startDate'].split()[0]
            end_date = session['endDate'].split()[0]

            try:
                comments = session['comments']
            except KeyError:
                comments = None


            # Set interface info and signal the new session
            proposal_text = proposal['number']
            if self.bag_user:
                bag_text = "{0.proposal} ({0.ldaplogin})".format(self.bag_user)
                title_text = bag_text
            else:
                title_text = proposal_text

            self.title_label.setText("<nobr>   User: <b>%s</b>" % title_text)
            
            tooltip = "ID: " + proposal_text
            if self.bag_user:
                tooltip += "\n" + bag_text

            tooltip += "\n\n" + title 
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


    def reset_proposal(self):
        """
        Descript. :
        """
        self.session_hwobj.set_proposal()

    def set_widget_login_mode(self):
        self.login_widget.setEnabled(True)
        self.login_widget.show()
        self.login_button.show()
        self.spacer_combo.show()
        self.proposal_combo.show()
        self.logout_button.hide()
        self.title_label.hide()
        self.user_group_widget.hide()
        self.hide_proposal_details()
        self.showing_proposal_details = False

    def set_widget_logout_mode(self):
        self.login_button.hide()
        self.login_widget.setDisabled(True)
        self.login_widget.hide()
        self.logout_button.show()
        self.title_label.show()
        self.hide_proposal_details()
        self.showing_proposal_details = False

    def proposal_number_typed(self, txt):
         # Only accepts typing up to 8 digits

        cursor_pos = self.proposal_number_ledit.cursorPosition()
        cur_text = str(self.proposal_number_ledit.text())

        if len(cur_text) > 0:
            valid_chars = string.digits + \
                      string.ascii_lowercase + string.ascii_uppercase 
            cur_text = ''.join(i for i in str(cur_text) if i in valid_chars)

        if len(cur_text) > 8:
            cur_text = cur_text[:8]

        self.check_proposal_details()  

        self.proposal_number_ledit.setText(cur_text)
        self.proposal_number_ledit.setCursorPosition(cursor_pos)

    def check_proposal_details(self):
        cur_text = str(self.proposal_number_ledit.text())

        if len(cur_text) == 8 and re.match('^\d{8}$',cur_text):
             # 8 digits could be a proposal / see if in bag system
             bag_records = self.get_baginfo(cur_text)
        else:
             bag_records = None

        if bag_records:
            self.show_proposal_details(bag_records)
            self.showing_proposal_details = True
        elif self.showing_proposal_details:
            self.hide_proposal_details()
            self.showing_proposal_details = False

        self.bag_records = bag_records
    
    def hide_proposal_details(self):
        self.proposal_combo.hide()
        self.spacer_combo.show()

    def show_proposal_details(self, bag_info):
        self.proposal_combo.show()
        names = ['no group']
        for record in bag_info:
             names.append(record.ldaplogin)
        self.proposal_combo.clear()
        self.proposal_combo.addItems( names )
        self.spacer_combo.hide()

    def get_baginfo(self, proposal):
        self.baginfo = BagInfo(location=self.identifiers_location)

        prop_info = self.baginfo.get_proposal(proposal, proptype='bag')
        if prop_info:
            today = date.today()
            #t_date = (2018,9,19)
            #t_date = (2015,11,21)
            t_date = (today.year, today.month, today.day)
      
            bag_records = prop_info.get_valid_records(t_date)
            return bag_records
        else:
            return None

    def show_popup_message(self, message, title, message_type):
        if message_type == 'info':
            icon = QMessageBox.Information
        elif message_type == 'warning':
            icon = QMessageBox.Warning
        elif message_type == 'error':
            icon = QMessageBox.Critical
        else:
            icon = QMessageBox.Information

        msg_dialog = QMessageBox(icon, title, message, \
                QMessageBox.NoButton,  self)

        s = self.font().pointSize()
        f = msg_dialog.font()
        f.setPointSize(s)
        msg_dialog.setFont(f)
        msg_dialog.updateGeometry()
        msg_dialog.show()


