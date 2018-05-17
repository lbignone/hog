from django.db import models
from django.db import transaction
from django.conf import settings

from gadget import pygadget

from core.models import Simulation, Snapshot, Ic

import glob

from gadget.utils import read_block, get_region_in_radius, get_pos_from_ids

from astropy import units as u


class GadgetSimulation(Simulation):

    snapshot_file_base = models.CharField(max_length=200, default='snapshot')
    file_number = models.IntegerField(blank=False, default=1)

    OUTPUTPOTENTIAL = models.BooleanField(default=False)
    OUTPUTACCELERATION = models.BooleanField(default=False)
    OUTPUTCHANGEOFENTROPY = models.BooleanField(default=False)
    OUTPUTTIMESTEP = models.BooleanField(default=False)

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

    boxlength = models.FloatField(blank=True, null=True, default=10000.0)

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


class GadgetRun(GadgetSimulation):

    # MAKEFILE options
    # Basic operation mode of code
    PERIODIC = models.BooleanField(default=True)
    UNEQUALSOFTENINGS = models.BooleanField(default=False)

    # Things that are always recommended
    PEANOHILBERT = models.BooleanField(default=True)
    WALLCLOCK = models.BooleanField(default=True)

    # TreePM options
    PMGRID = models.IntegerField(default=128)
    PLACEHIGHRESREGION = models.IntegerField(null=True, blank=True)
    ENLARGEREGION = models.FloatField(null=True, blank=True)
    ASMTH = models.FloatField(default=1.25)
    RCUT = models.FloatField(default=4.5)

    # Single/double precision
    DOUBLEPRECISION = models.BooleanField(default=False)
    DOUBLEPRECISION_FFTW = models.BooleanField(default=False)

    # Time integration options
    SYNCHRONIZATION = models.BooleanField(default=True)
    FLEXSTEPS = models.BooleanField(default=False)
    PSEUDOSYMMETRIC = models.BooleanField(default=False)
    NOSTOP_WHEN_BELOW_MINTIMESTEP = models.BooleanField(default=False)
    NOPMSTEPADJUSTMENT = models.BooleanField(default=False)

    # Output options
    HAVE_HDF5 = models.BooleanField(default=False)
    # OUTPUTPOTENTIAL
    # OUTPUTACCELERATION
    # OUTPUTCHANGEOFENTROPY
    # OUTPUTTIMESTEP

    # Things for special behaviour
    LONGIDS = models.BooleanField(default=False)

    # Parameterfile options
    # Filenames and file formats
    OutputDir = models.CharField(max_length=200)
    # SnapshotFileBase
    SnapFormat = models.IntegerField(default=1)
    # NumFilesPerSnapshot
    InitCondFile = models.CharField(max_length=200)
    ICFormat = models.IntegerField(default=1)
    EnergyFile = models.CharField(max_length=200, default='energy.txt')
    InfoFile = models.CharField(max_length=200, default='info.txt')
    TimingsFile = models.CharField(max_length=200, default='timings.txt')
    CpuFile = models.CharField(max_length=200, default='cpu.txt')
    RestartFile = models.CharField(max_length=200, default='restart.txt')

    # CPU-time limit and restart options
    TimeLimitCPU = models.FloatField(default=2.4e+06)
    ResubmitCommand = models.CharField(max_length=200, default='my-scriptfile')
    ResubmitOn = models.BooleanField(default=False)
    CpuTimeBetRestartFile = models.FloatField(default=15000)
    
    # Simulation specific parameters
    TimeBegin = models.FloatField(default=0.0163934)
    TimeMax = models.FloatField(default=1)
    # BoxSize
    PeriodicBoundariesOn = models.BooleanField(default=True)
    ComovingIntegrationOn = models.BooleanField(default=True)

    # Cosmological parameters
    # HubbleParam
    # Omega0
    # OmegaLambda
    # OmegaBaryon

    # Memory allocation
    BufferSize = models.FloatField(default=400)
    PartAllocFactor = models.FloatField(default=32)
    TreeAllocFactor = models.FloatField(default=0.7)

    # Gravitational force accuracy
    TypeOfOpeningCriterion = models.IntegerField(default=1)
    ErrTolTheta = models.FloatField(default=0.6)
    ErrTolForceAcc = models.FloatField(default=0.0025)

    # Time integration accuracy
    MaxSizeTimestep = models.FloatField(default=0.0125)
    MinSizeTimestep = models.FloatField(default=0)
    TypeOfTimestepCriterion = models.IntegerField(default=0)
    ErrTolIntAccuracy = models.FloatField(default=0.025)
    TreeDomainUpdateFrequency = models.FloatField(default=0.1)
    MaxRMSDisplacementFac = models.FloatField(default=0.125)

    # Output of snapshot files
    OutputListOn = models.BooleanField(default=False)
    OutputListFilename = models.CharField(max_length=200, default='output_times.txt')
    TimeOfFirstSnapshot = models.FloatField(default=0.047619048)
    TimeBetSnapshot = models.FloatField(default=1.0627825)
    TimeBetStatistics = models.FloatField(default=0.1)
    NumFilesWrittenInParallel = models.IntegerField(default=16)

    # System of units
    UnitVelocity_in_cm_per_s = models.FloatField(default=1e5)
    UnitLength_in_cm = models.FloatField(default=3.085678e21)
    UnitMass_in_g = models.FloatField(default=1.989e43)
    GravityConstantInternal = models.BooleanField(default=False)

    # SPH parameters
    DesNumNgb = models.IntegerField(default=64)
    MaxNumNgbDeviation = models.IntegerField(default=2)
    ArtBulkViscConst = models.FloatField(default=1.0)
    CourantFac = models.FloatField(default=0.15)
    InitGasTemp = models.FloatField(default=1e4)
    MinGasTemp = models.FloatField(default=20)
    MinGasHsmlFractional = models.FloatField(default=0.1)

    # Gravitational softening
    SofteningGas = models.FloatField(default=0)
    SofteningHalo = models.FloatField(default=18)
    SofteningDisk = models.FloatField(default=90)
    SofteningBulge = models.FloatField(default=450)
    SofteningStars = models.FloatField(default=0)
    SofteningBndry = models.FloatField(default=0)

    SofteningGasMaxPhys = models.FloatField(default=0)
    SofteningHaloMaxPhys = models.FloatField(default=3)
    SofteningDiskMaxPhys = models.FloatField(default=15)
    SofteningBulgeMaxPhys = models.FloatField(default=75)
    SofteningStarsMaxPhys = models.FloatField(default=0)
    SofteningBndryMaxPhys = models.FloatField(default=0)

    def get_path(self):
        root = settings.MEDIA_ROOT
        path = root + '/gadget/run/{id:d}_{name:s}/'
        path = path.format(id=self.id, name=self.name)
        return path

    def get_makefile_path(self):
        path = self.get_path()
        fname = path + 'Makefile'
        return fname

    def get_config_path(self):
        path = self.get_path()
        fname = path + '{id:d}_{name:s}.param'
        return fname.format(id=self.id, name=self.name)


