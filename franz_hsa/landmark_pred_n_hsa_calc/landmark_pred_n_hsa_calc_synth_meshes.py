from git import Repo
import os
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore
import datetime
from franz_hsa.landmark_evaluation.export_landmarks import export_landmarks
import json
import numpy as np
import pandas as pd
from pathlib import Path
import random
import re
import time
from tools.DataSetGraph import ReadPolyData
from tools.LandmarkingUtils import AddArraysToLandmarks
import vtk
random.seed(0)


def export_to_excel(hsa_indices, output_path, hsa_exec_params):
    # hsa index file should storage execution parameters, as well as subtype names
    """
    Exports the HSA indices for meshes of different subtypes.
    :param hsa_indices: a dictionary with keys as subtypes, inner keys as mesh id numbers, and HSA indices as values.
    :param output_path: a Path object to the .xlsx file to write the hsa indices data to.
    :param hsa_exec_params: a dictionary with instructive parameters for HSA measurement.
    """

    with pd.ExcelWriter(str(output_path.absolute())) as writer:
        for i, subtype in enumerate(list(hsa_indices.keys())):
            print(f'Exporting {subtype}...')
            # Generating the dataframe from the dictionary
            df = pd.DataFrame.from_dict(hsa_indices[subtype], orient='index', columns=['HSA index'])
            # Write the dataframe with subtype name as header
            df.to_excel(writer, sheet_name='Sheet1', startcol=i*3, startrow=1, index=True, header=[subtype])


def get_mesh_info(mesh_vtp_file_path, file_ending):
    """
    Return the subtype and id number of a mesh from a Path object.
    :param mesh_vtp_file_path: a Path object of a .vtp mesh file.
    :param file_ending: the final characters of the file name, e.g. '_cp.vtp' or '.vtp'
    :return: the mesh subtype and id number.
    """

    if '_cp' in file_ending:
        pattern = r'^(.*?)_inst_(\d{3})_cp$'
    else:  # no '_cp.abc', just '.abc'
        pattern = r'^(.*?)_inst_(\d{3})$'
    match = re.match(pattern, mesh_vtp_file_path.stem)
    mesh_subtype = match.group(1)
    mesh_id_num = int(match.group(2))

    return mesh_subtype, mesh_id_num


def place_three_landmarks_manually(mesh_vtp, landmark_coordinates=None):

    right_trag_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['TRAGION_RIGHT']))  # gets coordinates of 3D pt
    left_trag_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['TRAGION_LEFT']))
    nasion_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['NASION']))

    landmark_coords = np.vstack((right_trag_coords, left_trag_coords, nasion_coords))

    manual_landmarks = vtk.vtkPolyData()
    manual_landmarks.SetPoints(vtk.vtkPoints())
    for p in range(len(landmark_coords)):
        p_coords = tuple(landmark_coords[p, :])
        manual_landmarks.GetPoints().InsertNextPoint(*p_coords)

    landmark_names = ["TRAGION_RIGHT", "TRAGION_LEFT", "NASION"]  # must be defined in the right relative order
    landmarks_vtp = AddArraysToLandmarks(manual_landmarks, landmark_names)
    return landmarks_vtp


def place_landmarks_manually(mesh_vtp, landmark_coordinates=None):

    # Get landmark (x,y,z) coordinates from the mesh
    landmark_coords_dict = dict()
    for landmark in landmark_coordinates.keys():
        landmark_pt_id = int(landmark_coordinates[landmark])
        landmark_coords_dict[landmark] = np.array(mesh_vtp.GetPoint(landmark_pt_id))
        # right_trag_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['TRAGION_RIGHT']))

    coords_lst = list(landmark_coords_dict.values())
    landmark_coords = np.vstack(coords_lst)
    #
    # right_trag_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['TRAGION_RIGHT']))  # gets coordinates of 3D pt
    # left_trag_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['TRAGION_LEFT']))
    # nasion_coords = np.array(mesh_vtp.GetPoint(landmark_coordinates['NASION']))
    #
    # landmark_coords = np.vstack((right_trag_coords, left_trag_coords, nasion_coords))

    manual_landmarks = vtk.vtkPolyData()
    manual_landmarks.SetPoints(vtk.vtkPoints())
    for p in range(len(landmark_coords)):
        p_coords = tuple(landmark_coords[p, :])
        manual_landmarks.GetPoints().InsertNextPoint(*p_coords)

    landmark_names = list(landmark_coordinates.keys())  # must be defined in the right relative order
    landmarks_vtp = AddArraysToLandmarks(manual_landmarks, landmark_names)

    return landmarks_vtp


def get_landmark_coords(hsa_execution_parameters):
    """
    Convert the landmarks value {"TRAGION_RIGHT": "4869", "TRAGION_LEFT": "2431", "NASION": "9396"} to a dictionary
    {'TRAGION_RIGHT': 4869, 'TRAGION_LEFT': 2431, 'NASION': 9396} and returns that to the hsa_exec_parameters.
    :param hsa_execution_parameters: a dictionary with execution instructions for hsa measurement.
    """
    landmarks_str = hsa_execution_parameters['manual_landmarks']
    landmarks_dict = json.loads(landmarks_str)

    for landmark, point_id in landmarks_dict.items():
        landmarks_dict[landmark] = int(point_id)

    return landmarks_dict


