import vtk
from pathlib import Path
import os


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
    texture_array = vtk.vtkUnsignedCharArray()
    texture_array.SetName('Texture')
    texture_array.SetNumberOfComponents(3)

    for i in range(texture_data.GetNumberOfPoints()):
        pixel = texture_data.GetPointData().GetScalars().GetTuple(i)
        texture_array.InsertNextTuple3(*pixel)

    # Add the Data Array to the vtkPolyData
    mesh.GetPointData().AddArray(texture_array)
    print('Completed textured .vtp conversion.')

    return mesh


def write_vtp_file(polydata, vtp_file_path):
    print('Exporting the textured .vtp file...')
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(vtp_file_path)
    writer.SetInputData(polydata)
    writer.Update()


def convert_subtype_data():
    subtype_meshes_path = Path('C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/'
                               '3dphoto/franz-hsa/metopic')
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


if __name__ == '__main__':
    convert_subtype_data()

