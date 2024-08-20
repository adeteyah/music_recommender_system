import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Contoh dataset transaksi
data = {'bread': [1, 1, 0, 1, 1],
        'butter': [1, 0, 0, 1, 1],
        'milk': [0, 1, 1, 1, 0],
        'eggs': [1, 0, 0, 1, 0]}

df = pd.DataFrame(data)

# Menampilkan dataset
print("Dataset Transaksi:")
print(df)

# Menerapkan algoritma Apriori untuk menemukan frequent itemsets
# Dengan minimum support = 0.6 (atau 60%)
frequent_itemsets = apriori(df, min_support=0.6, use_colnames=True)

# Menampilkan frequent itemsets
print("\nFrequent Itemsets:")
print(frequent_itemsets)

# Menerapkan aturan asosiasi dengan minimum confidence = 0.7 (atau 70%)
rules = association_rules(
    frequent_itemsets, metric="confidence", min_threshold=0.7)

# Menampilkan aturan asosiasi
print("\nAturan Asosiasi:")
print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
