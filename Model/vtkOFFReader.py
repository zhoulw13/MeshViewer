from vtk import *

class vtkOFFReader(vtkPolyDataAlgorithm):
	def __init__(self):
		self.FileName = ""
		self.mesh = vtkPolyData()

	def SetFileName(self, fileName):
		self.FileName = fileName

	def Update(self):
		points = vtkPoints()
		cells = vtkCellArray()
		with open(self.FileName, 'r') as f:
			file = f.read().splitlines()
		for line in file[2:]:
			nums = line.split(' ')
			if len(nums) == 3:
				points.InsertNextPoint(list(map(float, nums)))
			elif len(nums) == 4:
				tri = vtkTriangle()
				tri.GetPointIds().SetId(0,int(nums[1]))
				tri.GetPointIds().SetId(1,int(nums[2]))
				tri.GetPointIds().SetId(2,int(nums[3]))
				cells.InsertNextCell(tri)

		self.mesh.SetPoints(points)
		self.mesh.SetPolys(cells)

	def GetOutput(self):
		return self.mesh


