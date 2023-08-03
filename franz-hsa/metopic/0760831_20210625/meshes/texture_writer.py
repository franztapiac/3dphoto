import vtk

# Set the file name of the OBJ file to be read
obj_file_name = "0760831_20210625.000128.obj"
obj_reader = vtk.vtkOBJReader()
obj_reader.SetFileName(obj_file_name)
obj_reader.Update()

# Get the vtkPolyData from the reader
polydata = obj_reader.GetOutput()

# Load the texture image (assuming it's in JPEG format)
texture_file_name = "0760831_20210625.000128.jpg"
texture_reader = vtk.vtkJPEGReader()
texture_reader.SetFileName(texture_file_name)
texture_reader.Update()

# Get the RGB texture data from the texture reader
texture_data = texture_reader.GetOutput()
print('f')

# Extract the RGB values from the texture data and create a Data Array
texture_array = vtk.vtkUnsignedCharArray()
texture_array.SetName("Texture")
texture_array.SetNumberOfComponents(3)  # Assuming RGB values (3 components)
texture_array.SetNumberOfTuples(texture_data.GetNumberOfPoints())

for i in range(texture_data.GetNumberOfPoints()):
    pixel = texture_data.GetPointData().GetScalars().GetTuple(i)
    texture_array.SetTuple3(i, pixel[0], pixel[1], pixel[2])

# Add the Data Array to the vtkPolyData
polydata.GetPointData().AddArray(texture_array)

# Save the vtkPolyData with the 'Texture' Data Array as a .vtp file
vtk_file_name = "test2.vtp"
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(vtk_file_name)
writer.SetInputData(polydata)
writer.Write()
