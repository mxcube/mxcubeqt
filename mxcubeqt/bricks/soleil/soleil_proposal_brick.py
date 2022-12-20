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
import string
from datetime import date
import subprocess

from mxcubeqt.utils import colors, icons, qt_import

from mxcubecore import HardwareRepository as HWR

from proposal_brick import ProposalBrick

from bag_info import BagInfo

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


#PROPOSAL_GUI_EVENT = qt_import.QEvent.User

class SoleilProposalBrick(ProposalBrick):
    
    #sessionSelected = qt_import.pyqtSignal(int, str, str, int, str, str, bool)
    #setWindowTitle = qt_import.pyqtSignal(str)
    #loggedIn = qt_import.pyqtSignal(bool)
    #userGroupSaved = qt_import.pyqtSignal(str)

    #NOBODY_STR = "<nobr><b>Login is required for collecting data!</b>"
    
    def __init__(self, *args):
        
        self.spacer_combo = qt_import.QComboBox()
        self.spacer_combo.setFixedWidth(100)
        self.spacer_combo.hide()
        
        self.spacer = qt_import.QSpacerItem(300, 10, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum)
        ProposalBrick.__init__(self, *args)
        self.proposal_number_ledit.setFixedWidth(100)
        
        self.bag_records = None
        self.bag_ldaplogin = None
        self.identifiers_location = '/etc/ispyb_identifiers'
        self.showing_proposal_details = False
        self.proposal_number_ledit.textChanged.connect(self.proposal_number_typed)
        self.proposal_number_ledit.returnPressed.connect(self.login)
        self.proposal_type_combox.hide()
        self.code_label.hide()
        self.dash_label.hide()
        self.password_label.hide()
        self.proposal_password_ledit.hide()
        self.log = logging.getLogger("GUI")
        self.root_log = logging.getLogger()

    def set_login_as_proposal_widget_layout(self):
        _login_as_proposal_widget_layout = qt_import.QHBoxLayout(
            self.login_as_proposal_widget
        )
        _login_as_proposal_widget_layout.addWidget(self.code_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_type_combox)
        _login_as_proposal_widget_layout.addWidget(self.dash_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_number_ledit)
        _login_as_proposal_widget_layout.addWidget(self.spacer_combo)
        _login_as_proposal_widget_layout.addWidget(self.password_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_password_ledit)
        _login_as_proposal_widget_layout.addItem(self.spacer)
        _login_as_proposal_widget_layout.addWidget(self.login_button)
        _login_as_proposal_widget_layout.addWidget(self.logout_button)
        _login_as_proposal_widget_layout.setSpacing(0)
        _login_as_proposal_widget_layout.setContentsMargins(0, 0, 0, 0)
            
    def login_successful(self, proposal_number=None):
        #self.root_log.info('proposal_dict %s ' % proposal_dict)
        #self.root_log.info('session_dict %s ' % session_dict)
        if proposal_number in ["", None]:
            proposal_number = subprocess.getoutput('whoami')
        #self.set_proposal(proposal_dict, session_dict)
        self.setEnabled(True)
        for widget in [self.proposal_number_ledit, self.user_group_ledit, self.proposal_password_ledit]: 
            colors.set_widget_color(widget, colors.LIGHT_GREEN, qt_import.QPalette.Base)
        self.spacer_combo.setStyleSheet("QComboBox {{ background-color: rgb{};}}".format(colors.LIGHT_GREEN.getRgb()))
        self.proposal_type_combox.hide()
        #self.spacer_combo.hide()
        self.dash_label.hide()
        #self.password_label.hide()
        #self.proposal_password_ledit.hide()
        if proposal_number is not None:
            self.proposal_number_ledit.setText(str(proposal_number))
    
    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """
        self.root_log.info('login()')
        self.saved_group = False
        colors.set_widget_color(self.user_group_ledit, 
                                           colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)
        
        self.root_log.info('self.login_as_user %s' % self.login_as_user)
        if not self.login_as_user:
            prop_type = str(self.proposal_type_combox.currentText())
            prop_number = str(self.proposal_number_ledit.text())
            prop_password = str(self.proposal_password_ledit.text())
            self.proposal_password_ledit.setText("")
            
            if self.bag_records:
                idx = self.spacer_combo.currentIndex()
                if idx > 0:
                    self.bag_user = self.bag_records[idx-1]
                    project_id = self.bag_user.projectid
                    #project_id = os.path.join(prop_number, self.bag_user.ldaplogin)
                    self.bag_ldaplogin = self.bag_user.ldaplogin
                    self.root_log.info("user is " + \
                        "{0.proposal} ({0.ldaplogin}) / ProjectID: {0.projectid}".format(self.bag_user))
                    self.root_log.info('bag_user %s' % str(self.bag_user))
                else:
                    project_id = None
                    self.bag_user = None
                    self.bag_ldaplogin = None
            else:
                project_id = None
                self.bag_user = None
            
            self.root_log.info("prop_number is %s (project_id=%s)" % (prop_number, project_id))
            
            if prop_type == "" and prop_number == "":
                if self.local_login_hwobj is None:
                    return self.refuse_login(False,"Local login not configured.")
                try:
                    locallogin_password = self.local_login_hwobj.password
                except AttributeError:
                    return self.refuse_login(False,"Local login not configured.")

                if prop_password != locallogin_password:
                    return self.refuse_login(None,"Invalid local login password.")

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
                self.log.debug("local login password validated")
             
                #return self.accept_login(prop_dict, pers_dict, lab_dict, ses_dict, cont_dict)
                return self.accept_login(prop_dict, ses_dict)

            if HWR.beamline.lims == None:
                return self.refuse_login(False,'Not connected to the ISPyB database, unable to get proposal.')

            try:
                if project_id != None:
                    self._do_login_as_proposal(prop_type, project_id, prop_password, HWR.beamline.lims.beamline_name)
                else:
                    self._do_login_as_proposal(prop_type, prop_number, prop_password, HWR.beamline.lims.beamline_name)
                self.login_successful(proposal_number=prop_number)
            except:
                import traceback
                self.root_log.info(traceback.format_exc())
                traceback.print_exc()
                self.root_log.info('Problem communicating with ISPyB, trying to log in as a local user')
                now = time.strftime("%Y-%m-%d %H:%M:S")
                prop_dict = {'code' : '', 'number' : '', 'title' : '', 'proposalId' : ''}
                ses_dict = {'sessionId' : '', 'startDate' : now, 'endDate' : now, 'comments' : ''}
                self.accept_login(prop_dict, ses_dict)
                self.login_successful()

    def logout_clicked(self):
        self.log_out()
        
    def log_out(self):
        # Reset brick info
        #self.proposal_number_ledit.setText("")
        self.proposal = None
        # self.sessionId=None
        self.person = None
        self.laboratory = None
        # Change mode from logout to login
        if not self.login_as_user:
            self.login_as_proposal_widget.setEnabled(True)
            self.login_button.show()
            self.logout_button.hide()
        # self.title_label.hide()
        #self.user_group_widget.hide()
        self.spacer_combo.clear()
        self.spacer_combo.hide()
        # resets active proposal
        self.reset_proposal()

        # self.proposalLabel.setText(ProposalBrick2.NOBODY_STR)
        # QToolTip.add(self.proposalLabel,"")

        # Emit signals clearing the proposal and session
        #self.setWindowTitle.emit(self["titlePrefix"])
        # self.sessionSelected.emit(None, None, None, None, None, None, None)
        self.loggedIn.emit(False)
        
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
        #logging.info('check_proposal_details')
        cur_text = str(self.proposal_number_ledit.text())
        #logging.info('check_proposal_details %s' % cur_text)
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
        
        if bag_records is not None and len(bag_records):
            logging.info('check_proposal_details bag_records %s' % bag_records)
        self.bag_records = bag_records
        
    def hide_proposal_details(self):
        self.proposal_combo.hide()
        self.spacer_combo.show()

    def show_proposal_details(self, bag_info):
        self.spacer_combo.show()
        names = ['no group']
        for record in bag_info:
             names.append(record.ldaplogin)
        self.spacer_combo.clear()
        self.spacer_combo.addItems(names)
        self.log.info('proposal_combo names %s' % names)
        #self.spacer_combo.hide()

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
        
    def set_proposal(self, proposal, session):
        HWR.beamline.lims.enable()
        HWR.beamline.session.proposal_code = proposal["code"]
        HWR.beamline.session.session_id = session["sessionId"]
        HWR.beamline.session.proposal_id = proposal["proposalId"]
        HWR.beamline.session.proposal_number = proposal["number"]

        HWR.beamline.session.set_proposal(code=proposal['code'],
                                          number=proposal['number'], 
                                          proposal_id=proposal['proposalId'], 
                                          session_id=session['sessionId'],
                                          bag_ldaplogin=self.bag_ldaplogin)
        
        # Change mode
        if not self.login_as_user:
            self.login_button.hide()
            self.login_as_proposal_widget.setDisabled(True)
            self.logout_button.show()

        # Store info in the brick
        self.proposal = proposal
        self.log.info('self.proposal %s' % self.proposal)
        self.session = session
        self.log.info('self.proposal %s' % self.session)
        
        code = proposal["code"].lower()
        self.log.info("code %s" % code)
        
        if code == "":
            self.root_log.warning(
                "Using local login: the data collected won't be stored in the database"
            )
            HWR.beamline.lims.disable()
            self.loggedIn.emit(False)
        else:
            msg = "Results in ISPyB will be stored under proposal %s%s - '%s'" % (
                proposal["code"],
                str(proposal["number"]),
                proposal["title"],
            )
            self.log.info(msg)
            self.loggedIn.emit(True)
        #header = ""
        ## Set interface info and signal the new session
        #proposal_text = "%s-%s" % (proposal['code'], proposal['number'])
        ##self.title_label.setText("<nobr>   User: <b>%s</b>" % proposal_text)
        #tooltip = "\n".join([proposal_text, header, title]) 
        #if comments:
            #tooltip += '\n'
            #tooltip += 'Comments: ' + comments 
        #self.title_label.setToolTip(tooltip)
        #self.user_group_widget.show()
        #self.user_group_ledit.setText("%s" % self.bag_ldaplogin)
        #self.user_group_ledit.setEnabled(False)
        
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