def place_landmarks_n_measure_hsa(vtp_data_path, hsa_exec_params):
    """
    This function computes the HSA indices for the synthetic data in the vtp path given the HSA execution parameters.
    :param vtp_data_path: a Path object to a directory with subtype subdirectories, each of which contains .vtp meshes.
    :param hsa_exec_params: a dictionary with execution parameters.
    :return: a dictionary of HSA indices for each mesh of the subtypes in the .vtp data path.
    """
    hsa_indices = dict()
    times = dict()
    verbose = hsa_exec_params['verbose']

    for subtype_folder in vtp_data_path.iterdir():

        hsa_indices[subtype_folder.name] = dict()
        times[subtype_folder.name] = dict()

        file_ending = hsa_exec_params['file_ending']
        for mesh_vtp_file_path in subtype_folder.glob(f'*{file_ending}'):

            mesh_subtype, mesh_id_num = get_mesh_info(mesh_vtp_file_path, file_ending)  # files must be named subtype1_control...

            if only_use_first_n_samples and (mesh_id_num > sample_n_size):
                break
            # Load mesh
            mesh = ReadPolyData(str(mesh_vtp_file_path))
            print(f'\nWorking on {mesh_subtype} case #{mesh_id_num}...')

            landmark_placement = hsa_exec_params['landmark_placement']
            tic = time.time()
            if landmark_placement == 'automatic':
                print('Computing the landmarks by automatic prediction...')
                # Place landmarks on mesh, compute its hsa index, and store
                landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=verbose,
                                              crop_percentage=hsa_exec_params['crop_percentage'])
            else:  # 'manual'
                print('Placing the landmarks by manual definition...')
                coordinates = get_landmark_coords(hsa_exec_params)
                # landmarks = place_three_landmarks_manually(mesh_vtp=mesh, landmark_coordinates=coordinates)
                landmarks = place_landmarks_manually(mesh_vtp=mesh, landmark_coordinates=coordinates)

            if hsa_exec_params['export_landmarks']:
                crop_percentage = hsa_exec_params['crop_percentage']
                export_landmarks(landmarks, mesh_vtp_file_path, f'cropped_{crop_percentage}_'
                                                                f'{landmark_placement}_landmark_placement')

            if hsa_exec_params['calculate_hsa']:
                print('Calculating the HSA index...')
                _, hsa_index = ComputeHSAandRiskScore(image=mesh, landmarks=landmarks,
                                                      landmark_placement=hsa_exec_params['landmark_placement'],
                                                      age=hsa_exec_params['age'], sex=hsa_exec_params['sex'],
                                                      verbose=verbose)
                print(f'HSA index for {mesh_subtype} mesh #{mesh_id_num}: {hsa_index:0.2f}')
                hsa_indices[mesh_subtype][mesh_id_num] = hsa_index

            toc = time.time() - tic
            print(f'Working on {mesh_subtype} case #{mesh_id_num} took {toc:.0f} seconds.')
            times[mesh_subtype][mesh_id_num] = toc

    return hsa_indices, times


def define_hsa_score_storage_path(hsa_execution_params):

    exp_date = datetime.date.today().strftime("%m%d")
    data_type = hsa_execution_params['data_type']
    sub_data_type = hsa_execution_params['sub_data_type']

    if hsa_execution_params['with_texture']:
        texture_state = 'textured'
    else:
        texture_state = 'untextured'

    if data_type == 'synthetic':  # TODO have hsa_exp_index come from hsa_ex params, not the global var
        hsa_scores_file_path = dir_to_store_hsa_results / f'{exp_date}_hsa_indices_exp_{hsa_experiment_index}_' \
                                                          f'{data_type}_data_{sub_data_type}_{texture_state}.xlsx'
    else:  # data_type = 'patient'
        hsa_scores_file_path = dir_to_store_hsa_results / f'{exp_date}_hsa_indices_{data_type}_data' \
                                              f'_{sub_data_type}.xlsx'

    return hsa_scores_file_path


def load_hsa_exec_parameters(params_db_path, hsa_exp_index):

    hsa_exec_params_db = pd.read_excel(params_db_path, index_col=0)  # index_col = 0 s.t. hsa_exp_index = df index

    hsa_exec_params = hsa_exec_params_db.loc[hsa_exp_index].to_dict()

    return hsa_exec_params


def get_hsa_or_landmarks(hsa_exp_index):

    hsa_exec_params = load_hsa_exec_parameters(params_db_path=hsa_exec_params_db_path, hsa_exp_index=hsa_exp_index)

    data_path = Path(hsa_exec_params['exp_data_path'])

    hsa_scores, times = place_landmarks_n_measure_hsa(vtp_data_path=data_path, hsa_exec_params=hsa_exec_params)

    if hsa_exec_params['calculate_hsa']:
        hsa_score_storage_path = define_hsa_score_storage_path(hsa_exec_params)
        export_to_excel(hsa_indices=hsa_scores, output_path=hsa_score_storage_path, hsa_exec_params=hsa_exec_params)
        times_path = hsa_score_storage_path.parent / (hsa_score_storage_path.stem + '_times.xlsx')
        export_to_excel(hsa_indices=times, output_path=times_path, hsa_exec_params=hsa_exec_params)


if __name__ == '__main__':
    repo_root_path = Path(repo_root_str_path)
    hsa_exec_params_db_path = repo_root_path / r"franz_hsa/landmark_pred_n_hsa_calc/hsa_execution_parameters.xlsx"
    only_use_first_n_samples = False  # TODO: add this and the next variable to hsa_execution_parameters
    sample_n_size = 2

    # Change this to a directory to storage the hsa results in
    dir_to_store_hsa_results = repo_root_path / r"franz_hsa/landmark_pred_n_hsa_calc/results"

    hsa_experiment_index = 10
    get_hsa_or_landmarks(hsa_experiment_index)



