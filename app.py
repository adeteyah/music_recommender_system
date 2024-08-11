import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = [
    '30Z12rJpW0M0u8HMFpigTB', ]

start = time.time()
cf.cf(ids)
end = time.time()
print("Time: ", end - start)

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
