import time
import scripts.seed.fill_playlists_attributes as fill_playlists_attributes

from scripts.rs import cbf
from scripts.rs import cbf_o
from scripts.rs import cf
from scripts.rs import cbf_cf
from scripts.rs import hf_cbf_cf_o
from scripts.rs import cf_cbf

fill_playlists_attributes.fill_playlists_table()

ids = [
    '5XeFesFbtLpXzIVDNQP22n',
    '1fDFHXcykq4iw8Gg7s5hG9',
    '1dGr1c8CrMLDpV6mPbImSI',
    '1FWsomP9StpCcXNWmJk8Cl',
    '22Nd3GuO7sHopPjdKccRcq',
    '4xqrdfXkTW4T0RauPLv3WA',
    '4reIsHKw5hUj4pV8zzMjLA',
    '5TpPSTItCwtZ8Sltr3vdzm',
]


print("\n#CF")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

print("\n# Generating CBF Result")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

print("\n# Generating HF-CF-CBF Result")
start = time.time()
cf_cbf.cf_cbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")

print("\n# Generating HF-CBF-CF Result")
start = time.time()
cbf_cf.cbf_cf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)
