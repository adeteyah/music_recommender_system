from scripts.rs import cbf
from scripts.rs import cf
from scripts.rs import hf_cbf_cf
from scripts.rs import hf_cf_cbf

input = ['id1', 'id2']

cbf.cbf_result(input)
cf.cf_result(input)
hf_cbf_cf.hf_cbf_cf_result(input)
hf_cf_cbf.hf_cf_cbf_result(input)