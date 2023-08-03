import pyvista as pv
# Load the .obj mesh
mesh = pv.read('0760831_20210625.000128.obj')
# Load the .jpg texture
texture = pv.read_texture('0760831_20210625.000128.jpg')
# Map the texture to the mesh
mesh.texture_map_to_sphere(inplace=True)
# Save the merged mesh with texture as a .vtp file
mesh.save('merged_mesh_with_texture.vtp')