import time

from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

ids = [
    '26WgejlZUG6TxLo8djVxUp',
    '56tKRucMdMNuslADmaxN9L',
    '5xuL74G1vQhSGn7WC3L3QL',
    '7bWHFauPVNfMYUVZnAXbo9',
    '2iOgTijjnxjtz7723Xs4sp'
]

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
hf_cbf_cf.hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

print("\nGenerating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start)
