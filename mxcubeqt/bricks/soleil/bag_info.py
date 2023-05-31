
import os
import sys
from datetime import date, timedelta

default_location = "/etc/ispyb_identifiers"

class ISPyB_Record(object):
    def __init__(self, values, proposal):

        self.proposal = proposal
        self.projectid = values[0]
        self.session_no = values[1]

        sdate = values[2]
        edate = values[3]

        self.start_date = date(*map(int, sdate.split('-')))
        self.end_date = date(*map(int, edate.split('-')))
        self.ldaplogin = values[4].strip()
        self.name = values[5].strip()

    def __repr__(self):
        return "ID: %s / Date: %s to %s / (%s)" % (self.projectid, str(self.start_date), str(self.end_date), self.ldaplogin)

class ISPyB_ID_File(object):

    def __init__(self,proposal,filepath):

        self.is_loaded = False

        self.proposal = proposal
        self.filepath = filepath
        self.file_type = os.path.splitext(filepath)[1][1:]

        self.fields = None
        self.records = []

    def get_type(self):
        return self.file_type

    def get_contents(self):
        if not self.is_loaded:
            self.load_contents()

    def load_contents(self):
        self.records = []
        for line in open(self.filepath).readlines():

            if line.startswith("#columns = "):
                 fields = line.strip()[11:].split(',')
                 self.fields = [field.strip().lower() for field in fields]

                 pid_no = self.fields.index('ispybprojectid')
                 sess_no = self.fields.index('session')
                 sdate_no = self.fields.index('startdate')
                 edate_no = self.fields.index('enddate')

                 if self.file_type == 'bag':
                     ldap_no = self.fields.index('ldaploginpi')
                     name_no = self.fields.index('bagname')
                 elif self.file_type == 'std':
                     ldap_no = self.fields.index('ldaploginmp')
                     name_no = self.fields.index('mpname')
                 else:
                     print("Wrong file type", self.file_type, self.filepath)

                 continue

            if self.fields and line.strip() and not line.startswith('#'):
                vals = line.split(',')
                if len(vals) >= len(self.fields):
                    pid = vals[pid_no]
                    sess = vals[sess_no]
                    sdate = vals[sdate_no]
                    edate = vals[edate_no]
                    ldap = vals[ldap_no]
                    name = vals[name_no]

                    rec = (pid,sess,sdate,edate,ldap,name)
            
                    self.records.append(ISPyB_Record(rec, self.proposal))

        self.is_loaded = True

    def get_fields(self):
        if not self.is_loaded:
            self.load_contents()

        return self.fields

    def get_valid_records(self, checkdate=None, maxdelta=1):

        ret = []

        if not self.is_loaded:
            self.load_contents()

        if checkdate is None:
            cdate = date.today()
        else:
            cdate = date( checkdate[0], checkdate[1], checkdate[2]  )

        for record in self.records:
            if cdate > record.start_date and cdate < record.end_date:
               # in period
               ret.append(record)
            elif abs(cdate-record.end_date) < timedelta(maxdelta):
               ret.append(record)
            elif abs(record.start_date-cdate) < timedelta(maxdelta) :
               ret.append(record)

        return ret
       
 
    def get_records(self):
        if not self.is_loaded:
            self.load_contents()

        return self.records


class BagInfo(object):

    def __init__(self, location=default_location):
        self.idfile_list = {}
        self.location = location
        self.load_idfiles(location)

    def load_idfiles(self, location):
        idfiles = os.listdir(location)
        for idfile in idfiles:
            if len(idfile) < 8:
               continue
            proposal = idfile[0:8]
            extension = os.path.splitext(idfile)[1][1:]

            filepath = os.path.join(location,idfile)
            self.idfile_list[proposal] = ISPyB_ID_File(proposal,filepath)
    
    def get_proposal(self, proposal, proptype=None):
        fileinfo = self.idfile_list.get(proposal, None)
        
        if not fileinfo:
            return None
        
        if proptype == 'bag':
            if fileinfo.get_type() != 'bag':
                fileinfo = None

        if proptype == 'std':
            if fileinfo.get_type() != 'std':
                fileinfo = None

        return fileinfo

if __name__ == '__main__':
    id_db = BagInfo()

    test_ids = ["99120089", "20180088", "20170745", "20170799", '20140758']
    oneday = (2015,11,21)

    test_ids = ["20100023"]

    if len(sys.argv) == 4:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        oneday = (year, month, day)
    elif len(sys.argv) == 2:
        test_ids = [sys.argv[1]]
        oneday = None

    td = 1

    for tid in test_ids:
        idfile = id_db.get_proposal(tid)
        if idfile:
            print("ID: ",tid, idfile.get_type())
            records = idfile.get_records()
            for record in records:
                print("    ", record)
           
            records = idfile.get_valid_records(oneday)
            for record in records:
                print("VALID    ", record)

