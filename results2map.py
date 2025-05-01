#!/usr/bin/env python3

import numpy as np
import os
import scipy.io
import nibabel as nib
import argparse
import pdb


# Define function to save the data as .mgz files
def write_mgz(data,filename,fspath):
    file=nib.freesurfer.mghformat.load(os.path.join(fspath, 'mri','orig.mgz'))
    file.header.set_data_dtype('float')
    file2save=nib.freesurfer.mghformat.MGHImage(data, affine=None, header=file.header)
    nib.save(file2save,filename)
    print(f"Writing {filename}")

# Define the main function that takes prfpath as input
def process_and_save(prfpath,fspath):
    # Load the .mat file (assuming there's only one file called result.mat)
    mat_file_path = os.path.join(prfpath, 'results.mat')
    tmp = scipy.io.loadmat(mat_file_path)

    # Extract the relevant data (assuming structure based on your example)
    model = tmp['results'][0, 0]['model'][0, 0]

    # Calculate the values
    mysigma = np.transpose(model['sigma'][0, 0]['major'][0, 0])
    myvexpl = np.transpose(1 - (model['rss'][0, 0] / model['rawrss'][0, 0]))
    myangle = np.transpose(np.arctan2(-model['y0'][0, 0], model['x0'][0, 0]))
    myangle_adj = (np.mod(90 - 180/np.pi * myangle + 180, 360) - 180)

    myx = np.transpose(model['x0'][0, 0])
    myy = np.transpose(model['y0'][0, 0])
    myeccen = np.transpose(np.sqrt(model['x0'][0, 0]**2 + model['y0'][0, 0]**2))

    # Define leftidx and rightidx using curvature files
    # Read curvature data
    lcurv = nib.freesurfer.read_morph_data(os.path.join(fspath, 'surf', 'lh.curv'))
    rcurv = nib.freesurfer.read_morph_data(os.path.join(fspath, 'surf', 'rh.curv'))

    # Define indices for left and right hemispheres
    leftidx = np.arange(len(lcurv))  # Left hemisphere indices
    rightidx = np.arange(len(rcurv)) + len(lcurv)  # Right hemisphere indices (offset by len(lcurv))


    # Write the results to .mgz files
    write_mgz(myangle[leftidx], os.path.join(prfpath, 'lh.angle.mgz'),fspath)
    write_mgz(myangle[rightidx], os.path.join(prfpath, 'rh.angle.mgz'),fspath)
    write_mgz(myangle_adj[leftidx], os.path.join(prfpath, 'lh.angle_adj.mgz'),fspath)
    write_mgz(myangle_adj[rightidx], os.path.join(prfpath, 'rh.angle_adj.mgz'),fspath)
    write_mgz(myeccen[leftidx], os.path.join(prfpath, 'lh.eccen.mgz'),fspath)
    write_mgz(myeccen[rightidx], os.path.join(prfpath, 'rh.eccen.mgz'),fspath)
    write_mgz(mysigma[leftidx], os.path.join(prfpath, 'lh.sigma.mgz'),fspath)
    write_mgz(mysigma[rightidx], os.path.join(prfpath, 'rh.sigma.mgz'),fspath)
    write_mgz(myvexpl[leftidx], os.path.join(prfpath, 'lh.vexpl.mgz'),fspath)
    write_mgz(myvexpl[rightidx], os.path.join(prfpath, 'rh.vexpl.mgz'),fspath)
    write_mgz(myx[leftidx], os.path.join(prfpath, 'lh.x.mgz'),fspath)
    write_mgz(myx[rightidx], os.path.join(prfpath, 'rh.x.mgz'),fspath)
    write_mgz(myy[leftidx], os.path.join(prfpath, 'lh.y.mgz'),fspath)
    write_mgz(myy[rightidx], os.path.join(prfpath, 'rh.y.mgz'),fspath)

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and save .mgz files from result.mat.")
    parser.add_argument('prfpath', type=str, help="Path to the directory containing result.mat")
    parser.add_argument('fspath', type=str, help=" Subject's freesurfer directory")

    args = parser.parse_args()
    
    # Call the function to process the data and save the .mgz files
    process_and_save(args.prfpath, args.fspath)
