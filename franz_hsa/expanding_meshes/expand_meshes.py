import os
from pathlib import Path
import pyvista as pv


def write_ply_file_pv(mesh, savepath):
    points = mesh.points
    faces = mesh.faces
    numVertices = mesh.n_points
    numFaces = mesh.n_faces
    faces = faces.reshape((numFaces, 4))
    with open(savepath, 'w+') as fileOut:
        # Writes ply header
        fileOut.write("ply\n")
        fileOut.write("format ascii 1.0\n")
        fileOut.write("comment VCGLIB generated\n")
        fileOut.write("element vertex " + str(numVertices) + "\n")
        fileOut.write("property float x\n")
        fileOut.write("property float y\n")
        fileOut.write("property float z\n")

        fileOut.write("element face " + str(numFaces) + "\n")
        fileOut.write("property list uchar int vertex_indices\n")
        fileOut.write("end_header\n")

        for i in range(numVertices):
            # writes "x y z" of current vertex
            fileOut.write(str(points[i,0]) + " " + str(points[i,1]) + " " + str(points[i,2]) + "255\n")

        # Writes faces
        for f in faces:
            #print(f)
            # WARNING: Subtracts 1 to vertex ID because PLY indices start at 0 and OBJ at 1
            fileOut.write("3 " + str(f[1]) + " " + str(f[2]) + " " + str(f[3]) + "\n")


def create_dir(new_dir_path: Path):
    """
    Create a new directory with the input path.

    :param new_dir_path: path to the new directory to create.
    :type new_dir_path: Path
    """
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)


def expand_meshes(meshes_dir_path: Path, subtypes_to_expand: list, template_path: Path, template_ref: str):
    """
    Expand the meshes from the input meshes path to the volume of the template, and export the expanded meshes to a new
    directory.

    :param meshes_dir_path: path to the directory where the meshes are stored within subtype subdirectories.
    :type meshes_dir_path: Path
    :param subtypes_to_expand: string names of the subtype (directories) to include in the expansion, e.g. ['metopic']
    :type subtypes_to_expand: list
    :param template_path: path to the template mesh to expanded meshes to.
    :type template_path: Path
    :param template_ref: a reference or ID name for the template to annotate the new created directory.
    :type template_ref: str
    """
    template_mesh = pv.read(str(template_path))
    target_volume = template_mesh.volume
    print(f'\ntarget_volume = {target_volume:.0f}\n')

    expanded_meshes_dir_path = meshes_dir_path.parent / (meshes_dir_path.stem + f'_expanded_to_{template_ref}' )
    create_dir(expanded_meshes_dir_path)

    for subtype_dir in meshes_dir_path.iterdir():
        if subtype_dir.name not in subtypes_to_expand:
            continue
        expanded_subtype_dir = expanded_meshes_dir_path / subtype_dir.stem
        create_dir(expanded_subtype_dir)
        for mesh_ply_file_path in subtype_dir.glob('*.ply'):
            print(f'Working with mesh {mesh_ply_file_path.name}')
            mesh = pv.read(str(mesh_ply_file_path))
            print(f'original_mesh_volume = {mesh.volume:.0f}')

            scaling_factor = (target_volume/mesh.volume)**(1/3)
            mesh.points *= scaling_factor
            print(f'scaled_mesh_volume = {mesh.volume:.0f}')

            new_scaled_ply_path = expanded_subtype_dir / mesh_ply_file_path.name
            write_ply_file_pv(mesh, str(new_scaled_ply_path))
            print(f'Exported expanded mesh to {str(new_scaled_ply_path)}\n')


if __name__ == "__main__":

    path_to_template = Path(r"C:\Users\franz\Documents\work\projects\arp\data\patient_data\1716156\pre\meshes\for_hsa\1716156_20210716.000026_neck_cropped.obj")
    template_id = 'pat_sag_1716156_pre'
    path_to_meshes_dir = Path(r"C:\Users\franz\Documents\work\projects\arp\data\synthetic_data\synthetic_data_original_untextured_unclipped_ply")
    subtypes = ['metopic', 'sagittal']
    expand_meshes(meshes_dir_path=path_to_meshes_dir, subtypes_to_expand=subtypes,
                  template_path=path_to_template, template_ref=template_id)
