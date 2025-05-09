import nibabel as nb
import numpy as np
import bvbabel
import os
import pdb
# ---------------------------------------------------------------------
# Input paths
MGZ_FILE = "/Users/administrator/Documents/akinetopsia/derivatives/fmriprep_floc/sub-wlsubj140_ses-nyu3t02_task-floc_run-1_space-fsnative_hemi-R_bold.func.mgz"
# ---------------------------------------------------------------------
# Load MGZ timecourse data
img = nb.load(MGZ_FILE)
data = np.squeeze(np.asanyarray(img.dataobj))  # Shape: (vertices, timepoints)

# Reshape if needed
if data.ndim == 4:
    data = data.reshape(data.shape[0], data.shape[3])
elif data.ndim == 3:
    data = data.reshape(data.shape[0], -1)

n_vertices, n_timepoints = data.shape
print(f"✅ MGZ loaded: {n_vertices} vertices, {n_timepoints} timepoints")

# ---------------------------------------------------------------------
# Write to MTC (BV expects shape: [timepoints, vertices])
basename = os.path.splitext(os.path.basename(MGZ_FILE))[0]
outname = os.path.join(os.path.dirname(MGZ_FILE), f"{basename}.mtc")
#pdb.set_trace()
header, _ = bvbabel.mtc.create_mtc()
header['Nr vertices'] =data.shape[0]
header['Nr time points'] =data.shape[1]

bvbabel.mtc.write_mtc(outname, header, data.T)
print(f"✅ MTC saved: {outname}")