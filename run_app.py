import time

from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

input = ['0VjIjW4GlUZAMYd2vXMi3b',
         '22I3h5AOENlH4CqXJsEbFR', '72cGBEqu7RitIOoACXYjfR']

print("\nGenerating CBF Result")
start = time.time()
cbf.cbf_result(input)
end = time.time()
print("CBF execution time: ", end - start)

print("\nGenerating CF Result")
start = time.time()
cf.cf_result(input)
end = time.time()
print("CF execution time: ", end - start)

# print("\nGenerating HF-CBF-CF Result")
# start = time.time()
# hf_cbf_cf.hf_cbf_cf_result(input)
# end = time.time()
# print("HFCBFCF execution time: ", end - start)

# print("\nGenerating HF-CF-CBF Result")
# start = time.time()
# hf_cf_cbf.hf_cf_cbf_result(input)  # hasil cf pakein cbf
# end = time.time()
# print("HFCFCBF execution time: ", end - start)

print('\n')
