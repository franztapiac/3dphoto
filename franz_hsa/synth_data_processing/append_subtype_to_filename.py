from pathlib import Path
import pyvista as pv


def append_subtype_to_filename(data_dir_path, file_extension):
    """
    Takes in a parent directory, within which are subdirectories with mesh files (likely .ply).
    Reads the meshes and exports after appending the subtype name to the front of the mesh filename.
    :param data_dir_path: a Path object to the parent directory of the subtype data.
    :param file_extension: a string with format '.***', wherein '.' is needed, and *** is the extension abbreviation.
    """
    for subtype_dir in data_dir_path.iterdir():
        for mesh_file_path in subtype_dir.glob(f'*{file_extension}'):
            mesh = pv.read(str(mesh_file_path.absolute()))
            new_mesh_filename = f'{subtype_dir.name}_{mesh_file_path.name}'
            new_mesh_path = mesh_file_path.parent / new_mesh_filename
            mesh.save(str(new_mesh_path.absolute()))


if __name__ == '__main__':
    data_path = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply")
    extension = '.ply'
    append_subtype_to_filename(data_path, extension)
