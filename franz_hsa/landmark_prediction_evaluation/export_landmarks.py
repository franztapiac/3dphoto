import os
from pathlib import Path
import pyvista as pv
from vtkmodules.util import numpy_support


def get_landmark_coordinates(landmarks_vtp):
    """Extract the landmark coordinates from a vtkPolyData object.

    Args:
        landmarks_vtp (vtkPolyData): The VTK PolyData object containing the landmarks.

    Returns:
        ndarray: A NumPy array with shape (n, 3) where each row contains the (x, y, z) coordinates of a landmark.
    """
    points = landmarks_vtp.GetPoints()
    data_array = points.GetData()
    landmark_coordinates = numpy_support.vtk_to_numpy(data_array)
    return landmark_coordinates


def export_landmarks(landmarks, mesh_file_path: Path, landmark_def_details='', ):
    """
    Export images of the landmarks placed on the mesh.
    :param landmarks: the vtk object with the predicted landmarks.
    :param mesh_file_path: the Path object to the file path of the mesh
    :param landmark_def_details: a string for specifically defining the landmark storage directory according to the exp.
    """

    landmark_coordinates = get_landmark_coordinates(landmarks)

    landmark_ply = pv.PolyData(landmark_coordinates)
    landmark_ply_path = mesh_file_path.parent / ('predicted_landmarks_' + landmark_def_details) / (mesh_file_path.stem +
                                                                                                   '_landmarks.ply')
    if not os.path.exists(landmark_ply_path.parent):
        os.makedirs(landmark_ply_path.parent)
    print(f'Exporting the landmarks to {str(landmark_ply_path.absolute())}.')
    landmark_ply.save(str(landmark_ply_path))
