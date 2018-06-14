from fluidimage.topologies.experimental.piv import TopologyPIV
from fluidimage.topologies.experimental.executer_await_multiproc import ExecuterAwaitMultiprocs
import os

params = TopologyPIV.create_default_params()

params.series.path = '../../../image_samples/Karman/Images2'
params.series.ind_start = 1

params.piv0.shape_crop_im0 = 32
params.multipass.number = 2
params.multipass.use_tps = True

# params.saving.how has to be equal to 'complete' for idempotent jobs
# (on clusters)
params.saving.how = 'complete'
params.saving.postfix = 'piv_complete'


topology = TopologyPIV(params, logging_level='info')
#topology.make_code_graphviz('topo.dot')

topology.compute(executer=ExecuterAwaitMultiprocs(topology), sequential=True)