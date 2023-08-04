import vtk


def read_obj_file(obj_file_path):
    obj_reader = vtk.vtkOBJReader()
    obj_reader.SetFileName(obj_file_path)
    obj_reader.Update()
    return obj_reader.GetOutput()


def read_texture_file(texture_file_path):
    texture_reader = vtk.vtkJPEGReader()
    texture_reader.SetFileName(texture_file_path)
    texture_reader.Update()
    return texture_reader.GetOutput()


def set_texture_array(mesh, texture_data):
    texture_array = vtk.vtkFloatArray()
    texture_array.SetName('Texture')
    texture_array.SetNumberOfComponents(3)
    texture_array.SetNumberOfTuples(texture_data.GetNumberOfPoints())

    for i in range(texture_data.GetNumberOfPoints()):  # change this
        pixel = texture_data.GetPointData().GetScalars().GetTuple(i)
        texture_array.InsertNextTuple3(*pixel)

    # Add the Data Array to the vtkPolyData
    mesh.GetPointData().AddArray(texture_array)

    return mesh

def write_vtp_file(polydata, vtp_file_name):
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(vtp_file_name)
    writer.SetInputData(polydata)
    writer.Update()

if __name__ == '__main__':
    obj_file_path = 'sagittal/1785463_20220715_PLC/meshes/1785463_20220715_PLC.000156.obj'
    obj_file = read_obj_file(obj_file_path)
    texture_file_path = "sagittal/1785463_20220715_PLC/meshes/1785463_20220715_PLC.000156.jpg"
    texture_file = read_texture_file(texture_file_path)
    vtp_file = set_texture_array(obj_file, texture_file)
    vtp_file_name = "sagittal/1785463_20220715_PLC/meshes/1785463_20220715_PLC.000156.vtp"
    write_vtp_file(vtp_file, vtp_file_name)

