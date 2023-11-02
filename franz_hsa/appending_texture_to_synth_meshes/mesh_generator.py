import h5py
import numpy
from pathlib import Path
import vtk

def write_shape_texture_vtp(points,cells,texture,name):
    vtk_points = vtk.vtkPoints()
    for pt in points:
        vtk_points.InsertNextPoint(pt[0],pt[1],pt[2])
    vtk_cells = vtk.vtkCellArray()
    for cl in cells:
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, cl[0])
        triangle.GetPointIds().SetId(1, cl[1])
        triangle.GetPointIds().SetId(2, cl[2])
        vtk_cells.InsertNextCell(triangle)
    # Write to polydata
    pd = vtk.vtkPolyData()
    pd.SetPoints(vtk_points)
    pd.SetPolys(vtk_cells)
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("color")
    for val in texture:
        colors.InsertNextTuple3(*val)
    pd.GetPointData().SetScalars(colors)
    pd.Modified()
    ply_writer = vtk.vtkXMLPolyDataWriter()
    ply_writer.SetFileName(name)
    ply_writer.SetInputData(pd)
    ply_writer.Write()

if __name__ == '__main__':

    # For repeatability
    numpy.random.seed(42)

    # List keys:
    # Model contains the statistical model
    # Representer contains points and cells
    cur_h5 = h5py.File("shape_model.h5",'r')
    print(cur_h5.keys())
    print(cur_h5['model'].keys())
    print(cur_h5['representer'].keys())

    my_cells = numpy.array(cur_h5['representer']['cells']).transpose()
    my_points = numpy.array(cur_h5['representer']['points']).transpose()
    my_texture = numpy.array(cur_h5['model']['mean']).reshape((-1,3)) * 255
    print("Proof that texture is there")
    print(my_texture)

    # Random generation of a couple of textures
    # This works analogly to a generation of shape samples
    my_mu = numpy.array(cur_h5['model']['mean'])
    my_pc = numpy.array(cur_h5['model']['pcaBasis'])
    my_var = numpy.array(cur_h5['model']['pcaVariance'])
    for i in range(10):
        my_alpha = numpy.random.normal(loc=0.2,scale=0.5,size=(100,))
        texture_observation = my_mu + my_var**0.5 * my_alpha @ my_pc
        new_texture = numpy.array(texture_observation).reshape((-1,3)) * 255
        new_texture[new_texture > 255] = 255
        new_texture[new_texture < 0] = 0
        write_shape_texture_vtp(my_points,my_cells,new_texture,f"out{i}.vtp")

