import dbm.dumb
import shelve
import dbm
import sys

class DumbDbmShelve(shelve.Shelf):
    def __init__(self, *args, **kwargs):
        shelve.Shelf.__init__(self, dbm.dumb.open(*args), **kwargs)

if __name__ == '__main__':
  if dbm._defaultmod is not None and dbm._defaultmod.__name__ != 'gdbm':
    s=DumbDbmShelve(sys.argv[1])
  else:
    s=shelve.open(sys.argv[1])
  s.close()

