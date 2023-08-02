import os
import pyvista as pv

# Set the input and output directories
ply_directory = "path/to/ply_files"
vtp_directory = "path/to/vtp_output"

# Get a list of all .ply files in the input directory
ply_files = [file for file in os.listdir(ply_directory) if file.endswith('.ply')]

# Iterate through the .ply files and convert/save them to .vtp
for ply_file in ply_files:
    # Load the .ply file using PyVista
    mesh = pv.read(os.path.join(ply_directory, ply_file))

    # Get the base filename without the extension
    base_filename = os.path.splitext(ply_file)[0]

    # Define the output .vtp filename
    vtp_filename = base_filename + ".vtp"

    # Save the mesh in .vtp format
    mesh.save(os.path.join(vtp_directory, vtp_filename))