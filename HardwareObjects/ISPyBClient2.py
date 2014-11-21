"""
A client for ISPyB Webservices. 
"""

import logging
import gevent
import suds; logging.getLogger("suds").setLevel(logging.INFO)

from suds.transport.http import HttpAuthenticated
from suds.client import Client
from suds import WebFault
from suds.sudsobject import asdict
from urllib2 import URLError
from HardwareRepository.BaseHardwareObjects import HardwareObject
from datetime import datetime
from collections import namedtuple
from pprint import pformat


# Production web-services:    http://160.103.210.1:8080/ispyb-ejb3/ispybWS/
# Test web-services:          http://160.103.210.4:8080/ispyb-ejb3/ispybWS/

# The WSDL root is configured in the hardware object XML file.
_WSDL_ROOT = '' 
_WS_BL_SAMPLE_URL = _WSDL_ROOT + 'ToolsForBLSampleWebService?wsdl'
_WS_SHIPPING_URL = _WSDL_ROOT + 'ToolsForShippingWebService?wsdl'
_WS_COLLECTION_URL = _WSDL_ROOT + 'ToolsForCollectionWebService?wsdl'
_WS_USERNAME = 'ispybws1'
_WS_PASSWORD = '!5pybws1'

_CONNECTION_ERROR_MSG = "Could not connect to ISPyB, please verify that " + \
                        "the server is running and that your " + \
                        "configuration is correct"


SampleReference = namedtuple('SampleReference', ['code',
                                                 'container_reference',
                                                 'sample_reference',
                                                 'container_code'])

def trace(fun):
    def _trace(*args):      
        log_msg = "lims client " + fun.__name__ + " called with: "
        
        for arg in args[1:]:
            try:
                log_msg += pformat(arg, indent = 4, width = 80) + ', '
            except:
                pass

        logging.getLogger("ispyb_client").debug(log_msg)        
        result = fun(*args)

        try:
            result_msg = "lims client " + fun.__name__ + \
                " returned  with: " + pformat(result, indent = 4, width = 80)
        except:
            pass
            
        logging.getLogger("ispyb_client").debug(result_msg)
        return result

    return _trace


def in_greenlet(fun):
    def _in_greenlet(*args, **kwargs):
        log_msg = "lims client " + fun.__name__ + " called with: "
        
        for arg in args[1:]:
            try:
                log_msg += pformat(arg, indent = 4, width = 80) + ', '
            except:
                pass
                
        logging.getLogger("ispyb_client").debug(log_msg)
        task = gevent.spawn(fun, *args)
        if kwargs.get("wait", False):
          task.get()

    return _in_greenlet


def utf_encode(res_d):
    for key in res_d.iterkeys():
        if isinstance(res_d[key], dict):
            utf_encode(res_d)
        
        if isinstance(res_d[key], suds.sax.text.Text):
            try:
                res_d[key] = res_d[key].encode('utf8', 'ignore')
            except:
                pass

    return res_d


