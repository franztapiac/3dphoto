import h5py
import numpy as np
import os
from pathlib import Path
import pyvista as pv
import vtk

# This code was kindly provided by:
# Matthias Schaufelberger, M.Sc.
# Scientific Staff
# Karlsruhe Institute of Technology (KIT)
# Institute of Biomedical Engineering

# The application of texture was kindly provided


def write_shape_texture_vtp(points, cells, texture, name):

    # Define points
    vtk_points = vtk.vtkPoints()
    for pt in points:
        vtk_points.InsertNextPoint(pt[0], pt[1], pt[2])

    # Define cells
    vtk_cells = vtk.vtkCellArray()
    for cl in cells:
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, cl[0])
        triangle.GetPointIds().SetId(1, cl[1])
        triangle.GetPointIds().SetId(2, cl[2])
        vtk_cells.InsertNextCell(triangle)

    # Create mesh with points and cells
    pd = vtk.vtkPolyData()
    pd.SetPoints(vtk_points)
    pd.SetPolys(vtk_cells)

    # Update the mesh with a Texture array corresponding to each point
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName('Texture')
    for val in texture:
        colors.InsertNextTuple3(*val)
    pd.GetPointData().SetScalars(colors)
    pd.Modified()

    # Export the mesh as .vtp
    ply_writer = vtk.vtkXMLPolyDataWriter()
    ply_writer.SetFileName(name)
    ply_writer.SetInputData(pd)
    ply_writer.Write()


def get_mesh_data(mesh_file_path):
    """
    Reads a mesh and extracts with point and cell data.
    :param mesh_file_path: A Path object to a mesh in .ply format.
    :return: The mesh points and cell data.
    """

    mesh_ply = pv.read(str(mesh_file_path.absolute()))

    points = np.asarray(mesh_ply.points)

    n_cells = mesh_ply.n_cells
    cells = []
    for cell_index in range(n_cells):
        cells.append(mesh_ply.cell_point_ids(cell_index))
    cells = np.asarray(cells)

    return points, cells


def load_texture_model(tex_model_path):
    """
    Reads the texture model and returns its mean and pca parameters.
    :param tex_model_path: a Path object to the texture model in .h5 format.
    """

    texture_model = h5py.File(tex_model_path, 'r')
    texture_mean = np.array(texture_model['model']['mean'])
    texture_pcs = np.array(texture_model['model']['pcaBasis'])
    texture_var = np.array(texture_model['model']['pcaVariance'])

    return texture_mean, texture_pcs, texture_var


def generate_mesh_texture(texture_mean, texture_pcs, texture_var):
    """
    Generates a unique texture for a mesh.
    :param texture_mean: A numpy array (1 x 135,243) for the mean texture object.
    :param texture_pcs: A numpy array (50 x 135,243) for the principal component basis of varying textures.
    :param texture_var: A numpy array (1 x 50) for the texture variability.
    :return: A numpy array (45,081 x 3) with texture data for a 45,081-point mesh.
    """
    var_weighting = np.random.normal(loc=0.2, scale=0.5, size=(50,))
    texture_to_process = texture_mean + texture_var ** 0.5 * var_weighting @ texture_pcs

    mesh_texture = np.array(texture_to_process).reshape((-1, 3)) * 255
    mesh_texture[mesh_texture > 255] = 255
    mesh_texture[mesh_texture < 0] = 0

    return mesh_texture


def create_mesh_directory(tex_files_path, subtype_folder, mesh_path):
    textured_mesh_path = tex_files_path / subtype_folder.name / (mesh_path.stem + '.vtp')
    if not os.path.exists(textured_mesh_path.parent):
        os.mkdir(textured_mesh_path.parent)

    return textured_mesh_path


def generate_textured_files(tex_model_path, untex_files_path, tex_files_path):
    """
    For each subtype mesh, reads it, appends a unique texture to it, and exports the mesh in .vtp format.
    :param tex_model_path: a Path object to the texture model in .h5 format.
    :param untex_files_path: a Path obj to the dir with subtype names as subdirs, where the .ply untextured meshes lie.
    :param tex_files_path: a Path obj to the dir to export .vtp textured meshes within subtype subdirectories.
    """

    texture_mean, texture_pcs, texture_var = load_texture_model(tex_model_path)

    for subtype_folder in untex_files_path.iterdir():

        for mesh_path in subtype_folder.glob('*.ply'):

            mesh_points, mesh_cells = get_mesh_data(mesh_path)
            mesh_texture = generate_mesh_texture(texture_mean, texture_pcs, texture_var)
            textured_mesh_path = create_mesh_directory(tex_files_path, subtype_folder, mesh_path)
            write_shape_texture_vtp(mesh_points, mesh_cells, mesh_texture, str(textured_mesh_path.absolute()))
            print('f')


if __name__ == '__main__':

    texture_model_path = Path('./texture_model.h5')

    untextured_files_path = \
        Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synth_data_original_untextured")

    textured_files_path = \
        Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synth_data_original_textured")

    generate_textured_files(tex_model_path=texture_model_path,
                            untex_files_path=untextured_files_path, tex_files_path=textured_files_path)
