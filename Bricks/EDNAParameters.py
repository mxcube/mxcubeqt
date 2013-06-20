"""
brick interfacing with the edna workflow engine, asks for parameters
when the workflow engine needs some
"""

import types
import logging
import tempfile
import os
from qt import *
from lxml import etree
from BlissFramework.BaseComponents import BlissWidget
#from XSDataMXv1 import XSDataCharacterisation
from XSDataMXCuBEv1_3 import XSDataResultMXCuBE
from XSDataMXCuBEv1_3 import XSDataMXCuBEParameters
from ednaxmlhelper import get_field_containers, get_fields
from paramsgui import FieldsWidget



class EDNAParameters(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('edna object', 'string', '')
        self.addProperty('workflows base dir', 'string', '')

        #when starting a workflow we emit this signal and expect
        #to get the beamline params through the slot
        self.defineSlot('updateBeamlineParameters', ())
        self.defineSlot("populate_workflow_widget",({}))  
        self.defineSignal('beamlineParametersNeeded', ())
        self.defineSignal('workflowAvailable', ())

        #we need the session id
        self.defineSlot('login_changed', ())

        self.beamline_params = dict()

        self.session_id = None
        self.params_widget = None
        self.workflow = None
        self.edna = None
        self.previous_workflow_state = None
        self.workflow_output_file = None
        self.process_dir = None
        QGridLayout(self, 4, 2)
        self.workflows_box = QHBoxLayout()
        self.ok_button = QPushButton('Continue', self)
        self.abort_button = QPushButton('Abort', self)

        self.workflow_list = QComboBox(self)
        self.start_button = QPushButton('Start', self)
        self.workflows_box.addWidget(self.workflow_list)
        self.workflows_box.addWidget(self.start_button)

        self.layout().addMultiCellLayout(self.workflows_box, 0, 0, 0, 1)

        self.info_label = QLabel(self)
        self.info_label.setSizePolicy(QSizePolicy.MinimumExpanding,
                                      QSizePolicy.Fixed)

        self.layout().addWidget(self.ok_button, 2, 0)
        self.layout().addWidget(self.abort_button, 2, 1)
        self.layout().addMultiCellWidget(self.info_label, 3, 3, 0, 1)

        QObject.connect(self.ok_button, SIGNAL('clicked()'),
                        self.send_parameters)
        QObject.connect(self.abort_button, SIGNAL('clicked()'),
                        self.abort_workflow)
        QObject.connect(self.start_button, SIGNAL('clicked()'),
                        self.start_workflow)
        QObject.connect(self.workflow_list, SIGNAL('activated ( const QString &)'),
                        self.workflow_selected)
        # name -> model path mapping
        self.workflows = dict()

    def init(self):
        pass

    def setExpertMode(self, expert):
        self.setEnabled(True)
        self.emit(PYSIGNAL('workflowAvailable'), (True, ))
        #self.setEnabled(expert)
        #self.emit(PYSIGNAL('workflowAvailable'), (expert, ))

    def propertyChanged(self, prop, old_val, new_val):
        if prop == 'mnemonic':
            if self.workflow is not None:
                self.disconnect(self.workflow, PYSIGNAL('parametersNeeded'),
                                self.prompt_parameters)
            self.workflow = self.getHardwareObject(new_val)
            if self.workflow is not None:
                #get the state
                state = self.workflow.state.getValue()
                self.workflow_state_changed((state,))
                self.connect(self.workflow, PYSIGNAL('parametersNeeded'),
                             self.prompt_parameters)
                self.connect(self.workflow, PYSIGNAL('stateChanged'),
                             self.workflow_state_changed)
                self.connect(self.workflow, PYSIGNAL('currentActorChanged'),
                             self.current_actor_changed)
                #populate the available workflows list
                self.refresh_workflows()
        if prop == 'edna object':
            self.edna = self.getHardwareObject(new_val)
            logging.debug('%r: Edna object is now %s (%r)', self, new_val, self.edna)

    def prompt_parameters(self, xml):
        logging.debug('got back XML from server:\n%s', xml)
        # Edited by Olof 2013/04/16: Temporary fix for handling messages containing
        # XML markup
        #xml_root = etree.fromstring(xml)
        xml_root = etree.fromstring(xml, parser=etree.XMLParser(recover=True))

        # Special case until Olof implements the saner XML format on the server side
        if xml_root.tag == 'message':
            message = dict(type='message', level='info', text='no message')
            for node in xml_root:
                option = node.tag.strip()
                # rename type to level, as type is used for the type
                # this is unfortunate
                if option == 'type':
                    option = 'level'
                message[option] = node.text.strip()
            fields = [message]
        else:            
            containers = get_field_containers(xml_root)
            if len(containers) == 0: return
            fields = get_fields(containers[0])
            if self.params_widget is not None:
                self.layout().removeChild(self.params_widget)
        self.params_widget = FieldsWidget(fields, self)

        current_values = self.workflow.get_values_map()
        logging.debug('current values are: %s', current_values)
        self.params_widget.set_values(current_values)
        self.layout().addMultiCellWidget(self.params_widget, 1, 1, 0, 1)
        self.params_widget.show()
        self.ok_button.setEnabled(True)
        


    def send_parameters(self):
        if self.params_widget is not None:
            params_map = self.params_widget.get_parameters_map()
            logging.debug('setting values %r', params_map)
            self.workflow.set_values_map(params_map)
    
    def refresh_workflow_state(self, new_state, actor):
        #abort button should never be disabled
        new_state = str(new_state) #convert from DevState to string
        if self.params_widget is not None: self.params_widget.setEnabled(new_state == "OPEN")
        self.ok_button.setEnabled(new_state == "OPEN")

        # only available when engine is idle
        self.start_button.setEnabled(new_state == "ON")
        self.workflow_list.setEnabled(new_state == "ON")

        if new_state == "RUNNING":
            message = 'Workflow engine running (actor: %s)' % self.workflow.current_actor.getValue()
        elif new_state == "STANDBY":
            message = 'Workflow engine paused'
        elif new_state == "ON":
            self.refresh_workflows()
            message = 'Workflow engine idle'
        elif new_state == "OPEN":
            try:
                actor_name = self.workflow.current_actor.getValue()
            except:
                actor_name = 'Unknown actor'
            message = 'Actor %s waiting for parameters' % actor_name
        elif new_state == "None":
            message = 'Workflow engine is offline'
        else:
            message = 'Workflow engine is in a state it should not be in (%r)' % (new_state, )
            #self.start_button.setEnabled(new_state == "ON")
            #self.workflow_list.setEnabled(new_state == "ON")
        self.info_label.setText(message)
        logging.info(message)

    def current_actor_changed(self, actor):
        if type(actor) == types.ListType or type(actor) == types.TupleType:
            actor = actor[0]
        try:
            state = self.workflow.state.getValue()
            self.refresh_workflow_state(state, actor)
        except:
            self.info_label.setText('Lost connection with workflow engine')
        
    def workflow_state_changed(self, new_state): 
        new_state = str(new_state)
        logging.debug('%s: new workflow state is %r', self.name(), new_state)
        if type(new_state) == types.ListType or type(new_state) == types.TupleType:
            new_state = new_state[0]
        try:
            actor = self.workflow.current_actor.getValue()
            self.refresh_workflow_state(new_state, actor)
        except:
            self.info_label.setText('Lost connection with workflow engine')
        if new_state == "ON" and self.previous_workflow_state == "RUNNING":
            # workflow finished, open the output file and use an EDNACaracterize method to
            # continue the work
            if self.workflow_output_file is not None and os.path.exists(self.workflow_output_file):
                logging.debug('Workflow finished, sending the results to %r', self.edna)
                logging.debug('Workflow file is %s', self.workflow_output_file)
                try:
                    data = XSDataResultMXCuBE.parseFile(self.workflow_output_file)
                    self.edna.readEDNAResults(data.getCharacterisationResult(), self.workflow_output_file,
                                              self.beamline_params['directory'], self.beamline_params['prefix'],
                                              int(self.beamline_params['run_number']),
                                              process_dir=self.process_dir, do_inducedraddam=False)
                    logging.debug('Results sent')
                except:
                    logging.debug('Malformed or empty results file')
            else:
                logging.debug('Workflow finished, no result file')
            # then remove the current widget with the parameters
            if self.params_widget is not None:
                self.layout().removeChild(self.params_widget)
        self.previous_workflow_state = new_state

    def abort_workflow(self):
        if self.workflow is not None:
            self.workflow.abort()

    def refresh_workflows(self):
        # keep the name of the current workflow so we can reselect it
        # by default
        previous_workflow = str(self.workflow_list.currentText())
        previous_workflow_index = None
        self.workflows.clear()
        workflows = self.workflow.get_available_workflows()
        self.workflow_list.clear()
        for (w,i) in zip(workflows, range(len(workflows))):
            path = w['path']
            name = w['name']
            if name == previous_workflow:
                previous_workflow_index = i
            self.workflow_list.insertItem(name)
            self.workflows[name] = w
        if previous_workflow_index is not None:
            self.workflow_list.setCurrentItem(previous_workflow_index)
        self.workflow_selected(self.workflow_list.currentText())

    def start_workflow(self):
        #get the beamline params
        logging.debug('requesting beamline parameters')
        self.emit(PYSIGNAL('beamlineParametersNeeded'), ())
        name = str(self.workflow_list.currentText())
        params = ['modelpath', self.workflows[name]['path']]
        #blparams = XSDataMXCuBEParameters()
        for k,v in self.beamline_params.iteritems():
            # we'll have to lookup how those are specified someday
            # it's a (bool, string, string) tuple
            if k in ['mad_1_energy', 'mad_2_energy', 'mad_3_energy', 'mad_4_energy']:
                if v[0] is False:
                    param = None
                else:
                    param = v[1]
            elif k == 'sum_images':
                param = v[0]
            elif k == 'inverse_beam':
                param = v[0]
            else: param=v
            logging.debug('setting %s to %r', k, param)
            #setattr(blparams, k, param)
            params.append(k)
            params.append(str(param))
        # we also need the session id
        #blparams.sessionId = self.session_id
        #output_dir = self.beamline_params['directory'].replace('RAW_DATA', 'PROCESSED_DATA')
        # we'll need that one later to pass to the edna characterise HO
        #self.process_dir = output_dir
	#if not os.path.exists(output_dir):
        #    os.makedirs(output_dir)
        #(handle, filename) = tempfile.mkstemp(suffix='.xml', prefix='edna_output_', dir=output_dir)
        #blparams.output_file = filename
        
        # convert that stuff to xml
        #params.append('mxcube_parameters')
        #params.append(blparams.marshal())
        #self.workflow_output_file = filename
        logging.debug('starting workflow %s with params %r', name, params)
        self.workflow.start(params)

    def updateBeamlineParameters(self, params):
        logging.debug('got beamline param update, new values: %r', params)
        self.beamline_params = dict()
	# as XSDataSomethingSomething marshalling routing uses format string
	# BUT does not enforces its arg type, we have to do some type
	# conversion, lest it will explode when we call marshal() on it       
        floats = ['exposure_time', 'resolution', 'resolution_at_corner', 'x_beam', 'y_beam', 'beam_size_x', 'beam_size_y', 'overlap', 'osc_start', 'osc_range', 'kappaStart', 'current_detdistance', 'current_wavelength', 'phiStart', 'current_energy', 'current_osc_start'] 
        ints = ['sessionId', 'blSampleId', 'first_image', 'number_images', 'run_number', 'number_passes'] 
        for k,v in params.iteritems():
            value = v
            if k in floats:
                logging.debug('converting %s (%r) to float', k, v)
                value = float(v)
            if k in ints:
                logging.debug('converting %s (%r) to int', k, v)
                value = int(v)
            self.beamline_params[k] = value


    def workflow_selected(self, name):
        if type(name) != types.StringType:
            name = str(name)
        #get the path of the html describing the WF
        workflow_doc = self.workflows[name]['doc']
        if self.params_widget is not None:
            self.layout().removeChild(self.params_widget)
        self.params_widget = QTextBrowser(self)
        if os.path.exists(workflow_doc):
            self.params_widget.setSource(workflow_doc)
        else:
            self.params_widget.setText('<center><b>no documentation available</b></center>')
        # add the browser to the layout
        self.layout().addMultiCellWidget(self.params_widget, 1, 1, 0, 1)
        self.params_widget.show()


    def login_changed(self, *login_infos):
        logging.debug('user logged in, logins_info: %r', login_infos)
        if len(login_infos) == 1 and login_infos[0] == None:
            self.session_id = None
        else:
            self.session_id = int(login_infos[0])


    def populate_workflow_widget(self, item):
         self.beamline_params['directory'] = item.get_model().path_template.directory
         self.beamline_params['prefix'] = item.get_model().path_template.get_prefix()
         self.beamline_params['run_number'] = item.get_model().path_template.run_number
         self.beamline_params['collection_software'] = 'mxCuBE - 2.0'
         self.beamline_params['sample_node_id'] = item.get_model().get_parent().\
                                                  get_parent()._node_id
         self.beamline_params['group_node_id'] = item.get_model().get_parent().\
                                                 get_parent()._node_id
