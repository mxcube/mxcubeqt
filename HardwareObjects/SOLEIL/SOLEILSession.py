
from HardwareRepository import HardwareRepository
import logging
import os

import Session

class SOLEILSession(Session.Session):

    def __init__(self, *args, **kwargs):
        Session.Session.__init__(self,*args, **kwargs)
        self.username = ''
        self.gid = ''
        self.uid = ''

    def path_to_ispyb(self, path):
        path = path.replace( self["file_info"].getProperty('base_directory'),
                      self["file_info"].getProperty('ispyb_base_directory'))
        return path

    def set_user_info(self, username, user_id, group_id ):
        logging.debug("SESSION - User %s logged in. gid=%s / uid=%s " % (username,group_id,user_id))
        self.username = username 
        self.group_id = group_id 
        self.user_id = user_id 

    def get_ruche_info(self, path):
        if self.is_inhouse( self.username ):
           usertype = 'soleil'
        else:
           usertype = 'users'

        basedir = os.path.dirname( path )
        ruchepath = basedir.replace( self["file_info"].getProperty('base_directory'), '' )
        if ruchepath and ruchepath[0] == os.path.sep:
            ruchepath = ruchepath[1:]
                      
        infostr = "%s %s:%s %s %s" % (usertype,self.user_id, self.group_id, basedir,ruchepath)
        return infostr

def test():
    import os
    hwr_directory = os.environ["XML_FILES_PATH"]

    hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
    hwr.connect()

    sess = hwr.getHardwareObject("/session")

    path = "/data1-1/test/visitor/mx2014/px1/20150120/ARCHIVE/mx2014/mx2014_2_4.snapshot.jpeg"
    ispyb_path = sess.path_to_ispyb(path)
 
    print path
    print "  will become "
    print ispyb_path
 
    sess.set_user_info('mx2014', '143301', '14330')
    print sess.get_ruche_info(path)

if __name__ == '__main__':
    test()
