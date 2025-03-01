from git import Repo
import os
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
import json
import numpy as np
from numpy import random
from pathlib import Path
import pyvista as pv
import re
from Analyze3DPhotogram import ReadImage
from franz_hsa.landmark_pred_n_hsa_calc.tools_synth_data_processing import place_landmarks_manually
from franz_hsa.landmark_evaluation.export_landmarks import export_landmarks
from franz_hsa.utils.utils_landmarks import load_landmark_points
from vtkmodules.util import numpy_support


def create_pv_plotter(mesh_path, pred_landmarks_path=None, landmarks_pts_path=None, landmark_labels=None):
    """
    Creates a PyVista plotter window showing one mesh with its manual or predicted landmarks.
    :param mesh_path: Path; to the mesh .ply file.
    :param pred_landmarks_path: Path; to the predicted landmarks .ply file.
    :param landmarks_pts_path: Path; to the landmarks points Excel file.
    """

    p = pv.Plotter()
    mesh = pv.read(str(mesh_path))
    p.add_mesh(mesh)
    if pred_landmarks_path:
        landmark_coordinates = pv.read(str(pred_landmarks_path))
    else:  # assumes that manual_landmarks if given
        landmark_coordinates = get_landmark_coordinates(mesh=mesh, landmarks_points_path=landmarks_pts_path)
    if landmark_labels:
        landmarks_array = numpy_support.vtk_to_numpy(landmark_coordinates.GetPoints().GetData())
        p.add_point_labels(landmarks_array, landmark_labels, font_size=20, point_color='red', point_size=20,
                           render_points_as_spheres=True, always_visible=True, shadow=True)
    else:
        p.add_points(landmark_coordinates, render_points_as_spheres=True, point_size=15, color='r')
    p.add_text('{}'.format(mesh_path.name), position='upper_right', color='k')
    p.view_xy()
    p.show()


def visualise_landmarks_per_mesh(meshes_to_visualise, ply_synth_data_path, file_end, vis_control_meshes=True,
                                 pred_landmarks_path=None, landmarks_pts_path=None):
    """
    Creates a PyVista Plotter visual of a mesh and its HSA-predicted landmarks.
    :param meshes_to_visualise: a dictionary with format {'subtypes': [mesh id numbers] }, for IDing a mesh to vis.
    :param ply_synth_data_path: Path; to the synthetic .ply format data.
    :param file_end: string; ending characters of a file name (downsampled: '_cp.ply', original: '.ply')
    :param vis_control_meshes: a bool object for whether to visualise the control meshes with their landmarks.
    :param pred_landmarks_path: Path; to the predicted .ply landmarks.
    :param landmarks_pts_path: Path; to the landmarks points Excel file.
    """

    if not vis_control_meshes:
        del meshes_to_visualise['control']

    for subtype in list(meshes_to_visualise.keys()):

        subtype_folder = ply_synth_data_path / subtype
        mesh_id_nums = meshes_to_visualise[subtype]

        if pred_landmarks_path:
            landmarks_coordinates_dir = pred_landmarks_path / subtype / 'predicted_landmarks_cropped_0_' \
                                                                        'automatic_landmark_placement'

        for mesh_id_num in mesh_id_nums:
            zero_padded_id = str(mesh_id_num).zfill(3)
            mesh_file_path = list(subtype_folder.glob(f'*{zero_padded_id}{file_end}'))[0]

            if pred_landmarks_path:
                mesh_predicted_landmarks_path = list(landmarks_coordinates_dir.glob(f'*{zero_padded_id}_'
                                                                                    f'cp_pred_landmarks.ply'))[0]

                create_pv_plotter(mesh_path=mesh_file_path, pred_landmarks_path=mesh_predicted_landmarks_path)

            elif landmarks_pts_path:
                create_pv_plotter(mesh_path=mesh_file_path, landmarks_pts_path=landmarks_pts_path)


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


def get_landmark_coordinates(mesh, landmarks_points_path):
    """
    Generate a PyVista landmarks object from the landmark point information.
    :param mesh: PyVista Ply PolyData; a non-clipped synthetic mesh.
    :param landmarks_points_path: Path; to an Excel file with points for each landmarking object.
    """

    landmark_points = load_landmark_points(landmarks_points_path)

    # Get landmark (x,y,z) coordinates from the mesh
    landmark_coords_dict = dict()
    for landmark in landmark_points.keys():
        landmark_pt_id = int(landmark_points[landmark])
        landmark_coords_dict[landmark] = np.array(mesh.points[landmark_pt_id])

    # Generate .ply landmarks file
    coords_lst = list(landmark_coords_dict.values())
    landmark_coordinates = np.vstack(coords_lst)

    return landmark_coordinates


