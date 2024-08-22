import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf
import scripts.tools.to_print as compile_result

ids = [
    '1yKAqZoi8xWGLCf5vajroL',
    '1ZPVEo8RfmrEz8YAD5n6rW',
    '6AI3ezQ4o3HUoP6Dhudph3',
]

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
