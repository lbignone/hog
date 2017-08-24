from django.db import models

from gadget.models import GadgetIc
from core.models import Ic, BoxRegion, EllipsoidRegion
from polymorphic.models import PolymorphicModel
from django.conf import settings


class MusicRegion(PolymorphicModel):
    _point_filename = None
    pass

    # def __str__(self):
    #   return self.region.__str__()


class MusicBoxRegion(MusicRegion):
    region = models.ForeignKey(BoxRegion, on_delete=models.PROTECT,
                               blank=False)

    @property
    def region_type(self):
        return 'box'


class MusicEllipsoidRegion(MusicRegion):

    region = models.ForeignKey(EllipsoidRegion, on_delete=models.PROTECT,
                               blank=False)

    region_point_shift_help = """[optional] If the simulation from which the
    coordinates in region_point_file have been determined was already a zoom
    simulation, the coordinates in the IC file need to be shifted back to
    their original position (the zoom region had been centered). Specify here
    the shift that was applied in the centering of the zoom region, as has
    been output by MUSIC in the line, e.g. - Domain will be shifted by (-12,
    -12, -12) If you specify the shift, also the levelmin of that simulation
    needs to be specified as below"""

    region_point_shift = models.CharField(max_length=200, blank=True,
                                          help_text=region_point_shift_help)

    region_levelmin_help = """[optional, but req. if region_point_shift is
    specified] The levelmin of the zoom-in simulation that has been run to
    determine the points that determine the region"""

    region_point_levelmin = models.CharField(max_length=200, blank=True,
                                             help_text=region_levelmin_help)

    @property
    def region_type(self):
        return 'ellipsoid'

    def get_path(self):
        return self.region.get_path()

    @property
    def region_point_file(self):
        if self._point_filename is None:
            self._point_filename = self.region.get_point_filename()
        
        return self._point_filename

    def __str__(self):
        return self.region.__str__()


