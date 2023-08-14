# 3dphoto landmarking
This is a repository for [Geometric learning and statistical modeling for surgical outcomes evaluation in craniosynostosis using 3D photogrammetry.](https://doi.org/10.1016/j.cmpb.2023.107689).
This repository contains two models as described in the manuscript.
1. Automated craniofacial landmarking model, stored as a [TorchScript](https://pytorch.org/docs/stable/jit.html) jit file and found in ``data/CraniofacialLandmarkingModel.dat``. 
2. Normative model of head surface development, stored as a [Shelve](https://docs.python.org/3/library/shelve.html) and found in ``NormativePCAModel/PCAModel.dat``


![Network diagram as found in published manuscript](/diagrams/AnalysisDiagram.jpg)

## Dependencies:
Dependencies for this model can be found in the Requirements.txt file. 
*Once Python 3.9 is installed, install the requirements with*:

```python
python -m pip install -r Requirements.txt
```


## Using the code
To calculate the Craniosynostosis Risk Score and the Head Shape Anomaly Index for a given 3D photogram, use the following code:
```python
python Analyze3DPhotogram.py --input_filename "/path/to/input/3Dphotogram.vtp" --age AGE_OF_PATIENT_IN_DAYS --sex M_FOR_MALE_F_FOR_FEMALE
```

Due to data privacy agreements, we are not able to share any example data. To run this code, you will need an image in VTK [PolyData format (.vtp)](https://vtk.org/doc/nightly/html/classvtkPolyData.html) containing the entire head and face that is cropped around the mid-neck. If your data is not cropped and includes the shoulders of the patient, you should use the cropping functionality by enabling the *--crop_data* flag. This model was trained on data collected using a [3DMD-Head system](https://3dmd.com/products/).

### Quick summary
**Input**: VTK PolyData file.

**Output**: Craniosynostosis risk score (0%-100%) and Head Shape Anomaly Index.

## Troubleshooting
- Example code will not run:
    - Be sure you have not altered the "CraniofacialLandmarkingModel.dat" file in any way.
    - Be sure that you are trying to load a valid VTK PolyData file.
    - Be sure that you have installed the required dependencies as noted in the **Dependencies** section.
- Landmarks are not placed correctly:
    - To evaluate the landmark accuracy, run the testing script with the following:

    ```python
    python TestLandmarkingModel --input_filename "/path/to/input/3Dphotogram.vtp"
    ```
    This script will save the landmarks and photogram (including any cropping) to folder containing your input photogram. If the landmarks do not look accurate, adjust the cropping flag with *--crop_data*. If the data is not properly cropped, adjust the percentage option using the *--crop_percentage* flag.
    - If the problem persists, your data may be something we have not seen before! If possible, please email the corresponding author (connor.2.elkhill@cuanschutz.edu) so that we may evaluate.
- Photogram processing takes a long time:
    - You can profile each step of this analysis using the following command:
    ```python
    python ProfileAnalysisPipeline.py --input_filename "/path/to/input/3Dphotogram.vtp" --age AGE_OF_PATIENT_IN_DAYS --sex M_FOR_MALE_F_FOR_FEMALE
    ```

Any other questions? Please email the corresponding author Connor Elkhill at connor.2.elkhill@cuanschutz.edu
