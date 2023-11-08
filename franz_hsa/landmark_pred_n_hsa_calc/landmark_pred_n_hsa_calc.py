from git import Repo
import os
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
import datetime
from franz_hsa.landmark_evaluation.export_landmarks import export_landmarks
from franz_hsa.utils.utils_landmarks import load_landmark_points
from numpy import isnan
import pandas as pd
from pathlib import Path
import random
import time
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
            df = pd.DataFrame.from_dict(hsa_indices[subtype])
            df = df.transpose()

            # Updating the column names of the dataframe
            column_names_mapping = {0: 'hsa_score', 1: 'cs_risk_score', 2: 'exec_duration'}
            df.rename(columns=column_names_mapping, inplace=True)
            df = df.rename_axis('id')

            # Write the dataframe with subtype name as header
            mesh_data_len = len(list(hsa_indices[subtype].values())[0])
            df.to_excel(writer, sheet_name='hsa_output', startcol=i*(mesh_data_len + 2), startrow=1, index=True)
            worksheet = writer.sheets['hsa_output']
            worksheet.write(0, i * (mesh_data_len + 2), subtype)

    print(f'Exported data to {str(output_path.absolute())}.')


def define_hsa_score_storage_path(hsa_execution_params, exp_index):

    time_stamp = datetime.datetime.now().strftime("%m%d;%H%M")
    hsa_model = hsa_execution_params['hsa_model']
    data_type = hsa_execution_params['data_type']
    sub_data_type = hsa_execution_params['sub_data_type']
    landmark_placement = hsa_execution_params['landmark_placement']
    num_landmarks = hsa_execution_params['num_landmarks']

    if data_type == 'synthetic':  # TODO have hsa_exp_index come from hsa_ex params, not the global var
        if hsa_execution_params['with_texture']:
            texture_state = 'textured'
        else:
            texture_state = 'untextured'
        hsa_scores_file_path = dir_to_store_hsa_results / f'{time_stamp}_hsa_v{hsa_model}_indices_exp_{exp_index}_' \
                                                          f'{data_type}_data_{sub_data_type}_{texture_state}_' \
                                                          f'{num_landmarks}_{landmark_placement}_landmarks.xlsx'
    else:  # data_type = 'patient'
        hsa_scores_file_path = dir_to_store_hsa_results / f'{time_stamp}_hsa_v{hsa_model}_indices_{data_type}_data' \
                                                          f'_{sub_data_type}_{num_landmarks}_{landmark_placement}_' \
                                                          f'landmarks.xlsx'

    return hsa_scores_file_path


