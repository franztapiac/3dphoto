# Implementation of the HSA index at the Erasmus MC
Franz A. Tapia Chaca

franz.tapia-chaca@outlook.com

## <u>Content</u>
Franz's work with the HSA index spanned 4 categories:
1. Appending RGB texture to synthetic meshes
2. Expanding meshes
3. Calculating the HSA on synthetic and patient meshes
4. Evaluating the landmarking prediction
5. Converting mesh files from .ply to .vtp format

Each category has its own subdirectory, and how the corresponding scripts work is 
explained below.

## <u>1) Appending RGB texture to synthetic meshes</u>

Within this folder, there is 1 script:

### a) ``texture_generator.py``

![Addition of texture to synthetic mesh](diagrams/texture_writing.png)

With this script, we can load the synthetic meshes (constituted by 45,081 points) 
and the texture_model.h5 published by Matthias Schaufelberger et al. 
([publication](https://www.mdpi.com/2075-4418/12/7/1516)) to apply unique textures to those meshes.

Given three paths (the path to the texture model, untextured data directory, and the export directory), 
the script works by:
1. Loading the texture model from texture_model.h5.
And then for each mesh:
2. Getting its points and cells,
3. Creating a .vtp mesh object,
4. Generating a texture for the mesh from the PCA model,
5. Writing the texture onto the .vtp object,
6. Creating a directory for exporting the .vtp mesh, and
7. Exporting the .vtp mesh in the export directory.

To run the script, define the three paths at the main call of the script.

## <u>2) Expanding meshes</u>

### a) ``expand_meshes.py``

**Purpose:** Expand meshes from a directory (stored in subtype subdirectories)
to match the volume of a template mesh.

Within the main module, define four things. See their definitions in the docstring of the 
``expand_meshes()`` function.
1. ``path_to_template``
2. ``template_id``
3. ``path_to_meshes_dir``
4. ``subtypes``

## <u>3) HSA calculation</u>

Within this folder, there are 3 scripts, and one Excel file:

### 1. ``create_reduced_landmark_ref.py``

This script loads the existing landmark reference with 27 landmarks, collects the 
names and coordinates of the landmarks of interest, and exports a reduced landmarks
polydata object with the names and coordinates of the landmarks of interest.

Note that the landmarks in the full or reduced template MUST follow this relative
order:
``["TRAGION_RIGHT","SELLION","TRAGION_LEFT","EURYON_RIGHT","EURYON_LEFT","FRONTOTEMPORALE_RIGHT","FRONTOTEMPORALE_LEFT","VERTEX","NASION","GLABELLA","OPISTHOCRANION","GNATHION","STOMION","ZYGION_RIGHT","ZYGION_LEFT","GONION_RIGHT","GONION_LEFT","SUBNASALE","ENDOCANTHION_RIGHT","ENDOCANTHION_LEFT","EXOCANTHION_RIGHT","EXOCANTHION_LEFT","ALAR_RIGHT","ALAR_LEFT","NASALE_TIP","SUBLABIALE","UPPER_LIP"]``
This is the relative order that the 27 points in the landmark reference object follow, 
and PlaceLandmarks() (within Analyse3DPhotogram.py) predicts a landmarks object with
this order.

This order must be kept, as within the function RegisterPatientToTemplate()
(in tools/PhotoAnalysisTools.py), the (x, y, z) coordinates of each landmark 
are collected from both the predicted and template landmark object, one landmark 
at a time. Thus, a pair collected (x, y, z) coordinates must correspond to the same
landmark. These collected landmark coordinates are then used to register the patient sample
to the template.

Thus, if we are interested to get the nasion, and left and right tragion, 
we must reduce the template landmarks with the relative order that these landmarks
originally appear with. This is ensured by the get_reduced_landmarks_n_coords() function
of this script herein.

For example, if we request for the landmarks
``['NASION', 'TRAGION_LEFT', 'TRAGION_RIGHT']``, we get the following output:

![Landmark reduction example](diagrams/landmark_reduction.png)

After creating a reduced landmark template, we can check it:

![Checking landmark reduction](diagrams/landmark_reduction_check.png)

Finally, to use the reduced landmark template, it must be defined in ``__init__.py``.

### ``hsa_execution_parameters.xlsx``
This Excel file contains a set of defined parameters to execute within 
``hsa_calculator_synth_meshes.py``. 

<u>Be sure NOT TO delete or change any rows!</u>
While these parameters are also saved with the exported .hsa file, they are only 
saved if HSA files are exported (currently, 28 Aug 2023), not if only landmarks
are exported. Thus, this document serves as a log of HSA executions for either 
landmark exporting or hsa prediction with predicted or automatic landmarks. Also, 
if you edit one exp_data_path value, that row won't be functional on someone else's
directory. If you don't want to show your directory on this publicly shared Excel file
(through GitHub), delete the exp_data_path value before committing.

The contents of the Excel file are as follows. Note that within 
``hsa_calculator_synth_meshes.py``, the Excel files is turned into a dict. 
Thus, the resulting keys are:
1. hsa_exp_index: an integer ID for the HSA experiment. This is a required input in 
__main__ of ``hsa_calculator_synth_meshes.py``.
2. data_type: a string for 'patient' or 'synthetic' data.
3. sub_data_type: a string. 'downsampled' (synthetic original data processed by Tareq) or 'original'
   (the synthetic Version V2 data of [Schaufelberger](https://zenodo.org/record/6390158)) for
synthetic data. 'sagittal', 'metopic', or 'pre_n_post_op' for patient data.
4. with_texture: a bool for whether the data has texture or not.
5. exp_data_path: an absolute path to the data directory within your terminal. This data directory
must be a parent directory of subtype subdirectories, within which lie the meshes. See below
   (Synthetic data processing: ``append_subtype_to_filname.py`` for how this parent directory
ought to be structured).
6. file_ending: a string for the rest of the filename (including extension) after 'subtype_inst_abc'.
Thus, if the filename is control_inst_001_cp.vtp, then file_ending is '_cp.ply', and for 
control_inst_001.vtp, the file_ending is '.vtp'.
7. age: the age of the patient represented by the mesh, in days.
8. sex: a character for 'M' or 'F'.
9. crop: a bool for whether to crop the mesh from the bottom.
10. crop_percentage: a percentage amount with which to crop the mesh from the bottom. 
11. landmark_placement: a string, 'manual' or 'automatic', determining whether the landmarks 
defined in manual_landmarks are placed, or automatically generated by predicting with Elkhill's
landmark prediction model.
12. manual_landmarks
13. export_landmarks
14. calculate_hsa
15. verbose



### 1. ``landmark_pred_n_hsa_calc.py``

This is the central script for landmark prediction and HSA index calculation
for either synthetic or patient data. Functions for processing either type of 
data is imported from ``tools_synth_data_processing.py`` or 
``tools_patient_data_processing.py``. The parameters for hsa calculation are
defined in ``hsa_execution_parameters.xlsx``.


### 2. ``hsa_calculator_patient_pre_n_post_op.py``



### 3. ``run_various_crop_percentages.py``

## <u>Landmark evaluation</u>

Within this folder, there are 2 scripts:

### 1. ``export_landmarks.py``

Holds functions for exporting a .vtp landmarks object as a .ply landmarks file.

### 2. ``visualise_landmarks.py``

This script has two options, which can be accessed by ``use_case = 1`` or ``use_case = 2``, respectively.:
1. Visualisation of landmarks predicted by Connor's landmark prediction.

![Example landmark visualisation](diagrams/landmark_vis_example.png)

Generates a window that displays meshes with landmarks. The meshes can be those from the test set of a KDE model.
The landmarks can be those predicted with Elkhill's landmark prediction method.

2. Visualisation of landmarks manually defined by point IDs from synthetic meshes.

![Landmark annotation](diagrams/landmark_annotation.png)







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


## Synthetic data processing

### ``append_subtype_to_filename.py``
![Append subtype to filename](diagrams/append_subtype_to_filename.png)

See docstring in code for explanation.


## Not a folder, others:


### ``get_file_names.py``


### ``test.py``

### ``texture_writer.py``