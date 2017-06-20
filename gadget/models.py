from django.db import models
from django.db import transaction

from gadget import pygadget

from core.models import Simulation, Snapshot, Ic

import glob

from gadget.utils import read_block, get_region_in_radius, get_pos_from_ids

from astropy import units as u


class GadgetSimulation(Simulation):

    snapshot_file_base = models.CharField(max_length=200)
    file_number = models.IntegerField(blank=False)

    pot = models.BooleanField(default=False)
    accel = models.BooleanField(default=False)
    endt = models.BooleanField(default=False)
    tstp = models.BooleanField(default=False)

    velocity_in_cm_per_s = models.FloatField(default=1e5)
    length_in_cm = models.FloatField(default=3.085678e21)
    mass_in_g = models.FloatField(default=1.989e43)

    mass_gas = models.FloatField(blank=True, null=True)
    mass_halo = models.FloatField(blank=True, null=True)
    mass_disk = models.FloatField(blank=True, null=True)
    mass_buldge = models.FloatField(blank=True, null=True)
    mass_stars = models.FloatField(blank=True, null=True)
    mass_bndry = models.FloatField(blank=True, null=True)

    sfr = models.BooleanField(default=False)

    feedback = models.BooleanField(default=False)

    cooling = models.BooleanField(default=False)

    boxlength = models.FloatField(blank=True, null=True)

    stellar_age = models.BooleanField(default=False)

    metals = models.BooleanField(default=False)

    entr_ics = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def unit_length(self):
        """
        Return internal unit length

        """
        h = self.h
        unit_length = u.def_unit('gadget_length', self.length_in_cm * u.cm / h)
        return unit_length

    @property
    def unit_mass(self):
        """
        Return internal unit mass

        """
        h = self.h
        unit_mass = u.def_unit('gadget_mass', self.mass_in_g * u.g / h)
        return unit_mass

    def get_box_length(self):
        """
        Return box length in internal simulation units

        """
        return self.boxlength * self.unit_length

    def import_from_location(self):
        """
        Import simulation data and load snapshots based on snapshots located
        in self.location

        """

        fname = self.location + '/' + self.snapshot_file_base + '_000'

        if self.file_number > 1:
            multiple_files = True
        else:
            multiple_files = False

        snap = pygadget.Simulation(fname, pot=self.pot, accel=self.accel,
                                   endt=self.endt, tstp=self.tstp,
                                   multiple_files=multiple_files)

        self.sfr = snap.flags['sfr']
        self.feedback = snap.flags['feedback']
        self.cooling = snap.flags['cooling']
        self.stellar_age = snap.flags['stellar_age']
        self.metals = snap.flags['metals']
        self.entr_ics = snap.flags['entr_ics']

        self.file_number = snap.file_number

        self.boxlength = snap.box_size
        self.Omega_m = snap.omega_matter
        self.Omega_l = snap.omega_lambda
        self.h = snap.h

        self.mass_gas = snap.particle_mass['gas']
        self.mass_halo = snap.particle_mass['halo']
        self.mass_disk = snap.particle_mass['disk']
        self.mass_buldge = snap.particle_mass['buldge']
        self.mass_stars = snap.particle_mass['stars']
        self.mass_bndry = snap.particle_mass['bndry']

        self.save()

        self.load_snapshots()

    @transaction.atomic
    def load_snapshots(self):
        """
        Loads snapshots located in the simulation location

        """

        fname = self.location + '/' + self.snapshot_file_base

        if self.file_number > 1:
            fname += '*.0'
        else:
            fname += '*'

        ls = glob.glob(fname)
        ls.sort()

        for fname in ls:
            self.load_snapshot(fname)

    def load_snapshot(self, fname):
        """
        Load snapshot located at fname

        """

        snap = pygadget.Simulation(fname, pot=self.pot, accel=self.accel,
                                   endt=self.endt, tstp=self.tstp)

        if self.file_number > 1:
            snap_number = int(fname[-5:-2])
        else:
            snap_number = int(fname[-3:])

        d = {'simulation': self,
             'snap_number': snap_number,
             'n_gas': snap.particle_total_numbers['gas'],
             'n_halo': snap.particle_total_numbers['halo'],
             'n_disk': snap.particle_total_numbers['disk'],
             'n_buldge': snap.particle_total_numbers['buldge'],
             'n_stars': snap.particle_total_numbers['stars'],
             'n_bndry': snap.particle_total_numbers['bndry'],
             'cosmic_time': snap.cosmic_time,
             'redshift': snap.redshift,
             }

        s = GadgetSnapshot(**d)
        s.save()


class GadgetSnapshot(Snapshot):

    n_gas = models.IntegerField()
    n_halo = models.IntegerField()
    n_disk = models.IntegerField()
    n_buldge = models.IntegerField()
    n_stars = models.IntegerField()
    n_bndry = models.IntegerField()

    cosmic_time = models.FloatField()
    redshift = models.FloatField()

    @property
    def file_number(self):
        """
        Return the number of files per snapshot

        """

        return self.simulation.file_number

    @property
    def fname(self):
        """
        Return the full fname of the snapshot

        """

        location = self.simulation.location
        snap_number = self.snap_number
        snapshot_file_base = self.simulation.snapshot_file_base

        fname = location + '/' + snapshot_file_base + '_{:03d}'

        fname = fname.format(snap_number)

        return fname

    def get_region_in_radius(self, centre, radius):
        """
        See gadget.utils.get_region_in_radius

        """

        return get_region_in_radius(self, centre, radius)

    def read_block(self, block_type, particle_type):
        """
        See gadget.utils.read_block

        """

        return read_block(self, block_type, particle_type)


class GadgetIc(Ic):
    file_number = models.IntegerField(blank=False)

    def read_block(self, block_type, particle_type, is_IC=True):
        """
        See gadget.utils.read_block

        """
        return read_block(self, block_type, particle_type, is_IC=is_IC)

    def get_pos_by_region(self, reg):
        """
        See gadget.utils.get_pos_from_ids

        """

        return get_pos_from_ids(self, reg)
