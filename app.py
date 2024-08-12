import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['4kPlQKwtPrnqLgrmmKFSlA',
       '03qu1u4hDyepQQi2lNxCka', '0afhq8XCExXpqazXczTSve']

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
