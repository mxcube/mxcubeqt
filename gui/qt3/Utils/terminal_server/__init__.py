from terminal_server import *
from gevent import monkey

monkey.patch_all(thread=False, subprocess=False)
