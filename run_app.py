import time
import scripts.seed as seed

from scripts.rs import cbf
from scripts.rs import cbf_o
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

seed.fill_playlists_table()

ids = [
    '2d6m2F4I7wCuAKtSsdhh83',
    '6TYQRlRci6AkVrN9a5C7ne',
    '0XHWClSz0v6RIaRSGqJH3X',
    '61mWefnWQOLf90gepjOCb3',
    '08mG3Y1vljYA6bvDt4Wqkj',
    '65EK5h5IS7wCkAeaatbdgg',
    '4uxsv9PjV3Yeyn51RdWvGJ',
    '4ZfTrSH5UwTqsKVQCaGvi3',
    '7BvjH5QT5Umiq21dgbvLXb',
    '6EdSN1iGtLPhcz43QDRkdK',
    '4KqTGPPmXowMPEoShSVOta',
    '4xNXqEBx1VXuph56zyUzBg',
]

# CBF
print("\n# Generating CBF Result")
start = time.time()
cbf.cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

# Optimized by Normalization
print("\n# Generating Optimized CBF Result")
start = time.time()
cbf_o.o_cbf_result(ids)
end = time.time()
print("CBF execution time: ", end - start)

# CF
print("\n# Generating CF Result")
start = time.time()
cf.cf_result(ids)
end = time.time()
print("CF execution time: ", end - start)

# HF CBF CF (From O_CBF Combined with ???)
print("\n# Generating HF-CBF-CF Result")
start = time.time()
hf_cbf_cf.hfcbfcf_result(ids)
end = time.time()
print("HFCBFCF execution time: ", end - start)

# HF CF CBF (From CF Combined with Euclidean Distance)
print("\n# Generating HF-CF-CBF Result")
start = time.time()
hf_cf_cbf.hfcfcbf_result(ids)
end = time.time()
print("HFCFCBF execution time: ", end - start, "\n")
