import scipy.io
import numpy as np
import torch

# ====== CONFIGURATION ======
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

# ====== LOAD BETA DATA ======
mat = scipy.io.loadmat('example_betas.mat')
data_np = mat['data_last']  # shape: (X, Y, Z, 6)
X, Y, Z, N = data_np.shape

# ====== CREATE STIMULUS MOVIE ======
nPix = 400
x = np.linspace(0, 10, nPix)  # 0–10 deg
stim_movie = np.zeros((6, nPix))
stim_movie[0, :] = x < 0.9
stim_movie[1, :] = (x >= 0.9) & (x < 1.8)
stim_movie[2, :] = (x >= 1.8) & (x < 3.3)
stim_movie[3, :] = (x >= 3.3) & (x < 4.7)
stim_movie[4, :] = (x >= 4.7) & (x < 6.48)
stim_movie[5, :] = (x >= 6.48) & (x < 9.0)

# Convert to torch
x_torch = torch.tensor(x, dtype=torch.float32, device=device)
stim_torch = torch.tensor(stim_movie, dtype=torch.float32, device=device)

# ====== FITTING FUNCTION ======
def fit_voxel(betas_np):
    betas = torch.tensor(betas_np, dtype=torch.float32, device=device)

    A = torch.tensor([betas.max()], dtype=torch.float32, requires_grad=True, device=device)
    mu = torch.tensor([3.0], dtype=torch.float32, requires_grad=True, device=device)
    sigma = torch.tensor([1.0], dtype=torch.float32, requires_grad=True, device=device)
    baseline = torch.tensor([betas.min()], dtype=torch.float32, requires_grad=True, device=device)

    optimizer = torch.optim.LBFGS([A, mu, sigma, baseline], max_iter=50, line_search_fn='strong_wolfe')

    def closure():
        optimizer.zero_grad()
        gauss = A * torch.exp(-(x_torch - mu) ** 2 / (2 * sigma ** 2))
        response = torch.sum(stim_torch * gauss, dim=1) + baseline
        loss = torch.nn.functional.mse_loss(response, betas)
        loss.backward()
        return loss

    try:
        optimizer.step(closure)
        with torch.no_grad():
            gauss = A * torch.exp(-(x_torch - mu) ** 2 / (2 * sigma ** 2))
            pred = torch.sum(stim_torch * gauss, dim=1) + baseline
            ss_res = torch.sum((betas - pred) ** 2)
            ss_tot = torch.sum((betas - torch.mean(betas)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else torch.tensor(0.0)
        return mu.item(), sigma.item(), r2.item()
    except Exception:
        return np.nan, np.nan, np.nan

# ====== RUN FIT ACROSS VOXELS ======
mu_map = np.full((X, Y, Z), np.nan, dtype=np.float32)
sigma_map = np.full((X, Y, Z), np.nan, dtype=np.float32)
r2_map = np.full((X, Y, Z), np.nan, dtype=np.float32)

for i in range(X):
    for j in range(Y):
        for k in range(Z):
            betas = data_np[i, j, k, :]
            if np.all(np.isfinite(betas)) and np.any(betas != 0):
                mu, sigma, r2 = fit_voxel(betas)
                mu_map[i, j, k] = mu
                sigma_map[i, j, k] = sigma
                r2_map[i, j, k] = r2

# ====== SAVE RESULT ======
scipy.io.savemat('prf_fit_torch_mps_with_r2.mat', {
    'mu_map': mu_map,
    'sigma_map': sigma_map,
    'r2_map': r2_map
})
