from pathlib import Path
from vtkmodules.vtkIOPLY import vtkPLYReader
from tools.DataSetGraph import WritePolyData

vtp_data_path = Path(
    'C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/3dphoto/franz-hsa/synth_data/vtp')
ply_data_path = Path(
    'C:/Users/franz/Documents/work/projects/arp/quantification-methods/hsa/3dphoto/franz-hsa/synth_data/ply')


def ReadPlyfile(ply_file_path):
    reader = vtkPLYReader()
    reader.SetFileName(ply_file_path)
    reader.Update()
    poly_data = reader.GetOutput()
    return poly_data


def convert_ply_files_to_vtp():

    for subtype_folder in ply_data_path.iterdir():
        for mesh_ply_file_path in subtype_folder.glob('*_cp.ply'):
            vtp_file_path = vtp_data_path / subtype_folder.name / (mesh_ply_file_path.stem + '.vtp')
            ply_file = ReadPlyfile(str(mesh_ply_file_path))
            WritePolyData(ply_file, str(vtp_file_path))