def place_landmarks_n_measure_hsa_on_synth_data(data_path, hsa_exec_params):
    """
    This function computes the HSA indices for the synthetic data in the vtp path given the HSA execution parameters.
    :param data_path: a Path object to a directory with subtype subdirectories, each of which contains .vtp meshes.
    :param hsa_exec_params: a dictionary with execution parameters.
    :return: a dictionary of HSA indices for each mesh of the subtypes in the .vtp data path.
    """

    hsa_and_times = dict()  # patient: {'sagittal, pre, post': {patient ID: HSA, CS risk, time}

    for subtype_folder in data_path.iterdir():  # for each patient folder
        if 'all' not in hsa_exec_params['included_subtypes'] and \
                subtype_folder.name not in hsa_exec_params['included_subtypes']:
            continue

        hsa_and_times[subtype_folder.name] = dict()

        file_ending = hsa_exec_params['file_ending']
        for mesh_vtp_file_path in subtype_folder.glob(f'*{file_ending}'):

            mesh_subtype, mesh_id_num = get_mesh_info(mesh_vtp_file_path, file_ending)

            # Load mesh
            mesh = ReadPolyData(str(mesh_vtp_file_path))
            print(f'\nWorking on {mesh_subtype} case #{mesh_id_num}...')

            # place landmarks
            tic = time.time()
            landmark_placement = hsa_exec_params['landmark_placement']
            crop_percentage = hsa_exec_params['crop_percentage']
            if landmark_placement == 'manual':
                print('Placing the landmarks by manual definition...')
                coordinates = get_landmark_coords(hsa_exec_params)
                landmarks = place_landmarks_manually(mesh_vtp=mesh, landmark_coordinates=coordinates)
            else:  # 'automatic'
                print('Computing the landmarks by automatic prediction...')
                landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=hsa_exec_params['verbose'],
                                              crop_percentage=crop_percentage)
            hsa_exec_params['num_landmarks'] = landmarks.GetNumberOfPoints()

            # export landmarks
            if hsa_exec_params['export_landmarks']:
                export_landmarks(landmarks=landmarks, mesh_file_path=mesh_vtp_file_path,
                                 landmark_placement=landmark_placement, cropping_info=f'mesh_cropped_{crop_percentage}')

            # calculate hsa
            if hsa_exec_params['calculate_hsa']:
                print('Calculating the HSA index...')
                cs_risk_score, hsa_index = ComputeHSAandRiskScore(image=mesh, landmarks=landmarks,
                                                                  age=hsa_exec_params['age'],
                                                                  sex=hsa_exec_params['sex'],
                                                                  verbose=hsa_exec_params['verbose'])
                toc = time.time() - tic
                print(f'Scores for {mesh_subtype} mesh #{mesh_id_num}: '
                      f'HSA index: {hsa_index:0.2f}, '
                      f'CS risk score: {cs_risk_score:0.2f}')
                hsa_and_times[mesh_subtype][mesh_id_num] = [hsa_index, cs_risk_score, toc]
                print(f'Working on {mesh_subtype} case #{mesh_id_num} took {toc:.0f} seconds.')

    return hsa_and_times


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
            if hsa_exec_params['export_vtp_mesh']:
                vtp_path = str(mesh_file_path.parent / (mesh_file_path.stem + '.vtp'))
                WritePolyData(mesh, vtp_path)
            print(f'\nWorking on {subtype} case #{patient_id}...')

            # Place and export landmarks
            tic = time.time()
            landmark_placement = hsa_exec_params['landmark_placement']
            if landmark_placement == 'manual':
                print('Placing the landmarks by manual definition...')
                landmarks_path = mesh_file_path.parent / 'manual_landmarks.xlsx'
                coordinates = load_landmark_points(landmarks_path)
                # landmarks = place_three_landmarks_manually(mesh_vtp=mesh, landmark_coordinates=coordinates)
                landmarks = place_landmarks_manually(mesh_vtp=mesh, landmark_coordinates=coordinates)
            elif landmark_placement == 'none':
                pass
            else:  # automatic
                print('Computing the landmarks by automatic prediction...')
                landmark_placement = hsa_exec_params['landmark_placement']
                landmarks, _ = PlaceLandmarks(mesh, crop=hsa_exec_params['crop'], verbose=hsa_exec_params['verbose'],
                                              crop_percentage=hsa_exec_params['crop_percentage'])

            if hsa_exec_params['export_landmarks']:
                crop_percentage = hsa_exec_params['crop_percentage']
                export_landmarks(landmarks, mesh_file_path, landmark_placement, f'mesh_cropped_{crop_percentage}')

            # calculate hsa
            if hsa_exec_params['calculate_hsa']:
                print('Calculating the HSA index...')
                cs_risk_score, hsa_index = ComputeHSAandRiskScore(image=mesh, landmarks=landmarks,
                                                                  age=patient_age, sex=patient_sex,
                                                                  verbose=hsa_exec_params['verbose'])
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
        hsa_scores_n_times = place_landmarks_n_measure_hsa_on_synth_data(data_path=data_path,
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

    if isnan(hsa_exec_params['hsa_model']):
        raise Exception('You must enter an hsa_model in hsa_execution_parameters: '
                        'either 1 (before metopic update) or 2 (for metopic update).')

    if ',' in hsa_exec_params['included_subtypes']:
        hsa_exec_params['included_subtypes'] = hsa_exec_params['included_subtypes'].split(', ')

    return hsa_exec_params


if __name__ == '__main__':

    repo_root_path = Path(repo_root_str_path)
    hsa_exec_params_db_path = repo_root_path / r"franz_hsa/landmark_pred_n_hsa_calc/hsa_execution_parameters.xlsx"
    dir_to_store_hsa_results = repo_root_path / 'franz_hsa/hsa_output'

    # Define your experiment index and where to store the exported data
    experiment_index = 13
    hsa_execution_parameters = load_hsa_exec_parameters(params_db_path=hsa_exec_params_db_path,
                                                        hsa_exp_index=experiment_index)
    hsa_model = hsa_execution_parameters['hsa_model']
    print(f'Using HSA model v{hsa_model}.')
    if hsa_model == 1:
        from franz_hsa.hsa_v1.Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore, ReadImage
        from franz_hsa.hsa_v1.tools.DataSetGraph import ReadPolyData, WritePolyData
    else:  # 2
        from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore, ReadImage
        from tools.DataSetGraph import ReadPolyData, WritePolyData

    # Execute the HSA model
    execute_hsa_by_params(hsa_execution_parameters, experiment_index)
