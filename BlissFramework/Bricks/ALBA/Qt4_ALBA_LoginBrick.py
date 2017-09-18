
__category__ = "ALBA"

from BlissFramework.Utils import Qt4_widget_colors
from Qt4_ProposalBrick2 import Qt4_ProposalBrick2

class Qt4_ALBA_LoginBrick(Qt4_ProposalBrick2):

    def __init__(self,*args):
        Qt4_ProposalBrick2.__init__(self, *args)

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
          

            prop_type = 'av'
            prop_number = '2020000007'

            self._do_login_as_proposal(prop_type, prop_number, prop_password, self.lims_hwobj.beamline_name)

