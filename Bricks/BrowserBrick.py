import logging
import os
from os.path import abspath
import time
import types
from datetime import datetime, timedelta

try:
    import cPickle as pickle
except ImportError:
    import pickle

from BlissFramework import BaseComponents
from BlissFramework import Icons
import BlissFramework

from qt import *
from qttable import QTable, QTableItem

__category__ = 'gui_utils'

class BrowserBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        #map displayed string in the history list -> actual file path
        self.history_map = dict()

        self.layout = QVBoxLayout(self)

        self.defineSlot('load_file', ())
        self.defineSlot('login_changed', ())
        # New slot created for displaying html pages from the queue (Olof 2013/04/25)
        self.defineSlot('new_html', ())
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('history', 'string', '', hidden=True)
        self.addProperty('sessions ttl (in days)', 'integer', '30')

        #make sure the history property is a pickled dict
        try:
            hist = pickle.loads(self.getProperty('history').getValue())
        except: # EOFError if the string is empty but let's not count on it
            self.getProperty('history').setValue(pickle.dumps(dict()))

        # maybe defer that for later
        self.cleanup_history()

        self.main_layout = QSplitter(self)
        self.main_layout.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        # left part of the splitter
        self.history_box = QVBox(self.main_layout)
        self.history_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.sort_order = True

        self.sort_col = None

        self.history = QTable(self.history_box)
	self.history.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))
        self.history.setSelectionMode(QTable.SingleRow)
        self.history.setNumCols(3)
        self.history.verticalHeader().hide()
        self.history.setLeftMargin(0)
        self.history.setSorting(False)
        QObject.connect(self.history,
                        SIGNAL('currentChanged(int,int)'),
                        self.history_changed)
    
        #by default sorting only sorts the columns and not whole rows.
        #let's reimplement that
        QObject.connect(self.history.horizontalHeader(),
                        SIGNAL('clicked(int)'),
                        self.sort_column)

        header = self.history.horizontalHeader()
        header.setLabel(0, 'Time and date')
        header.setLabel(1, 'Prefix')
        header.setLabel(2, 'Run number')
        
        self.clear_history_button = QPushButton('Clear history', self.history_box)
        self.history_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        QObject.connect(self.clear_history_button, SIGNAL('clicked()'),
                        self.clear_history)

        # Right part of the splitter
        self.browser_box = QWidget(self.main_layout)
        QVBoxLayout(self.browser_box)
        self.browser_box.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.top_layout = QHBoxLayout(self.browser_box)

        self.back_button = QToolButton(self.browser_box)
        self.back_button.setIconSet(QIconSet(Icons.load('Left2')))
        self.back_button.setTextLabel('Back')
        self.back_button.setUsesTextLabel(True)
        self.back_button.setTextPosition(QToolButton.BelowIcon)
        self.back_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.forward_button = QToolButton(self.browser_box)
        self.forward_button.setIconSet(QIconSet(Icons.load('Right2')))
        self.forward_button.setTextLabel('Forward')
        self.forward_button.setUsesTextLabel(True)
        self.forward_button.setTextPosition(QToolButton.BelowIcon)
        self.forward_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.top_layout.addWidget(self.back_button)
        self.top_layout.addWidget(self.forward_button)

        self.browser_box.layout().addLayout(self.top_layout)

        self.browser = QTextBrowser(self.browser_box)
        self.browser.setReadOnly(True)
	self.browser_box.layout().addWidget(self.browser)

        self.layout.addWidget(self.main_layout)

        #initially disabled
        self.forward_button.setEnabled(False)
        self.back_button.setEnabled(False)
        #connections
        QObject.connect(self.browser, SIGNAL('backwardAvailable(bool)'),
                        self.back_button.setEnabled)
        QObject.connect(self.browser, SIGNAL('forwardAvailable(bool)'),
                        self.forward_button.setEnabled)
        QObject.connect(self.back_button, SIGNAL('clicked()'),
                        self.browser.backward)
        QObject.connect(self.forward_button, SIGNAL('clicked()'),
                        self.browser.forward)

        self.edna = None


        # resize the splitter to something like 1/4-3/4
