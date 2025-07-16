#!/bin/bash

SUB=sub-S1
SURF_DIR=/Users/administrator/Downloads/jan_prf/derivatives/prfvista/${SUB}/ses-s1
SUBJECTS_DIR=/Users/administrator/Downloads/jan_prf/derivatives/freesurfer
export SUBJECTS_DIR
OUT_DIR=${SURF_DIR}/volumes
TEMPLATE=${SUBJECTS_DIR}/${SUB}/mri/T1.mgz

mkdir -p "$OUT_DIR"

cd "$SURF_DIR" || exit

for lh_file in lh.*.mgz; do
    mapname=$(basename "$lh_file" .mgz | cut -d. -f2)
    rh_file="rh.${mapname}.mgz"

    if [[ -f "$rh_file" ]]; then
        echo "🔄 Projecting: $mapname"

        # Output paths
        lh_vol="$OUT_DIR/lh_${mapname}_vol.nii.gz"
        rh_vol="$OUT_DIR/rh_${mapname}_vol.nii.gz"
        out_vol="$OUT_DIR/${mapname}_combined_vol.nii.gz"

        # Surface to volume
        mri_surf2vol --surfval "$lh_file" --subject "$SUB" --hemi lh \
            --fillribbon --identity "$SUB" --template "$TEMPLATE" --o "$lh_vol"

        mri_surf2vol --surfval "$rh_file" --subject "$SUB" --hemi rh \
            --fillribbon --identity "$SUB" --template "$TEMPLATE" --o "$rh_vol"

        # Combine (average)
        fslmaths "$lh_vol" -add "$rh_vol" -div 2 "$out_vol"

        echo "✅ Saved: $out_vol"
    else
        echo "⚠️  Missing $rh_file for $mapname"
    fi
done

