from pathlib import Path
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore
import re
import pandas as pd
import os
import datetime

import random
from tools.DataSetGraph import ReadPolyData
random.seed(0)


def load_hsa_scores(hsa_indices_xlsx_path):
    """
    Loads the hsa scores from the previously exported .xlsx file of hsa scores.
    :param hsa_indices_xlsx_path: a Path object to the .xlsx file containing the hsa data.
    :return: a dictionary with keys as subtypes, inner keys as mesh id numbers, and HSA indices as values.
    """

    hsa_indices_data = pd.read_excel(hsa_indices_xlsx_path, header=None)

    header = hsa_indices_data.iloc[0]
    subtypes_df = header[header.notna()]
    subtypes = subtypes_df.values.tolist()
    subtypes_cols = subtypes_df.index.tolist()

    hsa_scores = dict()

    for i, subtype in enumerate(subtypes):
        hsa_scores[subtype] = dict()
        mesh_ids = hsa_indices_data.iloc[2:, subtypes_cols[i]]
        mesh_ids = mesh_ids[mesh_ids.notna()].tolist()
        subtype_data = hsa_indices_data.iloc[2:, subtypes_cols[i]+1]
        subtype_data = subtype_data[subtype_data.notna()].tolist()
        subtype_data = [float(item) for item in subtype_data]
        for j, mesh_id in enumerate(mesh_ids):
            hsa_scores[subtype][mesh_id] = subtype_data[j]

    return hsa_scores


def export_to_excel(hsa_indices, output_path):
    """
    Exports the HSA indices for meshes of different subtypes.
    :param hsa_indices: a dictionary with keys as subtypes, inner keys as mesh id numbers, and HSA indices as values.
    :param output_path: a Path object to the .xlsx file to write the hsa indices data to.
    """

    with pd.ExcelWriter(str(output_path.absolute())) as writer:
        for i, subtype in enumerate(list(hsa_indices.keys())):
            print(f'Exporting {subtype}...')

            # Generating the dataframe from the dictionary
            size = len(hsa_indices.keys())
            df = pd.DataFrame.from_dict(hsa_indices[subtype], orient='index', columns=['HSA index'])
            df.to_excel(writer, sheet_name='Sheet1', startcol=i*(size+2), startrow=1, index=True)


def get_mesh_info(mesh_vtp_file_path):
    """
    Return the subtype and id number of a mesh from a Path object.
    :param mesh_vtp_file_path: a Path object of a .vtp mesh file.
    :return: the mesh subtype and id number.
    """

    pattern = r'^(.*?)_inst_(\d{3})_cp$'
    match = re.match(pattern, mesh_vtp_file_path.stem)
    mesh_subtype = match.group(1)
    mesh_id_num = int(match.group(2))

    return mesh_subtype, mesh_id_num


def calculate_hsa_scores(vtp_data_path, hsa_exec_params):
    """
    This function computes the HSA indices for the synthetic data in the vtp path given the HSA execution parameters.
    :param vtp_data_path: a Path object to a directory with subtype subdirectories, each of which contains .vtp meshes.
    :param hsa_exec_params: a dictionary with execution parameters.
    :return: a dictionary of HSA indices for each mesh of the subtypes in the .vtp data path.
    """
    hsa_indices = dict()

    for subtype_folder in vtp_data_path.iterdir():

        hsa_indices[subtype_folder.name] = dict()

        for mesh_vtp_file_path in subtype_folder.glob('*_cp.vtp'):

            # Load mesh and get its info
            mesh = ReadPolyData(str(mesh_vtp_file_path))
            mesh_subtype, mesh_id_num = get_mesh_info(mesh_vtp_file_path)
            print(f'Working on {mesh_subtype} case #{mesh_id_num}...')

            # Place landmarks on mesh, compute its hsa index, and store
            landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=True,
                                          crop_percentage=hsa_exec_params['crop_percentage'])

            if hsa_exec_params['calculate_hsa']:
                _, hsa_index = ComputeHSAandRiskScore(mesh, landmarks, hsa_exec_params['age'], hsa_exec_params['sex'],
                                                      verbose=False)
                hsa_indices[mesh_subtype][mesh_id_num] = hsa_index

    return hsa_indices


def load_hsa_of_synth_data():
    """
    Run this to load onto memory the HSA indices of the synthetic data.
    Define the path to the existing data for loading, and to the synthetic data for execution.
    """

    hsa_scores_file_path = Path('hsa_scores.xlsx')

    if os.path.exists(hsa_scores_file_path):
        hsa_scores = load_hsa_scores(hsa_scores_file_path)
    else:
        vtp_format_synth_data_dir = Path('../synth_data/vtp_python')
        exec_time_label = datetime.datetime.now().strftime("%B_%d_%H_%M")
        hsa_execution_parameters = {'age': 200,
                                    'sex': 'M',
                                    'crop': False,
                                    'crop_percentage': 0,
                                    'calculate_hsa': False,
                                    'time_label_of_exec': exec_time_label}
        hsa_scores = calculate_hsa_scores(vtp_format_synth_data_dir, hsa_execution_parameters)
        export_to_excel(hsa_scores, output_path=hsa_scores_file_path)


if __name__ == '__main__':
    load_hsa_of_synth_data()

