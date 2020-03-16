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

from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


PROPOSAL_GUI_EVENT = QtImport.QEvent.User


class ProposalGUIEvent(QtImport.QEvent):
    def __init__(self, method, arguments):
        QtImport.QEvent.__init__(self, PROPOSAL_GUI_EVENT)
        self.method = method
        self.arguments = arguments


class ProposalBrick(BaseWidget):

    sessionSelected = QtImport.pyqtSignal(int, str, str, int, str, str, bool)
    setWindowTitle = QtImport.pyqtSignal(str)
    loggedIn = QtImport.pyqtSignal(bool)
    userGroupSaved = QtImport.pyqtSignal(str)

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
        self.local_login_hwobj = None

        # Internal values -----------------------------------------------------
        self.login_as_user = None

        self.proposal = None
        self.person = None
        self.laboratory = None
        # self.sessionId=None
        self.inhouseProposal = None
        self.instance_server_hwobj = None
        self.secondary_proposals = []

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
        self.main_gbox = QtImport.QGroupBox("ISPyB proposal", self)

        self.login_as_proposal_widget = QtImport.QWidget(self.main_gbox)
        code_label = QtImport.QLabel("  Code: ", self.login_as_proposal_widget)
        self.proposal_type_combox = QtImport.QComboBox(self.login_as_proposal_widget)
        self.proposal_type_combox.setEditable(True)
        self.proposal_type_combox.setFixedWidth(60)
        dash_label = QtImport.QLabel(" - ", self.login_as_proposal_widget)
        self.proposal_number_ledit = QtImport.QLineEdit(self.login_as_proposal_widget)
        self.proposal_number_ledit.setFixedWidth(60)
        password_label = QtImport.QLabel("   Password: ", self.login_as_proposal_widget)
        self.proposal_password_ledit = QtImport.QLineEdit(self.login_as_proposal_widget)
        self.proposal_password_ledit.setEchoMode(QtImport.QLineEdit.Password)
        # self.proposal_password_ledit.setFixedWidth(40)
        self.login_button = QtImport.QPushButton("Login", self.login_as_proposal_widget)
        self.login_button.setFixedWidth(70)
        self.logout_button = QtImport.QPushButton("Logout", self.main_gbox)
        self.logout_button.hide()
        self.logout_button.setFixedWidth(70)
        self.login_as_proposal_widget.hide()

        self.login_as_user_widget = QtImport.QWidget(self.main_gbox)
        self.proposal_combo = QtImport.QComboBox(self.login_as_user_widget)

        self.user_group_widget = QtImport.QWidget(self.main_gbox)
        # self.title_label = QtGui.QLabel(self.user_group_widget)
        # self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.user_group_label = QtImport.QLabel("  Group: ", self.user_group_widget)
        self.user_group_ledit = QtImport.QLineEdit(self.user_group_widget)
        self.user_group_ledit.setFixedSize(100, 27)
        self.user_group_save_button = QtImport.QToolButton(self.user_group_widget)
        self.user_group_save_button.setText("Set")
        self.user_group_save_button.setFixedHeight(27)
        self.saved_group = True

        # Layout --------------------------------------------------------------
        _user_group_widget_hlayout = QtImport.QHBoxLayout(self.user_group_widget)
        _user_group_widget_hlayout.setSpacing(2)
        # _user_group_widget_hlayout.addWidget(self.title_label)
        _user_group_widget_hlayout.addWidget(self.user_group_label)
        _user_group_widget_hlayout.addWidget(self.user_group_ledit)
        _user_group_widget_hlayout.addWidget(self.user_group_save_button)
        _user_group_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.user_group_widget.hide()

        _login_as_proposal_widget_layout = QtImport.QHBoxLayout(
            self.login_as_proposal_widget
        )
        _login_as_proposal_widget_layout.addWidget(code_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_type_combox)
        _login_as_proposal_widget_layout.addWidget(dash_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_number_ledit)
        _login_as_proposal_widget_layout.addWidget(password_label)
        _login_as_proposal_widget_layout.addWidget(self.proposal_password_ledit)
        _login_as_proposal_widget_layout.addWidget(self.login_button)
        _login_as_proposal_widget_layout.setSpacing(2)
        _login_as_proposal_widget_layout.setContentsMargins(0, 0, 0, 0)

        _login_as_user_widget_layout = QtImport.QHBoxLayout(self.login_as_user_widget)
        _login_as_user_widget_layout.addWidget(self.proposal_combo)
        _login_as_user_widget_layout.setSpacing(2)
        _login_as_user_widget_layout.setContentsMargins(0, 0, 0, 0)

        _main_gboxlayout = QtImport.QHBoxLayout(self.main_gbox)
        _main_gboxlayout.addWidget(self.login_as_proposal_widget)
        _main_gboxlayout.addWidget(self.logout_button)
        _main_gboxlayout.addWidget(self.login_as_user_widget)
        _main_gboxlayout.addStretch()
        _main_gboxlayout.addWidget(self.user_group_widget)
        _main_gboxlayout.setSpacing(2)
        _main_gboxlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
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
        Colors.set_widget_color(
            self.proposal_number_ledit, Colors.LIGHT_RED, QtImport.QPalette.Base
        )
        Colors.set_widget_color(
            self.proposal_password_ledit, Colors.LIGHT_RED, QtImport.QPalette.Base
        )

    def save_group(self):
        user_group = str(self.user_group_ledit.text())

        pattern = r"^[a-zA-Z0-9_-]*$"
        valid = re.match(pattern, user_group, flags=0).group() == user_group

        if valid:
            self.saved_group = True
            Colors.set_widget_color(
                self.user_group_ledit, Colors.LIGHT_GREEN, QtImport.QPalette.Base
            )
            msg = "User group set to: %s" % str(self.user_group_ledit.text())
            logging.getLogger("GUI").info(msg)
            self.userGroupSaved.emit(self.user_group_ledit.text())
        else:
            msg = "User group not valid, please enter a valid user group"
            logging.getLogger("GUI").info(msg)
            Colors.set_widget_color(
                self.user_group_ledit, Colors.LIGHT_RED, QtImport.QPalette.Base
            )

    def user_group_changed(self, value):
        if self.saved_group:
            msg = "User group changed, press set to apply change"
            logging.getLogger("GUI").warning(msg)
            Colors.set_widget_color(
                self.user_group_ledit, Colors.LINE_EDIT_CHANGED, QtImport.QPalette.Base
            )
        self.saved_group = False

    def customEvent(self, event):
        if self.is_running():
            if event.type() == PROPOSAL_GUI_EVENT:
                try:
                    method = event.method
                    arguments = event.arguments
                except (Exception, diag):
                    logging.getLogger().exception(
                        "ProposalBrick2: problem in event! (%s)" % str(diag)
                    )
                except BaseException:
                    logging.getLogger().exception("ProposalBrick2: problem in event!")
                else:
                    # logging.getLogger().debug("ProposalBrick2: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception as diag:
                            logging.getLogger().exception(
                                "ProposalBrick2: uncaught exception! (%s)" % str(diag)
                            )
                        except BaseException:
                            logging.getLogger().exception(
                                "ProposalBrick2: uncaught exception!"
                            )
                        else:
                            # logging.getLogger().debug("ProposalBrick2: custom event finished")
                            pass
                    else:
                        logging.getLogger().warning(
                            "ProposalBrick2: uncallable custom event!"
                        )

    # Enabled/disabled the login/logout button
    def setButtonEnabled(self, state):
        self.login_button.setEnabled(state)
        self.logout_button.setEnabled(state)

    def impersonateProposal(self, proposal_code, proposal_number):
        if BaseWidget.is_instance_user_id_inhouse():
            self._do_login_as_proposal(
                proposal_code,
                proposal_number,
                None,
                HWR.beamline.lims.beamline_name,
                impersonate=True,
            )
        else:
            logging.getLogger().debug(
                "ProposalBrick2: cannot impersonate unless logged as the inhouse user!"
            )

    # Opens the logout dialog (modal); if the answer is OK then logout the user
    def logout_clicked(self):
        if (
            QtImport.QMessageBox.question(
                self,
                "Confirm logout",
                "Press OK to logout.",
                QtImport.QMessageBox.Ok,
                QtImport.QMessageBox.Cancel,
            )
            == QtImport.QMessageBox.Ok
        ):
            self.log_out()

    # Logout the user; reset the brick; changes from logout mode to login mode
    def log_out(self):
        # Reset brick info
        self.proposal_number_ledit.setText("")
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
        self.user_group_widget.hide()

        # resets active proposal
        self.reset_proposal()

        # self.proposalLabel.setText(ProposalBrick2.NOBODY_STR)
        # QToolTip.add(self.proposalLabel,"")

        # Emit signals clearing the proposal and session
        self.setWindowTitle.emit(self["titlePrefix"])
        # self.sessionSelected.emit(None, None, None, None, None, None, None)
        self.loggedIn.emit(False)

    def reset_proposal(self):
        HWR.beamline.session.proposal_code = None
        HWR.beamline.session.session_id = None
        HWR.beamline.session.proposal_id = None
        HWR.beamline.session.proposal_number = None

    # Sets the current session; changes from login mode to logout mode
    def set_proposal(self, proposal, session):
        HWR.beamline.lims.enable()
        HWR.beamline.session.proposal_code = proposal["code"]
        HWR.beamline.session.session_id = session["sessionId"]
        HWR.beamline.session.proposal_id = proposal["proposalId"]
        HWR.beamline.session.proposal_number = proposal["number"]

        # Change mode
        if not self.login_as_user:
            self.login_button.hide()
            self.login_as_proposal_widget.setDisabled(True)
            self.logout_button.show()

        # Store info in the brick
        self.proposal = proposal

        code = proposal["code"].lower()

        if code == "":
            logging.getLogger().warning(
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
            logging.getLogger("GUI").debug(msg)
            self.loggedIn.emit(True)

    def set_codes(self, codes):
        codes_list = codes.split()
        self.proposal_type_combox.clear()
        for cd in codes_list:
            self.proposal_type_combox.addItem(cd)

    def run(self):
        self.setEnabled(HWR.beamline.session is not None)

        self.login_as_user = HWR.beamline.lims.get_login_type() == "user"
        if self.login_as_user:
            self.login_as_user_widget.show()
            self.login_as_proposal_widget.hide()
        else:
            self.login_as_user_widget.hide()
            self.login_as_proposal_widget.show()

        # find if we are using dbconnection, etc. or not
        if not HWR.beamline.lims:
            self.login_as_proposal_widget.hide()
            self.login_button.hide()
            # self.title_label.setText("<nobr><b>%s</b></nobr>" % os.environ["USER"])
            # self.title_label.show()
            self.user_group_widget.show()
            HWR.beamline.session.proposal_code = ""
            HWR.beamline.session.session_id = 1
            HWR.beamline.session.proposal_id = ""
            HWR.beamline.session.proposal_number = ""

            self.setWindowTitle.emit(self["titlePrefix"])
            # self.loggedIn.emit(False)
            # self.sessionSelected.emit(None, None, None, None, None, None, None)
            self.loggedIn.emit(True)
            self.sessionSelected.emit(
                HWR.beamline.session.session_id,
                str(os.environ["USER"]),
                0,
                "",
                "",
                HWR.beamline.session.session_id,
                False,
            )
        else:
            self.setWindowTitle.emit(self["titlePrefix"])
            # self.sessionSelected.emit(None, None, None, None, None, None, None)
            self.loggedIn.emit(False)

            if self.login_as_user:
                if os.getenv("SUDO_USER"):
                    user_name = os.getenv("SUDO_USER")
                else:
                    user_name = os.getenv("USER")
                self._do_login_as_user(user_name)

        start_server_event = ProposalGUIEvent(self.start_servers, ())
        QtImport.QApplication.postEvent(self, start_server_event)

    def start_servers(self):
        if self.instance_server_hwobj is not None:
            self.instance_server_hwobj.initialize_instance()

    def refuse_login(self, stat, message=None):
        if message is not None:
            if stat is False:
                icon = QtImport.QMessageBox.Critical
            elif stat is None:
                icon = QtImport.QMessageBox.Warning
            elif stat is True:
                icon = QtImport.QMessageBox.Information
            msg_dialog = QtImport.QMessageBox(
                "Register user",
                message,
                icon,
                QtImport.QMessageBox.Ok,
                QtImport.QMessageBox.NoButton,
                QtImport.QMessageBox.NoButton,
                self,
            )
            s = self.font().pointSize()
            f = msg_dialog.font()
            f.setPointSize(s)
            msg_dialog.setFont(f)
            msg_dialog.updateGeometry()
            msg_dialog.show()

        self.setEnabled(True)

    def accept_login(self, proposal_dict, session_dict):
        self.set_proposal(proposal_dict, session_dict)
        self.setEnabled(True)

    def set_ispyb_down(self):
        msg_dialog = QtImport.QMessageBox(
            "Register user",
            "Couldn't contact "
            + "the ISPyB database server: you've been logged as the local user.\n"
            + "Your experiments' information will not be stored in ISPyB!",
            QtImport.QMessageBox.Warning,
            QtImport.QMessageBox.Ok,
            QtImport.QMessageBox.NoButton,
            QtImport.QMessageBox.NoButton,
            self,
        )
        s = self.font().pointSize()
        f = msg_dialog.font()
        f.setPointSize(s)
        msg_dialog.setFont(f)
        msg_dialog.updateGeometry()
        msg_dialog.show()

        now = time.strftime("%Y-%m-%d %H:%M:S")
        prop_dict = {"code": "", "number": "", "title": "", "proposalId": ""}
        ses_dict = {"sessionId": "", "startDate": now, "endDate": now, "comments": ""}
        self.accept_login(prop_dict, ses_dict)

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        self.saved_group = False
        Colors.set_widget_color(self.user_group_ledit, Colors.WHITE)
        self.user_group_ledit.setText("")
        self.setEnabled(False)

        if not self.login_as_user:
            prop_type = str(self.proposal_type_combox.currentText())
            prop_number = str(self.proposal_number_ledit.text())
            prop_password = str(self.proposal_password_ledit.text())
            self.proposal_password_ledit.setText("")

            if prop_type == "" and prop_number == "":
                if self.local_login_hwobj is None:
                    return self.refuse_login(False, "Local login not configured.")
                try:
                    locallogin_password = self.local_login_hwobj.password
                except AttributeError:
                    return self.refuse_login(False, "Local login not configured.")

                if prop_password != locallogin_password:
                    return self.refuse_login(None, "Invalid local login password.")

                now = time.strftime("%Y-%m-%d %H:%M:S")
                prop_dict = {"code": "", "number": "", "title": "", "proposalId": ""}
                ses_dict = {
                    "sessionId": "",
                    "startDate": now,
                    "endDate": now,
                    "comments": "",
                }
                return self.accept_login(prop_dict, ses_dict)

            if HWR.beamline.lims is None:
                return self.refuse_login(
                    False,
                    "Not connected to the ISPyB database, unable to get proposal.",
                )

            self._do_login_as_proposal(
                prop_type,
                prop_number,
                prop_password,
                HWR.beamline.lims.beamline_name
            )

    def pass_control(self, has_control_id):
        pass

    def have_control(self, have_control):
        pass

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "codes":
            self.set_codes(new_value)
        elif property_name == "localLogin":
            self.local_login_hwobj = self.get_hardware_object(new_value, optional=True)
        elif property_name == "instanceServer":
            if self.instance_server_hwobj is not None:
                self.disconnect(
                    self.instance_server_hwobj, "passControl", self.pass_control
                )
                self.disconnect(
                    self.instance_server_hwobj, "haveControl", self.have_control
                )
            self.instance_server_hwobj = self.get_hardware_object(
                new_value, optional=True
            )
            if self.instance_server_hwobj is not None:
                self.connect(
                    self.instance_server_hwobj, "passControl", self.pass_control
                )
                self.connect(
                    self.instance_server_hwobj, "haveControl", self.have_control
                )
        elif property_name == "icons":
            icons_list = new_value.split()
            try:
                self.login_button.setIcon(Icons.load_icon(icons_list[0]))
            except IndexError:
                pass
            try:
                self.logout_button.setIcon(Icons.load_icon(icons_list[1]))
            except IndexError:
                pass
        elif property_name == "secondaryProposals":
            self.secondary_proposals = new_value.split()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def _do_login_as_proposal(
        self,
        proposal_code,
        proposal_number,
        proposal_password,
        beamline_name,
        impersonate=False,
    ):
        # Get proposal and sessions
        logging.getLogger().debug("ProposalBrick: querying ISPyB database...")
        prop = HWR.beamline.lims.getProposal(proposal_code, proposal_number)

        # Check if everything went ok
        prop_ok = True
        try:
            prop_ok = prop["status"]["code"] == "ok"
        except KeyError:
            prop_ok = False
        if not prop_ok:
            self.set_ispyb_down()
            BaseWidget.set_status_info("ispyb", "error")
        else:
            self.select_proposal(prop)
            BaseWidget.set_status_info(
                "user", "%s%s@%s" % (proposal_code, str(proposal_number), beamline_name)
            )
            BaseWidget.set_status_info("ispyb", "ready")

    def proposal_combo_activated(self, item_index):
        self.select_proposal(self.proposals[item_index])

    def select_proposal(self, selected_proposal):
        beamline_name = HWR.beamline.lims.beamline_name
        proposal = selected_proposal["Proposal"]
        # person = selected_proposal['Person']
        # laboratory = selected_proposal['Laboratory']
        sessions = selected_proposal["Session"]
        # Check if there are sessions in the proposal
        todays_session = None
        if sessions is None or len(sessions) == 0:
            pass
        else:
            # Check for today's session
            for session in sessions:
                beamline = session["beamlineName"]
                start_date = "%s 00:00:00" % session["startDate"].split()[0]
                end_date = "%s 23:59:59" % session["endDate"].split()[0]
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
            is_inhouse = HWR.beamline.session.is_inhouse(
                proposal["code"], proposal["number"]
            )
            if not is_inhouse:
                if BaseWidget.is_instance_role_client():
                    self.refuse_login(
                        None, "You don't have a session scheduled for today!"
                    )
                    return

            current_time = time.localtime()
            start_time = time.strftime("%Y-%m-%d 00:00:00", current_time)
            end_time = time.mktime(current_time) + 60 * 60 * 24
            tomorrow = time.localtime(end_time)
            end_time = time.strftime("%Y-%m-%d 07:59:59", tomorrow)

            # Create a session
            new_session_dict = {}
            new_session_dict["proposalId"] = selected_proposal["Proposal"]["proposalId"]
            new_session_dict["startDate"] = start_time
            new_session_dict["endDate"] = end_time
            new_session_dict["beamlineName"] = beamline_name
            new_session_dict["scheduled"] = 0
            new_session_dict["nbShifts"] = 3
            new_session_dict["comments"] = "Session created by MXCuBE"
            session_id = HWR.beamline.lims.create_session(new_session_dict)
            new_session_dict["sessionId"] = session_id

            todays_session = new_session_dict
            localcontact = None
        else:
            session_id = todays_session["sessionId"]
            logging.getLogger().debug(
                "ProposalBrick: getting local contact for %s" % session_id
            )
            localcontact = HWR.beamline.lims.get_session_local_contact(session_id)

        self.accept_login(selected_proposal["Proposal"], todays_session)

    def _do_login_as_user(self, user_name):
        logging.getLogger().debug("ProposalBrick: querying ISPyB database...")

        self.proposals = HWR.beamline.lims.get_proposals_by_user(user_name)

        if len(self.proposals) == 0:
            logging.getLogger("GUI").error(
                "No proposals for user %s found in ISPyB" % user_name
            )
            self.set_ispyb_down()
            BaseWidget.set_status_info("ispyb", "error")
        else:
            self.proposal_combo.clear()
            proposal_tooltip = "Available proposals:"
            for proposal in self.proposals:
                proposal_info = "%s%s - %s" % (
                    proposal["Proposal"]["code"],
                    proposal["Proposal"]["number"],
                    proposal["Proposal"]["title"],
                )
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
                self.proposals[proposal_index]["Proposal"]["title"],
            )
            proposal_tooltip += "\nSelected proposal:\n   %s" % proposal_info
            self.proposal_combo.setToolTip(proposal_tooltip)
            logging.getLogger("GUI").info("ISPyB proposal: %s" % proposal_info)

            BaseWidget.set_status_info(
                "user", "%s@%s" % (user_name, HWR.beamline.lims.beamline_name)
            )
            BaseWidget.set_status_info("ispyb", "ready")

    def select_todays_proposal(self, proposal_list):
        """Selects a proposal that is assigned for current day
           If no session found then returns first proposal
        """
        for prop_index, proposal in enumerate(proposal_list):
            sessions = proposal["Session"]
            proposal_code_number = (
                proposal["Proposal"]["code"] + proposal["Proposal"]["number"]
            )
            if (
                len(sessions) > 0
                and not proposal_code_number in self.secondary_proposals
            ):
                # Check for today's session
                for session in sessions:
                    beamline = session["beamlineName"]
                    start_date = "%s 00:00:00" % session["startDate"].split()[0]
                    end_date = "%s 23:59:59" % session["endDate"].split()[0]
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
                            if beamline == HWR.beamline.lims.beamline_name:
                                # Check date
                                if (
                                    current_time >= start_time
                                    and current_time <= end_time
                                ):
                                    return prop_index

        # If no proposal with valid session found then the last
        # proposal from the list is selected
        return len(proposal_list) - 1
