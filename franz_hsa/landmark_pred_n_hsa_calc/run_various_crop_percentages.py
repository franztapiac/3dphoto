import numpy as np
import subprocess

# Define the range and step for your variable
start_value = 0
end_value = 0.6
step = 0.05

crop_percentages = np.arange(start_value, end_value + step, step)
crop_percentages = np.round(crop_percentages, decimals=2)
# Loop through the values and run the main script
for crop_percentage in crop_percentages:
    command = (
        f'python Analyze3DPhotogram.py '
        f'--input_filename "C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\sagittal\\1781297_20221104_NCH\\meshes\\1781297_20221104_NCH.000014.obj" '
        f'--age 250 --sex M --verbose --crop_image --crop_percentage {crop_percentage}'
    )
    subprocess.run(command, shell=True)
 # "C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\sagittal\\1781297_20221104_NCH\\meshes\\1781297_20221104_NCH.000014.obj"
 # age 250