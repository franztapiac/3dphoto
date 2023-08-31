import json

import numpy.random
from numpy import random
from pathlib import Path
import pyvista as pv
import re

"""
Purpose of script:
Generates a window that displays meshes with landmarks. The meshes can be those from the test set of a KDE model.
The landmarks can be those predicted with Elkhill's landmark prediction method.

Three functions are used to generate this functionality:
1. visualise_landmarks_per_mesh: creates the window displaying a mesh and its landmarks. Click 'X' for the next mesh. 
2. get_mesh_ids_per_subtype: gets mesh subtype and id for all meshes in a test set file (file has paths to mesh files). 
3. visualise_landmarks_per_model: receives user input for which model's meshes to display, and whether to display 
the control meshes. 
"""


def create_pv_plotter(mesh_path, pred_landmarks_path=None, manual_landmarks=None):
    """
    Creates a PyVista plotter window showing one mesh with its manual or predicted landmarks.
    :param mesh_path: Path; to the mesh .ply file.
    :param pred_landmarks_path: Path; to the predicted landmarks .ply file.
    :param manual_landmarks: PyVista object; landmark coordinates.
    """

    p = pv.Plotter()
    p.add_mesh(pv.read(str(mesh_path)))
    if pred_landmarks_path:
        landmark_coordinates = pv.read(str(pred_landmarks_path))
    else:  # assumes that manual_landmarks if given
        landmark_coordinates = manual_landmarks
    p.add_points(landmark_coordinates, render_points_as_spheres=True, point_size=15, color='r')
    p.add_text('{}'.format(mesh_path.name), position='upper_right', color='k')
    p.view_xy()
    p.show()


def visualise_landmarks_per_mesh(meshes_to_visualise, ply_synth_data_path, vis_control_meshes=True,
                                 pred_landmarks_path=None, manual_landmarks=None):
    """
    Creates a PyVista Plotter visual of a mesh and its HSA-predicted landmarks.
    :param meshes_to_visualise: a dictionary with format {'subtypes': [mesh id numbers] }, for IDing a mesh to vis.
    :param ply_synth_data_path: Path; to the synthetic .ply format data.
    :param vis_control_meshes: a bool object for whether to visualise the control meshes with their landmarks.
    :param pred_landmarks_path: Path; to the predicted .ply landmarks.
    :param manual_landmarks: PyVista mesh; manually defined landmarks.
    """

    if not vis_control_meshes:
        del meshes_to_visualise['control']

    for subtype in list(meshes_to_visualise.keys()):

        subtype_folder = ply_synth_data_path / subtype
        mesh_id_nums = meshes_to_visualise[subtype]

        if pred_landmarks_path:
            landmarks_coordinates_dir = pred_landmarks_path / subtype  # if ldnmks path is input

        for mesh_id_num in mesh_id_nums:
            zero_padded_id = str(mesh_id_num).zfill(3)
            mesh_file_path = list(subtype_folder.glob(f'*{zero_padded_id}_cp.ply'))[0]

            if pred_landmarks_path:
                mesh_predicted_landmarks_path = list(landmarks_coordinates_dir.glob(f'*{zero_padded_id}_'
                                                                                    f'cp_pred_landmarks.ply'))[0]

                create_pv_plotter(mesh_path=mesh_file_path, pred_landmarks_path=mesh_predicted_landmarks_path)

            elif manual_landmarks:
                create_pv_plotter(mesh_path=mesh_file_path, manual_landmarks=manual_landmarks)


def get_mesh_ids_randomly(quantity, subtypes_lst):
    """
    Generate a dictionary with randomly mesh ID numbers for each input subtype.
    :param quantity: int; number of mesh IDs to generate per subtype.
    :param subtypes_lst: list; subtype string names to return in the returned dictionary.
    """

    mesh_ids_per_subtype = dict()

    for subtype in subtypes_lst:
        random_mesh_ids = list(random.randint(1, 101, size=quantity))
        if subtype not in mesh_ids_per_subtype:
            mesh_ids_per_subtype[subtype] = []
        mesh_ids_per_subtype[subtype] = random_mesh_ids

    return mesh_ids_per_subtype


def get_mesh_ids_per_subtype(json_file_path):
    """
    Reads the list of path to mesh files and generates a dict with format {'subtypes': [mesh id numbers] }.
    :param json_file_path: the Path object to the json file with the list of mesh file Paths of the model test dataset.
    :return: a dict with format {'subtypes': [mesh id numbers] }.
    """
    mesh_ids_per_subtype = dict()

    with open(json_file_path, "r") as file:
        json_data = file.read()
    paths_list = json.loads(json_data)

    for i, str_path in enumerate(paths_list):
        file_name = Path(str_path).stem
        pattern = r'^(.*?)_inst_(\d+)_cp_.*$'
        match = re.search(pattern, file_name)

        subtype = match.group(1)
        mesh_id_num = int(match.group(2))

        if subtype not in mesh_ids_per_subtype:
            mesh_ids_per_subtype[subtype] = []
        mesh_ids_per_subtype[subtype].append(mesh_id_num)

    return mesh_ids_per_subtype


def get_landmarks_object(landmarks_points_path):
    """
    Generate a PyVista landmarks object from the landmark point information.
    :param landmarks_points_path: Path; to an Excel file with points for each landmarking object.
    """

    # read excel into pandas / dict

    # convert into vtp

    # convert vtp to ply
    # landmark_ply = pv.PolyData(landmark_coordinates)

    # return ply
    # TODO: convert landmarks object
    return 1


def visualise_landmarks_per_model(model_name, visualise_control_meshes):
    """
    Generates a window that displays a mesh with landmarks. The window is generated by PyVista.
    :param model_name: string name of the KDE model to visualising the meshes of the corresponding test dataset.
    :param visualise_control_meshes: bool for whether to display the control (healthy) meshes with their landmarks.
    """

    test_set_paths_per_model = {'model_A_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_both.json'),
                                'model_M_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_metopicB.json'),
                                'model_S_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_sagittalB.json')}

    file_w_meshes_paths = test_set_paths_per_model[model_name]
    mesh_ids_per_subtype = get_mesh_ids_per_subtype(json_file_path=file_w_meshes_paths)
    # TODO: Fix vis function so that this function still works
    visualise_landmarks_per_mesh(meshes_to_visualise=mesh_ids_per_subtype, vis_control_meshes=visualise_control_meshes)


def visualise_manually_defined_landmarks(landmarks_pts_path, data_path, meshes_num, subtypes_lst):
    landmarks = get_landmarks_object(landmarks_pts_path)
    mesh_ids_per_subtype = get_mesh_ids_randomly(meshes_num, subtypes_lst)
    visualise_landmarks_per_mesh(meshes_to_visualise=mesh_ids_per_subtype, ply_synth_data_path=data_path,
                                 manual_landmarks=landmarks)


if __name__ == '__main__':
    use_case = 2

    if use_case == 1:  # Visualise predicted landmarks
        # There are three model names: model_A_Aug01, model_M_Aug01 and model_S_Aug01
        visualise_landmarks_per_model(model_name='model_A_Aug01', visualise_control_meshes=False)

    else:  # Visualise manually defined landmarks
        landmarks_path = Path("./landmark_points.xlsx")
        synth_data_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply")
        n_meshes_per_subtype = 3
        subtypes = ['control', 'metopic', 'sagittal']
        visualise_manually_defined_landmarks(landmarks_pts_path=landmarks_path, data_path=synth_data_path,
                                             meshes_num=n_meshes_per_subtype, subtypes_lst=subtypes)
