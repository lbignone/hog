from django.contrib import admin

from .models import GadgetSimulation, GadgetSnapshot, GadgetIc


def import_from_location(modeladmin, request, queryset):
    for obj in queryset:
        obj.import_from_location()


def import_from_fname(modeladmin, request, queryset):
    for obj in queryset:
        obj.import_from_location()


class GadgetSimulationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'location',
        'snapshot_file_base',
        'file_number',

        'boxlength',
        'Omega_m',
        'Omega_l',
        'h',

        'mass_gas',
        'mass_halo',
        'mass_disk',
        'mass_buldge',
        'mass_stars',
        'mass_bndry',

        'pot',
        'accel',
        'endt',
        'tstp',

        'sfr',
        'feedback',
        'cooling',
        'stellar_age',
        'metals',
        'entr_ics',
    )

    actions = [import_from_location, ]


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
admin.site.register(GadgetSnapshot, GadgetSnapshotAdmin)
admin.site.register(GadgetIc)
