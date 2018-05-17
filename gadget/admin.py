from django.contrib import admin

from .models import GadgetSimulation, GadgetRun, Gadget3Run, GadgetSnapshot, GadgetIc
from .utils import makefile_options, new_makefile_options

import easy


def import_from_location(modeladmin, request, queryset):
    for obj in queryset:
        obj.import_from_location()


def import_from_fname(modeladmin, request, queryset):
    for obj in queryset:
        obj.import_from_location()


class GadgetSimulationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'location',
        'snapshot_file_base',
        'file_number',

        'boxlength',
        'Omega_m',
        'Omega_l',
        'Omega_b',
        'h',

        'mass_gas',
        'mass_halo',
        'mass_disk',
        'mass_buldge',
        'mass_stars',
        'mass_bndry',

        'OUTPUTPOTENTIAL',
        'OUTPUTACCELERATION',
        'OUTPUTCHANGEOFENTROPY',
        'OUTPUTTIMESTEP',

        'sfr',
        'feedback',
        'cooling',
        'stellar_age',
        'metals',
        'entr_ics',
    )

    actions = [import_from_location, ]


class GadgetRunAdmin(GadgetSimulationAdmin):

    raw_id_fields = ("ic",)
    fk1 = easy.ForeignKeyAdminField('ic')

    fieldsets = [(None, {'fields': ['name',
                                    'category',
                                    'ic',
                                    ]}),
                 ('MAKEFILE options', {'fields': makefile_options}),
                 ('Filenames and file formats', {'fields': ['OutputDir',
                                                           'SnapFormat',
                                                           'snapshot_file_base',
                                                           'file_number',
                                                           'InitCondFile',
                                                           'ICFormat',
                                                           'EnergyFile',
                                                           'InfoFile',
                                                           'TimingsFile',
                                                           'CpuFile',
                                                           'RestartFile',]}),
                 ('CPU-time limit and restart', {'fields': ['TimeLimitCPU',
                                                            'ResubmitCommand',
                                                            'ResubmitOn',
                                                            'CpuTimeBetRestartFile',]}),
                 ('Simulation specific parameters', {'fields': ['TimeBegin',
                                                                'TimeMax',
                                                                'boxlength',
                                                                'PeriodicBoundariesOn',
                                                                'ComovingIntegrationOn',]}),
                 ('Cosmological parameters', {'fields': ['Omega_m',
                                                         'Omega_l',
                                                         'Omega_b',
                                                         'h',]}),
                 ('Memory allocation', {'fields': ['BufferSize',
                                                   'PartAllocFactor',
                                                   'TreeAllocFactor',]}),
                 ('Gravitational force accuracy', {'fields': ['TypeOfOpeningCriterion',
                                                              'ErrTolTheta',
                                                              'ErrTolForceAcc',]}),
                 ('Time integration accuracy', {'fields': ['MaxSizeTimestep',
                                                           'MinSizeTimestep',
                                                           'TypeOfTimestepCriterion',
                                                           'ErrTolIntAccuracy',
                                                           'TreeDomainUpdateFrequency',
                                                           'MaxRMSDisplacementFac',]}),
                 ('Output of snapshot files', {'fields': ['OutputListOn',
                                                          'OutputListFilename',
                                                          'TimeOfFirstSnapshot',
                                                          'TimeBetSnapshot',
                                                          'TimeBetStatistics',
                                                          'NumFilesWrittenInParallel']}),
                 ('System of units', {'fields': ['velocity_in_cm_per_s',
                                                 'length_in_cm',
                                                 'mass_in_g',
                                                 'GravityConstantInternal',]}),
                 ('SPH parameters', {'fields': ['DesNumNgb',
                                                'MaxNumNgbDeviation',
                                                'ArtBulkViscConst',
                                                'CourantFac',
                                                'InitGasTemp',
                                                'MinGasTemp',
                                                'MinGasHsmlFractional',]}),
                 ('Gravitational softening', {'fields': ['SofteningGas',
                                                         'SofteningHalo',
                                                         'SofteningDisk',
                                                         'SofteningBulge',
                                                         'SofteningStars',
                                                         'SofteningBndry',
                                                         'SofteningGasMaxPhys',
                                                         'SofteningHaloMaxPhys' ,
                                                         'SofteningDiskMaxPhys' ,
                                                         'SofteningBulgeMaxPhys',
                                                         'SofteningStarsMaxPhys',
                                                         'SofteningBndryMaxPhys',]}),
                  ('Others', {'fields': ['sfr',
                                         'feedback',
                                         'cooling',
                                         'metals',
                                         'entr_ics']}),
                ]


    list_filter = ('category', )
    search_fields = ['name', 'id']


