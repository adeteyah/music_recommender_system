import time

from scripts import cf
from scripts import cf_cbf
from scripts import cbf
from scripts import cbf_cf

n_separator = 20

ids = ['6T7MAQCekVb3UnCykjX3BP',
       '0v1XpBHnsbkCn7iJ9Ucr1l', '1BLfQ6dPXmuDrFmbdfW7Jl']

print('\n', "- " * n_separator, '\n')

start = time.time()
cf.cf(ids)
end = time.time()
print("Execution time: ", end - start)

print('\n', "- " * n_separator, '\n')

# start = time.time()
# cf_cbf.cfcbf(ids)
# end = time.time()
# print("Execution time: ", end - start)

# print('\n', "- " * n_separator, '\n')

start = time.time()
cbf.cbf(ids)
end = time.time()
print("Execution time: ", end - start)

print('\n', "- " * n_separator, '\n')

# start = time.time()
# cbf_cf.cbfcf(ids)
# end = time.time()
# print("Execution time: ", end - start)

# print('\n', "- " * n_separator, '\n')
