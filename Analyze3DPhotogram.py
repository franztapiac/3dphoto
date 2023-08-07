from tools.DataSetGraph import ReadPolyData, WritePolyData, LoadOBJFile
import pdb
from os import path
import argparse
from tools.LandmarkingUtils import RunInference
from tools.PhotoAnalysisTools import AlignPatientToTemplate, GenerateSphericalMapOfData, ComputeFromSphericalImage

def ReadImage(imagefilename):
    if imagefilename.endswith('.obj'):
        image = LoadOBJFile(imagefilename)
    else:
        image = ReadPolyData(imagefilename)
    return image

def PlaceLandmarks(image, crop=True, verbose = True, crop_percentage = 0.4):
    '''
    Inputs:
        data_filename: String pointing to the 3D photogram
        crop: Option to crop the 3D photogram if the image includes shoulders, etc.
            Image must be close cropped around the neck!
    '''
    #VTK xml reader
    if verbose:
        print('Placing craniofacial landmarks...')
    #run the inference
    landmarks = RunInference(image, crop=crop, crop_percentage = crop_percentage)
    return landmarks, image

def ComputeHSAandRiskScore(image, landmarks, age, sex, verbose = True):
    '''
    Inputs:
        image: vtk polydata of the 3D photogram
        landmarks: landmarks generated by PlaceLandmarks
        age: age of patient in days
        sex: 0 for female, 1 for male
    '''
    #now, compute the HSA index and risk score!
    if verbose:
        print('Aligning image to template...')
    output_mesh, transform = AlignPatientToTemplate(image, landmarks)
    if verbose:
        print('Generating spherical image...')
    spherical_image = GenerateSphericalMapOfData(output_mesh, transform)
    if verbose:
        print('Computing risk score and HSA index...')
    riskScore, HSA_index = ComputeFromSphericalImage(spherical_image, age, sex)
    return riskScore, HSA_index

def ValidVTP(param):
    _, ext = path.splitext(param)
    if (ext.lower() not in ('.vtp','.obj','.vtk')) or not (path.isfile(param)):
        raise argparse.ArgumentTypeError('File must be a valid VTK PolyData file (.vtp) or OBJ file (.obj)')
    return param

def ConstructArguments():
    parser = argparse.ArgumentParser(description='Process 3D photogram')
    ## Required arguments
    parser.add_argument('--input_filename', metavar = 'input_filename', required = True, type = ValidVTP,
        help='Input data path')

    parser.add_argument('--age', required = True, type = float, metavar = 'age',
        help='Age of the patient in days.')

    parser.add_argument('--sex', required = True, type = str, metavar = 'sex', choices = ['M','F'], 
        help='Sex of the patient (F is female, M is male).')

    parser.add_argument('--verbose', action='store_true', help='Print out information during the processing steps.' )

    parser.add_argument('--crop_image',action='store_true', help = 'Option to crop the data to ensure the shoulders are not included in the photogram.')
    parser.add_argument('--crop_percentage',action = 'store',default=0.4, type = float,
                        help = 'Percentage of the image to crop out. Adjust this parameter between 0-1 to control cropping amount.')
    return parser

def ParseArguments():
    parser = ConstructArguments()
    return parser.parse_args()

if __name__ == "__main__":
    #parse the arguments, python automatically takes the system args
    args = ParseArguments()
    #first, let's start with the landmarks
    image = ReadImage(args.input_filename)
    landmarks, image = PlaceLandmarks(image, crop=args.crop_image, verbose=args.verbose, crop_percentage = args.crop_percentage)
    #now the metrics!
    riskScore, HSA_index = ComputeHSAandRiskScore(image, landmarks, args.age, args.sex, verbose=args.verbose)
    print(f'Results calculated from the image: {args.input_filename}\n\tCraniosynostosis Risk Score: {riskScore:0.2f}%\n\tHead Shape Anomaly Index: {HSA_index:0.2f}')