class ISPyBClient2(HardwareObject):
    """
    Web-service client for ISPyB.
    """

    def __init__(self, name):
        HardwareObject.__init__(self, name)
        self.__shipping = None
        self.__collection = None
        self.__tools_ws = None
        self.__translations = {}
        self.__disabled = False
        self.beamline_name = False
        
        logger = logging.getLogger('ispyb_client')
        
        try:
            formatter = \
                logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr = logging.FileHandler('/users/blissadm/log/ispyb_client.log')
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr) 
        except:
            pass

        logger.setLevel(logging.INFO)

      
    def init(self):
        """
        Init method declared by HardwareObject.
        """
        session_hwobj = self.getObjectByRole('session')
        
        try:
            # ws_root is a property in the configuration xml file
            if self.ws_root:
                global _WSDL_ROOT
                global _WS_BL_SAMPLE_URL
                global _WS_SHIPPING_URL
                global _WS_COLLECTION_URL
                global _WS_SCREENING_URL

                _WSDL_ROOT = self.ws_root.strip()
                _WS_BL_SAMPLE_URL = _WSDL_ROOT + \
                    'ToolsForBLSampleWebService?wsdl'
                _WS_SHIPPING_URL = _WSDL_ROOT + \
                    'ToolsForShippingWebService?wsdl'
                _WS_COLLECTION_URL = _WSDL_ROOT + \
                    'ToolsForCollectionWebService?wsdl'

                t1 = HttpAuthenticated(username = _WS_USERNAME, 
                                      password = _WS_PASSWORD)
                
                t2 = HttpAuthenticated(username = _WS_USERNAME, 
                                      password = _WS_PASSWORD)
                
                t3 = HttpAuthenticated(username = _WS_USERNAME, 
                                      password = _WS_PASSWORD)
                
                try: 
                    self.__shipping = Client(_WS_SHIPPING_URL, timeout = 3,
                                             transport = t1, cache = None)
                    self.__collection = Client(_WS_COLLECTION_URL, timeout = 3,
                                               transport = t2, cache = None)
                    self.__tools_ws = Client(_WS_BL_SAMPLE_URL, timeout = 3,
                                             transport = t3, cache = None)
                    
                except URLError:
                    logging.getLogger("ispyb_client")\
                        .exception(_CONNECTION_ERROR_MSG)
                    return
        except:
            logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
            return
 
        # Add the porposal codes defined in the configuration xml file
        # to a directory. Used by translate()
        try:
            proposals = session_hwobj['proposals']
            
            for proposal in proposals:
                code = proposal.code
                self.__translations[code] = {}
                try:
                    self.__translations[code]['ldap'] = proposal.ldap
                except AttributeError:
                    pass
                try:
                    self.__translations[code]['ispyb'] = proposal.ispyb
                except AttributeError:
                    pass
                try:
                    self.__translations[code]['gui'] = proposal.gui
                except AttributeError:
                    pass
        except IndexError:
            pass

        self.beamline_name = session_hwobj.beamline_name

    def translate(self, code, what):  
        """
        Given a proposal code, returns the correct code to use in the GUI,
        or what to send to LDAP, user office database, or the ISPyB database.
        """
        try:
            translated = self.__translations[code][what]
        except KeyError:
            translated = code
        return translated

    
    def clear_daily_email(self):
        raise NotImplementedException("Depricated ?")

    
    def send_email(self):
        raise NotImplementedException("Depricated ?")

    @trace
    def get_proposal(self, proposal_code, proposal_number):
        """
        Returns the tuple (Proposal, Person, Laboratory, Session, Status).
        Containing the data from the coresponding tables in the database
        the status of the database operations are returned in Status.
        
        :param proposal_code: The proposal code
        :type proposal_code: str
        :param proposal_number: The proposal number
        :type propsoal_number: int

        :returns: The dict (Proposal, Person, Laboratory, Sessions, Status).
        :rtype: dict
        """
        if self.__shipping:
            try:         
                try:
                    person = self.__shipping.service.\
                             findPersonByProposal(proposal_code, 
                                                  proposal_number)
                    if not person:
                        person = {}

                except WebFault, e:
                    logging.getLogger("ispyb_client").exception(e.message)
                    person = {}
 
                try: 
                    proposal = self.__shipping.service.\
                        findProposal(proposal_code, 
                                     proposal_number)

                    if proposal:
                        proposal.code = proposal_code
                    else:
                        return {'Proposal': {}, 
                                'Person': {}, 
                                'Laboratory': {}, 
                                'Session': {}, 
                                'status': {'code':'error'}}

                except WebFault, e:
                    logging.getLogger("ispyb_client").exception(e.message)
                    proposal = {}

                try: 
                    lab = self.__shipping.service.\
                        findLaboratoryByProposal(proposal_code, 
                                                 proposal_number)

                    if not lab:
                        lab = {}
                    
                except WebFault, e:
                    logging.getLogger("ispyb_client").exception(e.message)
                    lab = {}
                try:
                    res_sessions = self.__collection.service.\
                        findSessionsByProposalAndBeamLine(proposal_code,
                                                          proposal_number,
                                                          self.beamline_name)
                    sessions = []

                    # Handels a list of sessions
                    for session in res_sessions:
                        if session is not None :
                            try:
                                session.startDate = \
                                    datetime.strftime(session.startDate, 
                                                      "%Y-%m-%d %H:%M:%S")
                                session.endDate = \
                                    datetime.strftime(session.endDate, 
                                                      "%Y-%m-%d %H:%M:%S")
                            except:
                                pass

                            sessions.append(utf_encode(asdict(session)))

                except WebFault, e:
                    logging.getLogger("ispyb_client").exception(e.message)
                    sessions = []

            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
                return {'Proposal': {}, 
                        'Person': {}, 
                        'Laboratory': {}, 
                        'Session': {}, 
                        'status': {'code':'error'}}

            return  {'Proposal': utf_encode(asdict(proposal)), 
                     'Person': utf_encode(asdict(person)), 
                     'Laboratory': utf_encode(asdict(lab)), 
                     'Session': sessions, 
                     'status': {'code':'ok'}}
        
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_proposal: Could not connect to server," + \
                          " returning empty proposal")

            return {'Proposal': {}, 
                    'Person': {}, 
                    'Laboratory': {}, 
                    'Session': {}, 
                    'status': {'code':'error'}}

    @trace
    def get_session_local_contact(self, session_id):
        """
        Retrieves the person entry associated with the session id <session_id>
        
        :param session_id:
        :type session_id: int
        :returns: Person object as dict.
        :rtype: dict
        """

        if self.__shipping:
        
            try:
                person = self.__shipping.service.\
                    findPersonBySessionIdLocalContact(session_id)
            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
                person = {}
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
                person = {}

            if person is None:
                return {}
            else:
                utf_encode(asdict(person))
            
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_session_local_contact: Could not get " + \
                          "local contact")
            return {}

    @trace
    def store_data_collection(self, *args, **kwargs):
        try:
          return self._store_data_collection(*args, **kwargs)
        except gevent.GreenletExit:
          # aborted by user ('kill')
          raise
        except:
          # if anything else happens, let upper level process continue
          # (not a fatal error), but display exception still
          logging.exception("Could not store data collection")
          return (0,0,0)
          

    def _store_data_collection(self, mx_collection, beamline_setup = None):
        """
        Stores the data collection mx_collection, and the beamline setup
        if provided.

        :param mx_collection: The data collection parameters.
        :type mx_collection: dict
        
        :param beamline_setup: The beamline setup.
        :type beamline_setup: dict

        :returns: None

        """
        if self.__disabled:
            return (0,0,0)
        
        if self.__collection:
            data_collection = ISPyBValueFactory().\
                from_data_collect_parameters(mx_collection)

            group_id = self.store_data_collection_group(mx_collection)
            
            #if group_id:
            #    data_collection.dataCollectionGroupId = group_id

            if beamline_setup:
                lims_beamline_setup = ISPyBValueFactory.\
                    from_bl_config(beamline_setup)
          
                lims_beamline_setup.synchrotronMode = \
                    data_collection.synchrotronMode

                self.store_beamline_setup(mx_collection['sessionId'],
                                          lims_beamline_setup )

                detector_params = \
                    ISPyBValueFactory().detector_from_blc(beamline_setup,
                                                          mx_collection)
                
                detector = self.find_detector(*detector_params)
                detector_id = 0
                
                if detector:
                    detector_id = detector.detectorId
                    data_collection.detectorId = detector_id
                
            collection_id = self.__collection.service.\
                            storeOrUpdateDataCollection(data_collection)

            return (collection_id, detector_id)
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_data_collection: could not connect" + \
                          " to server")


    @trace
    def store_beamline_setup(self, session_id, beamline_setup):
        """
        Stores the beamline setup dict <beamline_setup>.

        :param session_id: The session id that the beamline_setup
                           should be associated with.
        :type session_id: int

        :param beamline_setup: The dictonary with beamline settings.
        :type beamline_setup: dict

        :returns beamline_setup_id: The database id of the beamline setup.
        :rtype: str
        """
       
        blSetupId = None
        if self.__collection:
        
            session = {}
       
            try:
                session = self.get_session(session_id)
            except:
                logging.getLogger("ispyb_client").exception(\
                    "ISPyBClient: exception in store_beam_line_setup")
            else:
                if session is not None:
                    try:
                        blSetupId = self.__collection.service.\
                                     storeOrUpdateBeamLineSetup(beamline_setup)
                        
                        session['beamLineSetupId'] = blSetupId
                        self.update_session(session)
                        
                    except WebFault, e:
                        logging.getLogger("ispyb_client").exception(e.message)
                    except URLError:
                        logging.getLogger("ispyb_client").\
                            exception(_CONNECTION_ERROR_MSG)
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_beamline_setup: could not connect" + \
                          " to server")

        return blSetupId


    #@trace
    @in_greenlet
    def update_data_collection(self, mx_collection, wait=False):
        """
        Updates the datacollction mx_collection, this requires that the
        collectionId attribute is set and exists in the database.

        :param mx_collection: The dictionary with collections parameters.
        :type mx_collection: dict

        :returns: None
        """  
        if self.__disabled:
            return

        if self.__collection:
            if 'collection_id' in mx_collection:
                try:
                    # Update the data collection group
                    self.store_data_collection_group(mx_collection)
                
                    data_collection = ISPyBValueFactory().\
                        from_data_collect_parameters(mx_collection)
  
                    self.__collection.service.\
                        storeOrUpdateDataCollection(data_collection)
                except WebFault:
                    logging.getLogger("ispyb_client").\
                        exception("ISPyBClient: exception in update_data_collection")
                except URLError:
                    logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
            else:
                logging.getLogger("ispyb_client").error("Error in update_data_collection: " + \
                                        "collection-id missing, the ISPyB data-collection is not updated.")
                
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in update_data_collection: could not connect" + \
                          " to server")


    @trace
    def update_bl_sample(self, bl_sample):
        """
        Creates or stos a BLSample entry. 

        :param sample_dict: A dictonary with the properties for the entry.
        :type sample_dict: dict
        """
        if self.__disabled:
           return {}

        if self.__tools_ws:
            try:
                status = self.__tools_ws.service.\
                    storeOrUpdateBLSample(bl_sample)
            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
                status = {}
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return status
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in update_bl_sample: could not connect to server")


    @in_greenlet
    def store_image(self, image_dict):
        """
        Stores the image (image parameters) <image_dict>
        
        :param image_dict: A dictonary with image pramaters.
        :type image_dict: dict

        :returns: None
        """
        if self.__disabled:
            return
        
        if self.__collection:
            if 'dataCollectionId' in image_dict:
                try:
                    self.__collection.service.storeOrUpdateImage(image_dict)
                except WebFault:
                    logging.getLogger("ispyb_client").\
                        exception("ISPyBClient: exception in store_image")
                except URLError:
                    logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
            else:
                logging.getLogger("ispyb_client").error("Error in store_image: " + \
                                                        "data_collection_id missing, could not store image in ISPyB")
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_image: could not connect to server")
        
    
    def __find_sample(self, sample_ref_list, code = None, location = None):
        """
        Returns the sample with the matching "search criteria" <code> and/or
        <location> with-in the list sample_ref_list.

        The sample_ref object is defined in the head of the file.
        
        :param sample_ref_list: The list of sample_refs to search.
        :type sample_ref: list
        
        :param code: The vial datamatrix code (or bar code)
        :param type: str

        :param location: A tuple (<basket>, <vial>) to search for.
        :type location: tuple
        """
        for sample_ref in sample_ref_list:
            
            if code and location:
                if sample_ref.code == code and \
                        sample_ref.container_reference == location[0] and \
                        sample_ref.sample_reference == location[1]:
                    return sample_ref
            elif code:
                if sample_ref.code == code:
                    return sample_ref
            elif location:
                if sample_ref.container_reference == location[0] and \
                       sample_ref.sample_reference == location[1]:
                    return sample_ref

        return None


    @trace 
    def get_samples(self, proposal_id, session_id):
        response_samples = None

        if self.__tools_ws:
            try:
                response_samples = self.__tools_ws.service.\
                    findSampleInfoLightForProposal(proposal_id, 
                                                   self.beamline_name) 
            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_image: could not connect to server")

        return response_samples


    @trace
    def get_session_samples(self, proposal_id, session_id, sample_refs):
        """
        Retrives the list of samples associated with the session <session_id>.
        The samples from ISPyB is cross checked with the ones that are
        currently in the sample changer.

        The datamatrix code read by the sample changer is used in case
        of conflict.

        :param proposal_id: ISPyB proposal id.
        :type proposal_id: int
        
        :param session_id: ISPyB session id to retreive samples for.
        :type session_id: int

        :param sample_refs: The list of samples currently in the
                            sample changer. As a list of sample_ref
                            objects
        :type sample_refs: list (of sample_ref objects).

        :returns: A list with sample_ref objects.
        :rtype: list
        """
        if self.__tools_ws: 
            sample_references = []
            session = self.get_session(session_id)
            response_samples = []

            for sample_ref in sample_refs:
                sample_reference = SampleReference(*sample_ref)
                sample_references.append(sample_reference)
            
            try:
                response_samples = self.__tools_ws.service.\
                    findSampleInfoLightForProposal(proposal_id, 
                                                   self.beamline_name)

            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)
                
            samples = []
            for sample in response_samples:
                try:
                    loc = [None, None]
                    try:
                      loc[0]=int(sample.containerSampleChangerLocation)
                    except:
                      pass
                    try:
                      loc[1]=int(sample.sampleLocation) 
                    except: 
                      pass

                    # Unmatched sample, just catch and do nothing
                    # (dont remove from sample_ref)
                    if not sample.code and \
                            not sample.sampleLocation:
                        pass
                    # Sample location and code was found in ISPyB and they match
                    # with the sample changer.
                    elif sample.code and sample.sampleLocation:
                        sc_sample = \
                            self.__find_sample(sample_references,
                                               code = sample.code,
                                               location = loc)

                        # The sample codes dose not match
                        if not sc_sample:
                            sc_sample = self.__find_sample(sample_references,
                                                           location = loc)
                            
                            if sc_sample.code != '':
                                sample.code = sc_sample.code

                        sample_references.remove(sc_sample)
                            
                            
                    # Only location was found, update with the code 
                    # from sample changer if it exists.
                    elif sample.sampleLocation:
                        sc_sample = \
                            self.__find_sample(sample_references,
                                               location = loc)
                        if sc_sample:
                            sample.sampleCode = sc_sample.code 
                            sample_references.remove(sc_sample)

                    # Sample code was found in ISPyB but dosent match with
                    # the samplechanger at given location
                    #
                    # Use the information from the sample changer.
                    else:
                        #Use sample changer code for sample  ?
                        sample.containerSampleChangerLocation = \
                            sample_references.containter_referance
                        sample.sampleLocation = \
                            sample_references.sample_reference

                        loc = (int(sample.containerSampleChangerLocation),
                               int(sample.sampleLocation))

                        sc_sample = \
                            self.__find_sample(sample_references,
                                               location = loc)
                        if sc_sample:
                            sample.code = sc_sample.code 
                            sample_references.remove(sc_sample)


                    samples.append(utf_encode(asdict(sample)))
                    
