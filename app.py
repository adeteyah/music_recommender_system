import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['3wlLknnMtD8yZ0pCtCeeK4', '6EIMUjQ7Q8Zr2VtIUik4He',
       '30Z12rJpW0M0u8HMFpigTB']

start = time.time()  # DONE
cf.cf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()  # TODO: CEK AF BOUND
cf_cbf.cf_cbf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()  # DONE
cbf.cbf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()  # DONE
cbf_cf.cbf_cf(ids)
end = time.time()
print("Time: ", end - start)
