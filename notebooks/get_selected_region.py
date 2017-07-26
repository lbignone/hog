from gadget import pygadget
import pandas as pd
from rockstar.models import RockstarCatalogue
from astropy import units as u
from astropy.utils.console import ProgressBar

catalogues = RockstarCatalogue.objects.all()
cat = catalogues[0]
cat_umass = cat.unit_mass
cat_ulength = cat.unit_length
cat_rlength = u.def_unit('kpc/h', cat.unit_length / 1000)
snap_ulength = cat.snapshot.simulation.gadgetsimulation.unit_length

boxlength = cat.snapshot.simulation.get_box_length().to(cat_ulength)

print(boxlength)

# df_selected = pd.read_hdf("selected.hdf5", key='2017-07-20 19:24:04.184707')
df_selected = pd.read_hdf("selected.hdf5", key='2017-07-24 20:16:20.495943')

fname = '/home/lbignone/simulations/lgzoom/out512/snapshot_014'
snap = pygadget.Simulation(fname, multiple_files=True)

radius = 1000

with ProgressBar(len(df_selected), ipython_widget=False) as pbar:
    for hid in df_selected.index:

        center = df_selected[['x', 'y', 'z']].loc[hid]
        center = center.values * cat_ulength.to(snap_ulength)

        ids = snap.select_ids_in_radius(center, radius, 'halo')

        pos = snap.read_block_by_ids('pos', 'halo', ids)

        pos.to_hdf('selected.hdf5', key='s' + str(hid))

        del(pos)

        pbar.update()
