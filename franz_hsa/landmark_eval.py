import json
import os
from pathlib import Path
import pyvista as pv
import re
from vtkmodules.util import numpy_support


def get_landmark_coordinates(landmarks_vtp):
    """Extract the landmark coordinates from a vtkPolyData object.

    Args:
        landmarks_vtp (vtkPolyData): The VTK PolyData object containing the landmarks.

    Returns:
        ndarray: A NumPy array with shape (n, 3) where each row contains the (x, y, z) coordinates of a landmark.
    """
    points = landmarks_vtp.GetPoints()
    dataArray = points.GetData()
    landmark_coordinates = numpy_support.vtk_to_numpy(dataArray)
    return landmark_coordinates


def export_landmarks(landmarks, mesh_file_path, time_now=''):
    """
    Export images of the landmarks placed on the mesh.
    :param landmarks: the vtk object with the predicted landmarks.
    :param mesh_file_path: the Path object to the file path of the mesh
    :param time_now: the datetime of when the whole experiment was begun
    """

    landmark_coordinates = get_landmark_coordinates(landmarks)

    landmark_ply = pv.PolyData(landmark_coordinates)
    landmark_ply_path = mesh_file_path.parent / ('predicted_landmarks_ply' + time_now) / (mesh_file_path.stem +
                                                                                          '_pred_landmarks.ply')
    if not os.path.exists(landmark_ply_path.parent):
        os.makedirs(landmark_ply_path.parent)

    landmark_ply.save(str(landmark_ply_path))


def manually_visualise_landmarks(meshes_to_visualise, vis_control):
    """
    Creates a PyVista Plotter visual of a mesh and its HSA-predicted landmarks.
    :param meshes_to_visualise: a dictionary with mesh subtypes and a list of mesh id numbers to visualise
    :param vis_control: a bool object for whether to visualise the control meshes with their landmarks
    """

    ply_synth_data_path = Path('./synth_data/ply')
    ply_landmarks_path = Path('./synth_data/vtp_python_ply_landmarks')

    if not vis_control:
        del meshes_to_visualise['control']

    for subtype in list(meshes_to_visualise.keys()):

        subtype_folder = ply_synth_data_path / subtype
        mesh_id_nums = meshes_to_visualise[subtype]
        landmarks_coordinates_dir = ply_landmarks_path / subtype

        for mesh_id_num in mesh_id_nums:
            zero_padded_id = str(mesh_id_num).zfill(3)
            mesh_file_path = list(subtype_folder.glob(f'*{zero_padded_id}_cp.ply'))[0]
            mesh_predicted_landmarks_path = list(landmarks_coordinates_dir.glob(f'*{zero_padded_id}_cp_pred_landmarks.ply'))[0]

            p = pv.Plotter()
            p.add_mesh(pv.read(str(mesh_file_path)))
            landmark_coordinates = pv.read(str(mesh_predicted_landmarks_path))
            p.add_points(landmark_coordinates, render_points_as_spheres=True, point_size=15, color='r')
            p.add_text('{}'.format(mesh_file_path.name), position='upper_right', color='k')
            p.view_xy()
            p.show()


def load_mesh_files_info(json_file_path):
    """
    Read the list of paths used in a test data set to create a dictionary of subtypes and mesh ids
    :param json_file_path: the Path object to the json file of the test dataset
    :return: a dictionary with subtypes as keys and a list of mesh id numbers as values
    """

    with open(json_file_path, "r") as file:
        json_data = file.read()
    paths_list = json.loads(json_data)

    mesh_id_per_subtype = dict()
    for i, path in enumerate(paths_list):
        pattern = r'\\([^\\]+)\\[^\\]+_(\d+)_'
        match = re.search(pattern, path)
        subtype = match.group(1)
        if subtype not in mesh_id_per_subtype:
            mesh_id_per_subtype[subtype] = []
        mesh_id = int(match.group(2))
        mesh_id_per_subtype[subtype].append(mesh_id)

    return mesh_id_per_subtype


def visualise_model_both_landmarks():
    """
    Run this to get a PyVista plotter showing a synthetic mesh with its predicted landmarks.
    The meshes shown are from the test dataset of the model trained with all subtypes.
    """
    model_both_test_data_path = Path('./synth_data/test_datasets/testdata_model_0108_both.json.json')
    dataset_meshes_ids = load_mesh_files_info(model_both_test_data_path)
    visualise_control = False
    manually_visualise_landmarks(dataset_meshes_ids, visualise_control)


def visualise_model_metopic_landmarks():
    """
    Run this to get a PyVista plotter showing a synthetic mesh with its predicted landmarks.
    The meshes shown are from the test dataset of the model trained only with control and metopic meshes.
    """
    model_both_test_data_path = Path('./synth_data/test_datasets/testdata_model_0108_metopicB.json.json')
    dataset_meshes_ids = load_mesh_files_info(model_both_test_data_path)
    visualise_control = False
    manually_visualise_landmarks(dataset_meshes_ids, visualise_control)


def visualise_model_sagittal_landmarks():
    """
    Run this to get a PyVista plotter showing a synthetic mesh with its predicted landmarks.
    The meshes shown are from the test dataset of the model trained only with control and sagittal meshes.
    """
    model_both_test_data_path = Path('./synth_data/test_datasets/testdata_model_0108_sagittalB.json.json')
    dataset_meshes_ids = load_mesh_files_info(model_both_test_data_path)
    visualise_control = False
    manually_visualise_landmarks(dataset_meshes_ids, visualise_control)


if __name__ == '__main__':
    visualise_model_both_landmarks()