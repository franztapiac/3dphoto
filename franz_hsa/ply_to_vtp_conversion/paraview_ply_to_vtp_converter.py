from paraview.simple import *
from pathlib import Path
paraview.simple._DisableFirstRenderCameraReset()

ply_data_path = Path("C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\synthetic_data\\synth_data_unclipped_ply")
vtp_data_path = Path("C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\synthetic_data\\synth_data_unclipped_vtp_paraview")

for subtype_folder in ply_data_path.iterdir():                  # for each subtype
    for mesh_file_path in subtype_folder.glob('*_cp.ply'):          # for each mesh
        mesh_file_name = mesh_file_path.name  # includes .ply extension
        mesh_file_str_path = str(mesh_file_path.absolute())

        mesh_ply = PLYReader(registrationName=mesh_file_name, FileNames=[mesh_file_str_path])

        # get active view
        renderView1 = GetActiveViewOrCreate('RenderView')

        # show data in view
        mesh_ply_Display = Show(mesh_ply, renderView1, 'GeometryRepresentation')

        # trace defaults for the display properties.
        mesh_ply_Display.Representation = 'Surface'

        # reset view to fit data
        renderView1.ResetCamera(False)

        # get the material library
        materialLibrary1 = GetMaterialLibrary()

        # update the view to ensure updated data information
        renderView1.Update()

        # export view
        mesh_vtp_file_path = vtp_data_path / subtype_folder.name / (mesh_file_path.stem + '.vtp')
        mesh_vtp_str_file_path = mesh_vtp_file_path.as_posix()
        ExportView(mesh_vtp_str_file_path, view=renderView1)

        # destroy sagittal_inst_005_cpply
        Delete(mesh_ply)
        del mesh_ply

        if mesh_file_name == 'control_inst_005_cp.ply':
            break
    if subtype_folder.name == 'control':
        break
