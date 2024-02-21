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

import logging
import os

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.bricks.proposal_brick import ProposalBrick, ProposalGUIEvent
from mxcubecore import HardwareRepository as HWR

class P11ProposalBrick(ProposalBrick):
    def __init__(self, *args):
        super(P11ProposalBrick, self).__init__(*args)

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
        proposal_code = HWR.beamline.session.get_current_proposal_code()

        if not HWR.beamline.lims or proposal_code is None:
            self.message_widget.setText("not connected")
            self.message_widget.show()
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
            self.proposal_number_ledit.setText("no ispyb")

            # self.loggedIn.emit(False)
            # self.sessionSelected.emit(None, None, None, None, None, None, None)
            self.loggedIn.emit(True)
            self.sessionSelected.emit(
                HWR.beamline.session.session_id,
                str(os.environ["USER"]),
                str(HWR.beamline.session.session_id),
                0,
                "",
                "",
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
            else:
                self.p11_login_as_proposal()

        start_server_event = ProposalGUIEvent(self.start_servers, ())
        qt_import.QApplication.postEvent(self, start_server_event)

    def p11_login_as_proposal(self):

        if HWR.beamline.lims.simulated_proposal == 1:
            proposal_code = HWR.beamline.lims.simulated_prop_code
            proposal_number = HWR.beamline.lims.simulated_prop_number
        else:
            proposal_code = HWR.beamline.session.get_current_proposal_code()
            proposal_number = HWR.beamline.session.get_current_proposal_number()

        logging.getLogger("HWR").debug(" PROPOSAL BRICK - code is %s" % proposal_code)
        logging.getLogger("HWR").debug(
            " PROPOSAL BRICK - number is %s" % proposal_number
        )

        self._do_login_as_proposal(
            proposal_code, proposal_number, None, HWR.beamline.lims.beamline_name,
        )
        logging.getLogger("HWR").debug("login as proposal done")

    def show_selected_proposal(self, proposal):

        beamtime_id = HWR.beamline.session.get_current_beamtime_id()
        prop_number = str(proposal["number"])
        prop_code = str(proposal["code"])

        prop_info = f"ID: {prop_code}-{prop_number} - BT_ID: {beamtime_id}"

        self.proposal_info.setText(prop_info)
        self.proposal_info.show()

        self.code_label.hide()
        self.proposal_type_combox.hide()
        self.proposal_number_ledit.hide()
        self.password_label.hide()
        self.proposal_password_ledit.hide()
