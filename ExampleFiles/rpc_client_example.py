import queue_model
import jsonpickle
import xmlrpclib

# Create a 'data collection' group and add a data collection
dcg = queue_model.TaskGroup(None)
dcg.set_name('Group')
dc = queue_model.DataCollection(dcg)
dc.set_name('dc-1')

# Some basic settings
dc.acquisitions[0].acquisition_parameters.exp_time = 5
dc.acquisitions[0].acquisition_parameters.num_images = 10

dc.acquisitions[0].path_template.directory = '/data/id14eh1/inhouse/opid141' +\
                                             '/20130515/RAW_DATA/burn-workflow/'
dc.acquisitions[0].path_template.prefix = 'ref-w1'
dc.acquisitions[0].path_template.num_files = 10

# Seralize the task
json_dcg_list = jsonpickle.encode([dcg])

s = xmlrpclib.ServerProxy('http://linoscarsson:8000')
s.log_message('Adding collection from example client.', 'info')
s.add_to_queue(json_dcg_list)

s.log_message('Collection added, starting queue.', 'info')
s.start_queue()
