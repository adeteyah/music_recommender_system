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
    '1fDFHXcykq4iw8Gg7s5hG9',
    '2UgCs0i0rNHUH2jKE5NZHE',
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
    '5xuL74G1vQhSGn7WC3L3QL',
    '7bWHFauPVNfMYUVZnAXbo9',
    '22Nd3GuO7sHopPjdKccRcq',
    '2iOgTijjnxjtz7723Xs4sp',
    '5CZ40GBx1sQ9agT82CLQCT',
    '5suV1gtfD3kGj5A3teIVtV',
    '1Y0HqJ0WOyfUX5AvvGlQKF',
    '3AJwUDP919kvQ9QcozQPxg',
    '5FVd6KXrgO9B3JPmC8OPst',
    '0mL82sxCRjrs3br407IdJh',
    '13sOb9V6Y3uCnRxY9HIZqP',
    '3JjnGLK8IxkNLvo8Lb3KOM',
    '4xqrdfXkTW4T0RauPLv3WA',
    '0ROj512WvJ1eqeELd7MEdJ',
    '0SpkyS1Q4MD8GaVcP5YjT4',
    '3hUxzQpSfdDqwM3ZTFQY0K',
    '7D0RhFcb3CrfPuTJ0obrod',
    '630DpnzdfjdVqv2yLfPbAX',
    '78Sw5GDo6AlGwTwanjXbGh',
    '2tGvwE8GcFKwNdAXMnlbfl',
    '3M0lSi5WW79CXQamgSBIjx',
    '1dQQ2QlnvXUehsRUrukKmf',
    '73jVPicY2G9YHmzgjk69ae',
    '0BxE4FqsDD1Ot4YuBXwAPp',
    '1w3azB0VuRFp79AduIwrIy',
    '2dIBMHByUGcNPzmYBJ6OAj',
    '3p4hRhMcb6ch8OLtATMaLw',
    '3vkCueOmm7xQDoJ17W1Pm3',
    '4EWBhKf1fOFnyMtUzACXEc',
    '4R2kfaDFhslZEMJqAFNpdd',
    '51lPx6ZCSalL2kvSrDUyJc',
    '7CyPwkp0oE8Ro9Dd5CUDjW',
    '7nQoDLkzCcoIpKPQt3eCdN',
    '01beCqR9wsVnwzkAJZyTqq',
    '3cKM7UXBZmgjEgEBTkaIlU',
    '1BxfuPKGuaTgP7aM0Bbdwr',
    '22bPsP2jCgbLUvh82U0Z3M',
    '3W4U7TEgILGpq0EmquurtH',
    '3pCt2wRdBDa2kCisIdHWgF',
    '5O2P9iiztwhomNh8xkR9lJ',
    '6ueq4MrVEcvUwe8E80SPar',
    '7MXVkk9YMctZqd1Srtv4MB',
    '1drRDlIBhcYUOaeMssBpEr',
    '26cvTWJq2E1QqN4jyH2OTU',
    '4Ssi6tKwrTHi5qvDndrZRP',
    '7ivYWXqrPLs66YwakDuSim',
    '18UsAG7SfOQ5sxJEdjAMH0',
    '1Fid2jjqsHViMX6xNH70hE',
    '3sqrvkNC6IPTIXvvbx9Arw',
    '7iTF9T1jum3Km6H6WMZpDC',
    '04S1pkp1VaIqjg8zZqknR5',
    '1NZs6n6hl8UuMaX0UC0YTz',
    '2AT8iROs4FQueDv2c8q2KE',
    '2LlOeW5rVcvl3QcPNPcDus',
    '4dtmj7X21gunWoQf98hW5L',
    '0X2bh8NVQ8svDQIn2AdCbW',
    '0otRX6Z89qKkHkQ9OqJpKt',
    '3Eb5sztvEMa0Mqnb8DUAlU',
    '3hRV0jL3vUpRrcy398teAU',
    '4HBZA5flZLE435QTztThqH',
    '5EcGSkkNBMAWOePvLgKde1',
    '7zFXmv6vqI4qOt4yGf3jYZ',
    '0ug5NqcwcFR2xrfTkc7k8e',
    '1fzAuUVbzlhZ1lJAx9PtY6',
    '2EfZf8CglKPgpa96criANN',
    '2hHeGD57S0BcopfVcmehdl',
    '09mEdoA6zrmBPgTEN5qXmN',
    '1HNkqx9Ahdgi1Ixy2xkKkL',
    '1SKPmfSYaPsETbRHaiA18G',
    '1ZPVEo8RfmrEz8YAD5n6rW',
    '1qrpoAMXodY6895hGKoUpA',
    '2wAiFWjRupWmnDkQcu91MF',
    '2xlV2CuWgpPyE9e0GquKDN',
    '3TgMcrV32NUKjEG2ujn9eh',
    '5drW6PGRxkE6MxttzVLNk5',
    '68HocO7fx9z0MgDU0ZPHro',
    '77sMIMlNaSURUAXq5coCxE',
    '0M3HkE321xpCbCYqVKzr1q',
    '1acVBP8BcK6LTeNeFjfxnh',
    '2bdVgAQgosGUJoViVDNeOV',
    '2p8IUWQDrpjuFltbdgLOag',
    '4mkqoe1yptnwU5S537fYlT',
    '4reIsHKw5hUj4pV8zzMjLA',
    '5TpPSTItCwtZ8Sltr3vdzm',
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
