#!/usr/bin/env python
import cPickle
import sys
import os
import pprint
MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
sys.path.insert(0, MXCUBE_ROOT)
from BlissFramework.Utils import PropertyBag

if __name__ == '__main__':
  if len(sys.argv) > 1:
    try:
      f = open(sys.argv[1], 'r')
    except:
      print 'Could not open file',sys.argv[1]
      sys.exit(1)
  else:
    print 'Usage: %s <.gui file> > output_file' % sys.argv[0]
    sys.exit(1)

  config = eval(f.read())
  saved_config = []

  def add_children_properties(children_list, config_list):
    for child in children_list:
      d = {}
      config_list.append({child["name"]:d})
      propbag = cPickle.loads(child["properties"])
      for property in propbag.properties.itervalues():
        d[property.name]=property.getUserValue()
      add_children_properties(child["children"], config_list)

  
  add_children_properties(config, saved_config)

  pprint.pprint(saved_config)  
