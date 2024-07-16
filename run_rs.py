import time

from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

input = ['id1', 'id2']

start = time.time() 
cbf.cbf_result(input)
end = time.time() 
print("Execution time: ",end - start)

start = time.time() 
cf.cf_result(input)
end = time.time() 
print("Execution time: ",end - start)

start = time.time() 
hf_cbf_cf.hf_cbf_cf_result(input)
end = time.time() 
print("Execution time: ",end - start)

start = time.time() 
hf_cf_cbf.hf_cf_cbf_result(input)
end = time.time() 
print("Execution time: ",end - start)