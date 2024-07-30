import time
import scripts.seed.fill as fill

from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import cbf_cf
from scripts.rs import cf_cbf

fill.fill_playlists_table()

ids = [
    '5XeFesFbtLpXzIVDNQP22n',
    '1fDFHXcykq4iw8Gg7s5hG9',
]

print("\n#CF")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("Execution time: ", end - start)

print("\n# CBF")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("Execution time: ", end - start)

print("\n# CF-CBF")
start = time.time()
cf_cbf.cf_cbf_result(ids)
end = time.time()
print("Execution time: ", end - start, "\n")

print("\n# CBF-CF")
start = time.time()
cbf_cf.cbf_cf_result(ids)
end = time.time()
print("Execution time: ", end - start)
