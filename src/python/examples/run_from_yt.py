########################################################################
#
# yt wrapper for grackle example script
#
#
# Copyright (c) 2013, Enzo/Grackle Development Team.
#
# Distributed under the terms of the Enzo Public Licence.
#
# The full license is in the file LICENSE, distributed with this
# software.
########################################################################

import numpy as np
import os
import yt

from pygrackle import \
    chemistry_data, \
    grid_to_grackle

from pygrackle.fluid_container import \
    _yt_to_grackle

DS_NAME = "IsolatedGalaxy/galaxy0030/galaxy0030"

if 'YT_DATA_DIR' in os.environ:
    ds_path = os.sep.join([os.environ['YT_DATA_DIR'], DS_NAME])
else:
    ds_path = DS_NAME

ds = yt.load(ds_path)

my_chemistry = chemistry_data()
my_chemistry.use_grackle = 1
my_chemistry.primordial_chemistry = 1
my_chemistry.metal_cooling = 1
my_chemistry.self_shielding_method = 0
my_chemistry.H2_self_shielding = 0
my_dir = os.path.dirname(os.path.abspath(__file__))
grackle_data_file = bytearray(os.path.join(
    my_dir, "..", "..", "..", "input", "CloudyData_UVB=HM2012.h5"), 'utf-8')
my_chemistry.grackle_data_file = grackle_data_file

my_chemistry.comoving_coordinates = 0
my_chemistry.density_units = (ds.mass_unit / ds.length_unit**3).d
my_chemistry.length_units = ds.length_unit.d
my_chemistry.time_units = ds.time_unit.d
my_chemistry.velocity_units = (ds.length_unit / ds.time_unit).d
my_chemistry.a_units = 1.0
my_chemistry.a_value = 1.0

my_chemistry.initialize()

g = ds.index.grids[0]
old = dict((f, g[f].copy()) for f in ds.field_list)

dt = ds.quan(1, 'Myr').to('code_time').d
for fc in grid_to_grackle(my_chemistry, g):
    fc.solve_chemistry(dt)

for f in old:
    if f not in _yt_to_grackle: continue
    delta = np.abs(g[f] - old[f])/g[f]
    print(f, delta.min(), delta.max())
