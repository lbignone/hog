from django.contrib import admin

from .models import RockstarCatalogue, RockstarHalo


def import_from_location(modeladmin, request, queryset):
    for obj in queryset:
        obj.load_halos()


def set_region_point_file(modeladmin, request, queryset):
    for obj in queryset:
        obj.set_region_point_file()


class RockstarHaloAdmin(admin.ModelAdmin):
    list_display = (
        'catalogue',
        'hid',
        'descid',
        'mvir',
        'vmax',
        'vrms',
        'rvir',
        'rs',
        'np',
        'x',
        'y',
        'z',
        'vx',
        'vy',
        'vz',
        'jx',
        'jy',
        'jz',
        'spin',
        'rs_klypin',
        'mvir_all',
        'm200b',
        'm200c',
        'm500c',
        'm2500c',
        'xoff',
        'voff',
        'spin_bullock',
        'b_to_a',
        'c_to_a',
        'ax',
        'ay',
        'az',
        'b_to_a_500c',
        'pid',
    )

    search_fields = ['hid']
    list_filter = ('catalogue__snapshot', )


class RockstarCatalogueAdmin(admin.ModelAdmin):

    actions = [import_from_location, ]


admin.site.register(RockstarCatalogue, RockstarCatalogueAdmin)
admin.site.register(RockstarHalo, RockstarHaloAdmin)
