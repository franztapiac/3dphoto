import os
from pathlib import Path

folder_path = Path("C:\\Users\\franz\\Documents\\work\\projects\\arp\\data\\pre-and-post")

items = os.listdir(folder_path)
subdirectories = [item for item in items if os.path.isdir(os.path.join(folder_path, item))]
for subdir in subdirectories:
    print(subdir)
