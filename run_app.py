import time
import scripts.seed as seed

from scripts.rs import cbf
from scripts.rs import cbf_o
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

seed.fill_playlists_table()

ids = [
    '3vkCueOmm7xQDoJ17W1Pm3',
    '5vPO5ouEv8iedKWxzmSv7b',
    '3qhlB30KknSejmIvZZLjOD',
]
# CBF
print("\n# Generating CBF Result")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

# Optimized by Normalization
print("\n# Generating Optimized CBF Result")
start = time.time()
cbf_o.o_cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

# CF
print("\n# Generating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

# HF CBF CF (From O_CBF Combined with ???)
print("\n# Generating HF-CBF-CF Result")
start = time.time()
hf_cbf_cf.hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

# HF CF CBF (From CF Combined with Euclidean Distance)
print("\n# Generating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")
