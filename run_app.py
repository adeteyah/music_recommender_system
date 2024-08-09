import time

from scripts.rs import cf
from scripts.rs import cf_cbf
from scripts.rs import cbf
from scripts.rs import cbf_cf

ids = ['2eAZfqOm4EnOF9VvN50Tyc',
       '2G788tdaLtmkufuuNlBaGd', '2bdVgAQgosGUJoViVDNeOV']

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

# start = time.time()
# cbf_cf.cbf_cf(ids)
# end = time.time()
# print("Time: ", end - start)
