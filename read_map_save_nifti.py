import os
import bvbabel
import nibabel as nb
import numpy as np
import pprint
import pdb
import struct

from bvbabel.utils import read_variable_length_string, read_RGB_bytes
from bvbabel.utils import write_variable_length_string, write_RGB_bytes



def read_map(filename):
    """Read BrainVoyager MAP file.

    Parameters
    ----------
    filename : string
        Path to file.

    Returns
    -------
    header : dictionary
        Pre-data and post-data headers.
    data : 3D numpy.array
        Image data.

    """
    header = dict()
    with open(filename, 'rb') as f:
        # ---------------------------------------------------------------------
        # NR-MAP Header (Version 2)
        # ---------------------------------------------------------------------

        # Expected binary data: short int (2 bytes)
        data, = struct.unpack('<h', f.read(2))
        header["MapType"] = 't-values'
        header["NrOfSlices"] = int(data)
        data, = struct.unpack('<h', f.read(2))
        header["NrOfMaps"] = int(data)
        data, = struct.unpack('<h', f.read(2))
        header["DimX"] = int(data)
        data, = struct.unpack('<h', f.read(2))
        header["DimY"] = int(data)
        data, = struct.unpack('<h', f.read(2))
        header["ClusterSize"] = int(data)

        # Expected binary data: float (4 bytes)
        data, = struct.unpack('<f', f.read(4))
        header["Min"] = data  # 	Statistical threshold, critical value
        data, = struct.unpack('<f', f.read(4))
        header["Max"] = data # 	Statistical threshold, max value

        # Expected binary data: short int (2 bytes)
        if header["MapType"] == 'crosscorrelation':
	        data, = struct.unpack('<h', f.read(2))
	        header["NrOfLags"] = int(data)

        # Expected binary data: short int (2 bytes) 
        data, = struct.unpack('<h', f.read(2)) # Reserved field 9999
        # Expected binary data: short int (2 bytes)
        data, = struct.unpack('<h', f.read(2)) # Version 3

        data, = struct.unpack('<i', f.read(4)) # DF1
        header["df1"] = int(data)

        data, = struct.unpack('<i', f.read(4)) # DF2
        header["df2"] = int(data)

        # Expected binary data: variable-length string
        data = read_variable_length_string(f)  # Reserved field
        header["RTCName"] = data

        # ---------------------------------------------------------------------
        # Read MAP image data
        # ---------------------------------------------------------------------
        # A map file contains NrOfMaps (= NrOfSlices) 2D statistical images. Each image contains DimY*DimX data points.
        # Each data point (statistical value) is represented in 4 bytes (float). 
        # Each slice is preceded by a 2 byte (short int) value representing the slice index (i.e. '0' for slice 1 and 'NrOfMaps-1' for the last slice). 
        # There are some additional informations about MAP files which are specific to correlation and cross-correlation maps.
        #
        
        data_img = []#np.zeros( header['NrOfSlices'] * header['DimY'] * header['DimX'])

        for s in range(header['NrOfSlices']):

            # Expected binary data: short int (2 bytes)
            data, = struct.unpack('<h', f.read(2)) #Slice number
            data_img.append(np.reshape(np.fromfile(f, dtype='<f', count=header['DimY'] * header['DimX'], sep="", offset=0), (header['DimX'],header['DimY']))[:,:,None]) # slice data

            #print('Slice: ', data)

            temp_img = []
            #for y in range(header['DimY']):
            #    for x in range(header['DimX']):
            #        data, = struct.unpack('<f', f.read(4))
            #       temp_img.append(data)
            #data_img.append(np.reshape(temp_img,(header['DimY'],header['DimX']))[:,:,None])

        # -----------------------------------------------------------------

    data_img = np.concatenate(data_img, axis=2) # stuck the slices
    data_img = np.transpose(data_img, (1, 0, 2))
    data_img = data_img[::-1, ::-1,:]  # Flip BV axes

    return header, data_img



FILE = '/Users/administrator/Library/CloudStorage/Dropbox/flOC_NEI/scratch/projects/corevisiongrantnei/NEI_DATA/derivatives/fmriprep/sub-wlsubj121/ses-nyu3t02/func/face_vs_all.map'
header, data = read_map(FILE)
data_t = np.transpose(data, (1, 0, 2))  # from (73, 84, 75) to (84, 73, 75)
data_t = np.rot90(data_t, k=1, axes=(0, 1))  # rotate in XY plane

FILE_nii = '/Users/administrator/Library/CloudStorage/Dropbox/flOC_NEI/scratch/projects/corevisiongrantnei/NEI_DATA/derivatives/fmriprep/sub-wlsubj121/ses-nyu3t02/func/sub-wlsubj121_ses-nyu3t02_task-floc1_space-T1w_desc-preproc_bold.nii.gz'

# Save nifti for testing
basename = FILE.split(os.extsep, 1)[0]
outname = "{}_bvbabel.nii.gz".format(basename)

ref_img = nb.load(FILE_nii)
affine = ref_img.affine

# Create NIfTI image
img = nb.Nifti1Image(data_t, affine=affine)

# Save to disk
nb.save(img, outname)
