"""Convert MATLAB .mat surface data into BrainVoyager SMP format and save in same folder."""

import os
import numpy as np
import scipy.io as sio
import nibabel as nb
import bvbabel
import pdb
# ---- CONFIG ----
MAT_FILE = "/Users/administrator/Documents/fNIRS/pa_bar.mat"
MAT_KEY = "myangle_adj"  # change to the actual variable name inside the .mat file
MASK_FILE = "/Users/administrator/Documents/fNIRS/variance_bar.mat"
MAT_KEY_MASK = "myvexpl"  # change to the actual variable name inside the mask .mat file
# ---- LOAD DATA ----
mat = sio.loadmat(MAT_FILE)
data = np.squeeze(mat[MAT_KEY])  # assume shape (n_vertices,)
mat_mask = sio.loadmat(MASK_FILE)
data_mask = np.squeeze(mat_mask[MAT_KEY_MASK])  # assume shape (n_vertices,)

# Optional: load a mask
#mask = np.squeeze(np.asanyarray(nb.load(MASK_FILE).dataobj))
data = data * (data_mask > 0.42)  # optional masking

# ---- CREATE SMP ----
nr_vertices = data.shape[0]
smp_header, smp_data = bvbabel.smp.create_smp(nr_vertices=nr_vertices)
smp_header["Map"][0]["Threshold min"] = np.percentile(data, 5)
smp_header["Map"][0]["Threshold max"] = np.percentile(data, 95)

# ---- OUTPUT PATH ----
mat_dir = os.path.dirname(MAT_FILE)
mat_base = os.path.splitext(os.path.basename(MAT_FILE))[0]
outname = f"{mat_base}_bvbabel.smp"
outpath = os.path.join(mat_dir, outname)

# ---- WRITE SMP ----
#pdb.set_trace()  # Optional: set a breakpoint for debugging
bvbabel.smp.write_smp(outpath, smp_header, data[:, None])
print(f"Finished writing SMP to: {outpath}")