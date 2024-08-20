from sklearn.neighbors import NearestNeighbors
import numpy as np

# Contoh data
data = np.array([[1, 2], [2, 3], [3, 4], [5, 6], [8, 8]])

# Inisialisasi model NearestNeighbors dengan radius tertentu
radius = 2.5
nn = NearestNeighbors(radius=radius)
nn.fit(data)

# Query untuk menemukan semua poin dalam radius dari [3, 3]
query_point = np.array([[3, 3]])
neighbors_within_radius = nn.radius_neighbors(query_point)

# Menampilkan hasil
print("Poin dalam radius 2.5 dari [3, 3]:")
print(neighbors_within_radius[0])
