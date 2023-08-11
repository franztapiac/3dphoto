import os
from pathlib import Path
from Analyze3DPhotogram import PlaceLandmarks, ComputeHSAandRiskScore, ReadImage


def get_data_dir(device):
    if device == 'cpu':
        return Path('./franz-hsa/conversion-validation')
    elif device == 'cluster':
        return Path('/data/scratch/r092382/conversion-validation')


def test_conversion(device):

    data_dir = get_data_dir(device)

    for conversion_type_folder in data_dir.iterdir():               # for each paraview or python
        for file_path in conversion_type_folder.glob('*_cp.vtp'):       # load the files
            age = 100
            sex = 'M'
            verbose = True
            crop = False
            crop_percentage = 0

            mesh = ReadImage(str(file_path))
            landmarks, _ = PlaceLandmarks(mesh, crop=crop, verbose=verbose, crop_percentage=crop_percentage)
            riskScore, HSA_index = ComputeHSAandRiskScore(mesh, landmarks, age, sex, verbose=verbose)
            print(
                f'Results calculated from the image: {str(file_path)}\n\tCraniosynostosis Risk Score: {riskScore:0.2f}%\n\tHead Shape Anomaly Index: {HSA_index:0.2f}')


if __name__ == '__main__':
    curr_device = 'cpu'
    test_conversion(curr_device)

