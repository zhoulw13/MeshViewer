from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from Model.VtkViewer import *

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)
		uic.loadUi('Design/Mainwindow.ui', self)

		self.vtkViewer = VtkViewer()
		self.vtkWidget = QVTKRenderWindowInteractor(self.mainFrame)
		self.vtkWidget.setGeometry(QRect(0,0,self.mainFrame.frameGeometry().width(), self.mainFrame.frameGeometry().height()))
		self.vtkWidget.GetRenderWindow().AddRenderer(self.vtkViewer.renderer)
		self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

		# Action Events
		self.actionMesh.triggered.connect(self.loadMesh)
		self.actionColor.triggered.connect(self.loadColor)
		self.actionExit.triggered.connect(self.close)

		self.show()

	def loadMesh(self):
		fileName = QFileDialog.getOpenFileName(self, "Load Mesh", ".", "Mesh Files (*.obj *.off)")
		if len(fileName) == 0:
			return

		self.vtkViewer.loadMesh(fileName)
		self.interactor.Initialize()
		self.interactor.Start()

		a,b,c = self.vtkViewer.basicInfo()
		self.NumOfPoints.setText(str(a))
		self.NumOfLines.setText(str(b))
		self.NumOfCells.setText(str(c))

	def loadColor(self):
		fileName = QFileDialog.getOpenFileName(self, "Load Color", ".", "Color Files (*.txt)")
		if len(fileName) == 0:
			return
		if not self.vtkViewer.loadColor(fileName):
			return 

		self.interactor.Initialize()	
		self.interactor.Start()

		

