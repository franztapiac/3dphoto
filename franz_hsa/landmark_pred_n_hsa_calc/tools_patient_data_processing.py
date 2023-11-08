import pandas as pd
import re


def get_patient_age_and_sex(db_path, patient_id, subtype_sample):
    """
    Collects the patient age and sex from the patient_information.xlsx.
    :param db_path: Path; to patient_information.xlsx.
    :param patient_id: str; of the integer patient id.
    :param subtype_sample: str; of format subtype_pre or subtype_post.
    :return: patient_age (in days) and patient_sex ('M' or 'F')
    """

    data_overview = pd.read_excel(db_path)

    # Identify rows with patient_id
    patient_rows = data_overview[data_overview['patient_id'] == int(patient_id)]

    # Get 'pre' or 'post' sample from subtype_sample
    pattern = r'_(.*$)'
    match = re.search(pattern, subtype_sample)
    sample = match.group(1)

    # Initialise returning variables
    patient_age = 0
    patient_sex = 'a'

    # Get patient age and sex for the right '', 'pre', or 'post' sample
    for _, row in patient_rows.iterrows():
        if row['operative_sample'] == sample or pd.isna(row['operative_sample']):
            patient_age = row['age_at_imaging_in_days']
            patient_sex = row['sex']

    return patient_age, patient_sex
