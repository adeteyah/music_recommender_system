import time

from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

ids = ['01beCqR9wsVnwzkAJZyTqq', '5XeFesFbtLpXzIVDNQP22n', '0yc6Gst2xkRu0eMLeRMGCX', '0Eqg0CQ7bK3RQIMPw1A7pl',
       '4SqWKzw0CbA05TGszDgMlc', '5drW6PGRxkE6MxttzVLNk5', '6ilc4vQcwMPlvAHFfsTGng', '1SKPmfSYaPsETbRHaiA18G']

print("\nGenerating CBF Result")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

print("\nGenerating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

print("\nGenerating HF-CBF-CF Result")
start = time.time()
hf_cbf_cf.hf_cbf_cf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

print("\nGenerating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hf_cf_cbf_result(ids)  # hasil cf pakein cbf
end = time.time()
print("HFCFCBF execution time: ", end - start)