class Gadget3Run(GadgetRun):

    # Makefile options

    # Kernel
    WENDLAND_C4_KERNEL = models.BooleanField(default=True)
    WC4_BIAS_CORRECTION = models.BooleanField(default=True)

    MYSORT = models.BooleanField(default=True)
    MOREPARAMS = models.BooleanField(default=True)
    
    NO_ISEND_IRECV_IN_DOMAIN = models.BooleanField(default=False)
    NO_ISEND_IRECV_IN_PM = models.BooleanField(default=False)
    FIX_PATHSCALE_MPI_STATUS_IGNORE_BUG = models.BooleanField(default=False)

    # Artificial Viscosity
    TIME_DEP_ART_VISC = models.BooleanField(default=True)
    AB_ART_VISC = models.FloatField(default=4.0)

    # Artificial Conductiviy
    ARTIFICIAL_CONDUCTIVITY = models.BooleanField(default=True)
    TIME_DEP_ART_COND = models.FloatField(default=1.0)
    AB_COND_GRAVITY = models.FloatField(default=5.0)

    # Timestep options
    WAKEUP = models.FloatField(default=4.0)

    # Cecilia 's model
    CS_MODEL = models.BooleanField(default=True)      
    CS_FEEDBACK = models.BooleanField(default=True)
    CS_SNI = models.BooleanField(default=True)
    CS_SNII = models.BooleanField(default=True)
    CS_ENRICH = models.BooleanField(default=True)
    CS_TESTS = models.BooleanField(default=False)

    # More parameterfile options
    CoolingOn = models.BooleanField(default=False)
    StarformationOn = models.BooleanField(default=False)
    FactorSFR = models.FloatField(default=0.1)
    CritOverDensity = models.FloatField(default=57.7)
    CritPhysDensity = models.FloatField(default=0.318)
    DecouplingParam = models.FloatField(default=50)                   
    TlifeSNII = models.FloatField(default=0)
    Raiteri_TlifeSNII = models.FloatField(default=1)
    MinTlifeSNI = models.FloatField(default=1e8)
    MaxTlifeSNI = models.FloatField(default=1.1e9)
    RateSNI = models.FloatField(default=0.0015)
    SN_Energy_cgs = models.FloatField(default=7e50)
    Tcrit_Phase = models.FloatField(default=80000)
    DensFrac_Phase = models.FloatField(default=0.1)
    SN_Energy_frac_cold = models.FloatField(default=0.5)
    MaxHotHsmlParam = models.FloatField(default=10)
    InitialHotHsmlFactor  = models.FloatField(default=5)
    MaxNumHotNgbDeviation = models.FloatField(default=10)
    MaxSfrTimescale = models.FloatField(default=1.5)
    TempSupernova = models.FloatField(default=1e8)
    TempClouds = models.FloatField(default=1000)
    FactorSN = models.FloatField(default=0.1)
    FactorEVP = models.FloatField(default=1000)
    WindEfficiency = models.FloatField(default=2)
    WindFreeTravelLength = models.FloatField(default=20)
    WindEnergyFraction = models.FloatField(default=1)
    WindFreeTravelDensFac = models.FloatField(default=0.1)

    # Other parameters
    TimebinFile = models.CharField(max_length=200, default='timebins.txt')
    MaxMemSize = models.FloatField(default=3500)
    
    # Artificial Conductivity
    ArtCondConstant = models.FloatField(default=1.0)
    ArtCondMin = models.FloatField(default=0.0)

    # Artificial Viscosity
    ViscositySourceScaling = models.FloatField(default=0.0)
    ViscosityDecayLength = models.FloatField(default=4.0)
    ViscosityAlphaMin = models.FloatField(default=0.025)

    def get_makefile_path(self):
        path = self.get_path()
        fname = path + 'Config.sh'
        return fname

    def get_systype_path(self):
        path = self.get_path()
        fname = path + 'Makefile.systype'
        return fname

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
