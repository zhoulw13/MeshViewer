import sys
import vtk
from PyQt4.QtGui import *
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)

		reader = vtk.vtkOBJReader()
		reader.SetFileName('test/281.obj')
		reader.Update()

		lut = vtk.vtkLookupTable()
		lut.SetNumberOfTableValues(11)
		lut.SetTableRange(1,11)
		lut.Build()

		with open('test/281_color.txt', 'r') as f:
			colortxt = list(map(float, f.read().splitlines()))
		colors = vtk.vtkDoubleArray()
		colors.SetNumberOfTuples(len(colortxt))
		for i in range(len(colortxt)):
			colors.SetValue(i, colortxt[i])


		reader.GetOutput().GetCellData().SetScalars(colors)

		# Set Mapper and Actor
		mapper = vtk.vtkPolyDataMapper()
		if vtk.VTK_MAJOR_VERSION <= 5:
			mapper.SetInput(reader.GetOutput())
		else:
			mapper.SetInputData(reader.GetOutput())
		mapper.SetScalarRange(1, 11)
		mapper.SetScalarModeToUseCellData()
		mapper.SetColorModeToMapScalars()
		mapper.SetLookupTable(lut)

		actor = vtk.vtkActor()
		actor.SetMapper(mapper)

		self.frame = QFrame()
 
		self.vl = QVBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
		self.vl.addWidget(self.vtkWidget)
 
		self.ren = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

		self.ren.AddActor(actor)
		self.ren.SetBackground(0.5,0.3,0.16)
 
		self.ren.ResetCamera()
 
		self.frame.setLayout(self.vl)
		self.setCentralWidget(self.frame)

		self.show()
		self.iren.Initialize()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MainWindow()
	sys.exit(app.exec_())