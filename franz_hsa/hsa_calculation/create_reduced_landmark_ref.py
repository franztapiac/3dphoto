import datetime
from git import Repo
import os
from pathlib import Path
import sys
current_file_str_path = os.path.abspath(__file__)
repo_root_str_path = Repo(current_file_str_path, search_parent_directories=True).git.rev_parse("--show-toplevel")
sys.path.append(repo_root_str_path)
from tools.DataSetGraph import ReadPolyData, WritePolyData
from tools.LandmarkingUtils import AddArraysToLandmarks
import vtk

repo_dir_path = Path(repo_root_str_path)
full_landmarks_path = repo_dir_path / 'data/landmarks_full_templatespace.vtp'


def load_full_template():
    """
    Loads the full landmark template from its globally defined path.

    Returns
    -------
    The full landmark template in PolyData and summarised dictionary with format { 'landmark name': (x, y, z) coords }.
    """

    full_landmarks_polydata = ReadPolyData(str(full_landmarks_path.absolute()))

    full_landmarks_dict = dict()
    print('\nThe landmarks in the full template are ordered as:')
    for landmark_index in range(full_landmarks_polydata.GetNumberOfPoints()):
        landmark_name = full_landmarks_polydata.GetPointData().GetAbstractArray(1).GetValue(landmark_index)
        print(f'{landmark_index}: {landmark_name}')
        landmark_coords = full_landmarks_polydata.GetPoint(landmark_index)
        full_landmarks_dict[landmark_name] = landmark_coords

    return full_landmarks_polydata, full_landmarks_dict


def get_reduced_landmarks_n_coords(full_landmarks_n_coords, landmarks_of_int):
    """
    Collects the landmark names and coordinates from the full landmark template according to your landmarks of interest.

    Parameters
    ----------
    full_landmarks_n_coords a dictionary with format { 'landmark name': (x, y, z) coords }.
    landmarks_of_int        a list with the names of your landmarks of interest in any order.

    Returns
    -------
    a dictionary with format { 'landmark name': (x, y, z) coords } for the reduced landmark template.
    """

    reduced_landmarks_n_coords = dict()
    for landmark in full_landmarks_n_coords.keys():
        if landmark in landmarks_of_int:
            reduced_landmarks_n_coords[landmark] = full_landmarks_n_coords[landmark]

    return reduced_landmarks_n_coords


def create_reduced_landmarks_polydata(reduced_landmarks_n_coords):
    """
    Given a dictionary with landmarks of interest and their coordinates, generates a PolyData landmarks object.

    Parameters
    ----------
    reduced_landmarks_n_coords  a dictionary with format { 'landmark name': (x, y, z) coords }

    Returns
    -------
    a PolyData object for the reduced landmark template.
    """

    reduced_template_landmarks = vtk.vtkPolyData()
    reduced_template_landmarks.SetPoints(vtk.vtkPoints())

    landmarks_of_interest = list(reduced_landmarks_n_coords.keys())
    for landmark in landmarks_of_interest:
        landmark_coords = reduced_landmarks_n_coords[landmark]
        reduced_template_landmarks.GetPoints().InsertNextPoint(*landmark_coords)

    landmarks_vtp = AddArraysToLandmarks(reduced_template_landmarks, landmarks_of_interest)

    return landmarks_vtp


def get_landmarks_n_coords(landmarks_polydata):
    """
    Summarises the landmark PolyData into a dictionary, which includes the landmark names, indices, and coordinates.

    Parameters
    ----------
    landmarks_polydata  a PolyData object for either the full or reduced landmark template.

    Returns
    -------
    a dictionary with formation {'landmark name': {'index': i, 'coords': (x, y, z)} }, where i is the 0-indexed index
    of the landmark within the full or reduced PolyData landmark object.
    """

    landmarks_n_coords = dict()
    for landmark_index in range(landmarks_polydata.GetNumberOfPoints()):
        landmark_name = landmarks_polydata.GetPointData().GetAbstractArray(1).GetValue(landmark_index)
        landmarks_n_coords[landmark_name] = dict()
        landmarks_n_coords[landmark_name]['index'] = landmark_index

        landmark_coords = landmarks_polydata.GetPoint(landmark_index)
        landmarks_n_coords[landmark_name]['coords'] = landmark_coords

    return landmarks_n_coords


