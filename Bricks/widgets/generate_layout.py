import os
import sys
from subprocess import call

if __name__ == "__main__":

    for _file in os.listdir('./ui_files/'):
        if _file.endswith('.ui'):
            py_file = _file.split('.')[0] + '.py'
            print 'pyuic -x ./ui_files/' + str(_file) + ' > ' + py_file
            call('pyuic -x ./ui_files/' + str(_file) + ' > ' + py_file, shell = True)
