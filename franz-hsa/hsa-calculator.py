from pathlib import Path
from tools.DataSetGraph import WritePolyData, ReadPolyData
from vtkmodules.vtkIOPLY import vtkPLYReader
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore
import re
import pandas as pd

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


def load_hsa_scores(file_path):

    probability_data = pd.read_excel(file_path, header=None)

    header = probability_data.iloc[0]
    subtypes_df = header[header.notna()]
    subtypes = subtypes_df.values.tolist()
    subtypes_cols = subtypes_df.index.tolist()

    hsa_scores = dict()

    for i, subtype in enumerate(subtypes):
        hsa_scores[subtype] = dict()
        mesh_ids = probability_data.iloc[2:, subtypes_cols[i]]
        mesh_ids = mesh_ids[mesh_ids.notna()].tolist()
        subtype_data = probability_data.iloc[2:, subtypes_cols[i]+1]
        subtype_data = subtype_data[subtype_data.notna()].tolist()
        subtype_data = [float(item) for item in subtype_data]
        for j, mesh_id in enumerate(mesh_ids):
            hsa_scores[subtype][mesh_id] = subtype_data[j]
    return hsa_scores


def export_to_excel(data_dict, output_path):

    with pd.ExcelWriter(str(output_path.absolute())) as writer:
        for i, subtype in enumerate(list(data_dict.keys())):
            print(f'Exporting {subtype}...')
            # Generating the dataframe from the dictionary
            size = len(data_dict.keys())
            df = pd.DataFrame.from_dict(data_dict[subtype], orient='index', columns=['HSA index'])
            df.to_excel(writer, sheet_name='Sheet1', startcol=i*(size+2), startrow=1, index=True)




HSA_scores_path = Path('../franz-hsa/hsa_scores.xlsx')
subtypes = ['control', 'sagittal', 'metopic']
HSA_indeces = {subtype: {mesh_id: None for mesh_id in range(1, 101)} for subtype in subtypes}

for subtype_folder in vtp_data_path.iterdir():
    for mesh_vtp_file_path in subtype_folder.glob('*_cp.vtp'):
        mesh = ReadPolyData(str(mesh_vtp_file_path))

        # Define the regular expression pattern
        pattern = r'^(.*?)_inst_(\d{3})_cp$'
        match = re.match(pattern, mesh_vtp_file_path.stem)
        mesh_subtype = match.group(1)
        mesh_id_num = int(match.group(2))
        print(f'Working on {mesh_subtype} case #{mesh_id_num}...')

        landmarks, _ = PlaceLandmarks(mesh, crop=False, verbose=False, crop_percentage=0)

        _, HSA_index = ComputeHSAandRiskScore(mesh, landmarks, 100, 'M', verbose=False)

        HSA_indeces[mesh_subtype][mesh_id_num] = HSA_index

export_to_excel(HSA_indeces, output_path=HSA_scores_path)




# for subtype in HSA_indeces.keys():
#     mesh_ids_nums = list(HSA_indeces[subtype].keys())
#     for mesh_id in mesh_ids_nums:
#         # load vtp
#         # calculate HSA
#         # store HSA in HSA indeces
#         pass

# Export HSA indices to excel
# Load HSA indeces to excel