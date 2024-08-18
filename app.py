import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf
import scripts.tools.to_print as compile_result

ids = ['0rb4Q8QXJZwI63NPbL36Qd',
       '6AI3ezQ4o3HUoP6Dhudph3',
       '4kjI1gwQZRKNDkw1nI475M']

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
