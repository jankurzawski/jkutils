import os
import json
import pdb
# Set the path to your BIDS dataset and the sidecar JSON file
bids_root = "/Users/administrator/Library/CloudStorage/Dropbox/flOC_NEI/sub-wlsubj121/BIDS/"
subject = "wlsubj121"  # Example subject ID
session = "nyu3t01"
# Construct paths for both AP and PA sidecar JSON files
# Find all sidecar JSON files in the fmap directory that contain 'AP' or 'PA' in their names
fmap_dir = os.path.join(bids_root, f"sub-{subject}/ses-{session}/fmap")
sidecar_files = []
if os.path.exists(fmap_dir):
    for file in os.listdir(fmap_dir):
        if file.endswith(".json") and ("AP" in file or "PA" in file):
            sidecar_files.append(os.path.join(fmap_dir, file))

# Locate all functional runs in the dataset
func_files = []
subject_dir = os.path.join(bids_root, f"sub-{subject}")
for root, dirs, files in os.walk(subject_dir):
    for file in files:
        if file.endswith("_bold.nii.gz"):  # Adjust filter if needed
            func_path = os.path.relpath(os.path.join(root, file), subject_dir)
            func_files.append(func_path)
#pdb.set_trace()

# Update the IntendedFor field in both sidecar JSON files
for sidecar_file in sidecar_files:
    if os.path.exists(sidecar_file):
        with open(sidecar_file, "r") as f:
            sidecar_data = json.load(f)
    else:
        sidecar_data = {}

    sidecar_data["IntendedFor"] = func_files

    # Save the updated JSON
    with open(sidecar_file, "w") as f:
        json.dump(sidecar_data, f, indent=4)

    print(f"Updated {sidecar_file} with {len(func_files)} functional runs.")

