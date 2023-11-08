import pandas as pd
import numpy as np


def load_landmark_points(landmarks_points_path):
    """
    Load the .xlsx file with the manually defined landmark points into a dictionary.
    :return: landmark_points; dict; format {'landmark name': point ID}
    """
    # Convert Excel into dict
    landmarks_df = pd.read_excel(landmarks_points_path)
    landmark_points = landmarks_df.set_index('landmark_name').to_dict()['point_id']

    # Remove missing landmarks
    landmarks_to_remove = []
    for landmark in landmark_points.keys():
        if np.isnan(landmark_points[landmark]):
            landmarks_to_remove.append(landmark)
    for landmark in landmarks_to_remove:
        del landmark_points[landmark]

    return landmark_points