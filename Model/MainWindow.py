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
		self.buttonDraw.clicked.connect(self.draw)

		# Basic Info
		self.numOfPoints = 0
		self.numOfLines = 0
		self.numOfCells = 0


		self.show()

	def loadMesh(self):
		fileName = QFileDialog.getOpenFileName(self, "Load Mesh", ".", "Mesh Files (*.obj *.off)")
		if len(fileName) == 0:
			return

		self.vtkViewer.loadMesh(fileName)
		self.interactor.Initialize()
		self.interactor.Start()

		self.numOfPoints, self.numOfLines, self.numOfCells = self.vtkViewer.basicInfo()
		self.NumOfPointsText.setText(str(self.numOfPoints))
		self.NumOfLinesText.setText(str(self.numOfLines))
		self.NumOfCellsText.setText(str(self.numOfCells))

	def loadColor(self):
		fileName = QFileDialog.getOpenFileName(self, "Load Color", ".", "Color Files (*.txt)")
		if len(fileName) == 0 or self.vtkViewer.reader == None:
			return
		if not self.vtkViewer.loadColor(fileName):
			return 

		self.interactor.Initialize()	
		self.interactor.Start()

	def draw(self):
		if self.vtkViewer.reader == None:
			return

		num = self.inputID.text()
		if self.AP2.isChecked() or self.AP3.isChecked():
			try:
				num = list(map(int, num.split(' ')))
			except Exception:
				return
		else:
			try:
				num = int(num)
			except Exception:
				return

		if self.POP.isChecked() and num >= 0 and num < self.numOfPoints:
			self.vtkViewer.drawPOP(num)
		elif self.MOP.isChecked() and num >= 0 and num < self.numOfPoints:
			self.vtkViewer.drawMOP(num)
		elif self.MOM.isChecked() and num >= 0 and num < self.numOfCells:
			self.vtkViewer.drawMOM(num)
		elif self.NOM.isChecked() and num >= 0 and num < self.numOfCells:
			self.vtkViewer.drawNOM(num)
		elif (self.AP2.isChecked() or self.AP3.isChecked()) and max(num) < self.numOfPoints and min(num) >= 0:
			if self.AP2.isChecked():
				self.vtkViewer.drawArea(num, 2)
			else:
				self.vtkViewer.drawArea(num, 3)
		else:
			return

		self.interactor.Initialize()
		self.interactor.Start()


		

