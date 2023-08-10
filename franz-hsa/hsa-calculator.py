from pathlib import Path
from tools.DataSetGraph import WritePolyData, ReadPolyData
from vtkmodules.vtkIOPLY import vtkPLYReader
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore

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


subtypes = ['control', 'sagittal', 'metopic']
HSA_indeces = {subtype: {mesh_id: None for mesh_id in range(101)} for subtype in subtypes}

for subtype_folder in ply_data_path.iterdir():
    for mesh_vtp_file_path in subtype_folder.glob('*_cp.vtp'):
        mesh = ReadPolyData(mesh_vtp_file_path)

        landmarks, _ = PlaceLandmarks(mesh, crop=False, verbose=True, crop_percentage=0)

        _, HSA_index = ComputeHSAandRiskScore(mesh, landmarks, 100, 'M', verbose=True)



        # reader = PLYReader(FileName=str(mesh_ply_file_path))
        # writer = XMLPolyDataWriter(reader, FileName=str(vtp_file_path))
        # writer.UpdatePipeline()
        # load ply file
        # convert ply file to vtp
        # export vtp



# for subtype in HSA_indeces.keys():
#     mesh_ids_nums = list(HSA_indeces[subtype].keys())
#     for mesh_id in mesh_ids_nums:
#         # load vtp
#         # calculate HSA
#         # store HSA in HSA indeces
#         pass

# Export HSA indices to excel
# Load HSA indeces to excel