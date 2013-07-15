import jsonpickle
import xmlrpclib
import time
import sys
import imp

server = xmlrpclib.ServerProxy('http://localhost:8000')
print "Serialisation methods available for native queue objects:", server.queue_get_available_serialisations()
server.queue_set_serialisation("json")
BASE_DATA_DIRECTORY = '/data/id14eh1/inhouse/opid141/20130515/RAW_DATA/'

# Retrieve code of queue model from server and compile and import it
# Recipe from http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/

for (module_name, module_code) in server.queue_get_model_code():
    queue_model_objects = imp.new_module(module_name)
    exec module_code in queue_model_objects.__dict__
    sys.modules[module_name] = queue_model_objects


# Create a 'data collection' group and add a data collection
dcg = queue_model_objects.TaskGroup()
dcg.set_name('Interleaved MAD')
json_dcg = jsonpickle.encode(dcg)
server.log_message('Adding task group from example client.', 'info')
dcg_id = server.queue_add_child(1, json_dcg)

# Creating and configuring the energyscan
energy_scan = queue_model_objects.EnergyScan()
energy_scan.path_template.directory = BASE_DATA_DIRECTORY
energy_scan.path_template.base_prefix = 'escan'
energy_scan.set_name(energy_scan.path_template.get_prefix())

json_es = jsonpickle.encode(energy_scan)
server.log_message('Adding energy scan from example client.', 'info')
es_id = server.queue_add_child(dcg_id, json_es)

server.log_message('Executing queue.', 'info')
server.start_queue()

is_executing = server.is_queue_executing()

while(is_executing):
    time.sleep(1)
    is_executing = server.is_queue_executing()

server.log_message('Queue Executed from rpc client.', 'info')

#
# The queue was executed, get the results from the model.
#

energy_scan = jsonpickle.decode(server.queue_get_node(es_id))
energies = [(energy_scan.result.inflection, 'ip'),
            (energy_scan.result.first_remote, 'rm'),
            (energy_scan.result.second_remote, 'rm2'),
            (energy_scan.result.peak, 'pk')]

for energy in energies:
    dc = queue_model_objects.DataCollection()

    # Some basic settings
    dc.acquisitions[0].acquisition_parameters.exp_time = 5
    dc.acquisitions[0].acquisition_parameters.num_images = 10
    dc.acquisitions[0].acquisition_parameters.osc_start = 0
    dc.acquisitions[0].acquisition_parameters.osc_range = 45
    dc.acquisitions[0].acquisition_parameters.overlap = 0
    dc.acquisitions[0].acquisition_parameters.inverse_beam = True
    dc.acquisitions[0].acquisition_parameters.energy = energy[0]
    

    dc.acquisitions[0].path_template.directory = BASE_DATA_DIRECTORY
    dc.acquisitions[0].path_template.base_prefix = 'escan'
    dc.acquisitions[0].path_template.mad_prefix = energy[1]
    dc.set_name(dc.acquisitions[0].path_template.get_prefix())
    dc.acquisitions[0].path_template.num_files = 10

    # Seralize the task
    dc = jsonpickle.encode(dc)
    dc_id = server.queue_add_child(dcg_id, dc)
    server.log_message('Collection added for %s added' % energy[1], 'info')

server.log_message('Executing queue.', 'info')

server.start_queue()
# Or if you just want to execute the group
#server.queue_execute_entry_with_id(dcg_id)
