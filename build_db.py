from gadget.models import GadgetSimulation, GadgetSnapshot, GadgetIc
from rockstar.models import RockstarCatalogue

sim = GadgetSimulation()
sim.name = 'out512'
sim.location = '/run/media/lbignone/Seagate Expansion Drive/lbignone/simulations/lgzoom/out512'
sim.file_number = 8
sim.snapshot_file_base = 'snapshot'

ic = GadgetIc()
ic.name = 'out512'
ic.fname = '/run/media/lbignone/Seagate Expansion Drive/lbignone/simulations/lgzoom/ics_gadget_512base.dat'
ic.file_number = 1
ic.save()

sim.ic = ic

sim.import_from_location()

snap = GadgetSnapshot.objects.get(simulation=sim, snap_number=14)

catalogue = RockstarCatalogue()
catalogue.snapshot = snap
catalogue.location = '/run/media/lbignone/Seagate Expansion Drive/lbignone/simulations/lgzoom/out512/halos/14/hlist.txt'
catalogue.save()