#                         {'BLSample': utf_encode(asdict(sample.blSample)),
#                          'Container': utf_encode(asdict(sample.container)),
#                          'Crystal': utf_encode(asdict(sample.crystal)),
#                          'DiffractionPlan_BLSample': \
#                              utf_encode(asdict(sample.diffractionPlan)),
#                          'Protein': utf_encode(asdict(sample.protein))})
                except:
                    pass


            # Add the unmatched samples to the result from ISPyB
            for sample_ref in sample_references:
                samples.append(
                    {'code': sample_ref.code, 
                     'location': sample_ref.sample_reference,
                     'containerSampleChangerLocation': sample_ref.container_reference})
                #  samples.append(
#                     {'BLSample': {'code': sample_ref.code, 
#                                   'location': \
#                                   sample_ref.sample_reference},
#                      'Container': {'sampleChangerLocation': \
#                                        sample_ref.container_reference},
#                      'Crystal': {},
#                      'DiffractionPlan_BLSample': {},
#                      'Protein': {}})

            
            return {'loaded_sample': samples, 
                    'status': {'code':'ok'}}
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_session_samples: could not connect " + \
                          "to server")


    @trace
    def get_bl_sample(self, bl_sample_id):
        """
        Fetch the BLSample entry with the id bl_sample_id

        :param bl_sample_id:
        :type bl_sample_id: int

        :returns: A BLSampleWSValue, defined in the wsdl.
        :rtype: BLSampleWSValue

        """

        if self.__tools_ws:

            try:
                result = self.__tools_ws.service.findBLSample(bl_sample_id) 
            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return utf_encode(asdict(result))
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_bl_sample: could not connect to server")

    @trace
    def create_session(self, session_dict):
        """
        Create a new session for "current proposal", the attribute
        porposalId in <session_dict> has to be set (and exist in ISPyB).

        :param session_dict: Dictonary with session parameters.
        :type session_dict: dict

        :returns: The session id of the created session. 
        :rtype: int
        """
        if self.__collection:

            try:
                # The old API used date formated strings and the new
                # one uses DateTime objects. 
                session_dict["startDate"]  = datetime.\
                    strptime(session_dict["startDate"] , "%Y-%m-%d %H:%M:%S")
                session_dict["endDate"] = datetime.\
                    strptime(session_dict["endDate"], "%Y-%m-%d %H:%M:%S")

                session = self.__collection.service.\
                    storeOrUpdateSession(session_dict)

                # changing back to string representation of the dates,
                # since the session_dict is used after this method is called,
                session_dict["startDate"]  = datetime.\
                    strftime(session_dict["startDate"] , "%Y-%m-%d %H:%M:%S")
                session_dict["endDate"] = datetime.\
                    strftime(session_dict["endDate"], "%Y-%m-%d %H:%M:%S")

            except WebFault, e:
                session = {}
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return session
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in create_session: could not connect to server")


    @trace
    def update_session(self, session_dict):
        """
        Update the session with the data in <session_dict>, the attribute 
        sessionId in <session_dict> must be set. 

        Warning: Missing attibutes in <session_dict> will set to null,
                 this could leed to loss of data. 
        
        :param session_dict: The session to update.
        :type session_dict: dict 
                 
        :returns: None
        """
        if self.__collection:
            return self.create_session(session_dict)
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in update_session: could not connect to server")  

    @trace
    def store_energy_scan(self, energyscan_dict):
        """
        Store energyscan.
        
        :param energyscan_dict: Energyscan data to store.
        :type energyscan_dict: dict

        :returns Dictonary with the energy scan id:
        :rtype: dict
        """
        if self.__collection:
        
            status = {'energyScanId': -1}

            try:
                energyscan_dict['startTime'] = datetime.\
                    strptime(energyscan_dict["startTime"], "%Y-%m-%d %H:%M:%S")

                energyscan_dict['endTime'] = datetime.\
                    strptime(energyscan_dict["endTime"], "%Y-%m-%d %H:%M:%S")

                try:
                  del energyscan_dict['remoteEnergy'] 
                except KeyError:
                  pass

                status['energyScanId'] = self.__collection.service.\
                    storeOrUpdateEnergyScan(energyscan_dict)

            except WebFault:
                logging.getLogger("ispyb_client").\
                    exception("ISPyBClient: exception in store_energy_scan")
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return status
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_energy_scan: could not connect to" \
                          + " server")

    @trace
    def associate_bl_sample_and_energy_scan(self, entry_dict):

        if self.__collection:
        
            try:
                result = self.__collection.service.\
                    storeBLSampleHasEnergyScan(entry_dict['energyScanId'],
                                               entry_dict['blSampleId'])

            except WebFault, e:
                result = -1
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return result
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in associate_bl_sample_and_energy_scan: could" + \
                          " not connect to server")

    @trace
    def get_data_collection(self, data_collection_id):
        """
        Retrives the data collection with id <data_collection_id>

        :param data_collection_id: Id of data collection.
        :type data_collection_id: int

        :rtype: dict
        """
        if self.__collection:
        
            try:
                dc_response = self.__collection.service.\
                    findDataCollection(data_collection_id)

                dc = utf_encode(asdict(dc_response))
                dc['startTime'] = datetime.\
                    strftime(dc["startTime"] , "%Y-%m-%d %H:%M:%S")
                dc['endTime'] =  datetime.\
                    strftime(dc["endTime"] , "%Y-%m-%d %H:%M:%S")

            except WebFault, e:
                dc = {}
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                dc = {}
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return dc
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_data_collection: could not connect" + \
                          " to server")
            
    
    @trace
    def get_data_collection_id(self, dc_dict):

        if self.__collection.service:
        
            try:
                dc = self.__collection.service.\
                    findDataCollectionFromImageDirectoryAndImagePrefixAndNumber(
                    dc_dict['directory'], dc_dict['prefix'], 
                    dc_dict['run_number']) 
            except WebFault, e:
                dc = {}
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return dc
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_data_collection_id: could not" + \
                      " connect to server")


    @trace
    def get_sample_last_data_collection(self, blsampleid):
        raise NotImplementedException("Unused method ?")


    @trace
    def get_session(self, session_id):
        """
        Retrieves the session with id <session_id>.

        :returns: Dictionary with session data.
        :rtype: dict
        """
        if self.__collection:
            session = {}
            try:
                session = self.__collection.service.\
                    findSession(session_id)

                if session is not None :
                    session.startDate = datetime.strftime(session.startDate, 
                                                          "%Y-%m-%d %H:%M:%S")
                    session.endDate = datetime.strftime(session.endDate, 
                                                        "%Y-%m-%d %H:%M:%S")
                    session = utf_encode(asdict(session))

            except WebFault, e:
                logging.getLogger("ispyb_client").exception(e.message)
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return session

        else:
            logging.getLogger("ispyb_client").\
                exception("Error in get_session: could not connect to server")

    @trace
    def store_xfe_spectrum(self, xfespectrum_dict):
        """
        Stores a xfe spectrum.

        :returns: A dictionary with the xfe spectrum id.
        :rtype: dict

        """
        status = {'xfeFluorescenceSpectrumId': -1}

        if self.__collection:

            try:
                xfespectrum_dict['startTime'] = datetime.\
                    strptime(xfespectrum_dict["startTime"],"%Y-%m-%d %H:%M:%S")

                xfespectrum_dict['endTime'] = datetime.\
                    strptime(xfespectrum_dict["endTime"], "%Y-%m-%d %H:%M:%S")

                status['xfeFluorescenceSpectrumId'] = \
                    self.__collection.service.\
                    storeOrUpdateXFEFluorescenceSpectrum(xfespectrum_dict)

            except WebFault:
                logging.getLogger("ispyb_client").\
                    exception("ISPyBClient: exception in store_xfe_spectrum")
            except URLError:
                logging.getLogger("ispyb_client").exception(_CONNECTION_ERROR_MSG)

            return status
        else:
            logging.getLogger("ispyb_client").\
                exception("Error in store_xfe_spectrum: could not connect to" + 
                      " server")

    def disable(self):
        self.__disabled = True

 
    def enable(self):
        self.__disabled = False


    def isInhouseUser(self, proposal_code, proposal_number):
        """
        Returns True if the proposal is considered to be a
        in-house user.

        :param proposal_code: 
        :type proposal_code: str

        :param proposal_number:
        :type proposal_number: str

        :rtype: bool
        """
        for proposal in self['inhouse']:
            if proposal_code == proposal.code:
                if str(proposal_number) == str(proposal.number):
                    return True
        return False


    def find_detector(self, type, manufacturer,
                      model, mode):
        """
        Returns the Detector3VO object with the characteristics
        matching the ones given.        
        """

        if self.__collection:
            try:
                res= self.__collection.service.\
                       findDetectorByParam("", manufacturer, model, mode)
                return res
            except WebFault:
                logging.getLogger("ispyb_client").\
                    exception("ISPyBClient: exception in find_detector")
        else:
            logging.getLogger("ispyb_client").\
                exception("Error find_detector: could not connect to" + 
                      " server")


    def store_data_collection_group(self, mx_collection):
        """
        Stores or updates a DataCollectionGroup object.
        The entry is updated of the group_id in the
        mx_collection dictionary is set to an exisitng
        DataCollectionGroup id. 

        :param mx_collection: The dictionary of values to create the object from.
        :type mx_collection: dict

        :returns: DataCollectionGroup id
        :rtype: int
        """

        if self.__collection:
            group = ISPyBValueFactory().dcg_from_dc_params(mx_collection)

            group_id = self.__collection.service.\
                       storeOrUpdateDataCollectionGroup(group)

            return group_id


    def _store_data_collection_group(self, group_data):
        """
        """
        group_id = self.__collection.service.\
                   storeOrUpdateDataCollectionGroup(group_data)

        return group_id

    def store_centred_position(self, cpos):
        """
        """
        pos_id = -1
        mpos_dict = {'omega' : cpos.phi,
                     'phi': cpos.kappa_phi,
                     'kappa': cpos.kappa,
                     'phiX': cpos.focus,
                     'phiY': cpos.phiy,
                     'phiZ': cpos.phiz,
                     'sampX': cpos.sampx,
                     'sampY': cpos.sampy}
        try:
          mpos_dict['chi']=cpos.chi
        except AttributeError:
          pass
          
        msg = 'Storing position in LIMS'
        logging.getLogger("user_level_log").info(msg)
        
        try:
            pos_id = self.__collection.service.\
                     storeOrUpdateMotorPosition(mpos_dict)
        except ex:
            msg = 'Could not store centred position in lims: %s' % ex.message
            logging.getLogger("ispyb_client").exception(msg)

        return pos_id

    # Bindings to methods called from older bricks.
    getProposal = get_proposal
    getSessionLocalContact = get_session_local_contact
    createSession = create_session
    getSessionSamples = get_session_samples
    getSession = get_session
    storeDataCollection = store_data_collection
    storeBeamLineSetup = store_beamline_setup
    getDataCollection = get_data_collection
    updateBLSample = update_bl_sample
    getBLSample = get_bl_sample
    associateBLSampleAndEnergyScan = associate_bl_sample_and_energy_scan
    updateDataCollection = update_data_collection
    storeImage = store_image
    storeEnergyScan = store_energy_scan
    storeXfeSpectrum = store_xfe_spectrum
   
    # Methods that seems to be unused
    getSampleLastDataCollection = get_sample_last_data_collection
    getDataCollectionId = get_data_collection_id


