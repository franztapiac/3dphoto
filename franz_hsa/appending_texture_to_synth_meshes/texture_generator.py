import h5py
import numpy as np
import os
from pathlib import Path
import pyvista as pv
import vtk

# The functionalities here for loading the texture model, generating a mesh texture object,
# writing the texture to a mesh, and exporting were kindly provided by:
# Matthias Schaufelberger, M.Sc., Scientific Staff at the Institute of Biomedical Engineering
# in the Karlsruhe Institute of Technology (KIT)


def export_vtp_mesh(mesh_polydata, mesh_vtp_path):
    """
    Exports the polydata mesh with a 'Texture' array in the defined path.
    :param mesh_polydata: a vtk PolyData object with the mesh points, cells, and texture data.
    :param mesh_vtp_path: a string for the full path for the .vtp mesh to export.
    """

    ply_writer = vtk.vtkXMLPolyDataWriter()
    ply_writer.SetFileName(mesh_vtp_path)
    ply_writer.SetInputData(mesh_polydata)
    ply_writer.Write()


def create_vtp_mesh(mesh_points, mesh_cells):
    """
    Creates and returns a vtk PolyData mesh object from the .ply mesh points and cells.
    :param mesh_points: a numpy array (45,081 x 3) with the mesh point X,Y,Z coordinates.
    :param mesh_cells: a numpy array (45,081 x 3) with the point IDs that constitute each cell.
    :return: a vtk PolyData mesh object from the .ply mesh points and cells.
    """

    vtk_points = vtk.vtkPoints()
    for point in mesh_points:
        vtk_points.InsertNextPoint(*point)

    vtk_cells = vtk.vtkCellArray()
    for cell in mesh_cells:
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, cell[0])
        triangle.GetPointIds().SetId(1, cell[1])
        triangle.GetPointIds().SetId(2, cell[2])
        vtk_cells.InsertNextCell(triangle)

    mesh_polydata = vtk.vtkPolyData()
    mesh_polydata.SetPoints(vtk_points)
    mesh_polydata.SetPolys(vtk_cells)

    return mesh_polydata


def write_texture_on_vtp_mesh(mesh_polydata, mesh_texture):
    """
    Writes the texture information into the vtk PolyData object.
    :param mesh_polydata: a vtk PolyData mesh object with 45,081 points.
    :param mesh_texture: a numpy array (45,081 x 3) with RGB texture information for each mesh point.
    """

    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName('Texture')

    for point_texture in mesh_texture:
        colors.InsertNextTuple3(*point_texture)

    mesh_polydata.GetPointData().SetScalars(colors)
    mesh_polydata.Modified()


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
        # TODO: PyVistaDeprecationWarning: `cell_point_ids` is deprecated. Use `get_cell(i).point_ids` instead
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


def generate_mesh_texture(tex_mean, tex_pcs, tex_var):
    """
    Generates a unique texture for a 13151 mesh.
    :param tex_mean: A numpy array (1 x 39453) for the mean texture object.
    :param tex_pcs: A numpy array (100 x 39453) for the principal component basis of varying textures.
    :param tex_var: A numpy array (1 x 100) for the texture variability.
    :return: A numpy array (39453 x 3) with texture data for a 39453-point mesh.
    """
    var_weighting = np.random.normal(loc=0.2, scale=0.5, size=(100,))
    texture_to_process = tex_mean + tex_var ** 0.5 * var_weighting @ tex_pcs

    mesh_texture = np.array(texture_to_process).reshape((-1, 3)) * 255
    mesh_texture[mesh_texture > 255] = 255
    mesh_texture[mesh_texture < 0] = 0

    return mesh_texture


def create_mesh_directory(tex_files_path, subtype_name, mesh_name):
    """
    Defines the path and the parent path for the mesh to export in .vtp format.
    :param tex_files_path: a Path obj to the (potentially empty) dir to export the textured meshes.
    :param subtype_name: a string for the name of the subtype to create a subdirectory with.
    :param mesh_name: a string for the name of the input mesh .ply file.
    :return: a Path object for the exporting mesh in .vtp format.

    """
    if not os.path.exists(tex_files_path):
        os.mkdir(tex_files_path)

    if not os.path.exists(tex_files_path/subtype_name):
        os.mkdir(tex_files_path/subtype_name)

    if subtype_name in mesh_name:
        textured_mesh_path = tex_files_path / subtype_name / f'{mesh_name}.vtp'
    else:
        textured_mesh_path = tex_files_path / subtype_name / f'{subtype_name}_{mesh_name}.vtp'

    return textured_mesh_path


def generate_textured_files(tex_model_path, untex_ply_files_path, tex_files_path):
    """
    For each subtype mesh, reads it, appends a unique texture to it, and exports the mesh in .vtp format.
    :param tex_model_path: a Path object to the texture model in .h5 format.
    :param untex_ply_files_path: a Path obj to the dir with subtype names as subdirs, where the .ply untextured meshes lie.
    :param tex_files_path: a Path obj to the dir to export .vtp textured meshes within subtype subdirectories.
    """

    texture_mean, texture_pcs, texture_var = load_texture_model(tex_model_path)

    for subtype_folder in untex_ply_files_path.iterdir():
        for mesh_path in subtype_folder.glob('*.ply'):

            print(f'Loaded {subtype_folder.name} mesh {mesh_path.stem} in .ply format.')
            mesh_points, mesh_cells = get_mesh_data(mesh_path)
            mesh_vtp = create_vtp_mesh(mesh_points=mesh_points, mesh_cells=mesh_cells)

            print(f'Generating and applying texture to {subtype_folder.name} mesh {mesh_path.stem}...')
            mesh_texture = generate_mesh_texture(tex_mean=texture_mean, tex_pcs=texture_pcs, tex_var=texture_var)

            write_texture_on_vtp_mesh(mesh_polydata=mesh_vtp, mesh_texture=mesh_texture)

            textured_mesh_path = create_mesh_directory(tex_files_path=tex_files_path,
                                                       subtype_name=subtype_folder.name, mesh_name=mesh_path.stem)
            export_vtp_mesh(mesh_polydata=mesh_vtp, mesh_vtp_path=textured_mesh_path)
            print(f'Exported {subtype_folder.name} mesh {textured_mesh_path.stem} with texture in .vtp format '
                  f'at {str(textured_mesh_path)}.\n')


if __name__ == '__main__':

    texture_model_path = Path('./texture_model_13151_pts.h5')

    untextured_ply_format_files_path = \
        Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply")

    textured_files_path = \
        Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_textured_unclipped_vtp_paraview")

    generate_textured_files(tex_model_path=texture_model_path, untex_ply_files_path=untextured_ply_format_files_path,
                            tex_files_path=textured_files_path)
