from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Contoh data: dua vektor dalam bentuk array numpy
vector_1 = np.array([1, 0, 0, 2])
vector_2 = np.array([1, 0, 1, 2])

# Menghitung cosine similarity
cosine_sim = cosine_similarity([vector_1], [vector_2])

# Output hasil
print("Cosine Similarity antara vector_1 dan vector_2:", cosine_sim[0][0])
