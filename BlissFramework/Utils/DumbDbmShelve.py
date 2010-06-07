import dumbdbm
import shelve
import anydbm
import sys

class DumbDbmShelve(shelve.Shelf):
    def __init__(self, *args, **kwargs):
        shelve.Shelf.__init__(self, dumbdbm.open(*args), **kwargs)

if __name__ == '__main__':
  if anydbm._defaultmod is not None and anydbm._defaultmod.__name__ != 'gdbm':
    s=DumbDbmShelve(sys.argv[1])
  else:
    s=shelve.open(sys.argv[1])
  s.close()

