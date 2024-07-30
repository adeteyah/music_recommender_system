import time
import scripts.seed.fill_playlists_attributes as fill_playlists_attributes

from scripts.rs import cbf
from scripts.rs import cbf_o
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cbf_cf_o
from scripts.rs import hf_cf_cbf

fill_playlists_attributes.fill_playlists_table()

ids = [
    '5XeFesFbtLpXzIVDNQP22n',
    '2UgCs0i0rNHUH2jKE5NZHE',
    '1fDFHXcykq4iw8Gg7s5hG9',
    '6ilc4vQcwMPlvAHFfsTGng',
    '4SqWKzw0CbA05TGszDgMlc',
    '0yc6Gst2xkRu0eMLeRMGCX',
    '1dGr1c8CrMLDpV6mPbImSI',
    '1FWsomP9StpCcXNWmJk8Cl',
    '1RMJOxR6GRPsBHL8qeC2ux',
    '2LBqCSwhJGcFQeTHMVGwy3',
    '2eAvDnpXP5W0cVtiI0PUxV',
    '086myS9r57YsLbJpU0TgK9',
    '26WgejlZUG6TxLo8djVxUp',
    '3afkJSKX0EAMsJXTZnDXXJ',
    '4kfjA6WfgKBt7I7YKuDCkU',
    '56tKRucMdMNuslADmaxN9L',
    '5CZ40GBx1sQ9agT82CLQCT',
    '5xuL74G1vQhSGn7WC3L3QL',
    '7bWHFauPVNfMYUVZnAXbo9',
    '22Nd3GuO7sHopPjdKccRcq',
    '2iOgTijjnxjtz7723Xs4sp',
    '5suV1gtfD3kGj5A3teIVtV',
    '3AJwUDP919kvQ9QcozQPxg',
    '0mL82sxCRjrs3br407IdJh',
    '13sOb9V6Y3uCnRxY9HIZqP',
    '1Y0HqJ0WOyfUX5AvvGlQKF',
    '5FVd6KXrgO9B3JPmC8OPst',
    '3JjnGLK8IxkNLvo8Lb3KOM',
    '4xqrdfXkTW4T0RauPLv3WA',
    '0ROj512WvJ1eqeELd7MEdJ',
    '0SpkyS1Q4MD8GaVcP5YjT4',
    '3hUxzQpSfdDqwM3ZTFQY0K',
    '630DpnzdfjdVqv2yLfPbAX',
]

# print("\n# Generating CBF Result")
# start = time.time()
# cbf.cbf_result(ids)
# end = time.time()
# print("CBF execution time: ", end - start)

# print("\n# Generating HF-CBF-CF Result")
# start = time.time()
# hf_cbf_cf.hfcbfcf_result(ids)
# end = time.time()
# print("HFCBFCF execution time: ", end - start)

print("\n# Generating CBF (Optimized) Result")
start = time.time()
cbf_o.o_cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

print("\n# Generating HF-CBF-CF (Optimized) Result")
start = time.time()
hf_cbf_cf_o.o_hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

print("\n# Generating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

print("\n# Generating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")
