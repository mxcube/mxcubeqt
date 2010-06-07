#$Id: FileChooser.py,v 1.1 2004/08/10 10:05:09 guijarro Exp $
from qt import *

class FileChooser(QVBox):
    def __init__(self, parent):
        QVBox.__init__(self, parent)

	import os, os.path
	self.defaultDir = os.getcwd() + '/ '

	self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
	self.setSpacing(10)
	self.setMargin(0)

        QLabel('Data file prefix :', self)
	fileBox = QHBox(self)
	self.lblDirectory = QLabel(self.defaultDir, fileBox)
	self.lblDirectory.setAutoResize(True)
	self.txtFilename = QLineEdit(fileBox)
	self.cmdBrowse = QPushButton('Browse', fileBox)
	self.cmdSetAsCurrentFile = QPushButton('Set as data file', self)

        QObject.connect(self.cmdBrowse, SIGNAL('clicked()'), self.cmdBrowseClicked)
	QObject.connect(self.cmdSetAsCurrentFile, SIGNAL('clicked()'), self.cmdSetAsCurrentFileClicked)


    def setDefaultDir(self, dir):
	import os.path
	self.defaultDir = os.path.normpath(dir) + '/ '


    def cmdBrowseClicked(self):
	directory = QFileDialog.getExistingDirectory(self.defaultDir)  

        if not directory.isEmpty():
            directory = str(directory)
            import os.path
            self.lblDirectory.setText(os.path.normpath(directory) + '/ ')


    def cmdSetAsCurrentFileClicked(self):
	import os, os.path

	dir = os.path.normpath(str(self.lblDirectory.text())[:-1])
	file = str(self.txtFilename.text())
	
	if len(file) > 0:
	    path = os.path.join(dir, file)
	    existingFiles = ''
	    root, dirs, files = os.walk(dir).next()	
	
	    for f in files+dirs:
              if f.startswith(file):
		existingFiles += '%s\n' % f
		 
	    if len(existingFiles) > 0:
	      if QMessageBox.question(None, 'Filename conflict', 'Are you sure you want to delete these files :\n%s' % existingFiles, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel) != QMessageBox.Yes:
		return

	    self.emit(PYSIGNAL('dataFileChanged'), (path, ))
