import vtk
from pathlib import Path
import os
from tools.DataSetGraph import ReadPolyData
import vtkmodules
import pyvista as pv

def read_obj_file(mesh_file_path):
    print('Reading the .obj file...')
    obj_reader = vtk.vtkOBJReader()
    obj_reader.SetFileName(mesh_file_path)
    obj_reader.Update()
    return obj_reader.GetOutput()


def read_texture_file(tex_file_path):
    print('Reading the .jpg texture file...')
    texture_reader = vtk.vtkJPEGReader()
    texture_reader.SetFileName(tex_file_path)
    texture_reader.Update()
    return texture_reader.GetOutput()


def create_textured_vtp_file(mesh, texture_data):
    print('Converting the .obj with .jpg to textured .vtp...')
    # texture_array = vtk.vtkUnsignedCharArray()
    # texture_array.SetName('Texture')
    # texture_array.SetNumberOfComponents(3)
    #
    # for i in range(texture_data.GetNumberOfPoints()):  # change this
    #     pixel = texture_data.GetPointData().GetScalars().GetTuple(i)
    #     print(pixel)
    #     texture_array.InsertNextTuple3(*pixel)
    #
    # # Add the Data Array to the vtkPolyData
    # mesh.GetPointData().AddArray(texture_array)
    # print('Completed textured .vtp conversion.')

    # Perform texture mapping
    texture_coords_array_name = mesh.GetPointData().GetArrayName(0)
    texture_coords = mesh.GetPointData().GetArray(texture_coords_array_name)

    # Create a new Data Array to store the texture coordinates
    texture_array = vtk.vtkFloatArray()
    texture_array.SetName('Texture')
    texture_array.SetNumberOfComponents(3)  # Assuming 2D texture coordinates (U, V)
    # texture_array.SetNumberOfTuples(mesh.GetNumberOfPoints())

    # Copy the texture coordinates to the new Data Array
    for i in range(mesh.GetNumberOfPoints()):
        uvw = [0.0, 0.0, 0.0]
        uv = texture_coords.GetTuple(i)
        uvw[:2] = uv
        texture_array.InsertNextTuple3(i, uv[0], uv[1])

    # Add the Data Array to the vtkPolyData
    mesh.GetPointData().AddArray(texture_array)

    return mesh


def write_vtp_file(polydata, vtp_file_path):
    print('Exporting the textured .vtp file...')
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(vtp_file_path)
    writer.SetInputData(polydata)
    writer.Update()


def convert_subtype_data():
    subtype_meshes_path = Path('C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/3dphoto/franz-hsa/metopic')
    patient_paths = os.listdir(subtype_meshes_path)

    for i, patient_path in enumerate(patient_paths):
        print(f'Working on patient {i}...')
        patient_files_path = subtype_meshes_path / patient_path / 'meshes'
        patient_files = os.listdir(patient_files_path)

        obj_file_path = None
        texture_file_path = None

        for file in patient_files:
            if file.endswith('.obj'):
                obj_file_path = patient_files_path / file
            elif file.endswith('.jpg'):
                texture_file_path = patient_files_path / file

        obj_file = read_obj_file(obj_file_path)
        texture_file = read_texture_file(texture_file_path)
        vtp_file = create_textured_vtp_file(obj_file, texture_file)
        export_path = patient_files_path / str(obj_file_path.stem + '.vtp')
        write_vtp_file(vtp_file, str(export_path))


def test_on_single_file():
    subtype_meshes_path = 'C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/3dphoto/franz-hsa/metopic/1193281_20220722_PLC/meshes/export_scence2.vtp'
    polydata = ReadPolyData(subtype_meshes_path)

    texture_file_path = 'C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/3dphoto/franz-hsa/metopic/1193281_20220722_PLC/meshes/export_scence2.png'
    texture_reader = vtk.vtkPNGReader()
    texture_reader.SetFileName(texture_file_path)
    texture_reader.Update()

    # Get the texture coordinates from the .vtp file
    texture_coords = polydata.GetPointData().GetArray('TCoords_')

    texture_array = vtk.vtkFloatArray()
    texture_array.SetName("Texture Coordinates")
    texture_array.SetNumberOfComponents(3)  # 3D texture coordinates (U, V, W)
    texture_array.SetNumberOfTuples(polydata.GetNumberOfPoints())

    # Copy the texture coordinates to the new Data Array
    for i in range(polydata.GetNumberOfPoints()):
        uvw = [0.0, 0.0, 0.0]  # Initialize the 3D texture coordinate to (0, 0, 0)
        uv = texture_coords.GetTuple(i)
        uvw[:2] = uv  # Copy the first 2 components (U, V) from the original texture coordinates
        texture_array.SetTuple(i, uvw)

    # Add the Data Array to the vtkPolyData
    polydata.GetPointData().AddArray(texture_array)

    # Create a texture map
    texture_map = vtk.vtkTextureMapToPlane()
    texture_map.SetInputData(polydata)
    texture_map.Update()

    # Get the mapped polydata
    mapped_polydata = texture_map.GetOutput()

    # Load the texture coordinates into the mapped polydata
    mapped_polydata.GetPointData().SetTCoords(mapped_polydata.GetPointData().GetArray('Texture Coordinates'))

    # Create a texture from the image
    texture = vtk.vtkTexture()
    texture.SetInputConnection(texture_reader.GetOutputPort())

    # Assign the texture to the mapped polydata
    mapped_polydata.GetPointData().AddArray(texture)
    mapped_polydata.GetPointData().SetActiveTexture(texture.GetTextureUnit())

    print('f')

if __name__ == '__main__':
    test_on_single_file()