class Gadget3RunAdmin(GadgetRunAdmin):

    fieldsets = [(None, {'fields': ['name',
                                    'category',
                                    'ic',
                                    ]}),
                 ('MAKEFILE options', {'fields': new_makefile_options}),
                 ('Filenames and file formats', {'fields': ['OutputDir',
                                                           'SnapFormat',
                                                           'snapshot_file_base',
                                                           'file_number',
                                                           'InitCondFile',
                                                           'ICFormat',
                                                           'EnergyFile',
                                                           'InfoFile',
                                                           'TimingsFile',
                                                           'CpuFile',
                                                           'RestartFile',
                                                           'TimebinFile',]}),
                 ('CPU-time limit and restart', {'fields': ['TimeLimitCPU',
                                                            'ResubmitCommand',
                                                            'ResubmitOn',
                                                            'CpuTimeBetRestartFile',]}),
                 ('Simulation specific parameters', {'fields': ['TimeBegin',
                                                                'TimeMax',
                                                                'boxlength',
                                                                'PeriodicBoundariesOn',
                                                                'ComovingIntegrationOn',]}),
                 ('Cosmological parameters', {'fields': ['Omega_m',
                                                         'Omega_l',
                                                         'Omega_b',
                                                         'h',]}),
                 ('Memory allocation', {'fields': ['BufferSize',
                                                   'PartAllocFactor',
                                                   'TreeAllocFactor',
                                                   'MaxMemSize',]}),
                 ('Gravitational force accuracy', {'fields': ['TypeOfOpeningCriterion',
                                                              'ErrTolTheta',
                                                              'ErrTolForceAcc',]}),
                 ('Time integration accuracy', {'fields': ['MaxSizeTimestep',
                                                           'MinSizeTimestep',
                                                           'TypeOfTimestepCriterion',
                                                           'ErrTolIntAccuracy',
                                                           'TreeDomainUpdateFrequency',
                                                           'MaxRMSDisplacementFac',]}),
                 ('Output of snapshot files', {'fields': ['OutputListOn',
                                                          'OutputListFilename',
                                                          'TimeOfFirstSnapshot',
                                                          'TimeBetSnapshot',
                                                          'TimeBetStatistics',
                                                          'NumFilesWrittenInParallel']}),
                 ('System of units', {'fields': ['velocity_in_cm_per_s',
                                                 'length_in_cm',
                                                 'mass_in_g',
                                                 'GravityConstantInternal',]}),
                 ('SPH parameters', {'fields': ['DesNumNgb',
                                                'MaxNumNgbDeviation',
                                                'ArtBulkViscConst',
                                                'CourantFac',
                                                'InitGasTemp',
                                                'MinGasTemp',
                                                'MinGasHsmlFractional',]}),
                 ('Gravitational softening', {'fields': ['SofteningGas',
                                                         'SofteningHalo',
                                                         'SofteningDisk',
                                                         'SofteningBulge',
                                                         'SofteningStars',
                                                         'SofteningBndry',
                                                         'SofteningGasMaxPhys',
                                                         'SofteningHaloMaxPhys' ,
                                                         'SofteningDiskMaxPhys' ,
                                                         'SofteningBulgeMaxPhys',
                                                         'SofteningStarsMaxPhys',
                                                         'SofteningBndryMaxPhys',]}),
                  ('Others', {'fields': ['sfr',
                                         'feedback',
                                         'cooling',
                                         'metals',
                                         'entr_ics']}),
                  ('More parameterfile options', {'fields': ['CoolingOn',
                                                             'StarformationOn',
                                                             'FactorSFR',
                                                             'CritOverDensity',
                                                             'CritPhysDensity',
                                                             'DecouplingParam',
                                                             'TlifeSNII',
                                                             'Raiteri_TlifeSNII',
                                                             'MinTlifeSNI',
                                                             'MaxTlifeSNI',
                                                             'RateSNI',
                                                             'SN_Energy_cgs',
                                                             'Tcrit_Phase',
                                                             'DensFrac_Phase',
                                                             'SN_Energy_frac_cold',
                                                             'MaxHotHsmlParam',
                                                             'InitialHotHsmlFactor',
                                                             'MaxNumHotNgbDeviation',
                                                             'MaxSfrTimescale',
                                                             'TempSupernova',
                                                             'TempClouds',
                                                             'FactorSN',
                                                             'FactorEVP',
                                                             'WindEfficiency',
                                                             'WindFreeTravelLength',
                                                             'WindEnergyFraction',
                                                             'WindFreeTravelDensFac']}),
                  ('Artificial Conductivity', {'fields': ['ArtCondConstant',
                                                          'ArtCondMin']}),
                  ('Artificial Viscosity', {'fields': ['ViscositySourceScaling',
                                                       'ViscosityDecayLength',
                                                       'ViscosityAlphaMin']}),                                                           
                ]


class GadgetSnapshotAdmin(admin.ModelAdmin):

    list_display = (
        'simulation',
        'snap_number',
        'redshift',
        'cosmic_time',
        'n_gas',
        'n_halo',
        'n_disk',
        'n_buldge',
        'n_stars',
        'n_bndry',
    )

    list_filter = ('simulation', )


admin.site.register(GadgetSimulation, GadgetSimulationAdmin)
admin.site.register(GadgetRun, GadgetRunAdmin)
admin.site.register(Gadget3Run, Gadget3RunAdmin)
admin.site.register(GadgetSnapshot, GadgetSnapshotAdmin)
admin.site.register(GadgetIc)