def visualise_landmarks_per_model(model_name, visualise_control_meshes):
    """
    Generates a window that displays a mesh with landmarks. The window is generated by PyVista.
    :param model_name: string name of the KDE model to visualising the meshes of the corresponding test dataset.
    :param visualise_control_meshes: bool for whether to display the control (healthy) meshes with their landmarks.
    """

    test_set_paths_per_model = {'model_A_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_both.json'),
                                'model_M_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_metopicB.json'),
                                'model_S_Aug01': Path('../synth_data/test_datasets/testdata_model_0108_sagittalB.json')}

    data_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_downsampled_untextured_unclipped_ply")
    pred_landmarks_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_downsampled_untextured_unclipped_vtp_python")
    file_w_meshes_paths = test_set_paths_per_model[model_name]
    mesh_ids_per_subtype = get_mesh_ids_per_subtype(json_file_path=file_w_meshes_paths)
    visualise_landmarks_per_mesh(meshes_to_visualise=mesh_ids_per_subtype, ply_synth_data_path=data_path,
                                 file_end='_cp.ply', vis_control_meshes=visualise_control_meshes,
                                 pred_landmarks_path=pred_landmarks_path)


def visualise_manually_defined_landmarks(landmarks_pts_path, data_path, meshes_num, subtypes_lst):
    mesh_ids_per_subtype = get_mesh_ids_randomly(meshes_num, subtypes_lst)
    file_ending = '.ply'
    visualise_landmarks_per_mesh(meshes_to_visualise=mesh_ids_per_subtype, ply_synth_data_path=data_path,
                                 file_end=file_ending, landmarks_pts_path=landmarks_pts_path)


if __name__ == '__main__':
    use_case = 2
    landmarks_option = 'full'

    if use_case == 1:  # Visualise predicted landmarks
        # There are three model names: model_A_Aug01, model_M_Aug01 and model_S_Aug01
        visualise_landmarks_per_model(model_name='model_A_Aug01', visualise_control_meshes=False)

    elif use_case == 2:  # Visualise manually defined landmarks
        if landmarks_option == 'full':
            landmarks_path = Path("./landmark_points_full.xlsx")
        else:
            landmarks_path = Path("./landmark_points_reduced.xlsx")
        synth_data_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply")
        n_meshes_per_subtype = 5
        subtypes = ['control', 'metopic', 'sagittal']
        visualise_manually_defined_landmarks(landmarks_pts_path=landmarks_path, data_path=synth_data_path,
                                             meshes_num=n_meshes_per_subtype, subtypes_lst=subtypes)
    elif use_case == 3:  # Give one landmarks file and one mesh
        vtp_mesh_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\patient_data\sagittal_patient_data_sept2023\1689340\pre\meshes\1689340_210702.000070_neck_cropped.vtp")
        obj_mesh_path = vtp_mesh_path.parent / (vtp_mesh_path.stem + '.obj')
        vtp_mesh = ReadImage(str(vtp_mesh_path.absolute()))
        landmarks_path = vtp_mesh_path.parent / 'manual_landmarks.xlsx'
        coordinates = load_landmark_points(landmarks_path)
        landmarks = place_landmarks_manually(mesh_vtp=vtp_mesh, landmark_coordinates=coordinates)
        landmarks_ply_path = export_landmarks(landmarks, vtp_mesh_path, 'manual', f'mesh_cropped_0')
        create_pv_plotter(mesh_path=obj_mesh_path, pred_landmarks_path=landmarks_ply_path)

    elif use_case == 4:
        case_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply\sagittal\sagittal_inst_038.ply")
        p = pv.Plotter()
        mesh = pv.read(str(case_path))
        p.add_mesh(mesh)
        p.add_text('{}'.format(case_path.name), position='upper_right', color='k')
        p.view_xy()
        p.show()
    else:  # 5
        landmark_names = ["TRAGION_RIGHT","SELLION","TRAGION_LEFT","EURYON_RIGHT","EURYON_LEFT","FRONTOTEMPORALE_RIGHT","FRONTOTEMPORALE_LEFT","VERTEX","NASION","GLABELLA","OPISTHOCRANION","GNATHION","STOMION","ZYGION_RIGHT","ZYGION_LEFT","GONION_RIGHT","GONION_LEFT","SUBNASALE","ENDOCANTHION_RIGHT","ENDOCANTHION_LEFT","EXOCANTHION_RIGHT","EXOCANTHION_LEFT","ALAR_RIGHT","ALAR_LEFT","NASALE_TIP","SUBLABIALE","UPPER_LIP"]
        mesh_dir_str_path = r"C:\Users\franz\Documents\work\projects\arp\data\patient_data\sagittal_patient_data_sept2023\1773993\pre"
        mesh_dir = Path(mesh_dir_str_path)
        obj_mesh_path = list((mesh_dir / 'meshes').glob('*_neck_cropped.obj'))[0]
        landmarks_ply_parent = obj_mesh_path.parent / 'predicted_landmarks_cropped_0_automatic_landmark_placement'
        landmarks_ply_path = list(landmarks_ply_parent.glob('*.ply'))[0]
        create_pv_plotter(mesh_path=obj_mesh_path, pred_landmarks_path=landmarks_ply_path, landmark_labels=landmark_names)
