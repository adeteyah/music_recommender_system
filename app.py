import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf
import scripts.tools.to_print as compile_result

ids = ['6m6PTfVXdPZT6scb1TaONP',
       '0W6yE4Jmee6TKnvXEZOy2P', '6UDtY4939Z6p8gwuHhXb3g']

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

print('Compiled: result/to_recommend/compiled.txt')

compile_result.process_directory()
