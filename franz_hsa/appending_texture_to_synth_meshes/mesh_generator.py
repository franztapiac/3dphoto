import h5py
import numpy
from pathlib import Path
import vtk

def write_shape_texture_vtp(points,cells,name):
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

    # Test generation of shape samples
    my_mu = numpy.array(cur_h5['model']['mean'])
    my_pc = numpy.array(cur_h5['model']['pcaBasis'])
    my_var = numpy.array(cur_h5['model']['pcaVariance'])
    for i in range(10):
        my_alpha = numpy.random.normal(loc=0.2,scale=0.5,size=(100,))
        shape_observation = my_mu + my_var**0.5 * my_alpha @ my_pc
        write_shape_texture_vtp(my_points,my_cells,shape_observation,f"out{i}.vtp")

