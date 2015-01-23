from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import Procedure
import os
import logging
import ldap

"""
<procedure class="LdapLogin">
  <ldaphost>ldaphost.mydomain</ldaphost>
  <ldapport>389</ldapport>
  <ldapdc>esrf.fr</ldapdc>
</procedure>
"""

###
### Checks the proposal password in a LDAP server
###
class SOLEILLdapLogin(Procedure):
    def __init__(self,name):
        Procedure.__init__(self,name)
        self.ldapConnection=None

    # Initializes the hardware object
    def init(self):
        ldaphost=self.getProperty('ldaphost')
        ldapdc=self.getProperty('ldapdc')
        if ldaphost is None:
            logging.getLogger("HWR").error("LdapLogin: you must specify the LDAP hostname")
        else:
            ldapport=self.getProperty('ldapport')

            if ldapport is None:
                logging.getLogger("HWR").debug("LdapLogin: connecting to LDAP server %s",ldaphost)
                self.ldapConnection=ldap.open(ldaphost)
            else:
                logging.getLogger("HWR").debug("LdapLogin: connecting to LDAP server %s:%s",ldaphost,ldapport)
                self.ldapConnection=ldap.open(ldaphost,int(ldapport))
                self.ldapConnection.simple_bind_s()

        if ldapdc is not None:
            parts=ldapdc.split(".")
            self.dcparts=""
            comma=""
            for part in parts:
               self.dcparts += "dc=%s%s" % (part,comma)
               comma=","
        else:
            self.dcparts="dc=esrf,dc=fr"

    # Creates a new connection to LDAP if there's an exception on the current connection
    def reconnect(self):
        if self.ldapConnection is not None:
            try:
                self.ldapConnection.result(timeout=0)
            except ldap.LDAPError,err:
                ldaphost=self.getProperty('ldaphost')
                ldapport=self.getProperty('ldapport')
                if ldapport is None:
                    logging.getLogger("HWR").debug("LdapLogin: reconnecting to LDAP server %s",ldaphost)
                    self.ldapConnection=ldap.open(ldaphost)
                    self.ldapConnection.simple_bind_s()
                else:
                    logging.getLogger("HWR").debug("LdapLogin: reconnecting to LDAP server %s:%s",ldaphost,ldapport)
                    self.ldapConnection=ldap.open(ldaphost,int(ldapport))
                    self.ldapConnection.simple_bind_s()
            
    # Logs the error message (or LDAP exception) and returns the respective tuple
    def cleanup(self,ex=None,msg=None):
        if ex is not None:
            try:
                msg=ex[0]['desc']
            except (IndexError,KeyError,ValueError,TypeError):
                msg="generic LDAP error"
        logging.getLogger("HWR").debug("LdapLogin: %s" % msg)
        if ex is not None:
            self.reconnect()
        return (False,msg)

    # Check password in LDAP
    def getinfo(self,username):

        found = self.search_user(username)

        if not found:
            return self.cleanup(msg="unknown proposal %s" % username)
        else:
            dn, info = found[0]
            return info

    def login(self,username,password,retry=True):

        if self.ldapConnection is None:
            return self.cleanup(msg="no LDAP server configured")

        found = self.search_user(username)

        if not found:
            return self.cleanup(msg="unknown proposal %s" % username)
        if password=="":
            return self.cleanup(msg="invalid password for %s" % username)

        for dn,entry in found:
            dn = str(dn)

        logging.getLogger("HWR").error("LdapLogin: found: %s" % dn)
        
        logging.getLogger("HWR").debug("LdapLogin: validating %s" % username)
        handle=self.ldapConnection.simple_bind(dn,password)
        try:
            result=self.ldapConnection.result(handle)
        except ldap.INVALID_CREDENTIALS:
            return self.cleanup(msg="invalid password for %s" % username)
        except ldap.LDAPError,err:
            if retry:
                self.cleanup(ex=err)
                return self.login(username,password,retry=False)
            else:
                return self.cleanup(ex=err)
        logging.getLogger("HWR").debug("LdapLogin: searching for %s" % username)

        return (True,username)

    def search_user(self,username):

        logging.getLogger("HWR").debug("LdapLogin: searching for %s (dcparts are: %s)" % (username, self.dcparts))

        try:
            found=self.ldapConnection.search_s(self.dcparts, ldap.SCOPE_SUBTREE, "uid="+username)
        except ldap.LDAPError,err:
            if retry:
                self.cleanup(ex=err)
                return self.login(username,password,retry=False)
            else:
                return self.cleanup(ex=err)
        else:
            return found


def test():
    hwr_directory = os.environ["XML_FILES_PATH"] 

    print hwr_directory
    hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
    hwr.connect()

    conn = hwr.getHardwareObject("/ldapconnection")
    #conn.login("20141015", "4dBM0lx3pw")

    ok,name = conn.login("99140198", "5u4Twf70K5")
    ok,name = conn.login("legrand", "5u4Twf70K5")

    #info = conn.getinfo("legrand")
    info = conn.getinfo("99140198")

    if info:
         print "GID:", info.get('gidNumber','')
         print "UID:", info.get('uidNumber','')
         print "title:", info.get('title','')


if __name__ == '__main__':
   test()
