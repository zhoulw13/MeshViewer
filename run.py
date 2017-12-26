import sys
from PyQt4.QtGui import *
from Model.MainWindow import *

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MainWindow()
	sys.exit(app.exec_())