import os
from __init__ import MODEL_DIR
from pathlib import Path
import shelve

atlasPath = os.path.join(MODEL_DIR, 'PCAModel')
print(str(atlasPath))
print(str(Path(atlasPath).absolute()))
with shelve.open(atlasPath, 'r') as atlasInformation:
    indices = atlasInformation['indices']
    model = atlasInformation['model']