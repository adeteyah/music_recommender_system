import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['0qQ0R0SwHzLODkswy3fedU', '51hCDS4gLzfGbyVgVE2i4o',
       '7mKXEaBVWuV0dMqN0gaCBm', '2BgEsaKNfHUdlh97KmvFyo', '01380RE6UfsPSdiUIwrCoH']

# start = time.time()
# cf.cf(ids)
# end = time.time()
# print("Time: ", end - start)

# start = time.time()
# cf_cbf.cf_cbf(ids)
# end = time.time()
# print("Time: ", end - start)


start = time.time()
cbf.cbf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()
cbf_cf.cbf_cf(ids)
end = time.time()
print("Time: ", end - start)
