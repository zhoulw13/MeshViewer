import vtk
from Model.vtkOFFReader import vtkOFFReader

class VtkViewer:
	def __init__(self):
		self.reader = None
		self.mesh = vtk.vtkPolyData()
		self.edge = vtk.vtkPolyData()
		self.mapper = vtk.vtkPolyDataMapper()
		self.lut = vtk.vtkLookupTable()
		self.actor = vtk.vtkActor()
		self.renderer = vtk.vtkRenderer()
		self.renderer.SetBackground(1.0,0.9294,0.9294)

	def basicInfo(self):
		return (self.mesh.GetNumberOfPoints(),self.edge.GetNumberOfLines(),self.mesh.GetNumberOfCells())

	def loadMesh(self, fileName):
		if fileName.endswith('.obj'):
			self.reader = vtk.vtkOBJReader()
		elif fileName.endswith('.off'):
			self.reader = vtkOFFReader()
		else:
			return 
		self.reader.SetFileName(fileName)
		self.reader.Update()

		self.mesh = self.reader.GetOutput()

		extractEdge = vtk.vtkExtractEdges()
		extractEdge.SetInputData(self.mesh)
		extractEdge.Update()
		self.edge.DeepCopy(extractEdge.GetOutput())

		self.mapper.SetInputData(self.mesh)
		self.actor.SetMapper(self.mapper)
		self.renderer.AddActor(self.actor)

		#self.lut = vtk.vtkLookupTable()
		#self.mapper.SetLookupTable(self.lut)

	def loadColor(self, fileName):
		with open(fileName, 'r') as f:
			colortxt = list(map(float, f.read().splitlines()))

		if len(colortxt) != self.reader.GetOutput().GetNumberOfCells():
			return False

		colors = vtk.vtkFloatArray()
		colors.SetNumberOfTuples(len(colortxt))	
		for i in range(len(colortxt)):
			colors.SetValue(i, colortxt[i])

		self.lut.SetNumberOfTableValues(int(max(colortxt)-min(colortxt)+1))
		self.lut.SetTableRange(min(colortxt), max(colortxt))
		self.lut.Build()

		self.reader.GetOutput().GetCellData().SetScalars(colors)

		self.mapper.SetScalarRange(min(colortxt), max(colortxt))
		self.mapper.SetScalarModeToUseCellData()
		self.mapper.SetColorModeToMapScalars()
		self.mapper.SetLookupTable(self.lut)

		return True

