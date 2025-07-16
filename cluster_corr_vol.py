import numpy as np
import nibabel as nib
from scipy.stats import t
from scipy.ndimage import label
from nilearn.image import load_img

# --- PARAMETERS ---
file_path = "/Users/administrator/Library/CloudStorage/Dropbox/flOC_NEI/scratch/projects/corevisiongrantnei/NEI_DATA/derivatives/fmriprep/sub-wlsubj121/ses-nyu3t02/func/face_vs_all_bvbabel.nii.gz"
cluster_size_threshold = 10            # minimum number of voxels
voxel_p_threshold = 0.001             # cluster-forming p threshold (two-sided)
df = 240 - 5                          # degrees of freedom – adjust to your analysis

# --- LOAD T-MAP ---
img = load_img(file_path)
data = img.get_fdata()

# --- THRESHOLD (two-sided) ---
t_thresh = t.ppf(1 - voxel_p_threshold / 2, df)
mask = np.abs(data) > t_thresh

# --- CLUSTERING ---
labeled_array, num_clusters = label(mask)
cluster_sizes = np.array([(labeled_array == i).sum() for i in range(1, num_clusters + 1)])

# --- APPLY CLUSTER SIZE THRESHOLD ---
keep_clusters = [i for i, size in enumerate(cluster_sizes, 1) if size >= cluster_size_threshold]
corrected_mask = np.isin(labeled_array, keep_clusters)
corrected_mask = corrected_mask*data
# --- SAVE OUTPUT ---
corrected_img = nib.Nifti1Image(corrected_mask, img.affine, img.header)
output_file = file_path.replace(".nii.gz", "_cluster_corrected.nii.gz")
nib.save(corrected_img, output_file)

print(f"Cluster-corrected map saved to: {output_file}")