#        width = self.main_layout.width()
#        left = width / 4.0
#        right = width - left
#        logging.debug('setting splitter sizes to %d and %d', left, right)
#        self.main_layout.setSizes([left, right])
        
    def sort_column(self, col_number):
        logging.debug('%s: sorting with column %d', self, col_number)
        if col_number == self.sort_column:
            # switch the sort order
            self.sort_order = self.sort_order ^ True
        else:
            self.sort_order = True #else, ascending
            self.sort_column = col_number
        self.history.sortColumn(col_number, self.sort_order, True)

        # put the right decoration on the header label
        if self.sort_order:
            direction = Qt.Ascending
        else:
            direction = Qt.Descending
        self.history.horizontalHeader().setSortIndicator(col_number, direction)

    def load_file(self, path):
        if self.browser.mimeSourceFactory().data(path) == None:
            self.browser.setText('<center>FILE NOT FOUND</center>')
        else:
            self.browser.setSource(abspath(path))

    def history_changed(self, row, col):
        logging.debug('history elem selected: %d:%d', row, col)
        index = (str(self.history.text(row,0)),
                 str(self.history.text(row,1)),
                 str(self.history.text(row,2)))
        try:
            path = self.history_map[index]
            self.load_file(path)
        except KeyError, e:
            # can happen when qt sends us the signal with
            # null data and we get the key ("","","")
            pass

    def new_html(self, html_path, image_prefix, run_number):
	logging.getLogger().debug('got a new html page: %s, prefix: %r, run number: %s', html_path, image_prefix, run_number)

        # prepend the time and date to the path we just got so
        # the history is more readable
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        index = (time_string, str(image_prefix), str(run_number))
        self.history_map[index] = html_path
        # synchronize the history prop
        if self.current_user is not None:
            whole_history = pickle.loads(self.getProperty('history').getValue())
            whole_history[self.current_user] = self.history_map
            self.getProperty('history').setValue(pickle.dumps(whole_history))
                
        self.history.insertRows(self.history.numRows())
        logging.debug('numRows() is %d', self.history.numRows())
        rows = self.history.numRows() - 1

        self.history.setText(rows, 0, QString(time_string))
        self.history.setText(rows, 1, QString(str(image_prefix)))
        self.history.setText(rows, 2, QString(str(run_number)))

        logging.debug('numRows() is %d', self.history.numRows())

        self.load_file(html_path)
    
    def clear_history(self):
        self.history_map.clear()
        self.history.setNumRows(0)

    def propertyChanged(self, prop, oldval, newval):
        if prop == 'mnemonic':
            logging.getLogger().debug('BrowserBrick: using edna object %s', newval)
            if self.edna is not None:
                self.disconnect(self.edna, PYSIGNAL('newEDNAHTML'), self.new_html)
            self.edna = self.getHardwareObject(newval)
            logging.getLogger().debug('edna object is now: %s', self.edna)
            self.connect(self.edna, PYSIGNAL('newEDNAHTML'), self.new_html)
 
    def run(self):
        pass

    def login_changed(self, session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        logging.debug('BrowserBrick::login_changed: login changed to %r', session_id)
        if session_id is None:
            # user logged out
            logging.debug('user logged out')
            self.current_user = None
        else:
            self.current_user = (prop_code, prop_number)
            logging.debug('current user is now %r', self.current_user)
        self.clear_all()
        self.fill_history_for(self.current_user)

    def clear_all(self):
        self.clear_history()
        self.browser.setText('')

    def fill_history_for(self, user):
        if user is None: return

        logging.debug('loading history for user %s', user)
        
        whole_history = pickle.loads(self.getProperty('history').getValue())
        try:
            self.history_map = whole_history[user]
        except KeyError:
            #user has no history yet
            self.history_map = dict()
        for k,v in self.history_map.iteritems():
            self.history.insertRows(self.history.numRows())
            logging.debug('numRows() is %d', self.history.numRows())
            rows = self.history.numRows() - 1

            self.history.setText(rows, 0, k[0])
            self.history.setText(rows, 1, k[1])
            self.history.setText(rows, 2, k[2])

    def cleanup_history(self):
        histories = pickle.loads(self.getProperty('history').getValue())
        sessions_ttl = self.getProperty('sessions ttl (in days)').getValue()
        limit_date = datetime.now() - timedelta(sessions_ttl)
        #we're mutating the dict so do not use iteritems() just to be sure
        for user in histories.keys():
            history = histories[user]
            #get the keys where the date is more recent than the limit date
            valid_keys = [x for x in history.keys()
                          if datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S') > limit_date]
            #NB: old format was "%a, %d %b %Y %H:%M:%S"
            if len(valid_keys) != len(history):
                # some entries are too old, copy only the ones that are recent enough
                new_hist = dict((k,history[k]) for k in valid_keys)
                logging.debug('BrowserBrick: removed %d entries from saved history for user %s',
                              len(history) - len(valid_keys),
                              user)
                histories[user] = new_hist
        self.getProperty('history').setValue(pickle.dumps(histories))