class MusicIc(models.Model):

    # executable = models.ForeignKey(Music_build, blank=True)

    # [setup]

    boxlength_help = 'The size of the full simulation box in comoving Mpc/h'
    boxlength = models.FloatField(blank=False, help_text=boxlength_help)

    zstart_help = 'The starting redshift for the simulation'
    zstart = models.FloatField(blank=False)

    region = models.ForeignKey(MusicRegion, on_delete=models.PROTECT)

    levelmin_help = """The level of the coarse grid which covers the full
    simulation box. The number specified is the 2-log of the number of grid
    cells per dimension, e.g. a level of 7 corresponds to 2^7=128
    cells/dimension"""

    levelmin = models.IntegerField(blank=False, help_text=levelmin_help)

    levelmax_help = """The maximum refinement level in the simulation. This
    value has to be larger or equal to levelmin. This sets the effective
    resolution in the refinement region to 2 levelmax cells/dimension"""

    levelmax = models.IntegerField(blank=False, help_text=levelmax_help)

    levelmin_TF_help = """The level of the coarse grid when the density grid
    is computed (the convolution with the transfer function is performed).
    This can be set to a number larger than levelmin, the density field will
    be averaged down after the convolution has been performed and the Poisson
    solver is invoked. Essentially, this improves the accuracy of the coarser
    density modes when a low resolution in the coarsest level is desired in
    the final simulation"""

    levelmin_TF = models.IntegerField(blank=False, help_text=levelmin_TF_help)

    force_equal_extent_help = """Forces the refinement region to be a cube
    with edge length equal to the largest length determined from the region
    parameters"""

    force_equal_extent = models.BooleanField(blank=False, default=False,
                                             help_text=force_equal_extent_help)

    padding_help = """Number of grid cells in intermediate levels (when using
    levelmax>levelmin+1) surrounding the nested grids. The extent of an
    intermediate level is N/2+2*padding if N is the number of cells in the
    next finer level"""

    padding = models.IntegerField(blank=False, help_text=padding_help)

    overlap_help = """Number of extra padding cells for subgrids when
    computing the transfer function convolutions. These are discarded when
    computing the displacements but greatly reduce errors due to boundary
    effects"""

    overlap = models.IntegerField(blank=False, help_text=overlap_help)

    blocking_factor_help = """ This parameter can be used to require the
    dimensions of initial grids to be multiples of blocking_factor. Not used
    if parameter is not present. This is mainly necessary to optimize for
    block based AMR"""

    blocking_factor = models.IntegerField(blank=True, null=True,
                                          help_text=blocking_factor_help)

    align_top_help = """ Require subgrids to be always aligned with the
    coarsest grid? This is necessary for some codes (ENZO) but not for others
    (Gadget)"""

    align_top = models.BooleanField(blank=False, default=False,
                                    help_text=align_top_help)

    periodic_TF_help = """ This controls whether the transfer function kernel
    is periodic or not. The convolution is always periodic. Should be set to
    yes"""

    periodic_TF = models.BooleanField(blank=False, default=True,
                                      help_text=periodic_TF_help)

    baryons_help = """Set to yes if also initial conditions for baryons shall
    be generated"""

    baryons = models.BooleanField(blank=False, default=False,
                                  help_text=baryons_help)

    use_2LPT_help = """Set to yes if 2nd order Lagrangian perturbation theory
    shall be used to compute particle displacements and velocities"""

    use_2LPT = models.BooleanField(blank=False, default=False,
                                   help_text=use_2LPT_help)

    use_LLA_help = """Set to yes if the baryonic density field shall be
    computed using a second order expansion of the local Lagrangian
    approximation (LLA). See Section 5.3 in Hahn & Abel (2011)"""

    use_LLA = models.BooleanField(blank=False, default=False,
                                  help_text=use_LLA_help)

    center_vel_help = """Experimental feature to give the subvolume a kick
    opposite to its predicted motion over time to minimize movement of the
    high-resolution region with respect to the grid rest frame"""

    center_vel = models.BooleanField(blank=False, default=False,
                                     help_text=center_vel_help)

    # [cosmology]

    Omega_m_help = """The total matter density parameter (now)"""
    Omega_m = models.FloatField(blank=False, help_text=Omega_m_help)

    Omega_L_help = """The cosmological constant density parameter (now)"""
    Omega_L = models.FloatField(blank=False, help_text=Omega_L_help)

    Omega_b_help = """The baryon density parameter (now)"""
    Omega_b = models.FloatField(blank=False, help_text=Omega_b_help)

    H0_help = """The Hubble constant (now), in km/s/Mpc"""
    H0 = models.FloatField(blank=False, help_text=H0_help)

    sigma_8_help = """Normalization of the power spectrum"""
    sigma_8 = models.FloatField(blank=False, help_text=sigma_8_help)

    nspec_help = """Power law index of the density perturbation spectrum after
    inflation"""
    nspec = models.FloatField(blank=False, help_text=nspec_help)

    transfer_help = """Name of the transfer function plug-in to be used.
    Depending on the choice, there are different additional parameters that
    need to be set. MUSIC comes with the following default plug-ins: BBKS -
    for the Bardeen... fit to the transfer function without baryon features.
    eisenstein - for the Eisenstein & Hu (..) fit for the CDM transfer
    function with baryon features CAMB - for CAMB (...) output transfer
    functions (tabulated). The filename of the additional option transfer_file
    has to indicate the file from which the tabulated transfer function shall
    be read"""

    transfer_choices = (
        ('BBKS', 'BBKS'),
        ('eisenstein', 'eisenstein'),
        ('CAMB', 'CAMB'),
    )
    transfer = models.CharField(max_length=200, blank=False,
                                choices=transfer_choices,
                                help_text=transfer_help)

    YHe_help = """Helium abundance. This is used to compute the initial gas
    temperature if baryons are present. (Will only be used if the simulation
    code supports reading temperature fields). Optional. Default value:
    0.248"""

    YHe = models.FloatField(blank=False, default=0.248, help_text=YHe_help)

    gamma_help = """Adiabatic exponent. This is used to compute the initial
    gas temperature if baryons are present. (Will only be used if the
    simulation code supports reading temperature fields). Optional. Default
    value: 5/3"""
    gamma_default = 5. / 3
    gamma = models.FloatField(blank=False, default=gamma_default,
                              help_text=gamma_help)

    # [random]

    # [output]

    filename_help = """name and path of the file (or directory - depending on
    the plug-in) where the output data will be stored"""

    filename = models.CharField(max_length=200,
                                blank=True,
                                help_text=filename_help)

    # [poisson]

    laplace_order_help = """order of the finite difference approximation for
    the Laplacian operator"""

    laplace_order = models.IntegerField(blank=False,
                                        help_text=laplace_order_help)

    grad_order_help = """order of the finite difference approximation for the
    gradient operator"""

    grad_order = models.IntegerField(blank=False,
                                     help_text=grad_order_help)

    accuracy_help = """the residual norm required to establish convergence of
    the multigrid solver"""

    accuracy = models.FloatField(blank=False, help_text=accuracy_help)

    smoother_help = """name of the smoothing sweep method used in the
    multigrid method: gs (Gauss-Seidel), jacobi (Jacobi), sor (Successive
    Overrelaxation)"""

    smoother_choices = (
        ('gs', 'Gauss-Seidel'),
        ('jacobi', 'Jacobi'),
        ('sor', 'Successive Overrelaxation'),
    )

    smoother = models.CharField(max_length=200, blank=False,
                                choices=smoother_choices,
                                help_text=smoother_help)

    pre_smooth_help = """number of pre-smoothing sweeps"""

    pre_smooth = models.IntegerField(blank=False, help_text=pre_smooth_help)

    post_smooth_help = """number of post-smoothing sweeps"""

    post_smooth = models.IntegerField(blank=False, help_text=post_smooth_help)

    fft_fine_help = """controls whether the hybrid Poisson solver shall be
    used (see paper for details)"""

    fft_fine = models.BooleanField(blank=False, default=False,
                                   help_text=fft_fine_help)

    class Meta:
        abstract = True


