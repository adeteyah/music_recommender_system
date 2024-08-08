import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf
from scripts.rs import cbf_cf

ids = ['1fDFHXcykq4iw8Gg7s5hG9', '3E7dfMvvCLUddWissuqMwr']

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
