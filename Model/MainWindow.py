from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPolygonF, QPainter
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from Model.VtkViewer import *
import numpy as np

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
		self.buttonD2.clicked.connect(self.drawD2)

		# Basic Info
		self.numOfPoints = 0
		self.numOfLines = 0
		self.numOfCells = 0

		self.show()

	def loadMesh(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "Load Mesh", ".", "Mesh Files (*.obj *.off)")
		if len(fileName) == 0:
			return

		self.clear()

		self.vtkViewer.loadMesh(fileName)
		self.interactor.Initialize()
		self.interactor.Start()

		self.numOfPoints, self.numOfLines, self.numOfCells = self.vtkViewer.basicInfo()
		self.NumOfPointsText.setText(str(self.numOfPoints))
		self.NumOfLinesText.setText(str(self.numOfLines))
		self.NumOfCellsText.setText(str(self.numOfCells))

	def loadColor(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "Load Color", ".", "Color Files (*.txt)")
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

	def drawD2(self):
		if self.vtkViewer.reader == None:
			return

		num = self.inputD2.text()
		try:
			num = list(map(int, num.split(' ')))
		except Exception:
			return
		if len(num) != 2 or num[0] <= 1 or num[1] <= 1:
			return

		self.clear()

		histogram, scale = self.vtkViewer.d2Sample(num[0], num[1])

		d2Chart = QChart()
		d2Chart.legend().hide()
		polyline = QPolygonF(num[0])
		pointer = polyline.data()
		dtype, tinfo = np.float, np.finfo
		pointer.setsize(2*polyline.size()*tinfo(dtype).dtype.itemsize)
		memory = np.frombuffer(pointer, dtype)
		memory[:(num[0]-1)*2+1:2] = scale
		memory[1:(num[0]-1)*2+2:2] = histogram
		curve = QLineSeries()
		curve.append(polyline)

		d2Chart.addSeries(curve)
		d2Chart.createDefaultAxes()

		ChartView = QChartView(d2Chart)
		self.d2ChartLayout.addWidget(ChartView)

	def clear(self):
		for i in reversed(range(self.d2ChartLayout.count())):
			self.d2ChartLayout.itemAt(i).widget().setParent(None)
