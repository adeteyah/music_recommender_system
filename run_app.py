import time
import scripts.seed as seed

from scripts.rs import cbf
from scripts.rs_optimized import o_cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

seed.fill_playlists_table()

ids = [
    '5XeFesFbtLpXzIVDNQP22n',
    '1fDFHXcykq4iw8Gg7s5hG9',
    '6ilc4vQcwMPlvAHFfsTGng',
    '2LBqCSwhJGcFQeTHMVGwy3',
]
# CBF
print("\n# Generating CBF Result")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

print("\n# Generating Optimized CBF Result")
start = time.time()
o_cbf.o_cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

# CF
print("\n# Generating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

# HF CBF CF
print("\n# Generating HF-CBF-CF Result")
start = time.time()
hf_cbf_cf.hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

# HF CF CBF
print("\n# Generating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")
