from __future__ import unicode_literals

from django.db import transaction

from django.db import models

import numpy as np

from core.models import Catalogue, Structure

from rockstar.utils import get_region_in_radius

from astropy import units as u

# from rockstar.utils import generate_point_df, region_directory_path


class RockstarCatalogue(Catalogue):

    @transaction.atomic
    def load_halos(self):

        fname = self.location
        data = np.genfromtxt(fname)

        for row in data:

            halo = RockstarHalo(catalogue=self)

            d = {'catalogue': self,
                 'hid': row[0],
                 'descid': row[1],
                 'mvir': row[2],
                 'vmax': row[3],
                 'vrms': row[4],
                 'rvir': row[5],
                 'rs': row[6],
                 'np': row[7],
                 'x': row[8],
                 'y': row[9],
                 'z': row[10],
                 'vx': row[11],
                 'vy': row[12],
                 'vz': row[13],
                 'jx': row[14],
                 'jy': row[15],
                 'jz': row[16],
                 'spin': row[17],
                 'rs_klypin': row[18],
                 'mvir_all': row[19],
                 'm200b': row[20],
                 'm200c': row[21],
                 'm500c': row[22],
                 'm2500c': row[23],
                 'xoff': row[24],
                 'voff': row[25],
                 'spin_bullock': row[26],
                 'b_to_a': row[27],
                 'c_to_a': row[28],
                 'ax': row[29],
                 'ay': row[30],
                 'az': row[31],
                 'b_to_a_500c': row[32],
                 'pid': row[33],
                 }

            halo = RockstarHalo(**d)

            halo.save()

    @property
    def unit_length(self):
        """
        Return internal unit length.

        """
        h = self.snapshot.simulation.h
        unit = u.def_unit('Mpc/h', u.Mpc / h)

        return unit

    @property
    def unit_distance(self):
        """
        Return internal unit distance. Employd for distances and radii.

        """
        h = self.snapshot.simulation.h
        unit = u.def_unit('kpc/h', u.kpc / h)

        return unit

    @property
    def unit_mass(self):
        """
        Return internal unit mass,

        """
        h = self.snapshot.simulation.h
        unit = u.def_unit('solMass/h', u.Msun / h)

        return unit


class RockstarHalo(Structure):

    hid = models.IntegerField()
    descid = models.IntegerField()
    mvir = models.FloatField()
    vmax = models.FloatField()
    vrms = models.FloatField()
    rvir = models.FloatField()
    rs = models.FloatField()
    np = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    vx = models.FloatField()
    vy = models.FloatField()
    vz = models.FloatField()
    jx = models.FloatField()
    jy = models.FloatField()
    jz = models.FloatField()
    spin = models.FloatField()
    rs_klypin = models.FloatField()
    mvir_all = models.FloatField()
    m200b = models.FloatField()
    m200c = models.FloatField()
    m500c = models.FloatField()
    m2500c = models.FloatField()
    xoff = models.FloatField()
    voff = models.FloatField()
    spin_bullock = models.FloatField()
    b_to_a = models.FloatField()
    c_to_a = models.FloatField()
    ax = models.FloatField()
    ay = models.FloatField()
    az = models.FloatField()
    b_to_a_500c = models.FloatField()
    pid = models.IntegerField()

    def __str__(self):
        return str(self.catalogue) + '/' + str(self.hid)

    def get_region_in_radius(self, radius):
        """
        See rockstar.utils.get_region_in_radius.

        """
        return get_region_in_radius(self, radius)

    def get_radius(self):
        """
        Get radius in internal distance units.

        """
        return self.rvir * self.catalogue.unit_distance
