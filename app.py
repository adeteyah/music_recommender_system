import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['2kJwzbxV2ppxnQoYw4GLBZ', '5dn6QANKbf76pANGjMBida',
       '3Sbova9DAY3pc9GTAACT4b', '5O2P9iiztwhomNh8xkR9lJ', '4pvb0WLRcMtbPGmtejJJ6y']

start = time.time()  # DONE
cf.cf(ids)
end = time.time()
print("Time: ", end - start)

start = time.time()  # DONE
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
