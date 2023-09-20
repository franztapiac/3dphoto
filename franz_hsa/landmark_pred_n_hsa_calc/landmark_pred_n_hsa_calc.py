from git import Repo
import os
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore, ReadImage
import datetime
from franz_hsa.landmark_evaluation.export_landmarks import export_landmarks
import pandas as pd
from pathlib import Path
import random
import time
from tools.DataSetGraph import ReadPolyData
from tools_synth_data_processing import get_landmark_coords, get_mesh_info, place_landmarks_manually
from tools_patient_data_processing import get_patient_age_and_sex
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
            df = pd.DataFrame.from_dict(hsa_indices[subtype]) #, orient='index', columns=['HSA index'])
            df = df.transpose()

            # Updating the column names of the dataframe
            column_names_mapping = {0: 'hsa_score', 1: 'cs_risk_score', 2: 'exec_duration'}
            df.rename(columns=column_names_mapping, inplace=True)

            # Write the dataframe with subtype name as header
            mesh_data_len = len(list(hsa_indices[subtype].values())[0])
            df.to_excel(writer, sheet_name='hsa_output', startcol=i*(mesh_data_len + 2), startrow=1, index=True)
            worksheet = writer.sheets['hsa_output']
            worksheet.write(0, i * (mesh_data_len + 2), subtype)

    print(f'Exported data to {str(output_path.absolute())}.')


def define_hsa_score_storage_path(hsa_execution_params, exp_index):

    time_stamp = datetime.datetime.now().strftime("%m%d;%H%M")
    data_type = hsa_execution_params['data_type']
    sub_data_type = hsa_execution_params['sub_data_type']

    if data_type == 'synthetic':  # TODO have hsa_exp_index come from hsa_ex params, not the global var
        if hsa_execution_params['with_texture']:
            texture_state = 'textured'
        else:
            texture_state = 'untextured'
        hsa_scores_file_path = dir_to_store_hsa_results / f'{time_stamp}_hsa_indices_exp_{exp_index}_' \
                                                          f'{data_type}_data_{sub_data_type}_{texture_state}.xlsx'
    else:  # data_type = 'patient'
        hsa_scores_file_path = dir_to_store_hsa_results / f'{time_stamp}_hsa_indices_{data_type}_data' \
                                                          f'_{sub_data_type}.xlsx'

    return hsa_scores_file_path


def place_landmarks_n_measure_hsa_on_synth_data(data_path, hsa_exec_params):
    """
    This function computes the HSA indices for the synthetic data in the vtp path given the HSA execution parameters.
    :param data_path: a Path object to a directory with subtype subdirectories, each of which contains .vtp meshes.
    :param hsa_exec_params: a dictionary with execution parameters.
    :return: a dictionary of HSA indices for each mesh of the subtypes in the .vtp data path.
    """
    hsa_indices = dict()  # patient: {'sagittal, pre, post': {patient ID: HSA, CS risk, time}
    times = dict()
    verbose = hsa_exec_params['verbose']

    for subtype_folder in data_path.iterdir():  # for each patient folder
        # for each sample pre or post
        hsa_indices[subtype_folder.name] = dict()
        times[subtype_folder.name] = dict()

        file_ending = hsa_exec_params['file_ending']
        for mesh_vtp_file_path in subtype_folder.glob(f'*{file_ending}'):  # for each mesh

            mesh_subtype, mesh_id_num = get_mesh_info(mesh_vtp_file_path, file_ending)
            # files must be named subtype1_control...

            if only_use_first_n_samples and (mesh_id_num > sample_n_size):
                break
            # Load mesh
            mesh = ReadPolyData(str(mesh_vtp_file_path))
            print(f'\nWorking on {mesh_subtype} case #{mesh_id_num}...')

            # place and export landmarks
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

            # calculate hsa
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


def load_patient_mesh_file_paths(data_path, file_ending):
    """
    Identifies the paths to patient data to run through a KDE model.
    :param data_path: Path; to a directory with patient data.
    format: data_path / patientID / 'pre' or 'post'/ meshes / '*_rg_CN.ply'
    :param file_ending: str; the ending characters in the mesh filenames for file identification.
    :return: dict; format: {'subtype_pre/post': { mesh_id_num: Path(mesh) } }.
    """
    print('\n// Locating patient mesh samples //')
    meshes_file_paths = dict()
    subtype = data_path.name.split('_')[0]

    for patient_id_folder in data_path.iterdir():
        for time_sample in patient_id_folder.iterdir():
            print(f'\nFor patient #{patient_id_folder.name}, locating the {time_sample.name}-op mesh sample...')

            subtype_sample = f'{subtype}_{time_sample.name}'
            if subtype_sample not in meshes_file_paths:
                meshes_file_paths[subtype_sample] = dict()

            patient_sample_dir = time_sample / 'meshes'
            mesh_file_path = list(patient_sample_dir.glob(f'*{file_ending}'))[0]
            meshes_file_paths[subtype_sample][patient_id_folder.name] = mesh_file_path
            print(f'Located sample {mesh_file_path.name}.')

    return meshes_file_paths, subtype


