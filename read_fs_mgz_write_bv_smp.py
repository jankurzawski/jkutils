"""Convert Freesurfer *.pct.mgh file into BrainVoyager SMP format."""

import os
import numpy as np
import nibabel as nb
import bvbabel
import pdb
# NOTE: Full path to `<subjid>/surf/?h.w-g.pct.mgh` file. This file is a
# surface map that has gray to white matter signal intensity ratios for each
# vertex (ref: <https://surfer.nmr.mgh.harvard.edu/fswiki/pctsurfcon>)

FILE = "/Users/administrator/Documents/akinetopsia/derivatives/prfvista/sub-wlsubj140/ses-nyu3t01/rh.y.mgz"
#FILE = "/Users/administrator/Documents/akinetopsia/derivatives/GLMdenoise/sub-wlsubj140/ses-nyu3t01/rh.central_moving.mgz"
mask = "/Users/administrator/Documents/akinetopsia/derivatives/prfvista/sub-wlsubj140/ses-nyu3t01/rh.vexpl.mgz"
#mask = "/Users/administrator/Documents/akinetopsia/derivatives/GLMdenoise/sub-wlsubj140/ses-nyu3t01/rh.vexpl_glm.mgz"

# -----------------------------------------------------------------------------
# Read Freesurfer `*.w-g.pct.mgh` surface map
mgh = nb.load(FILE)
mask = nb.load(mask)
mgh_data = np.squeeze(np.asarray(mgh.dataobj))
mgh_data_mask = np.squeeze(np.asarray(mask.dataobj))

mgh_data = mgh_data * (mgh_data_mask > 0.05)
nr_vertices = mgh_data.shape[0]

# Generate dummy SMP file
smp_header, smp_data = bvbabel.smp.create_smp(nr_vertices=nr_vertices)

# Update some fields with mgh information
smp_header["Map"][0]["Threshold min"] = np.percentile(mgh_data, 5)
smp_header["Map"][0]["Threshold max"] = np.percentile(mgh_data, 95)

# Determine output name
basename = FILE[:-4]  # get rid of mgh extension
basename = basename.replace(".", "_")
outname = "{}_bvbabel.smp".format(basename)

# Save SMP file while using the freesurfer MGH data
bvbabel.smp.write_smp(outname, smp_header, mgh_data[:, None])

print('Finished.')
