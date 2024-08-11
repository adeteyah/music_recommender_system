import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['5Z2DNRAhs6r4VdINVkRhYY', '6YFzL1910P0fRFh865HmI3',
       '1zxfRSZcaonV1VXcY0PgY5', '6LF44wAs3h0K67RitTAfr5', '65fpYBrI8o2cfrwf2US4gq']

start = time.time()  # DONE
cf.cf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()  # TODO: AF BOUND BY FEATURE SELECT & SORT BY AUDIO FEATURES
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
