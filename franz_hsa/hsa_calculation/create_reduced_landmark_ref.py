from pathlib import Path
import sys
repo_dir_path = Path(r'C:\Users\franz\Documents\work\projects\arp\quantification-methods\hsa\3dphoto')
sys.path.append(str(repo_dir_path.absolute()))
from tools.DataSetGraph import ReadPolyData, WritePolyData
from tools.LandmarkingUtils import AddArraysToLandmarks
import vtk

full_template_landmarks_path = repo_dir_path / 'data/landmarks_full_templatespace.vtp'

full_template_landmarks = ReadPolyData(str(full_template_landmarks_path.absolute()))

landmarks_of_interest = ['TRAGION_RIGHT', 'TRAGION_LEFT', 'NASION']
# these names have to be ordered according to DefaultLandmarkNames() in LandmarkingUtils.py
# which have the same order as in the full_template_landmarks
# Thus, the landmarks object that I pass to ComputeHSAandRiskScore must also have the landmarks in this order

reduced_template_landmarks = vtk.vtkPolyData()
reduced_template_landmarks.SetPoints(vtk.vtkPoints())

for point_index in range(full_template_landmarks.GetNumberOfPoints()):
    landmark_name = full_template_landmarks.GetPointData().GetAbstractArray(1).GetValue(point_index)
    if landmark_name in landmarks_of_interest:
        landmark_coords = full_template_landmarks.GetPoint(point_index)
        print(f'The coordinates of the {landmark_name} in the full template are {landmark_coords}.')
        reduced_template_landmarks.GetPoints().InsertNextPoint(*landmark_coords)

landmarks_vtp = AddArraysToLandmarks(reduced_template_landmarks, landmarks_of_interest)

# Sanity check
for point in range(landmarks_vtp.GetNumberOfPoints()):
    new_landmark_name = landmarks_vtp.GetPointData().GetAbstractArray(1).GetValue(point)
    new_landmark_coords = landmarks_vtp.GetPoint(point)
    print(f'The coordinates of the {new_landmark_name} in the reduced template are {new_landmark_coords}.')

reduced_template_landmarks_path = full_template_landmarks_path.parent / 'landmarks_reduced_templatespace.vtp'
WritePolyData(landmarks_vtp, str(reduced_template_landmarks_path.absolute()))

