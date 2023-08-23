import pandas as pd

def load_hsa_scores(hsa_indices_xlsx_path):
    """
    Loads the hsa scores from the previously exported .xlsx file of hsa scores.
    :param hsa_indices_xlsx_path: a Path object to the .xlsx file containing the hsa data.
    :return: a dictionary with keys as subtypes, inner keys as mesh id numbers, and HSA indices as values.
    """

    hsa_indices_data = pd.read_excel(hsa_indices_xlsx_path, header=None)

    header = hsa_indices_data.iloc[0]
    subtypes_df = header[header.notna()]
    subtypes = subtypes_df.values.tolist()
    subtypes_cols = subtypes_df.index.tolist()

    hsa_scores = dict()

    for i, subtype in enumerate(subtypes):
        hsa_scores[subtype] = dict()
        mesh_ids = hsa_indices_data.iloc[2:, subtypes_cols[i]]
        mesh_ids = mesh_ids[mesh_ids.notna()].tolist()
        subtype_data = hsa_indices_data.iloc[2:, subtypes_cols[i]+1]
        subtype_data = subtype_data[subtype_data.notna()].tolist()
        subtype_data = [float(item) for item in subtype_data]
        for j, mesh_id in enumerate(mesh_ids):
            hsa_scores[subtype][mesh_id] = subtype_data[j]

    return hsa_scores