class ISPyBValueFactory():
    """
    Constructs ws objects from "old style" mxCuBE dictonaries.
    """
    @staticmethod
    def detector_from_blc(bl_config, mx_collect_dict):
        try:
            detector_manufacturer = bl_config.detector_manufacturer
            
            if type(detector_manufacturer) is str:
                detector_manufacturer = detector_manufacturer.upper()
        except:
            detector_manufacturer = ""

        try:
            detector_type = bl_config.detector_type
        except:
            detector_type = ""

        try:
            detector_model = bl_config.detector_model
        except:
            detector_model = ""
        
        try:
            modes=("Software binned", "Unbinned", "Hardware binned")
            det_mode = int(mx_collect_dict['detector_mode'])
            detector_mode = modes[det_mode]
        except (KeyError, IndexError, ValueError, TypeError):
            detector_mode = ""

        return (detector_type, detector_manufacturer,
                detector_model, detector_mode)

    
    @staticmethod
    def from_bl_config(bl_config):
        """
        Creates a beamLineSetup3VO from the bl_config dictionary.
        :rtype: beamLineSetup3VO
        """
        ws_client = None
        beamline_setup = None
        
        try:
            ws_client = Client(_WS_COLLECTION_URL,
                               cache = None)

            beamline_setup = ws_client.factory.create('ns0:beamLineSetup3VO')
        except:
            raise
        try:      
            synchrotron_name = \
                             bl_config.synchrotron_name
            beamline_setup.synchrotronName = synchrotron_name
        except (IndexError, AttributeError), e:
            beamline_setup.synchrotronName = "ESRF"  

        if bl_config.undulators:
          i = 1
          for und in bl_config.undulators:
            beamline_setup.__setattr__('undulatorType%d' % i, und.type)
            i += 1

        try:
          beamline_setup.monochromatorType = \
              bl_config.monochromator_type
          
          beamline_setup.focusingOptic = \
              bl_config.focusing_optic
          
          beamline_setup.beamDivergenceVertical = \
              bl_config.beam_divergence_vertical
          
          beamline_setup.beamDivergenceHorizontal = \
              bl_config.beam_divergence_horizontal
          
          beamline_setup.polarisation = \
              bl_config.polarisation

          beamline_setup.minExposureTimePerImage = \
              bl_config.minimum_exposure_time
          
          beamline_setup.goniostatMaxOscillationSpeed = \
              bl_config.maximum_phi_speed
          
          beamline_setup.goniostatMinOscillationWidth = \
              bl_config.minimum_phi_oscillation

        except:
            pass

        beamline_setup.setupDate = datetime.now()

        return beamline_setup

    
    @staticmethod
    def dcg_from_dc_params(mx_collect_dict):
        """
        Creates a dataCollectionGroupWS3VO object from a mx_collect_dict.
        """

        group = None

        try:
            ws_client = Client(_WS_COLLECTION_URL,
                               cache = None)

            group = \
                  ws_client.factory.create('ns0:dataCollectionGroupWS3VO')
        except:
            raise
        else:
            try:    
                group.actualContainerBarcode = \
                    mx_collect_dict['actualContainerBarcode']
            except:
                pass

            try:   
                group.actualContainerSlotInSC = \
                    mx_collect_dict['actualContainerSlotInSC']
            except KeyError:
                pass


            try:        
                group.actualSampleBarcode = \
                    mx_collect_dict['actualSampleBarcode']
            except KeyError:
                pass


            try:     
                group.actualSampleSlotInContainer = \
                    mx_collect_dict['actualSampleSlotInContiner']
            except KeyError:
                pass


            try:
                group.blSampleId = \
                    mx_collect_dict['sample_reference']['blSampleId']
            except KeyError,diag:
                pass


            try:
                group.comments = mx_collect_dict['comment']
            except KeyError,diag:
                pass

            group.endTime = datetime.now()

