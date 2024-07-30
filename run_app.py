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
    '1FWsomP9StpCcXNWmJk8Cl',
    '1RMJOxR6GRPsBHL8qeC2ux',
    '2LBqCSwhJGcFQeTHMVGwy3',
    '2eAvDnpXP5W0cVtiI0PUxV',
    '086myS9r57YsLbJpU0TgK9',
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
