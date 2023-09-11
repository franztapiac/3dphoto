import json
import numpy as np
import re
from tools.LandmarkingUtils import AddArraysToLandmarks
import vtk


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
