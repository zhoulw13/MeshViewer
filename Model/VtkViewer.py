import vtk
from Model.vtkOFFReader import vtkOFFReader
import math, random
import numpy as np

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
		self.scale = 0

	def basicInfo(self):
		return (self.mesh.GetNumberOfPoints(),self.edge.GetNumberOfLines(),self.mesh.GetNumberOfCells())

	def loadMesh(self, fileName):
		if fileName.endswith('.obj'):
			self.reader = vtk.vtkOBJReader()
		elif fileName.endswith('.off'):
			self.reader = vtkOFFReader()
		else:
			return 

		self.renderer.RemoveAllViewProps()

		self.reader.SetFileName(fileName)
		self.reader.Update()

		self.mesh = self.reader.GetOutput()

		extractEdge = vtk.vtkExtractEdges()
		extractEdge.SetInputData(self.mesh)
		extractEdge.Update()
		self.edge.DeepCopy(extractEdge.GetOutput())
		self.calculateScale()

		self.mapper.SetInputData(self.mesh)
		self.actor.SetMapper(self.mapper)
		self.renderer.AddActor(self.actor)

	def calculateScale(self):
		self.scale = 0
		p1 = [0.0, 0.0, 0.0]
		p2 = [0.0, 0.0, 0.0]
		line = vtk.vtkIdList()
		self.edge.GetLines().InitTraversal()
		while(self.edge.GetLines().GetNextCell(line)):
			self.edge.GetPoint(line.GetId(0), p1)
			self.edge.GetPoint(line.GetId(1), p2)
			self.scale += math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p1, p2))
		self.scale /= self.edge.GetNumberOfLines()

		return 

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

	def addActor(self, mapper, color):
		actor = vtk.vtkActor()
		actor.SetMapper(mapper)
		actor.GetProperty().SetColor(color)

		self.renderer.AddActor(actor)

	def drawPoint(self, pointId, size, color):
		sphere = vtk.vtkSphereSource()
		sphere.SetCenter(self.mesh.GetPoint(pointId))
		sphere.SetRadius(size*self.scale)
		sphere.Update()

		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputData(sphere.GetOutput())

		self.addActor(mapper, color)


	def drawLine(self, start, end, color):
		line = vtk.vtkLineSource()
		line.SetPoint1(start)
		line.SetPoint2(end)
		line.Update()

		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputData(line.GetOutput())

		self.addActor(mapper, color)


	def drawCells(self, cellIdList, color):
		triangles = vtk.vtkCellArray()
		pointslist = vtk.vtkIdList()
		fullPoints = self.mesh.GetPoints()
		partPoints = vtk.vtkPoints()
		for i in range(cellIdList.GetNumberOfIds()):
			cell = cellIdList.GetId(i)
			triangle = self.mesh.GetCell(cell)
			triangles.InsertNextCell(triangle)
			self.mesh.GetCellPoints(cell, pointslist)
			partPoints.InsertPoints(pointslist, pointslist, fullPoints)

		trianglePoly = vtk.vtkPolyData()
		trianglePoly.SetPoints(partPoints)
		trianglePoly.SetPolys(triangles)

		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputData(trianglePoly)

		self.addActor(mapper, color)

	def drawPOP(self, pointId):
		self.drawPoint(pointId, 0.25, (1,0,0))

		cells = vtk.vtkIdList()
		adjacentPoints = []
		self.mesh.GetPointCells(pointId, cells)
		for i in range(cells.GetNumberOfIds()):
			points = vtk.vtkIdList()
			self.mesh.GetCellPoints(cells.GetId(i), points)
			for j in range(points.GetNumberOfIds()):
				id = points.GetId(j)
				if id != pointId and id not in adjacentPoints:
					self.drawPoint(id, 0.15, (1,1,0))

	def drawMOP(self, pointId):
		self.drawPoint(pointId, 0.25, (1,0,0))
		cells = vtk.vtkIdList()
		self.mesh.GetPointCells(pointId, cells)
		self.drawCells(cells, (1,1,0))
			
	def drawMOM(self, cellId):
		cells = vtk.vtkIdList()
		cells.InsertNextId(cellId)
		self.drawCells(cells, (1,0,0))

		cells = vtk.vtkIdList()
		points = vtk.vtkIdList()
		self.mesh.GetCellPoints(cellId, points)
		for i in range(points.GetNumberOfIds()):
			for j in range(i+1, points.GetNumberOfIds()):
				cells1 = vtk.vtkIdList()
				cells2 = vtk.vtkIdList()
				self.mesh.GetPointCells(points.GetId(i), cells1)
				self.mesh.GetPointCells(points.GetId(j), cells2)
				intersection = list(set(self.vtkIdlist2list(cells1)).intersection(self.vtkIdlist2list(cells2)))
				intersection.remove(cellId)
				cells.InsertNextId(intersection[0])
		self.drawCells(cells, (1,1,0))

	def drawNOM(self, cellId):
		points = vtk.vtkIdList()
		self.mesh.GetCellPoints(cellId, points)
		p1 = [0.0, 0.0, 0.0]
		p2 = [0.0, 0.0, 0.0]
		p3 = [0.0, 0.0, 0.0]
		self.mesh.GetPoint(points.GetId(0), p1)
		self.mesh.GetPoint(points.GetId(1), p2)
		self.mesh.GetPoint(points.GetId(2), p3)

		start = [sum(x)/3 for x in zip(p1,p2,p3)]
		norm = [0.0, 0.0, 0.0]
		vtk.vtkMath.Cross([a-b for a,b in zip(p2,p1)], [a-b for a,b in zip(p3, p1)], norm)
		vtk.vtkMath.Normalize(norm)
		end = [a+self.scale*b for a,b in zip(start, norm)]
		self.drawLine(start, end, (1,1,0))

	def drawArea(self, pointIds, limit):
		cellCount = {}
		cells = vtk.vtkIdList()
		for point in pointIds:
			tmp = vtk.vtkIdList()
			self.mesh.GetPointCells(point, tmp)
			for i in range(tmp.GetNumberOfIds()):
				key = tmp.GetId(i)
				if key in cellCount:
					cellCount[key] += 1
				else:
					cellCount[key] = 1
		for k,v in cellCount.items():
			if v >= limit:
				cells.InsertNextId(k)
		self.drawCells(cells, (1,1,0))

	def d2Sample(self, bins, sampleNum):
		points = self.mesh.GetPoints()

		distance = []
		for i in range(sampleNum):
			id1, id2 = random.sample(range(self.mesh.GetNumberOfPoints()), 2)
			p1 = points.GetPoint(id1)
			p2 = points.GetPoint(id2)
			distance.append(math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p1, p2)))

		histogram = [0.0]*bins
		minimum = min(distance)
		maximum = max(distance)
		scale = (maximum - minimum) / (bins-1)

		for d in distance:
			histogram[int((d - minimum)/scale)] += 1
		histogram = [x/sampleNum for x in histogram]
		return np.array(histogram), scale*np.array(range(bins))

	def vtkIdlist2list(self, idList):
		result = []
		for i in range(idList.GetNumberOfIds()):
			result.append(idList.GetId(i))
		return result