#         try:
#             group.crystalClass = mx_collect_dict['crystalClass']
#         except KeyError,diag:
#              pass

#         modes=("Software binned", "Unbinned", "Hardware binned")

#         try:
#             det_mode = int(mx_collect_dict['detector_mode'])
#             group.detectorMode = modes[det_mode]
#         except (KeyError, IndexError, ValueError, TypeError):
#             det_mode = 1
#             group.detectorMode = modes[det_mode]


            try:
                try:
                    helical_used = mx_collect_dict['helical']
                except:
                    helical_used = False
                else:
                    if helical_used:
                        mx_collect_dict['experiment_type'] = 'Helical'
                        mx_collect_dict['comment'] = 'Helical'

                try:
                    directory = mx_collect_dict['fileinfo']['directory']
                except:
                    directory = ''
                else:
                    if 'mesh' in directory:
                        mesh_used = True
                    else:
                        mesh_used = False

                    if mesh_used:
                        mx_collect_dict['experiment_type'] = 'Mesh'
                        comment = mx_collect_dict.get("comment", "")
                        if not comment:
                            try:
                                mx_collect_dict['comment'] = \
                                    'Mesh: phiz:' +  str(mx_collect_dict['motors'].values()[0]) + \
                                    ', phiy' + str(mx_collect_dict['motors'].values()[1])
                            except:
                                mx_collect_dict['comment'] = 'Mesh: Unknown motor positions'   

                group.experimentType = mx_collect_dict['experiment_type']
            except KeyError,diag:
                pass


            try:
                group.sessionId = mx_collect_dict['sessionId']
            except:
                pass

            try:
                start_time = mx_collect_dict["collection_start_time"]
                start_time = datetime.\
                             strptime(start_time , "%Y-%m-%d %H:%M:%S")
                group.startTime = start_time
            except:
                pass

            try:
                group.dataCollectionGroupId = mx_collect_dict["group_id"]
            except:
                pass

            return group

        
    @staticmethod
    def from_data_collect_parameters(mx_collect_dict):
        """
        Ceates a dataCollectionWS3VO from mx_collect_dict.
        :rtype: dataCollectionWS3VO
        """
        if len(mx_collect_dict['oscillation_sequence']) != 1:
            raise ISPyBArgumentError("ISPyBServer: number of oscillations" + \
                                     " must be 1 (until further notice...)")
        ws_client = None
        data_collection = None

        try:
            ws_client = Client(_WS_COLLECTION_URL,
                               cache = None)

            data_collection = \
                ws_client.factory.create('ns0:dataCollectionWS3VO')
        except:
            raise

        osc_seq = mx_collect_dict['oscillation_sequence'][0]

        try:
            data_collection.runStatus = mx_collect_dict["status"] 
            data_collection.axisStart = osc_seq['start']

            data_collection.axisEnd = (\
                float(osc_seq['start']) +\
                    (float(osc_seq['range']) - float(osc_seq['overlap'])) *\
                    float(osc_seq['number_of_images']))

            data_collection.axisRange = osc_seq['range']
            data_collection.overlap = osc_seq['overlap']
            data_collection.numberOfImages = osc_seq['number_of_images']
            data_collection.startImageNumber = osc_seq['start_image_number']
            data_collection.numberOfPasses = osc_seq['number_of_passes']
            data_collection.exposureTime = osc_seq['exposure_time']
            data_collection.imageDirectory = \
                mx_collect_dict['fileinfo']['directory']

            if osc_seq.has_key('kappaStart'):
                if osc_seq['kappaStart']!=0 and osc_seq['kappaStart']!=-9999:
                    data_collection.rotationAxis = 'Omega' 
                    data_collection.omegaStart = osc_seq['start']
                else:
                    data_collection.rotationAxis = 'Phi'
            else:
                data_collection.rotationAxis = 'Phi'
                osc_seq['kappaStart'] = -9999
                osc_seq['phiStart'] = -9999

            data_collection.kappaStart = osc_seq['kappaStart']
            data_collection.phiStart = osc_seq['phiStart']

        except KeyError,diag:
            err_msg = \
                "ISPyBClient: error storing a data collection (%s)" % str(diag)
            raise ISPyBArgumentError(err_msg)

        data_collection.detector2theta = 0 

        try:
            data_collection.dataCollectionId = \
                int(mx_collect_dict['collection_id'])
        except KeyError:
            pass

        try:
            data_collection.wavelength = mx_collect_dict['wavelength']
        except KeyError,diag:
            pass

        res_at_edge = None
        try:
            try:
                res_at_edge = float(mx_collect_dict['resolution'])
            except:
                res_at_edge = float(mx_collect_dict['resolution']['lower'])
        except KeyError:
            try:
                res_at_edge = float(mx_collect_dict['resolution']['upper'])
            except:
                pass
        if res_at_edge is not None:
            data_collection.resolution = res_at_edge

        try:
            data_collection.resolutionAtCorner = \
                mx_collect_dict['resolutionAtCorner']
        except KeyError:
            pass

        try:
            data_collection.detectorDistance = \
                mx_collect_dict['detectorDistance']
        except KeyError,diag:
            pass

        try:
            data_collection.xbeam = mx_collect_dict['xBeam']
            data_collection.ybeam = mx_collect_dict['yBeam']
        except KeyError,diag:
            pass

        try:
            data_collection.beamSizeAtSampleX = \
                mx_collect_dict['beamSizeAtSampleX']
            data_collection.beamSizeAtSampleY = \
                mx_collect_dict['beamSizeAtSampleY']
        except KeyError:
            pass
            
        try:
            data_collection.beamShape = mx_collect_dict['beamShape']
        except KeyError:
            pass

        try:
            data_collection.slitGapHorizontal = \
                mx_collect_dict['slitGapHorizontal']
            data_collection.slitGapVertical = \
                mx_collect_dict['slitGapVertical']
        except KeyError:
            pass

        try:
            data_collection.imagePrefix = mx_collect_dict['fileinfo']['prefix']
        except KeyError,diag:
            pass

        try:                
            data_collection.imageSuffix = mx_collect_dict['fileinfo']['suffix']
        except KeyError,diag:
            pass
        try:
            data_collection.fileTemplate = \
                mx_collect_dict['fileinfo']['template']
        except KeyError,diag:
            pass

        try:
            data_collection.dataCollectionNumber = \
                mx_collect_dict['fileinfo']['run_number']
        except KeyError,diag:
            pass

        try:
            data_collection.synchrotronMode = \
                mx_collect_dict['synchrotronMode']
            data_collection.flux = mx_collect_dict['flux']
        except KeyError,diag:
            pass

        try:
            data_collection.flux_end = mx_collect_dict['flux_end']
        except KeyError,diag:
            pass

        try:
            data_collection.transmission = mx_collect_dict["transmission"]
        except KeyError:
            pass

        try:
            data_collection.undulatorGap1 = mx_collect_dict["undulatorGap1"]
            data_collection.undulatorGap2 = mx_collect_dict["undulatorGap2"]
            data_collection.undulatorGap3 = mx_collect_dict["undulatorGap3"]
        except KeyError:
            pass

        try:
            data_collection.xtalSnapshotFullPath1 = \
                mx_collect_dict['xtalSnapshotFullPath1']
            data_collection.xtalSnapshotFullPath2 = \
                mx_collect_dict['xtalSnapshotFullPath2']
            data_collection.xtalSnapshotFullPath3 = \
                mx_collect_dict['xtalSnapshotFullPath3']
            data_collection.xtalSnapshotFullPath4 = \
                mx_collect_dict['xtalSnapshotFullPath4']
        except KeyError:
            pass

        try:
            data_collection.centeringMethod = \
                mx_collect_dict['centeringMethod']
        except KeyError :
            pass

        try:   
            data_collection.actualCenteringPosition = \
                mx_collect_dict['actualCenteringPosition']
        except KeyError:
            pass


        try:
            data_collection.dataCollectionGroupId = mx_collect_dict["group_id"]
        except KeyError:
            pass


        try:
            data_collection.detectorId = mx_collect_dict["detector_id"]
        except KeyError:
            pass
                
        try:
             data_collection.strategySubWedgeOrigId = \
                 mx_collect_dict['screening_sub_wedge_id']
        except:
             pass
         
        try:
            start_time = mx_collect_dict["collection_start_time"]
            start_time = datetime.\
                         strptime(start_time , "%Y-%m-%d %H:%M:%S")
            data_collection.startTime = start_time
        except:
            pass

        if mx_collect_dict.has_key('lims_start_pos_id'):
            data_collection.startPositionId = mx_collect_dict['lims_start_pos_id']

        if mx_collect_dict.has_key('lims_end_pos_id'):
            data_collection.endPositionId = mx_collect_dict['lims_end_pos_id']

        data_collection.endTime = datetime.now()

        return data_collection


class ISPyBArgumentError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.value)