def place_landmarks_n_measure_hsa_on_patient_data(mesh_file_paths, hsa_exec_params):

    print('\n// Placing landmarks and calculating HSA indices //')

    hsa_and_times = dict()
    verbose = hsa_exec_params['verbose']

    for subtype in mesh_file_paths.keys():
        hsa_and_times[subtype] = dict()

        for patient_id in mesh_file_paths[subtype].keys():

            # Get age and sex information for this specific patient
            age_n_sex_db_path = hsa_exec_params['age']
            patient_age, patient_sex = get_patient_age_and_sex(db_path=age_n_sex_db_path,
                                                               patient_id=patient_id,
                                                               subtype_sample=subtype)

            mesh_file_path = mesh_file_paths[subtype][patient_id]
            mesh = ReadImage(str(mesh_file_path.absolute()))
            print(f'\nWorking on {subtype} case #{patient_id}...')

            # Place and export landmarks
            tic = time.time()
            print('Computing the landmarks by automatic prediction...')
            landmark_placement = hsa_exec_params['landmark_placement']
            landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=verbose,
                                          crop_percentage=hsa_exec_params['crop_percentage'])

            if hsa_exec_params['export_landmarks']:
                crop_percentage = hsa_exec_params['crop_percentage']
                export_landmarks(landmarks, mesh_file_path, f'cropped_{crop_percentage}_'
                                                            f'{landmark_placement}_landmark_placement')

            # calculate hsa
            if hsa_exec_params['calculate_hsa']:
                print('Calculating the HSA index...')
                cs_risk_score, hsa_index = ComputeHSAandRiskScore(image=mesh, landmarks=landmarks,
                                                                  landmark_placement=landmark_placement,
                                                                  age=patient_age, sex=patient_sex,
                                                                  verbose=verbose)
                toc = time.time() - tic
                print(f'Scores for {subtype} mesh #{patient_id}: '
                      f'HSA index: {hsa_index:0.2f}, '
                      f'CS risk score: {cs_risk_score:0.2f}')
                hsa_and_times[subtype][patient_id] = [hsa_index, cs_risk_score, toc]
                print(f'Working on {subtype} case #{patient_id} took {toc:.0f} seconds.')

    return hsa_and_times


def execute_hsa_by_params(hsa_exp_params, exp_index):

    # Load data and execute HSA
    data_path = Path(hsa_exp_params['exp_data_path'])
    if hsa_exp_params['data_type'] == 'synthetic':
        hsa_scores_n_times, times = place_landmarks_n_measure_hsa_on_synth_data(data_path=data_path,
                                                                                hsa_exec_params=hsa_exp_params)
    else:  # 'patient' data
        mesh_files_paths, dataset = load_patient_mesh_file_paths(data_path=data_path,
                                                                 file_ending=hsa_exp_params['file_ending'])
        hsa_scores_n_times = place_landmarks_n_measure_hsa_on_patient_data(mesh_file_paths=mesh_files_paths,
                                                                           hsa_exec_params=hsa_exp_params)

    # Store HSA output
    if hsa_exp_params['calculate_hsa']:
        hsa_score_storage_path = define_hsa_score_storage_path(hsa_exp_params, exp_index)
        export_to_excel(hsa_indices=hsa_scores_n_times, output_path=hsa_score_storage_path,
                        hsa_exec_params=hsa_exp_params)


def load_hsa_exec_parameters(params_db_path, hsa_exp_index):

    hsa_exec_params_db = pd.read_excel(params_db_path, index_col=0)  # index_col = 0 s.t. hsa_exp_index = df index
    hsa_exec_params = hsa_exec_params_db.loc[hsa_exp_index].to_dict()

    return hsa_exec_params


if __name__ == '__main__':

    repo_root_path = Path(repo_root_str_path)
    hsa_exec_params_db_path = repo_root_path / r"franz_hsa/landmark_pred_n_hsa_calc/hsa_execution_parameters.xlsx"
    only_use_first_n_samples = False  # TODO: add this and the next variable to hsa_execution_parameters
    sample_n_size = 2

    # Define your experiment index and where to store the exported data
    experiment_index = 11
    hsa_execution_parameters = load_hsa_exec_parameters(params_db_path=hsa_exec_params_db_path,
                                                        hsa_exp_index=experiment_index)
    dir_to_store_hsa_results = repo_root_path / r"franz_hsa/landmark_pred_n_hsa_calc/results"

    # Execute the HSA model
    execute_hsa_by_params(hsa_execution_parameters, experiment_index)

