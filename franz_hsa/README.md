# Implementation of the HSA index at the Erasmus MC
Franz A. Tapia Chaca

franz.tapia-chaca@outlook.com

## <u>HSA calculation</u>

### ``hsa_calculator.py``

### ``measure_hsa_pre_n_post_op.py``

### ``run_various_crop_percentages.py``

## <u>Landmark prediction evaluation</u>

Within this folder, there are 2 scripts:

### ``export_landmarks.py``

### ``visualise_landmarks.py``

![Example landmark visualisation](../diagrams/landmark_vis_example.png)

Generates a window that displays meshes with landmarks. The meshes can be those from the test set of a KDE model.
The landmarks can be those predicted with Elkhill's landmark prediction method.

Three functions are used to generate this functionality:
1. visualise_landmarks_per_mesh: creates the window displaying a mesh and its landmarks. Click 'X' for the next mesh. 
2. get_mesh_ids_per_subtype: gets mesh subtype and id for all meshes in a test set file (file has paths to mesh files). 
3. visualise_landmarks_per_model: receives user input for which model's meshes to display, and whether to display 
the control meshes. 


## <u>.ply to .vtp conversion</u>


### ``conversion-validate.py``

### ``ply_to_vtp_converter.py``


## Not a folder, others:


### ``get_file_names.py``


### ``test.py``

### ``texture_writer.py``