def sanity_check(full_landmarks_polydata, reduced_landmarks_polydata):
    """
    Prints the relative order and coordinates of the landmarks in the reduced template, together with the landmark
    indices and coordinates of the same landmarks in the full template.

    Parameters
    ----------
    full_landmarks_polydata     a PolyData object of the full template landmarks.
    reduced_landmarks_polydata  the PolyData object generated for the reduced template landmarks.
    """

    reduced_landmarks_n_coords = get_landmarks_n_coords(reduced_landmarks_polydata)
    full_landmarks_n_coords = get_landmarks_n_coords(full_landmarks_polydata)

    print(f'\nThe landmarks in the reduced template are ordered as:')
    print('(Note: the left-most index corresponds to the landmark index in the full landmarks template.)')
    for lndmk in reduced_landmarks_n_coords.keys():
        full_lndmk_index = full_landmarks_n_coords[lndmk]['index']
        red_lndmk_index = reduced_landmarks_n_coords[lndmk]['index']
        print(f'{full_lndmk_index}: {lndmk}, with index {red_lndmk_index}')
    print('\n')

    for landmark in reduced_landmarks_n_coords.keys():
        full_landmark_coords = full_landmarks_n_coords[landmark]['coords']
        reduced_landmark_coords = reduced_landmarks_n_coords[landmark]['coords']
        print(f'The coordinates of the {landmark} \n'
              f'in the full template are        {full_landmark_coords}, and those\n'
              f'in the reduced template are     {reduced_landmark_coords}.\n')


def export_reduced_landmarks(reduced_landmarks_polydata, unique_name=False):
    """
    Exports the reduced landmarks PolyData object as a .vtp file.

    Parameters
    ----------
    reduced_landmarks_polydata  the PolyData object with the reduced landmark names and coordinates.
    unique_name                 a bool for whether to add a mmdd (month date) stamp onto the reduced landmark file name.

    """

    if unique_name:
        reduction_date = datetime.date.today().strftime("%m%d")
        reduced_template_landmarks_path = full_landmarks_path.parent / f'{reduction_date}_landmarks_reduced_templatespace.vtp'
    else:
        reduced_template_landmarks_path = full_landmarks_path.parent / 'landmarks_reduced_templatespace.vtp'

    WritePolyData(reduced_landmarks_polydata, str(reduced_template_landmarks_path.absolute()))


def generate_reduced_landmarks_template(landmarks_of_interest, unique_name):
    """
    Generates a reduced landmarks PolyData object from the full template according to your landmarks of interest.

    Parameters
    ----------
    landmarks_of_interest   a list of your landmarks of interest with the legal landmark names.
    unique_name             a bool for whether to add a mmdd (month date) stamp onto the reduced landmark file name.

    """

    full_landmarks_polydata, full_landmarks_n_coords = load_full_template()
    reduced_landmarks_n_coords = get_reduced_landmarks_n_coords(full_landmarks_n_coords=full_landmarks_n_coords,
                                                                landmarks_of_int=landmarks_of_interest)
    reduced_landmarks_polydata = create_reduced_landmarks_polydata(reduced_landmarks_n_coords)
    sanity_check(full_landmarks_polydata, reduced_landmarks_polydata)
    export_reduced_landmarks(reduced_landmarks_polydata, unique_name=unique_name)


if __name__ == '__main__':
    my_landmarks = ['NASION', 'TRAGION_LEFT', 'TRAGION_RIGHT']  # use the landmark names, can be in any order
    generate_reduced_landmarks_template(landmarks_of_interest=my_landmarks, unique_name=True)
