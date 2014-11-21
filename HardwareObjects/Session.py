"""
Session hardware object.

Contains information regarding the current session and methods to
access and manipulate this information.
"""
import os
import time

from HardwareRepository.BaseHardwareObjects import HardwareObject
import queue_model_objects_v1 as queue_model_objects

class Session(HardwareObject):
    def __init__(self, name):
        HardwareObject.__init__(self, name)
        self.session_id = None
        self.proposal_code = None
        self.proposal_number = None
        self.proposal_id = None
        self.in_house_users = []
        self.endstation_name = None
        self.session_start_date = None
        self.user_group = ''

        self.default_precision = '04'
        self.suffix = None
        self.base_directory = None
        self.base_process_directory = None
        self.raw_data_folder_name = None
        self.processed_data_folder_name = None

    # Framework-2 method, inherited from HardwareObject and called
    # by the framework after the object has been initialized.
    def init(self):
        self.endstation_name = self.getProperty('endstation_name').lower()
        self.suffix = self["file_info"].getProperty('file_suffix')
        self.base_directory = self["file_info"].\
                              getProperty('base_directory')

        self.base_process_directory = self["file_info"].\
            getProperty('processed_data_base_directory')

        self.raw_data_folder_name = self["file_info"].\
            getProperty('raw_data_folder_name')

        self.processed_data_folder_name = self["file_info"].\
            getProperty('processed_data_folder_name')

        inhouse_proposals = self["inhouse_users"]["proposal"]

        for prop in inhouse_proposals:
            self.in_house_users.append((prop.getProperty('code'),
                str(prop.getProperty('number'))))

        queue_model_objects.PathTemplate.set_archive_path(self['file_info'].getProperty('archive_base_directory'),
                                                          self['file_info'].getProperty('archive_folder'))


    def get_base_data_directory(self):
        """
        Returns the base data directory taking the 'contextual'
        information into account, such as if the current user
        is inhouse.

        :returns: The base data path.
        :rtype: str
        """
        user_category = ''
        directory = ''

        if self.session_start_date:
            start_time = self.session_start_date.split(' ')[0].replace('-', '')
        else:
            start_time = time.strftime("%Y%m%d")

        if self.is_inhouse():
            user_category = 'inhouse'
            directory = os.path.join(self.base_directory, self.endstation_name,
                                     user_category, self.get_proposal(),
                                     start_time)
        else:
            user_category = 'visitor'
            directory = os.path.join(self.base_directory, user_category,
                                     self.get_proposal(), self.endstation_name,
                                     start_time)

        return directory

    def get_base_image_directory(self):
        """
        :returns: The base path for images.
        :rtype: str
        """
        return os.path.join(self.get_base_data_directory(),
                            self.raw_data_folder_name)

    def get_base_process_directory(self):
        """
        :returns: The base path for procesed data.
        :rtype: str
        """
        return os.path.join(self.get_base_data_directory(),
                            self.processed_data_folder_name)

    def get_image_directory(self, sub_dir=None):
        """
        Returns the full path to images, using the name of each of
        data_nodes parents as sub directories.

        :param data_node: The data node to get additional
                          information from, (which will be added
                          to the path).
        :type data_node: TaskNode

        :returns: The full path to images.
        :rtype: str
        """
        directory = self.get_base_image_directory()

        if sub_dir:
            sub_dir = sub_dir.replace(' ', '').replace(':', '-')
            directory = os.path.join(directory, sub_dir) + os.path.sep
            
        return directory

    def get_process_directory(self, sub_dir=None):
        """
        Returns the full path to processed data, using the name of
        each of data_nodes parents as sub directories.

        :param data_node: The data node to get additional
                          information from, (which will be added
                          to the path).
        :type data_node: TaskNode

        :returns: The full path to images.
        """
        directory = self.get_base_process_directory()

        if sub_dir:
            sub_dir = sub_dir.replace(' ', '').replace(':', '-')
            directory = os.path.join(directory, sub_dir) + '/'

        return directory

    def get_default_prefix(self, sample_data_node = None, generic_name = False):
        """
        Returns the default prefix, using sample data such as the
        acronym as parts in the prefix.

        :param sample_data_node: The data node to get additional
                                 information from, (which will be
                                 added to the prefix).
        :type sample_data_node: Sample


        :returns: The default prefix.
        :rtype: str
        """
        proposal = self.get_proposal()
        prefix = proposal

        if sample_data_node:
            if sample_data_node.has_lims_data():
                prefix = sample_data_node.crystals[0].protein_acronym + \
                         '-' + sample_data_node.name
        elif generic_name:
            prefix = '<acronym>-<name>'

        return prefix

    def get_proposal(self):
        """
        :returns: The proposal, 'local-user' if no proposal is
                  available
        :rtype: str
        """
        proposal = 'local-user'

        if self.proposal_code and self.proposal_number:
            if self.proposal_code == 'ifx':
                self.proposal_code = 'fx'

            proposal = "%s%s" % (self.proposal_code,
                                 self.proposal_number)

        return proposal

    def is_inhouse(self, proposal_code=None, proposal_number=None):
        """
        Determines if a given proposal is considered to be inhouse.

        :param proposal_code: Proposal code
        :type propsal_code: str

        :param proposal_number: Proposal number
        :type proposal_number: str

        :returns: True if the proposal is inhouse, otherwise False.
        :rtype: bool
        """
        if not proposal_code:
            proposal_code = self.proposal_code

        if not proposal_number:
            proposal_number = self.proposal_number

        if (proposal_code, proposal_number) in self.in_house_users:
            return True
        else:
            return False

    def get_inhouse_user(self):
        """
        :returns: The current inhouse user.
        :rtype: tuple (<proposal_code>, <proposal_number>)
        """
        return self.in_house_users[0]

    def set_session_start_date(self, start_date_str):
        """
        :param start_date_str: The session start date
        :type start_date_str: str
        """
        self.session_start_date = start_date_str

    def get_session_start_date(self):
        """
        :returns: The session start date
        :rtype: str
        """
        return self.session_start_date

    def set_user_group(self, group_name):
        """
        :param group_name: Name of user group
        :type group_name: str
        """
        self.user_group = str(group_name)

    def get_group_name(self):
        """
        :returns: Name of user group
        :rtype: str
        """
        return self.user_group
