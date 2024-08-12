import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf_optimized as cbf
from scripts.rs import cbf_cf

ids = ['6ewcmBuzbHTUCrmN2Obnxz', '4ytx0PQvxNbZwaplFx2Wd1',
       '6UZL8ibn0YggrPz5lhqERT', '7su8VspD0Qlph5mXXBOe5Q', '0rk3F1mm2Yrvh4zSrNpa0J']

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
