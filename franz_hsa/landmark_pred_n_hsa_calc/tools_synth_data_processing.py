import json
import numpy as np
import re
import vtk


def default_landmark_names():
    return ["TRAGION_RIGHT", "SELLION", "TRAGION_LEFT", "EURYON_RIGHT", "EURYON_LEFT", "FRONTOTEMPORALE_RIGHT",
            "FRONTOTEMPORALE_LEFT", "VERTEX", "NASION", "GLABELLA", "OPISTHOCRANION", "GNATHION", "STOMION",
            "ZYGION_RIGHT", "ZYGION_LEFT", "GONION_RIGHT", "GONION_LEFT", "SUBNASALE", "ENDOCANTHION_RIGHT",
            "ENDOCANTHION_LEFT", "EXOCANTHION_RIGHT", "EXOCANTHION_LEFT", "ALAR_RIGHT", "ALAR_LEFT", "NASALE_TIP",
            "SUBLABIALE", "UPPER_LIP"]


def add_arrays_to_landmarks(landmarks, landmark_names=None):
    defaultColors = [
        [255, 0, 0],  # r
        [0, 255, 0],  # g
        [0, 0, 255],  # b
        [255, 0, 255],  # m
        [0, 255, 255],  # c
        [255, 255, 0]  # y
    ]

    num_landmarks = landmarks.GetNumberOfPoints()
    colorArray = vtk.vtkFloatArray()
    colorArray.SetName('Color')
    colorArray.SetNumberOfComponents(3)
    for x in range(num_landmarks):
        color = defaultColors[x % len(defaultColors)]
        colorArray.InsertNextTuple3(color[0], color[1], color[2])
    landmarks.GetPointData().AddArray(colorArray)

    nameArray = vtk.vtkStringArray()
    nameArray.SetName("LandmarkName")
    if landmark_names is None:
        landmark_names = default_landmark_names()
    if len(landmark_names) != num_landmarks:
        print('More landmarks in data than names specified. Leaving names blank for now...')
        landmark_names = [f'Landmark{x}' for x in range(num_landmarks)]
    for name in landmark_names:
        nameArray.InsertNextValue(name)
    landmarks.GetPointData().AddArray(nameArray)
    return landmarks


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

    coords_lst = list(landmark_coords_dict.values())
    landmark_coords = np.vstack(coords_lst)

    manual_landmarks = vtk.vtkPolyData()
    manual_landmarks.SetPoints(vtk.vtkPoints())
    for p in range(len(landmark_coords)):
        p_coords = tuple(landmark_coords[p, :])
        manual_landmarks.GetPoints().InsertNextPoint(*p_coords)

    landmark_names = list(landmark_coordinates.keys())  # must be defined in the right relative order
    landmarks_vtp = add_arrays_to_landmarks(manual_landmarks, landmark_names)

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
