from git import Repo
import os
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore
import datetime
from franz_hsa.landmark_prediction_evaluation.export_landmarks import export_landmarks
import numpy as np
import pandas as pd
from pathlib import Path
import random
import re
from tools.DataSetGraph import ReadPolyData
from tools.LandmarkingUtils import AddArraysToLandmarks
import vtk
random.seed(0)

results_storage_path = Path(r"C:\Users\franz\Documents\work\projects\arp\quantification-methods\tareq\kde_classifier\KDE_shape_classifier\experiments")
data_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data")
repo_root_path = Path(repo_root_str_path)
hsa_exec_params_db_path = repo_root_path / r"franz_hsa\hsa_calculation\hsa_execution_parameters.xlsx"


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


def place_landmarks_manually():
    landmark_coords = [[-54.8302, 0.423142, -21.3009],  # Tragion right
                       [53.0547, -5.48717, -21.5361],   # Tragion left
                       [1.36976, 1.29766, 43.735]]      # Nasion
    # coordinates from sagittal_inst_001_cp_paraview.vtp

    landmark_coords = np.asarray(landmark_coords)

    manual_landmarks = vtk.vtkPolyData()
    manual_landmarks.SetPoints(vtk.vtkPoints())
    for p in range(len(landmark_coords)):
        p_coords = tuple(landmark_coords[p,:])
        manual_landmarks.GetPoints().InsertNextPoint(*p_coords)

    landmark_names = ["TRAGION_RIGHT", "TRAGION_LEFT", "NASION"]  # must be defined in the right relative order
    landmarks_vtp = AddArraysToLandmarks(manual_landmarks, landmark_names)
    return landmarks_vtp


def calculate_hsa_scores(vtp_data_path, hsa_exec_params):
    """
    This function computes the HSA indices for the synthetic data in the vtp path given the HSA execution parameters.
    :param vtp_data_path: a Path object to a directory with subtype subdirectories, each of which contains .vtp meshes.
    :param hsa_exec_params: a dictionary with execution parameters.
    :return: a dictionary of HSA indices for each mesh of the subtypes in the .vtp data path.
    """
    hsa_indices = dict()
    verbose = hsa_exec_params['verbose']

    for subtype_folder in vtp_data_path.iterdir():

        hsa_indices[subtype_folder.name] = dict()

        for mesh_vtp_file_path in subtype_folder.glob('*_cp.vtp'):

            # Load mesh and get its info
            mesh = ReadPolyData(str(mesh_vtp_file_path))
            mesh_subtype, mesh_id_num = get_mesh_info(mesh_vtp_file_path)
            print(f'\nWorking on {mesh_subtype} case #{mesh_id_num}...')

            landmark_placement = hsa_exec_params['landmark_placement']
            if landmark_placement == 'automatically':
                print('Computing the landmarks by automatic prediction...')
                # Place landmarks on mesh, compute its hsa index, and store
                landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=verbose,
                                              crop_percentage=hsa_exec_params['crop_percentage'])
            else:  # 'manually'
                print('Placing the landmarks by manual definition...')
                landmarks = place_landmarks_manually()

            if hsa_exec_params['export_landmarks']:
                crop_percentage = hsa_exec_params['crop_percentage']
                export_landmarks(landmarks, mesh_vtp_file_path, f'cropped_{crop_percentage}_'
                                                                f'landmarks_placed_{landmark_placement}')

            if hsa_exec_params['calculate_hsa']:
                print('Calculating the HSA index...')
                _, hsa_index = ComputeHSAandRiskScore(image=mesh, landmarks=landmarks,
                                                      landmark_placement=hsa_exec_params['landmark_placement'],
                                                      age=hsa_exec_params['age'], sex=hsa_exec_params['sex'],
                                                      verbose=verbose)
                print(f'HSA index for {mesh_subtype} mesh #{mesh_id_num}: {hsa_index:0.2f}')
                hsa_indices[mesh_subtype][mesh_id_num] = hsa_index

    return hsa_indices


def define_hsa_score_storage_path(data_type, sub_data_type, with_texture):

    exp_date = datetime.date.today().strftime("%m%d")

    if with_texture:
        texture_state = 'textured'
    else:
        texture_state = 'untextured'

    if data_type == 'synthetic':
        hsa_scores_file_path = results_storage_path / f'{exp_date}_hsa_indices_{data_type}_data' \
                                              f'_{sub_data_type}_{texture_state}.xlsx'
    else:  # data_type = 'patient'
        hsa_scores_file_path = results_storage_path / f'{exp_date}_hsa_indices_{data_type}_data' \
                                              f'_{sub_data_type}.xlsx'

    return hsa_scores_file_path


def load_hsa_exec_parameters(params_db_path, hsa_exp_index):

    hsa_exec_params_db = pd.read_excel(params_db_path, index_col=0)  # index_col = 0 s.t. hsa_exp_index = df index

    hsa_exec_params = hsa_exec_params_db.loc[hsa_exp_index].to_dict()

    return hsa_exec_params


def load_hsa_of_synth_data():
    """
    Run this to load onto memory the HSA indices of the synthetic data.
    Define the path to the existing data for loading, and to the synthetic data for execution.
    """

    hsa_exec_params = load_hsa_exec_parameters(params_db_path=hsa_exec_params_db_path, hsa_exp_index=1)

    hsa_score_storage_path = define_hsa_score_storage_path(data_type=hsa_exec_params['data_type'],
                                                           sub_data_type=hsa_exec_params['sub_data_type'],
                                                           with_texture=hsa_exec_params['with_texture'])

    data_path_for_exp = data_path / hsa_exec_params['exp_data_path']
    hsa_scores = calculate_hsa_scores(vtp_data_path=data_path_for_exp, hsa_exec_params=hsa_exec_params)
    export_to_excel(hsa_scores, output_path=hsa_score_storage_path)


if __name__ == '__main__':
    load_hsa_of_synth_data()


