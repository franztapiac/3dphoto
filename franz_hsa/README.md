# Implementation of the HSA index at the Erasmus MC
Franz A. Tapia Chaca

franz.tapia-chaca@outlook.com

## <u>Appending texture to synthetic meshes</u>

Within this folder, there is 1 script:

### 1. ``demo_texture.py``

With this script, we can load synthetic meshes published by Matthias Schaufelberger et al. 
([publication](https://www.mdpi.com/2075-4418/12/7/1516)) and a texture_model.h5 to apply textures
to the synthetic meshes.

Input: a directory with untextured, synthetic meshes in .vtp format.

Output: a new directory with textured versions of the synthetic meshes, also in .vtp format.

## <u>HSA calculation</u>

Within this folder, there are 3 scripts:

### 1. ``hsa_calculator_synth_meshes.py``

### 2. ``hsa_calculator_patient_pre_n_post_op.py``

### 3. ``run_various_crop_percentages.py``

## <u>Landmark prediction evaluation</u>

Within this folder, there are 2 scripts:

### 1. ``export_landmarks.py``

### 2. ``visualise_landmarks.py``

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

### ``paraview_ply_to_vtp_converter.py``

This is a script that should be executed from the ParaView Python Script Editor.
If you try to execute it from your Python IDE, you may experience errors, even if you install paraview with pip.
ParaView requires its own environment called paraview python (which is installed within the software), 
and understanding how to establish paraview python into your separate python environment is complicated.

To execute this script from the ParaView Python Script Editor, only edit the ply_data_path and 
the vtp_data_path variables.
The ply_data_path should point to a directory with subtypes as subdirectories. 
The .ply meshes should be within those subdirectories
The vtp_data_path should have a similar directory structure, and be empty.

For each mesh of each subtype in ply_data_path, the script will automatically load the .ply mesh and 
export it as .vtp.

Download ParaView from [here](https://www.paraview.org/download/).

To access the ParaView Python Script Editor: Tools / Python Script Editor. Load this script for executing.
Then click: File / Run to execute the script.


### ``ply_to_vtp_converter.py``


## Not a folder, others:


### ``get_file_names.py``


### ``test.py``

### ``texture_writer.py``