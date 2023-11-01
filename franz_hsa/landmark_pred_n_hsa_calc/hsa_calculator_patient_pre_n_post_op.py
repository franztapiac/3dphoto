from Analyze3DPhotogram import ComputeHSAandRiskScore, PlaceLandmarks, ReadImage
import os
from pathlib import Path


def get_patient_ids_and_data_paths(main_directory):
    """
    Gets the patient ids and, for each patient, the paths to the directories for their pre-op and post-op data files.
    :param main_directory: a Path object to the directory wherein the patient data directories are.
    :return: a dict with patient ids as keys, 'pre' and 'post' as second keys, and Path objects to the resp. data files.
    """

    subdirectories = [subdir for subdir in main_directory.iterdir() if subdir.is_dir()]
    patient_subdirs = [subdir for subdir in subdirectories if subdir.name != 'results']
    patient_data_paths = {patient_subdir.name: {'pre': patient_subdir / 'pre' / 'meshes',
                                                'post': patient_subdir / 'post' / 'meshes'}
                                  for patient_subdir in patient_subdirs}
    return patient_data_paths


def get_patient_data_for_hsa_calc(patient_data_file_path):
    pass


def calculate_hsa_index(patient_mesh_path, patient_data):  # patient dat should include age and sex
    neck_cropped_mesh_file_path = list(patient_mesh_path.glob(f'*_neck_cropped.obj'))[0]
    mesh = ReadImage(str(neck_cropped_mesh_file_path))
    landmarks, _ = PlaceLandmarks(mesh, crop=False, verbose=True, crop_percentage=0)
    _, hsa_index = ComputeHSAandRiskScore(mesh, landmarks, age=100, sex='M', verbose=True)
    return hsa_index


def load_and_plot_hsa_scores():
    """
    Loads hsa scores from storage or model execution and plots them.
    """
    pre_and_post_op_data_path = Path("C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\pre_and_post_op")
    patient_data_file_path = pre_and_post_op_data_path / 'patient_data_for_hsa_calc.xlsx'
    hsa_indices_path = pre_and_post_op_data_path / 'results' / 'pre_and_post_op_hsa_scores.xlsx'

    if os.path.exists(hsa_indices_path):
        # plot hsa scores
        pass
    else:
        patient_data_paths = get_patient_ids_and_data_paths(pre_and_post_op_data_path)
        patient_data_for_hsa_calculation = get_patient_data_for_hsa_calc(patient_data_file_path)
        hsa_indices = {patient_id: {'pre': None, 'post': None} for patient_id in patient_data_paths}

        for patient_id in patient_data_paths.keys():
            for op_time in patient_data_paths[patient_id].keys():

                patient_data = patient_data_for_hsa_calculation[patient_id][op_time]
                print(f'Working with {op_time} operative data from patient {patient_id}...')
                patient_mesh_path = patient_data_paths[patient_id][op_time]
                hsa_index = calculate_hsa_index(patient_mesh_path, patient_data)
                hsa_indices[patient_id][op_time] = hsa_index
                print(f'HSA index is {hsa_index:0.2f}')
        # export dict as excel
        pass


if __name__ == '__main__':
    load_and_plot_hsa_scores()
