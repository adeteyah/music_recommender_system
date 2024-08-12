import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf
import scripts.tools.to_print as compile_result

ids = ['1P6VBsrhfvppwFV6Ae4Odr',
       '7zOVh5fGpEwSbZd0g9z80B', '1XvOEvWtfa879Wk1wKHZ1M']
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

compile_result.process_directory()
