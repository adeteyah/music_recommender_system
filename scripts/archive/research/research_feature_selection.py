import sqlite3
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler

# Koneksi ke database SQLite
db_path = 'data/main.db'  # Ganti dengan path yang benar
conn = sqlite3.connect(db_path)

# Mengambil data dari tabel songs
query = """
SELECT
    acousticness,
    danceability,
    energy,
    instrumentalness,
    key,
    liveness,
    loudness,
    mode,
    speechiness,
    tempo,
    time_signature,
    valence
FROM songs
"""
data = pd.read_sql_query(query, conn)

# Menutup koneksi database
conn.close()

# Menyiapkan fitur dan target
X = data.drop(columns=['valence'])
y = data['valence']

# Normalisasi fitur
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Menghitung korelasi Pearson
correlations = data.corr()['valence'].drop('valence')
print("Korelasi Pearson antara fitur dan target:")
print(correlations)

# Menghitung fitur penting menggunakan Decision Tree
model = DecisionTreeRegressor()
model.fit(X_scaled, y)
feature_importances = model.feature_importances_

# Menampilkan fitur penting
importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

print("\nFitur Penting dari Decision Tree:")
print(importance_df)