class MusicGadgetIc(GadgetIc, MusicIc):
    gadget_lunit_choices = (
        ('Mpc', 'Mpc'),
        ('kpc', 'kpc'),
        ('pc', 'pc'),
    )

    gadget_lunit = models.CharField(max_length=200, blank=False,
                                    default='kpc',
                                    choices=gadget_lunit_choices)

    gadget_munit_choices = (
        ('1e10Msol', '1e10Msol'),
        ('Msol', 'Msol'),
        ('Mearth', 'Mearth'),
    )

    gadget_munit = models.CharField(max_length=200, blank=False,
                                    default='1e10Msol',
                                    choices=gadget_munit_choices)

    gadget_vunit_choices = (
        ('km/s', 'km/s'),
        ('m/s', 'm/s'),
        ('cm/s', 'cm/s'),
    )

    gadget_vunit = models.CharField(max_length=200, blank=False,
                                    default='km/s',
                                    choices=gadget_vunit_choices)

    # gadget_num_files_help = """this will split the initial conditions file
    # into several files, necessary for very large particle numbers (> 2^31),
    # or for convenience reasons"""

    # gadget_num_files = models.IntegerField(blank=False, default=1,
    #                                        help_text=gadget_num_files_help)

    gadget_coarsetype_help = """Gadget particle type to be used for coarse
    particles (2,3 or 5), default is 5"""

    gadget_coarsetype = models.IntegerField(blank=False, default=5,
                                            help_text=gadget_coarsetype_help)

    gadget_spreadcoarse = models.BooleanField(blank=False, default=False)

    gadget_longids_help = """Use 64bit integers for particle IDs. Default if
    the parameter is not given is 32bit if less than 2^32 particles, 64bit if
    more"""

    gadget_longids = models.BooleanField(blank=False, default=False,
                                         help_text=gadget_longids_help)

    @property
    def output_format(self):
        return 'gadget2'

    def output_list(self):
        from music.utils import gadget_output_list
        return gadget_output_list(self)

    @property
    def gadget_num_files(self):
        return self.file_number

    def get_path(self):
        """
        Get path to the folder corresponding to the region.

        """
        root = settings.MEDIA_ROOT
        path = root + '/music/{id:d}_{name:s}/'
        path = path.format(id=self.id, name=self.name)

        return path

    def get_config_filename(self):
        """
        Get full path to the region point file.

        """
        path = self.get_path()
        fname = path + '{id:d}_{name:s}' + '.conf'

        return fname.format(id=self.id, name=self.name)

    def get_ic_filename(self):
        """
        Get full path to the region point file.

        """
        path = self.get_path()
        fname = path + self.filename

        return fname


class Seed(models.Model):
    ic = models.ForeignKey(Ic, on_delete=models.CASCADE, blank=False)
    level = models.IntegerField(blank=False)
    value = models.IntegerField(blank=False)

    class Meta:
        unique_together = ('ic', 'level')

