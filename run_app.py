import time
import scripts.seed.fill_playlists_attributes as fill_playlists_attributes

from scripts.rs import cbf
from scripts.rs import cbf_o
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cbf_cf_o
from scripts.rs import hf_cf_cbf

fill_playlists_attributes.fill_playlists_table()

ids = [
    '6rzVBHfKNDogRICqjzgGsE',
    '6uunyBNvRyzQl5imkPYdEb',
    '58zsLZPvfflaiIbNWoA22O',
    '5rxPi0MiR4miNK0rCmk980',
    '7Bpx2vsWfQFBACRz4h3IqH',
]

# print("\n# Generating CBF Result")
# start = time.time()
# cbf.cbf_result(ids)
# end = time.time()
# print("CBF execution time: ", end - start)

# print("\n# Generating HF-CBF-CF Result")
# start = time.time()
# hf_cbf_cf.hfcbfcf_result(ids)
# end = time.time()
# print("HFCBFCF execution time: ", end - start)

print("\n# Generating CBF (Optimized) Result")
start = time.time()
cbf_o.o_cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

print("\n# Generating HF-CBF-CF (Optimized) Result")
start = time.time()
hf_cbf_cf_o.o_hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

print("\n# Generating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

print("\n# Generating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")
