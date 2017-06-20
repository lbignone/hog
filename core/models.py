from django.db import models
from picklefield.fields import PickledObjectField
from polymorphic.models import PolymorphicModel
from django.conf import settings

from core.utils import region_filename


class Simulation(PolymorphicModel):

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    Omega_m = models.FloatField(blank=True, null=True)
    Omega_l = models.FloatField(blank=True, null=True)
    h = models.FloatField(blank=True, null=True)

    ic = models.ForeignKey('core.Ic', on_delete=models.PROTECT,
                           blank=True, null=True)

    def __str__(self):
        return self.name


class Snapshot(PolymorphicModel):

    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    snap_number = models.IntegerField()

    def __str__(self):
        return self.simulation.name + '/' + str(self.snap_number)


class Ic(PolymorphicModel):
    name = models.CharField(max_length=200)
    fname = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Catalogue(PolymorphicModel):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.PROTECT)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        text = str(self.snapshot)
        text += '/' + 'Catalogue'
        return text


class Structure(PolymorphicModel):
    catalogue = models.ForeignKey(Catalogue)


class Region(PolymorphicModel):
    name = models.CharField(max_length=200, blank=False)
    snapshot = models.ForeignKey(Snapshot, on_delete=models.PROTECT,
                                 blank=True, null=True)

    structure = models.ForeignKey(Structure, on_delete=models.PROTECT,
                                  blank=True, null=True)

    rtb_help = """Search radius equals rtb * Rvir"""
    rtb = models.FloatField(help_text=rtb_help, blank=True, null=True)

    region_point_file = models.FileField(upload_to=region_filename, blank=True,
                                         null=True)

    xc = models.FloatField(blank=True, null=True)
    yc = models.FloatField(blank=True, null=True)
    zc = models.FloatField(blank=True, null=True)

    N = models.IntegerField(blank=True, editable=False, null=True)

    V = models.FloatField(blank=True, editable=False, null=True)
    V_norm = models.FloatField(blank=True, editable=False, null=True)

    def __str__(self):
        return self.name

    def get_path(self):
        """
        Get path to the folder corresponding to the region.

        """
        root = settings.MEDIA_ROOT
        path = root + '/regions/{id:d}_{name:s}/'
        path = path.format(id=self.id, name=self.name)

        return path

    def get_point_filename(self):
        """
        Get full path to the region point file.

        """
        path = self.get_path()
        fname = path + 'region_point_file.txt'

        return fname


class EllipsoidRegion(Region):

    A_arr = PickledObjectField(blank=True, editable=False, null=True)

    a = models.FloatField(blank=True, null=True)
    b = models.FloatField(blank=True, null=True)
    c = models.FloatField(blank=True, null=True)


class BoxRegion(Region):

    ext_x = models.FloatField(blank=True, null=True)
    ext_y = models.FloatField(blank=True, null=True)
    ext_z = models.FloatField(blank=True, null=True)
