import os
DATA_DIR = '../data/'
MODEL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../NormativePCAModel/')
print(str(MODEL_DIR))
CLASSIFIER_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../CraniosynostosisClassifier/')
print(str(CLASSIFIER_DIR))

CRANIOFACIAL_LANDMARKING_MODEL_PATH = os.path.join(DATA_DIR, 'CraniofacialLandmarkingModel.dat')
print(str(CRANIOFACIAL_LANDMARKING_MODEL_PATH))
CRANIOFACIAL_LANDMARKING_NOTEXTURE_MODEL_PATH = os.path.join(DATA_DIR, 'CraniofacialLandmarkingModel-notexture.dat')
print(str(CRANIOFACIAL_LANDMARKING_NOTEXTURE_MODEL_PATH))
GLABELLA_CRANIALBASE_LANDMARKS_PATH = os.path.join(DATA_DIR, 'landmarks_glabella_new.vtp')
print(str(GLABELLA_CRANIALBASE_LANDMARKS_PATH))
EURYON_CRANIALBASE_LANDMARKS_PATH = os.path.join(DATA_DIR, 'landmarks_full_templatespace.vtp')
print(str(EURYON_CRANIALBASE_LANDMARKS_PATH))