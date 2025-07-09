import numpy as np
import bvbabel
import pdb
import matplotlib.pyplot as plt
# Load SRF file
header_srf, data_srf = bvbabel.srf.read_srf("/Users/administrator/Downloads/Colin27_iso1_brain_GM_D80k.srf")


# Load your mesh data (replace with your actual loading method)
mesh_data = data_srf  # Your dictionary with 'vertices' and 'faces'
vertices = mesh_data["vertices"]
faces = mesh_data["faces"]
nr_vertices = len(vertices)

# Step 1: Compute per-vertex surface area
def compute_vertex_areas(vertices, faces):
    vertex_areas = np.zeros(len(vertices), dtype=np.float32)
    for tri in faces:
        v0, v1, v2 = vertices[tri]
        area = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
        for i in tri:
            vertex_areas[i] += area / 3.0
    return vertex_areas

areas = compute_vertex_areas(vertices, faces)
# Step 2: Prepare SMP structure
smp_header, smp_data = bvbabel.smp.create_smp(nr_vertices=nr_vertices)

smp_data = areas[:, None]  # shape: (80000, 1)

pdb.set_trace()

# Step 3: Save to .smp
plt.hist(smp_data, bins=100)
#bvbabel.smp.write_smp("surface_area.smp", smp_header, smp_data)