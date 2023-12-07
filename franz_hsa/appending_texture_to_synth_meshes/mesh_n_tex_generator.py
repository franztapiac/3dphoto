"""
------------
Description:
------------
This is a short demo file to make it easier to use this respository.  It will
show you how to:
- Load a h5 shape model and the submodels
- Draw random samples from it
- Add texture to the file
- Store the shape as a vtp file (or as a ply file without texture)
-------------
Requirements:
-------------
This file requires:
- h5py to load the files,
- numpy for the basic mathematics, and
- vtk to write the files to the disk.
Usually, the recommended way to install the dependencies is using a virtual
environment, in which you can use
`pip install numpy vtk h5py`
-------------
Visualization:
-------------
If you would like to visualize the resulting models, I would recommend
Paraview, which is cross-platform and Free and Open Source Software.  To
display the texture, make sure, the color is not mapped as a scalar (in 5.10,
disable "MapScalars") and use a medium amount of ambient light if it is very
dark.
"""
# pylint-disable: invalid-name

import h5py
import numpy
import vtk

def write_shape_texture_vtp(model_points,model_cells,model_texture,name):
    """
    Write a file from model_points, model_cells, model_texture, and name.
    """
    vtk_points = vtk.vtkPoints()
    for point in model_points:
        vtk_points.InsertNextPoint(point[0],point[1],point[2])
    vtk_cells = vtk.vtkCellArray()
    for cell in model_cells:
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, cell[0])
        triangle.GetPointIds().SetId(1, cell[1])
        triangle.GetPointIds().SetId(2, cell[2])
        vtk_cells.InsertNextCell(triangle)
    # Append to polydata structure
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_cells)
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("color")
    for val in model_texture:
        colors.InsertNextTuple3(*val)
    polydata.GetPointData().SetScalars(colors)
    polydata.Modified()
    # Write to vtk polydata (vtp) file
    # For ply files use vtk.vtkPLYWriter()
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(name)
    writer.SetInputData(polydata)
    writer.Write()

def print_model_hierarchy(model):
    """
    Print the model hierarchy.
    """
    def printname(name):
        """
        Short helper for printing, aka to use f.visit()
        """
        print(name)
    print("Model hierarchy:")
    model.visit(printname)
    print("-----")

def pts_cls_from_h5(model_h5):
    """
    Return the representation (points and cells).  The points are the 3D mean
    shape points and do not carry any other statistical information.
    """
    cls = numpy.array(model_h5['representer/cells'])
    pts = numpy.array(model_h5['representer/points'])
    return pts,cls

def ssm_from_h5(model_h5):
    """
    Returns mean shape mu, principal components pc, and variance var from the
    model (texture for texture model, 3D shape for shape models).
    """
    model_mu = numpy.array(model_h5['model/mean'])
    model_pc = numpy.array(model_h5['model/pcaBasis'])
    model_var = numpy.array(model_h5['model/pcaVariance'])
    if model_var.ndim == 2:
        model_var = model_var.reshape(model_var.shape[1])
        model_mu = model_mu.reshape(model_mu.shape[1])
    return model_mu,model_pc,model_var

def draw_shape(model,model_alpha = None):
    """
    Draw a random sample from the model.
    """
    # Make random model if no parameter vector was provided
    if model_alpha is None:
        model_alpha = numpy.random.normal(loc=0,scale=1,size=(100))
    my_mu,my_pc,my_var = ssm_from_h5(model)
    # Check which one is smaller, the parameter vector alpha or the available
    # model parameters
    min_length = min(len(my_var),len(model_alpha))
    components = my_var[:min_length]**0.5 * model_alpha[:min_length] @ my_pc[:min_length]
    observation = my_mu + components
    return numpy.array(observation.reshape((-1,3)))

def draw_texture(model,model_alpha = None):
    """
    In addition to the shape, the texture needs to be multiplied and checked
    for the boundaries.
    """
    model_texture = draw_shape(model, model_alpha) * 255
    model_texture[model_texture > 255] = 255
    model_texture[model_texture < 0] = 0
    return model_texture

if __name__ == '__main__':
    # For repeatability
    version = 2
    numpy.random.seed(42)
    # Shape model (sagittal model)
    ssm_h5 = h5py.File(f"submodel_metopic_{version}.h5",'r')
    print_model_hierarchy(ssm_h5)
    # Get points, cells, and components if you need them:
    points,cells = pts_cls_from_h5(ssm_h5)
    if version == 2:
        points = numpy.transpose(points)
        cells = numpy.transpose(cells)
    mu,pc,var = ssm_from_h5(ssm_h5)
    tex_h5 = h5py.File(f"texture_model_{version}.h5",'r')
    # Draw shapes and textures
    for i in range(5):
        print(f"Creating mesh #{i}...",end = '')
        # Random vectors
        # my_alpha = numpy.random.normal(loc=0,scale=1,size=(100))
        # print(my_alpha)
        shape = draw_shape(ssm_h5)
        texture = draw_texture(tex_h5)
        write_shape_texture_vtp(shape,cells,texture,f"out{i}.vtp")
        print("Done")
