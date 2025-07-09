import numpy as np
import pandas as pd
from scipy.io import savemat

def parse_prt_onsets_per_condition(prt_path, total_timepoints):
    with open(prt_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    dm = []
    condition_names = []
    trial_list = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if any(line.startswith(prefix) for prefix in [
            "FileVersion", "ResolutionOfTime", "Experiment", "BackgroundColor",
            "TextColor", "TimeCourseColor", "TimeCourseThick", "Color", "NrOfConditions"
        ]):
            i += 1
            continue

        cond_name = line
        condition_names.append(cond_name)
        i += 1

        while i < len(lines) and not lines[i].isdigit():
            i += 1
        if i >= len(lines):
            break

        try:
            n_blocks = int(lines[i])
        except ValueError:
            i += 1
            continue
        i += 1

        col = np.zeros(total_timepoints)
        for _ in range(n_blocks):
            if i >= len(lines):
                break
            parts = lines[i].split()
            if len(parts) >= 2:
                try:
                    start = int(parts[0]) - 1  # BV uses 1-based indexing
                    if 0 <= start < total_timepoints:
                        col[start] = 1
                        trial_list.append({
                            'onset': start,
                            'duration': 1.0,
                            'trial_type': cond_name
                        })
                except ValueError:
                    pass
            i += 1

        dm.append(col)

    dm_matrix = np.column_stack(dm) if dm else np.zeros((total_timepoints, 0))
    design_df = pd.DataFrame(trial_list)
    return dm_matrix, condition_names, design_df

# -------------------------
# Main block
# -------------------------
if __name__ == "__main__":
    import os

    prt_files = [
        '/Users/administrator/Documents/jkutils/quadrants_run.prt',
    ]
    total_timepoints = 102

    dm_list = []
    design_dfs = []

    for prt_file in prt_files:
        if not os.path.exists(prt_file):
            print(f"⚠️ File not found: {prt_file}")
            continue
        try:
            dm, names, design = parse_prt_onsets_per_condition(prt_file, total_timepoints)
            dm_list.append(dm)
            design_dfs.append(design)
            print(f"✅ Parsed {prt_file}: {dm.shape[1]} conditions, {len(design)} events")
        except Exception as e:
            print(f"❌ Error parsing {prt_file}: {e}")

    # Save to .mat
    mat_data = {}
    for idx, (dm, design) in enumerate(zip(dm_list, design_dfs), start=1):
        mat_data[f'dm_matrix_{idx}'] = dm
        mat_data[f'design{idx}'] = design.to_dict('list')

    if mat_data:
        savemat('design_with_onsets.mat', mat_data)
        print("💾 Saved to design_with_onsets.mat")
    else:
        print("⚠️ No data saved. All files failed or missing.")


print(design)