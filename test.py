import vtk
import sys
from PyQt4.QtGui import *

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
print (reader.GetOutput().GetNumberOfCells())


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

# Visualize
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(1280, 720)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

renderer.AddActor(actor)
renderer.SetBackground(0.5, 0.3, 0.16)  # Background color salmon

renderWindow.Render()
renderWindowInteractor.Start()